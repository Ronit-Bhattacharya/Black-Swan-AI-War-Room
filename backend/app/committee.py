import asyncio
import json
from typing import Any

from .llm_client import generate_json_with_fallback

ALLOWED_DECISIONS = {"PROCEED", "PROCEED_WITH_CONDITIONS", "DEFER", "REJECT"}


def clean_string_list(value: Any) -> list[str]:
    """Return a clean, duplicate-free list of non-empty strings."""
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        text = str(item).strip()
        if text and text not in result:
            result.append(text)
    return result


def normalise_confidence(value: Any) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        confidence = 0.0
    return round(min(max(confidence, 0.0), 1.0), 2)


def normalise_decision(value: Any) -> str:
    decision = str(value or "DEFER").strip().upper().replace(" ", "_")
    return decision if decision in ALLOWED_DECISIONS else "DEFER"


def get_missing_inputs(
    classification: dict[str, Any],
    research_result: dict[str, Any],
) -> list[str]:
    return list(dict.fromkeys(
        clean_string_list(classification.get("missing_inputs", []))
        + clean_string_list(research_result.get("missing_inputs", []))
    ))


def evidence_is_sufficient(evidence_result: dict[str, Any]) -> bool:
    status = str(evidence_result.get("status", "REVIEW_REQUIRED")).strip().upper()
    try:
        verified_count = int(evidence_result.get("verified_evidence_count", 0))
    except (TypeError, ValueError):
        verified_count = 0
    return status == "PASS" and verified_count > 0


def get_financial_analysis(
    analysis_result: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not isinstance(analysis_result, dict):
        return None
    financial = analysis_result.get("financial")
    return financial if isinstance(financial, dict) and financial else None


def get_critical_scenarios(red_team_result: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = red_team_result.get("compound_scenarios", [])
    if not isinstance(scenarios, list):
        return []
    return [
        item for item in scenarios
        if isinstance(item, dict)
        and str(item.get("severity", "")).strip().upper() == "CRITICAL"
    ]


def deterministic_committee_decision(
    classification: dict[str, Any],
    research_result: dict[str, Any],
    evidence_result: dict[str, Any],
    red_team_result: dict[str, Any],
    analysis_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    missing_inputs = get_missing_inputs(classification, research_result)
    verified_evidence = evidence_is_sufficient(evidence_result)
    requires_financial = bool(classification.get("requires_financial_analysis", False))
    financial_available = get_financial_analysis(analysis_result) is not None
    critical_scenarios = get_critical_scenarios(red_team_result)
    unsupported_claims = clean_string_list(research_result.get("unsupported_claims", []))
    unresolved = list(dict.fromkeys(missing_inputs + unsupported_claims))

    reasons: list[str] = []
    if missing_inputs:
        reasons.append("Critical inputs remain missing.")
    if not verified_evidence:
        reasons.append("Verified source-backed evidence is unavailable.")
    if requires_financial and not financial_available:
        reasons.append("Financial analysis is required but has not been completed.")
    if critical_scenarios:
        reasons.append("Critical hypothetical Red Team scenarios require mitigation.")

    blocked = bool(missing_inputs) or not verified_evidence or (
        requires_financial and not financial_available
    )
    decision = "DEFER" if blocked else "PROCEED_WITH_CONDITIONS"
    if not reasons:
        reasons.append("No deterministic blocking condition was identified.")

    conditions = [
        "Authorised human approval is required.",
        "All critical assumptions must be validated.",
        "Supporting evidence must be reviewed before execution.",
        "Red Team mitigations and reversal conditions must be accepted.",
    ]
    if missing_inputs:
        conditions.append("Resolve all missing inputs before making an irreversible commitment.")
    if not verified_evidence:
        conditions.append("Collect and verify source-backed evidence.")
    if requires_financial and not financial_available:
        conditions.append("Complete deterministic financial analysis.")

    reversal_conditions = clean_string_list(red_team_result.get("reversal_conditions", [])) or [
        "Critical assumptions fail validation.",
        "Risk controls fail required testing.",
        "Expected financial or operational thresholds are breached.",
    ]

    return {
        "decision": decision,
        "confidence": 0.0,
        "executive_summary": (
            "The decision has been deferred pending verified evidence, required analysis and resolution of critical inputs."
            if decision == "DEFER"
            else "The decision may proceed only after all conditions, controls and human approvals are satisfied."
        ),
        "supporting_reasons": reasons,
        "conditions": list(dict.fromkeys(conditions)),
        "reversal_conditions": reversal_conditions,
        "unresolved_questions": unresolved,
        "critical_red_team_findings": critical_scenarios,
        "evidence_gate": "PASS" if verified_evidence else "REVIEW_REQUIRED",
        "human_approval_required": True,
        "approval_status": "PENDING",
        "source_retrieval_performed": bool(research_result.get("source_retrieval_performed", False)),
        "disclaimer": "Decision support only. Final approval must be provided by authorised human stakeholders.",
    }


def build_committee_prompt(
    classification: dict[str, Any],
    research_result: dict[str, Any],
    evidence_result: dict[str, Any],
    red_team_result: dict[str, Any],
    analysis_result: dict[str, Any] | None,
) -> str:
    payload = {
        "classification": classification,
        "research": {
            "status": research_result.get("status"),
            "missing_inputs": research_result.get("missing_inputs", []),
            "unsupported_claims": research_result.get("unsupported_claims", []),
            "source_retrieval_performed": research_result.get("source_retrieval_performed", False),
        },
        "evidence": evidence_result,
        "red_team": red_team_result,
        "deterministic_analysis": analysis_result if isinstance(analysis_result, dict) else {},
    }
    return f"""
You are the Decision Committee Agent for a Black Swan Decision War Room.
Use only the supplied input. Do not invent facts, evidence, sources, calculations,
dates, statistics or probabilities.

Mandatory rules:
- If verified evidence is unavailable, choose DEFER.
- If critical inputs remain missing, choose DEFER.
- If required financial analysis is unavailable, choose DEFER.
- Research plans are not evidence.
- Red Team scenarios are hypothetical, not verified facts.
- Human approval is always required and approval_status must remain PENDING.
- Return exactly one JSON object with no Markdown or outside commentary.

Input:
{json.dumps(payload, ensure_ascii=False, indent=2)}

Return this structure:
{{
  "decision": "PROCEED, PROCEED_WITH_CONDITIONS, DEFER or REJECT",
  "confidence": 0.0,
  "executive_summary": "summary",
  "supporting_reasons": ["reason"],
  "conditions": ["condition"],
  "reversal_conditions": ["condition"],
  "unresolved_questions": ["question"],
  "critical_red_team_findings": [],
  "evidence_gate": "PASS or REVIEW_REQUIRED",
  "human_approval_required": true,
  "approval_status": "PENDING",
  "source_retrieval_performed": false,
  "disclaimer": "Decision support only."
}}
""".strip()


def validate_critical_findings(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    findings: list[dict[str, Any]] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        challenge = str(item.get("challenge", "")).strip()
        if not challenge:
            continue
        findings.append({
            "id": str(item.get("id", f"RT-{index:03d}")).strip() or f"RT-{index:03d}",
            "risk_dimension": str(item.get("risk_dimension", "General uncertainty")).strip() or "General uncertainty",
            "challenge": challenge,
            "severity": str(item.get("severity", "CRITICAL")).strip().upper(),
        })
    return findings


def validate_committee_result(
    raw_result: dict[str, Any],
    fallback: dict[str, Any],
    classification: dict[str, Any],
    research_result: dict[str, Any],
    evidence_result: dict[str, Any],
    analysis_result: dict[str, Any] | None,
) -> dict[str, Any]:
    missing_inputs = get_missing_inputs(classification, research_result)
    verified_evidence = evidence_is_sufficient(evidence_result)
    requires_financial = bool(classification.get("requires_financial_analysis", False))
    financial_available = get_financial_analysis(analysis_result) is not None
    deterministic_block = bool(missing_inputs) or not verified_evidence or (
        requires_financial and not financial_available
    )

    decision = "DEFER" if deterministic_block else normalise_decision(raw_result.get("decision"))
    confidence = normalise_confidence(raw_result.get("confidence"))
    if deterministic_block:
        confidence = min(confidence, 0.49)

    reasons = clean_string_list(raw_result.get("supporting_reasons", fallback["supporting_reasons"])) or fallback["supporting_reasons"]
    conditions = clean_string_list(raw_result.get("conditions", fallback["conditions"])) or fallback["conditions"]
    human_condition = "Authorised human approval is required."
    if human_condition not in conditions:
        conditions.insert(0, human_condition)

    reversal = clean_string_list(raw_result.get("reversal_conditions", fallback["reversal_conditions"])) or fallback["reversal_conditions"]
    unresolved = clean_string_list(raw_result.get("unresolved_questions", fallback["unresolved_questions"]))
    unresolved = list(dict.fromkeys(unresolved + missing_inputs))
    summary = str(raw_result.get("executive_summary", fallback["executive_summary"])).strip() or fallback["executive_summary"]
    disclaimer = str(raw_result.get("disclaimer", fallback["disclaimer"])).strip() or fallback["disclaimer"]

    return {
        "decision": decision,
        "confidence": confidence,
        "executive_summary": summary,
        "supporting_reasons": reasons,
        "conditions": conditions,
        "reversal_conditions": reversal,
        "unresolved_questions": unresolved,
        "critical_red_team_findings": validate_critical_findings(
            raw_result.get("critical_red_team_findings", fallback["critical_red_team_findings"])
        ),
        "evidence_gate": "PASS" if verified_evidence else "REVIEW_REQUIRED",
        "human_approval_required": True,
        "approval_status": "PENDING",
        "source_retrieval_performed": bool(research_result.get("source_retrieval_performed", False)),
        "disclaimer": disclaimer,
        "llm_status": raw_result.get("llm_status", "COMPLETED"),
        "llm_warning": raw_result.get("llm_warning"),
        "llm_model": raw_result.get("llm_model"),
    }


async def generate_committee_decision(
    classification: dict[str, Any],
    evidence_result: dict[str, Any],
    red_team_result: dict[str, Any],
    research_result: dict[str, Any] | None = None,
    analysis_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate a fail-closed recommendation with a bounded Ollama call."""
    safe_research = research_result if isinstance(research_result, dict) else {}
    fallback = deterministic_committee_decision(
        classification=classification,
        research_result=safe_research,
        evidence_result=evidence_result,
        red_team_result=red_team_result,
        analysis_result=analysis_result,
    )
    prompt = build_committee_prompt(
        classification=classification,
        research_result=safe_research,
        evidence_result=evidence_result,
        red_team_result=red_team_result,
        analysis_result=analysis_result,
    )

    print("[COMMITTEE] Ollama generation started.", flush=True)

    try:
        raw_result = await asyncio.wait_for(
            generate_json_with_fallback(
                prompt,
                fallback,
                required_fields=[
                    "decision",
                    "confidence",
                    "executive_summary",
                    "supporting_reasons",
                    "conditions",
                    "reversal_conditions",
                    "unresolved_questions",
                    "evidence_gate",
                    "human_approval_required",
                    "approval_status",
                ],
                temperature=0.1,
                num_ctx=2048,
                num_predict=400,
                force_cpu=True,
                read_timeout=75.0,
                retry_count=0,
            ),
            timeout=90.0,
        )
        print(
            "[COMMITTEE] Ollama generation returned. "
            f"Status: {raw_result.get('llm_status')}",
            flush=True,
        )
    except asyncio.TimeoutError:
        print("[COMMITTEE] Timeout. Using deterministic fallback.", flush=True)
        raw_result = dict(fallback)
        raw_result["llm_status"] = "FALLBACK"
        raw_result["llm_warning"] = "Committee inference exceeded the 90-second agent timeout."
        raw_result["llm_model"] = None
    except Exception as exc:
        print(
            "[COMMITTEE] Ollama failed. Using deterministic fallback. "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )
        raw_result = dict(fallback)
        raw_result["llm_status"] = "FALLBACK"
        raw_result["llm_warning"] = f"{type(exc).__name__}: {exc}"
        raw_result["llm_model"] = None

    result = validate_committee_result(
        raw_result=raw_result,
        fallback=fallback,
        classification=classification,
        research_result=safe_research,
        evidence_result=evidence_result,
        analysis_result=analysis_result,
    )

    print(
        "[COMMITTEE] Result validated. "
        f"Decision: {result.get('decision')}. "
        f"LLM status: {result.get('llm_status')}.",
        flush=True,
    )
    return result
