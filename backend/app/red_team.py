import asyncio
import json

from typing import Any

from .llm_client import generate_json_with_fallback


ALLOWED_SEVERITIES = {
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
}


ALLOWED_LIKELIHOODS = {
    "RARE",
    "UNLIKELY",
    "POSSIBLE",
    "LIKELY",
    "UNKNOWN",
}


def clean_string_list(
    value: Any,
) -> list[str]:
    """
    Convert a model-generated value into a clean,
    duplicate-free list of strings.
    """

    if not isinstance(value, list):
        return []

    cleaned_items: list[str] = []

    for item in value:
        text = str(item).strip()

        if text and text not in cleaned_items:
            cleaned_items.append(text)

    return cleaned_items


def normalise_severity(
    value: Any,
) -> str:
    """
    Restrict severity to a controlled set of values.
    """

    severity = str(
        value or "HIGH"
    ).strip().upper()

    if severity not in ALLOWED_SEVERITIES:
        return "HIGH"

    return severity


def normalise_likelihood(
    value: Any,
) -> str:
    """
    Restrict likelihood to a controlled qualitative scale.

    The Red Team must not invent numerical probabilities.
    """

    likelihood = str(
        value or "UNKNOWN"
    ).strip().upper()

    if likelihood not in ALLOWED_LIKELIHOODS:
        return "UNKNOWN"

    return likelihood


def deterministic_challenge_for_risk(
    risk: str,
) -> dict[str, Any]:
    """
    Build a safe deterministic fallback challenge.

    This fallback does not claim that the scenario will happen.
    """

    risk_lower = risk.lower()

    if any(
        keyword in risk_lower
        for keyword in [
            "market",
            "customer",
            "adoption",
            "competition",
            "demand",
        ]
    ):
        return {
            "assumption": (
                "Market adoption and demand will develop "
                "within the expected range."
            ),
            "challenge": (
                "Customer adoption is materially slower than expected "
                "while competitive pressure increases."
            ),
            "transmission_path": [
                "Lower customer adoption",
                "Lower revenue",
                "Longer payback period",
                "Reduced strategic support",
            ],
            "impact": (
                "The business case may become commercially unattractive."
            ),
            "severity": "HIGH",
            "likelihood": "UNKNOWN",
        }

    if any(
        keyword in risk_lower
        for keyword in [
            "financial",
            "finance",
            "investment",
            "capital",
            "cost",
            "revenue",
            "liquidity",
        ]
    ):
        return {
            "assumption": (
                "Capital, operating costs and expected returns "
                "will remain within the planned range."
            ),
            "challenge": (
                "Implementation costs increase while expected "
                "financial benefits are delayed."
            ),
            "transmission_path": [
                "Higher implementation cost",
                "Delayed benefits",
                "Cash-flow pressure",
                "Reduced return on investment",
            ],
            "impact": (
                "The decision may fail to meet its financial thresholds."
            ),
            "severity": "HIGH",
            "likelihood": "UNKNOWN",
        }

    if any(
        keyword in risk_lower
        for keyword in [
            "regulation",
            "regulatory",
            "legal",
            "compliance",
            "policy",
        ]
    ):
        return {
            "assumption": (
                "The regulatory and compliance environment "
                "will remain manageable."
            ),
            "challenge": (
                "A regulatory interpretation or policy change creates "
                "new controls, approvals or operating restrictions."
            ),
            "transmission_path": [
                "Additional compliance requirement",
                "Implementation delay",
                "Additional cost",
                "Reduced operating flexibility",
            ],
            "impact": (
                "The proposed solution may require redesign or delayed launch."
            ),
            "severity": "HIGH",
            "likelihood": "UNKNOWN",
        }

    if any(
        keyword in risk_lower
        for keyword in [
            "cyber",
            "security",
            "privacy",
            "breach",
            "data",
        ]
    ):
        return {
            "assumption": (
                "Security, privacy and resilience controls "
                "will be sufficient."
            ),
            "challenge": (
                "A major security or privacy failure occurs "
                "during implementation or operation."
            ),
            "transmission_path": [
                "Control failure",
                "Operational disruption",
                "Investigation and remediation",
                "Reputational and regulatory exposure",
            ],
            "impact": (
                "The decision may cause material operational "
                "and reputational damage."
            ),
            "severity": "CRITICAL",
            "likelihood": "UNKNOWN",
        }

    if any(
        keyword in risk_lower
        for keyword in [
            "technology",
            "technical",
            "platform",
            "architecture",
            "integration",
            "scalability",
            "ai",
        ]
    ):
        return {
            "assumption": (
                "The selected technology will integrate, scale "
                "and perform as expected."
            ),
            "challenge": (
                "The technology does not meet scalability, integration "
                "or reliability expectations."
            ),
            "transmission_path": [
                "Technical limitation",
                "Delivery delay",
                "Additional remediation",
                "Reduced user adoption",
            ],
            "impact": (
                "The intended strategic and operational benefits "
                "may not be realised."
            ),
            "severity": "HIGH",
            "likelihood": "UNKNOWN",
        }

    if any(
        keyword in risk_lower
        for keyword in [
            "operation",
            "operational",
            "delivery",
            "workforce",
            "process",
            "execution",
        ]
    ):
        return {
            "assumption": (
                "The organisation has sufficient execution capacity "
                "and operational readiness."
            ),
            "challenge": (
                "The implementation exceeds available delivery, "
                "process and workforce capacity."
            ),
            "transmission_path": [
                "Execution bottleneck",
                "Schedule delay",
                "Cost escalation",
                "Service-level deterioration",
            ],
            "impact": (
                "Operations may deteriorate before the proposed "
                "benefits become available."
            ),
            "severity": "HIGH",
            "likelihood": "UNKNOWN",
        }

    if any(
        keyword in risk_lower
        for keyword in [
            "supplier",
            "supply",
            "logistics",
            "dependency",
            "vendor",
        ]
    ):
        return {
            "assumption": (
                "Critical suppliers and dependencies "
                "will remain available."
            ),
            "challenge": (
                "A critical supplier, vendor or dependency becomes "
                "unavailable or materially constrained."
            ),
            "transmission_path": [
                "Dependency failure",
                "Supply or service disruption",
                "Operational delay",
                "Customer impact",
            ],
            "impact": (
                "The proposed operating model may not remain viable."
            ),
            "severity": "CRITICAL",
            "likelihood": "UNKNOWN",
        }

    return {
        "assumption": (
            f"{risk} will remain within the organisation's "
            "expected operating range."
        ),
        "challenge": (
            f"{risk} deteriorates unexpectedly and interacts "
            "with other weaknesses."
        ),
        "transmission_path": [
            "Initial disruption",
            "Secondary operational impact",
            "Financial or strategic pressure",
            "Decision outcome deterioration",
        ],
        "impact": (
            "The expected outcome may become materially less favourable."
        ),
        "severity": "HIGH",
        "likelihood": "UNKNOWN",
    }


def deterministic_red_team_result(
    classification: dict[str, Any],
    research_result: dict[str, Any] | None = None,
    evidence_result: dict[str, Any] | None = None,
    analysis_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Generate a safe deterministic fallback.

    The fallback remains explicitly hypothetical and does not
    fabricate external evidence or probabilities.
    """

    risks = clean_string_list(
        classification.get(
            "risk_dimensions",
            [],
        )
    )

    if not risks:
        risks = [
            "Strategic uncertainty",
            "Operational execution",
            "External environment",
        ]

    challenges: list[
        dict[str, Any]
    ] = []

    for index, risk in enumerate(
        risks,
        start=1,
    ):
        challenge = (
            deterministic_challenge_for_risk(
                risk
            )
        )

        challenges.append(
            {
                "id": f"RT-{index:03d}",
                "risk_dimension": risk,
                **challenge,
                "scenario_classification": "HYPOTHETICAL",
            }
        )

    missing_inputs = clean_string_list(
        classification.get(
            "missing_inputs",
            [],
        )
    )

    research_missing = []

    if isinstance(
        research_result,
        dict,
    ):
        research_missing = clean_string_list(
            research_result.get(
                "missing_inputs",
                [],
            )
        )

    unresolved_inputs = list(
        dict.fromkeys(
            missing_inputs
            + research_missing
        )
    )

    return {
        "status": "COMPLETED",
        "scenario_classification": "HYPOTHETICAL",
        "assumptions_challenged": [
            challenge["assumption"]
            for challenge in challenges
        ],
        "compound_scenarios": challenges,
        "challenge_count": len(
            challenges
        ),
        "early_warning_indicators": [
            "Delivery milestones begin to slip",
            "Expected costs exceed approved thresholds",
            "Required evidence remains unavailable",
            "Operational or customer outcomes deteriorate",
        ],
        "mitigations": [
            "Use a phased or pilot implementation",
            "Define measurable stop-loss thresholds",
            "Maintain contingency funding and capacity",
            "Require human approval before irreversible commitments",
        ],
        "reversal_conditions": [
            "Critical evidence cannot be verified",
            "Financial or operational thresholds are breached",
            "A critical dependency becomes unavailable",
            "Risk controls fail required validation",
        ],
        "unresolved_inputs": unresolved_inputs,
        "summary": (
            "The proposed decision has been challenged using "
            "hypothetical compound failure scenarios."
        ),
        "evidence_used": False,
    }


def build_red_team_prompt(
    classification: dict[str, Any],
    research_result: dict[str, Any] | None,
    evidence_result: dict[str, Any] | None,
    analysis_result: dict[str, Any] | None,
) -> str:
    """
    Build the adversarial reasoning prompt.

    Only supplied case data and deterministic tool outputs may be used.
    """

    safe_research = (
        research_result
        if isinstance(
            research_result,
            dict,
        )
        else {}
    )

    safe_evidence = (
        evidence_result
        if isinstance(
            evidence_result,
            dict,
        )
        else {}
    )

    safe_analysis = (
        analysis_result
        if isinstance(
            analysis_result,
            dict,
        )
        else {}
    )

    prompt_payload = {
        "classification": classification,
        "research": {
            "status": safe_research.get(
                "status"
            ),
            "missing_inputs": (
                safe_research.get(
                    "missing_inputs",
                    [],
                )
            ),
            "unsupported_claims": (
                safe_research.get(
                    "unsupported_claims",
                    [],
                )
            ),
            "source_retrieval_performed": (
                safe_research.get(
                    "source_retrieval_performed",
                    False,
                )
            ),
        },
        "evidence": safe_evidence,
        "deterministic_analysis": safe_analysis,
    }

    return f"""
You are the Black Swan Red Team Agent for a Universal
Decision War Room.

Your role is to challenge the decision, expose hidden assumptions,
construct plausible compound failure scenarios and define conditions
under which the decision should be paused or reversed.

You do not have live source retrieval.

Rules:

- Use only the information supplied in the input.
- Do not invent facts, evidence, sources, dates or statistics.
- Do not invent numerical likelihoods or probabilities.
- Every scenario must be labelled HYPOTHETICAL.
- Distinguish missing evidence from verified evidence.
- Treat research plans and research questions as unevaluated tasks,
  not as evidence.
- Challenge the decision, but do not make the final committee decision.
- Include practical early warning indicators and mitigations.
- Include measurable or observable reversal conditions.
- Return exactly one valid JSON object.
- Do not use Markdown.
- Do not add commentary outside the JSON.

Input:

{json.dumps(prompt_payload, ensure_ascii=False, indent=2)}

Return this exact structure:

{{
  "status": "COMPLETED",
  "scenario_classification": "HYPOTHETICAL",
  "assumptions_challenged": [
    "assumption"
  ],
  "compound_scenarios": [
    {{
      "id": "RT-001",
      "risk_dimension": "risk",
      "assumption": "assumption being challenged",
      "challenge": "compound failure scenario",
      "transmission_path": [
        "step one",
        "step two"
      ],
      "impact": "potential impact",
      "severity": "LOW, MEDIUM, HIGH or CRITICAL",
      "likelihood": "RARE, UNLIKELY, POSSIBLE, LIKELY or UNKNOWN",
      "scenario_classification": "HYPOTHETICAL"
    }}
  ],
  "challenge_count": 0,
  "early_warning_indicators": [
    "observable warning"
  ],
  "mitigations": [
    "mitigation"
  ],
  "reversal_conditions": [
    "condition requiring pause or reversal"
  ],
  "unresolved_inputs": [
    "required information"
  ],
  "summary": "plain-English red-team summary",
  "evidence_used": false
}}
""".strip()


def validate_compound_scenario(
    item: Any,
    index: int,
) -> dict[str, Any] | None:
    """
    Validate one model-generated failure scenario.
    """

    if not isinstance(
        item,
        dict,
    ):
        return None

    challenge = str(
        item.get(
            "challenge",
            "",
        )
    ).strip()

    if not challenge:
        return None

    risk_dimension = str(
        item.get(
            "risk_dimension",
            "General uncertainty",
        )
    ).strip()

    assumption = str(
        item.get(
            "assumption",
            (
                "Current decision assumptions "
                "remain valid."
            ),
        )
    ).strip()

    impact = str(
        item.get(
            "impact",
            (
                "The decision outcome may become "
                "materially less favourable."
            ),
        )
    ).strip()

    transmission_path = (
        clean_string_list(
            item.get(
                "transmission_path",
                [],
            )
        )
    )

    if not transmission_path:
        transmission_path = [
            "Initial disruption",
            "Secondary impact",
            "Decision outcome deterioration",
        ]

    return {
        "id": str(
            item.get(
                "id",
                f"RT-{index:03d}",
            )
        ).strip()
        or f"RT-{index:03d}",
        "risk_dimension": (
            risk_dimension
            or "General uncertainty"
        ),
        "assumption": assumption,
        "challenge": challenge,
        "transmission_path": transmission_path,
        "impact": impact,
        "severity": normalise_severity(
            item.get(
                "severity"
            )
        ),
        "likelihood": normalise_likelihood(
            item.get(
                "likelihood"
            )
        ),
        "scenario_classification": "HYPOTHETICAL",
    }


def validate_red_team_result(
    raw_result: dict[str, Any],
    fallback: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate and normalise Ollama Red Team output.
    """

    raw_scenarios = raw_result.get(
        "compound_scenarios",
        []
    )

    validated_scenarios: list[
        dict[str, Any]
    ] = []

    if isinstance(
        raw_scenarios,
        list,
    ):
        for index, item in enumerate(
            raw_scenarios,
            start=1,
        ):
            validated = (
                validate_compound_scenario(
                    item,
                    index,
                )
            )

            if validated is not None:
                validated_scenarios.append(
                    validated
                )

    if not validated_scenarios:
        validated_scenarios = fallback[
            "compound_scenarios"
        ]

    assumptions_challenged = (
        clean_string_list(
            raw_result.get(
                "assumptions_challenged",
                [],
            )
        )
    )

    if not assumptions_challenged:
        assumptions_challenged = [
            scenario["assumption"]
            for scenario in validated_scenarios
        ]

    return {
        "status": "COMPLETED",
        "scenario_classification": "HYPOTHETICAL",
        "assumptions_challenged": (
            assumptions_challenged
        ),
        "compound_scenarios": (
            validated_scenarios
        ),
        "challenge_count": len(
            validated_scenarios
        ),
        "early_warning_indicators": (
            clean_string_list(
                raw_result.get(
                    "early_warning_indicators",
                    fallback[
                        "early_warning_indicators"
                    ],
                )
            )
        ),
        "mitigations": clean_string_list(
            raw_result.get(
                "mitigations",
                fallback["mitigations"],
            )
        ),
        "reversal_conditions": (
            clean_string_list(
                raw_result.get(
                    "reversal_conditions",
                    fallback[
                        "reversal_conditions"
                    ],
                )
            )
        ),
        "unresolved_inputs": (
            clean_string_list(
                raw_result.get(
                    "unresolved_inputs",
                    fallback[
                        "unresolved_inputs"
                    ],
                )
            )
        ),
        "summary": str(
            raw_result.get(
                "summary",
                fallback["summary"],
            )
        ).strip()
        or fallback["summary"],
        "evidence_used": bool(
            raw_result.get(
                "evidence_used",
                False,
            )
        ),
        "llm_status": raw_result.get(
            "llm_status",
            "COMPLETED",
        ),
        "llm_warning": raw_result.get(
            "llm_warning"
        ),
        "llm_model": raw_result.get(
            "llm_model"
        ),
    }


async def run_red_team(
    classification: dict[str, Any],
    research_result: dict[str, Any] | None = None,
    evidence_result: dict[str, Any] | None = None,
    analysis_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Run Ollama-powered adversarial analysis.

    If local inference is unavailable or exceeds the agent timeout,
    return the deterministic Red Team result without blocking the
    complete War Room workflow.
    """

    fallback = deterministic_red_team_result(
        classification=classification,
        research_result=research_result,
        evidence_result=evidence_result,
        analysis_result=analysis_result,
    )

    prompt = build_red_team_prompt(
        classification=classification,
        research_result=research_result,
        evidence_result=evidence_result,
        analysis_result=analysis_result,
    )

    print(
        "[RED TEAM] Ollama generation started.",
        flush=True,
    )

    try:
        raw_result = await asyncio.wait_for(
            generate_json_with_fallback(
                prompt,
                fallback,
                required_fields=[
                    "status",
                    "assumptions_challenged",
                    "compound_scenarios",
                    "early_warning_indicators",
                    "mitigations",
                    "reversal_conditions",
                    "summary",
                ],
                temperature=0.25,
                num_ctx=2048,
                num_predict=450,
                force_cpu=True,
                read_timeout=75.0,
                retry_count=0,
            ),
            timeout=90.0,
        )

        print(
            "[RED TEAM] Ollama generation returned. "
            f"Status: {raw_result.get('llm_status')}",
            flush=True,
        )

    except asyncio.TimeoutError:
        print(
            "[RED TEAM] Ollama exceeded the agent timeout. "
            "Using deterministic fallback.",
            flush=True,
        )

        raw_result = dict(fallback)

        raw_result["llm_status"] = (
            "FALLBACK"
        )

        raw_result["llm_warning"] = (
            "Red Team inference exceeded "
            "the 90-second agent timeout."
        )

        raw_result["llm_model"] = None

    except Exception as exc:
        print(
            "[RED TEAM] Ollama failed. "
            "Using deterministic fallback. "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        raw_result = dict(fallback)

        raw_result["llm_status"] = (
            "FALLBACK"
        )

        raw_result["llm_warning"] = (
            f"{type(exc).__name__}: {exc}"
        )

        raw_result["llm_model"] = None

    result = validate_red_team_result(
        raw_result,
        fallback,
    )

    print(
        "[RED TEAM] Red Team result validated.",
        flush=True,
    )

    return result

