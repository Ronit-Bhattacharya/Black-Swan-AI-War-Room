import json
from typing import Any

from .llm_client import generate_json_with_fallback


ALLOWED_PRIORITIES = {
    "CRITICAL",
    "HIGH",
    "MEDIUM",
    "LOW",
}


ALLOWED_STATUSES = {
    "PENDING",
    "BLOCKED_BY_INPUT",
    "READY_FOR_EVIDENCE",
}


def clean_string_list(
    value: Any,
) -> list[str]:
    if not isinstance(value, list):
        return []

    cleaned_items: list[str] = []

    for item in value:
        text = str(item).strip()

        if text and text not in cleaned_items:
            cleaned_items.append(text)

    return cleaned_items


def normalise_priority(
    value: Any,
) -> str:
    priority = str(
        value or "MEDIUM"
    ).strip().upper()

    if priority not in ALLOWED_PRIORITIES:
        return "MEDIUM"

    return priority


def normalise_status(
    value: Any,
) -> str:
    status = str(
        value or "PENDING"
    ).strip().upper()

    if status not in ALLOWED_STATUSES:
        return "PENDING"

    return status


def determine_source_type(
    question: str,
) -> list[str]:
    """
    Deterministic fallback source recommendations.

    These are source categories, not claims that any source
    has actually been retrieved.
    """

    question_lower = question.lower()

    source_types: list[str] = []

    if any(
        keyword in question_lower
        for keyword in [
            "market",
            "competitor",
            "customer",
            "adoption",
            "industry",
        ]
    ):
        source_types.extend(
            [
                "industry report",
                "company filing",
                "market dataset",
            ]
        )

    if any(
        keyword in question_lower
        for keyword in [
            "regulation",
            "regulatory",
            "policy",
            "compliance",
            "law",
        ]
    ):
        source_types.extend(
            [
                "regulator publication",
                "government publication",
                "official legal text",
            ]
        )

    if any(
        keyword in question_lower
        for keyword in [
            "financial",
            "cost",
            "revenue",
            "investment",
            "return",
            "budget",
        ]
    ):
        source_types.extend(
            [
                "audited financial statement",
                "management-approved financial assumption",
                "industry benchmark",
            ]
        )

    if any(
        keyword in question_lower
        for keyword in [
            "technology",
            "technical",
            "platform",
            "software",
            "architecture",
            "ai",
        ]
    ):
        source_types.extend(
            [
                "technical documentation",
                "architecture assessment",
                "independent benchmark",
            ]
        )

    if any(
        keyword in question_lower
        for keyword in [
            "cyber",
            "security",
            "privacy",
            "breach",
        ]
    ):
        source_types.extend(
            [
                "security assessment",
                "threat intelligence report",
                "official security standard",
            ]
        )

    if not source_types:
        source_types.extend(
            [
                "authoritative primary source",
                "independent secondary source",
            ]
        )

    return list(
        dict.fromkeys(source_types)
    )


def deterministic_research_plan(
    classification: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a safe fallback plan without fabricating research findings.
    """

    questions = clean_string_list(
        classification.get(
            "research_questions",
            []
        )
    )

    missing_inputs = clean_string_list(
        classification.get(
            "missing_inputs",
            []
        )
    )

    research_plan: list[
        dict[str, Any]
    ] = []

    for index, question in enumerate(
        questions,
        start=1,
    ):
        research_plan.append(
            {
                "id": f"RQ-{index:03d}",
                "question": question,
                "priority": "HIGH",
                "status": "READY_FOR_EVIDENCE",
                "preferred_source_types": (
                    determine_source_type(
                        question
                    )
                ),
                "evidence_required": True,
                "completion_criteria": (
                    "At least one authoritative source "
                    "and one independent corroborating source."
                ),
            }
        )

    return {
        "status": (
            "RESEARCH_REQUIRED"
            if research_plan
            else "NO_RESEARCH_QUESTIONS"
        ),
        "research_plan": research_plan,
        "research_count": len(
            research_plan
        ),
        "known_from_user": [],
        "missing_inputs": missing_inputs,
        "unsupported_claims": [],
        "evidence_collected": [],
        "summary": (
            "External source-backed evidence is required "
            "before factual conclusions can be produced."
        ),
        "source_retrieval_performed": False,
    }


def build_research_prompt(
    classification: dict[str, Any],
) -> str:
    domain = str(
        classification.get(
            "domain",
            "General decision intelligence",
        )
    )

    industry = str(
        classification.get(
            "industry",
            "Cross-industry",
        )
    )

    decision_type = str(
        classification.get(
            "decision_type",
            "Strategic decision",
        )
    )

    region = classification.get(
        "region"
    )

    objective = str(
        classification.get(
            "objective",
            "Evaluate the submitted decision",
        )
    )

    summary = str(
        classification.get(
            "summary",
            "",
        )
    )

    missing_inputs = clean_string_list(
        classification.get(
            "missing_inputs",
            [],
        )
    )

    research_questions = clean_string_list(
        classification.get(
            "research_questions",
            [],
        )
    )

    risk_dimensions = clean_string_list(
        classification.get(
            "risk_dimensions",
            [],
        )
    )

    return f"""
You are the Research Strategy Agent for a Universal
Black Swan Decision War Room.

You do not have access to live internet search, external databases,
company systems or current publications during this task.

Your role is to create a source-backed research plan.
Your role is not to invent research findings.

Rules:

- Do not invent statistics, market sizes, regulations, dates or facts.
- Do not invent URLs, publications, organisations or source titles.
- Do not claim that research has been completed.
- Do not present assumptions as evidence.
- Identify claims that require external verification.
- Recommend source categories, not fabricated sources.
- Put unavailable information under missing_inputs.
- evidence_collected must remain an empty list.
- source_retrieval_performed must be false.
- Return exactly one valid JSON object.
- Do not use Markdown.
- Do not include commentary outside the JSON.

Case classification:

Domain:
{domain}

Industry:
{industry}

Decision type:
{decision_type}

Region:
{region if region else "Not specified"}

Objective:
{objective}

Case summary:
{summary}

Known missing inputs:
{json.dumps(missing_inputs, ensure_ascii=False)}

Initial research questions:
{json.dumps(research_questions, ensure_ascii=False)}

Risk dimensions:
{json.dumps(risk_dimensions, ensure_ascii=False)}

Return this structure:

{{
  "status": "RESEARCH_REQUIRED",
  "research_plan": [
    {{
      "id": "RQ-001",
      "question": "specific research question",
      "priority": "CRITICAL, HIGH, MEDIUM or LOW",
      "status": "PENDING, BLOCKED_BY_INPUT or READY_FOR_EVIDENCE",
      "preferred_source_types": [
        "source category"
      ],
      "evidence_required": true,
      "completion_criteria": "how evidence should be validated"
    }}
  ],
  "research_count": 0,
  "known_from_user": [
    "fact explicitly supplied by the user"
  ],
  "missing_inputs": [
    "missing information"
  ],
  "unsupported_claims": [
    "claim requiring evidence"
  ],
  "evidence_collected": [],
  "summary": "plain-English research strategy summary",
  "source_retrieval_performed": false
}}
""".strip()


def validate_research_result(
    raw_result: dict[str, Any],
    fallback: dict[str, Any],
) -> dict[str, Any]:
    raw_plan = raw_result.get(
        "research_plan",
        []
    )

    validated_plan: list[
        dict[str, Any]
    ] = []

    if isinstance(raw_plan, list):
        for index, item in enumerate(
            raw_plan,
            start=1,
        ):
            if not isinstance(
                item,
                dict,
            ):
                continue

            question = str(
                item.get(
                    "question",
                    "",
                )
            ).strip()

            if not question:
                continue

            source_types = (
                clean_string_list(
                    item.get(
                        "preferred_source_types",
                        []
                    )
                )
            )

            if not source_types:
                source_types = (
                    determine_source_type(
                        question
                    )
                )

            validated_plan.append(
                {
                    "id": str(
                        item.get(
                            "id",
                            f"RQ-{index:03d}",
                        )
                    ).strip()
                    or f"RQ-{index:03d}",
                    "question": question,
                    "priority": (
                        normalise_priority(
                            item.get(
                                "priority"
                            )
                        )
                    ),
                    "status": (
                        normalise_status(
                            item.get(
                                "status"
                            )
                        )
                    ),
                    "preferred_source_types": (
                        source_types
                    ),
                    "evidence_required": True,
                    "completion_criteria": str(
                        item.get(
                            "completion_criteria",
                            (
                                "Evidence must be supported "
                                "by authoritative and "
                                "independent sources."
                            ),
                        )
                    ).strip(),
                }
            )

    if not validated_plan:
        validated_plan = fallback[
            "research_plan"
        ]

    status = str(
        raw_result.get(
            "status",
            "RESEARCH_REQUIRED",
        )
    ).strip().upper()

    if status not in {
        "RESEARCH_REQUIRED",
        "NO_RESEARCH_QUESTIONS",
        "INPUT_REQUIRED",
    }:
        status = "RESEARCH_REQUIRED"

    return {
        "status": status,
        "research_plan": validated_plan,
        "research_count": len(
            validated_plan
        ),
        "known_from_user": clean_string_list(
            raw_result.get(
                "known_from_user",
                [],
            )
        ),
        "missing_inputs": clean_string_list(
            raw_result.get(
                "missing_inputs",
                fallback[
                    "missing_inputs"
                ],
            )
        ),
        "unsupported_claims": clean_string_list(
            raw_result.get(
                "unsupported_claims",
                [],
            )
        ),
        "evidence_collected": [],
        "summary": str(
            raw_result.get(
                "summary",
                fallback["summary"],
            )
        ).strip()
        or fallback["summary"],
        "source_retrieval_performed": False,
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


async def run_research_agent(
    classification: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate a research strategy using Ollama.

    This agent does not retrieve live sources. It returns research tasks,
    missing evidence and source-type recommendations.
    """

    fallback = deterministic_research_plan(
        classification
    )

    prompt = build_research_prompt(
        classification
    )

    raw_result = (
        await generate_json_with_fallback(
            prompt,
            fallback,
            required_fields=[
                "status",
                "research_plan",
                "missing_inputs",
                "unsupported_claims",
                "summary",
                "source_retrieval_performed",
            ],
            temperature=0.1,
            num_ctx=4096,
            num_predict=600,
            force_cpu=True,
            retry_count=0,
        )
    )

    return validate_research_result(
        raw_result,
        fallback,
    )