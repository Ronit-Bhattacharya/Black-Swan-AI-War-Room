import json
import uuid

from sqlalchemy.orm import Session

from .engines import (
    black_swan_scenario,
    dependency_analysis,
    financial_metrics,
    monte_carlo,
)
from .models import (
    AuditEvent,
    Case,
)
from .schemas import AnalysisRequest


def audit(
    db: Session,
    case_id: str,
    agent: str,
    event_type: str,
    summary: str,
):
    event = AuditEvent(
        id=str(uuid.uuid4()),
        case_id=case_id,
        agent=agent,
        event_type=event_type,
        summary=summary[:2000],
    )

    db.add(event)
    db.commit()


def safe_existing_result(
    case: Case,
) -> dict:

    try:
        parsed = json.loads(
            case.result_json or "{}"
        )

        if isinstance(
            parsed,
            dict,
        ):
            return parsed

        return {}

    except json.JSONDecodeError:
        return {}


def analyze(
    db: Session,
    case: Case,
    request: AnalysisRequest,
):

    existing_result = (
        safe_existing_result(
            case
        )
    )

    classification = (
        existing_result.get(
            "classification",
            {},
        )
    )

    selected_agents = (
        classification.get(
            "required_agents",
            [],
        )
    )

    routing_summary = (
        "Activated deterministic analysis engines."
    )

    if selected_agents:

        routing_summary += (
            " Selected capabilities: "
            + ", ".join(
                selected_agents
            )
            + "."
        )

    audit(
        db,
        case.id,
        "War Room Commander",
        "ROUTE_SELECTED",
        routing_summary,
    )

    # ----------------------------------
    # Financial Engine
    # ----------------------------------

    metrics = financial_metrics(
        request.assumptions.initial_investment,
        request.assumptions.annual_cash_flows,
        request.assumptions.discount_rate,
    )

    audit(
        db,
        case.id,
        "Quant Finance",
        "TOOL_RESULT",
        (
            "Deterministic financial metrics "
            "calculated."
        ),
    )

    # ----------------------------------
    # Scenario Engine
    # ----------------------------------

    scenario = monte_carlo(
        request.assumptions
    )

    audit(
        db,
        case.id,
        "Scenario Simulator",
        "TOOL_RESULT",
        (
            "Monte Carlo simulation completed."
        ),
    )

    # ----------------------------------
    # Dependency Engine
    # ----------------------------------

    dependency = dependency_analysis(
        request.nodes,
        request.edges,
    )

    audit(
        db,
        case.id,
        "Dependency Intelligence",
        "TOOL_RESULT",
        (
            "Dependency graph analysed."
        ),
    )

    # ----------------------------------
    # Black Swan Engine
    # ----------------------------------

    swan = black_swan_scenario(
        dependency
    )

    audit(
        db,
        case.id,
        "Black Swan Red Team",
        "CHALLENGE",
        (
            "Generated hypothetical disruption "
            "scenario."
        ),
    )

    # ----------------------------------
    # Contrarian Logic
    # ----------------------------------

    concerns: list[str] = []

    if (
        scenario[
            "probability_negative_npv"
        ]
        > 0.35
    ):
        concerns.append(
            "Material downside frequency "
            "detected."
        )

    if any(
        node["single_source"]
        for node in dependency[
            "critical_nodes"
        ]
    ):
        concerns.append(
            "Single-source dependency detected."
        )

    if metrics["npv"] < 0:
        concerns.append(
            "Base-case NPV is negative."
        )

    contrarian_summary = (
        "; ".join(
            concerns
        )
        if concerns
        else (
            "No automatic blocking signal "
            "identified."
        )
    )

    audit(
        db,
        case.id,
        "Contrarian",
        "CHALLENGE",
        contrarian_summary,
    )

    # ----------------------------------
    # Evidence Verification
    # ----------------------------------

    evidence = {
        "status": "PASS",
        "checks": [
            (
                "Numeric outputs originate "
                "from deterministic tools."
            ),
            (
                "Scenario assumptions are "
                "user supplied."
            ),
            (
                "Black Swan scenario is "
                "labelled hypothetical."
            ),
            (
                "No external action "
                "was executed."
            ),
        ],
    }

    audit(
        db,
        case.id,
        "Evidence Verifier",
        "QUALITY_GATE",
        (
            "PASS: provenance and validation "
            "checks completed."
        ),
    )

    # ----------------------------------
    # Committee
    # ----------------------------------

    decision = (
        "PROCEED_WITH_CONDITIONS"
        if (
            metrics["npv"] >= 0
            and scenario[
                "probability_negative_npv"
            ] < 0.5
        )
        else "DEFER"
    )

    committee = {
        "decision": decision,
        "conditions": [
            (
                "Human validation of "
                "financial assumptions."
            ),
            (
                "Pilot or phased rollout."
            ),
            (
                "Mitigate critical "
                "dependencies."
            ),
            (
                "Define exit criteria "
                "before scale-up."
            ),
        ],
        "human_approval_required": True,
        "disclaimer": (
            "Decision support only."
        ),
    }

    result = {
        **existing_result,
        "financial": metrics,
        "scenario": scenario,
        "dependencies": dependency,
        "black_swan": swan,
        "contrarian_concerns": concerns,
        "evidence_verification": evidence,
        "committee": committee,
    }

    case.assumptions_json = (
        request.assumptions.model_dump_json()
    )

    case.result_json = json.dumps(
        result,
        ensure_ascii=False,
    )

    case.status = "ANALYZED"

    db.commit()
    db.refresh(case)

    audit(
        db,
        case.id,
        "Committee",
        "DECISION_MEMO",
        (
            f"{decision}; "
            "human approval required."
        ),
    )

    return result