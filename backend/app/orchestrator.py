from time import perf_counter
from typing import Any

from .committee import (
    generate_committee_decision,
)
from .evidence_store import evidence_store
from .memory import memory_store
from .red_team import run_red_team
from .research_agent import (
    run_research_agent,
)


AGENT_ORDER = [
    "case_understanding",
    "research_agent",
    "market_intelligence",
    "competition_intelligence",
    "technology_assessment",
    "financial_impact",
    "quant_finance",
    "operations_analysis",
    "supply_chain_analysis",
    "cyber_risk",
    "regulatory_risk",
    "policy_analysis",
    "stakeholder_analysis",
    "environmental_risk",
    "reputation_risk",
    "dependency_intelligence",
    "scenario_simulator",
    "black_swan_red_team",
    "contrarian",
    "evidence_verifier",
    "committee",
]


def log_agent(
    case_id: str,
    message: str,
) -> None:
    print(
        f"[ORCHESTRATOR][{case_id}] "
        f"{message}",
        flush=True,
    )


async def run_orchestration(
    case_id: str,
    classification: dict[str, Any],
    analysis_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Execute the asynchronous War Room workflow.
    """

    orchestration_started = (
        perf_counter()
    )

    log_agent(
        case_id,
        "Orchestration started.",
    )

    required_agents = classification.get(
        "required_agents",
        [],
    )

    if not isinstance(
        required_agents,
        list,
    ):
        required_agents = []

    execution_log: list[
        dict[str, Any]
    ] = []

    # ----------------------------------
    # RESEARCH
    # ----------------------------------

    research_result: dict[str, Any] = {
        "status": "SKIPPED",
        "research_plan": [],
        "research_count": 0,
        "missing_inputs": [],
        "unsupported_claims": [],
        "source_retrieval_performed": False,
    }

    if "research_agent" in required_agents:
        agent_started = perf_counter()

        log_agent(
            case_id,
            "Research Agent started.",
        )

        try:
            research_result = (
                await run_research_agent(
                    classification
                )
            )

            duration = round(
                perf_counter()
                - agent_started,
                2,
            )

            execution_log.append(
                {
                    "agent": (
                        "research_agent"
                    ),
                    "status": "COMPLETED",
                    "duration_seconds": (
                        duration
                    ),
                    "llm_status": (
                        research_result.get(
                            "llm_status"
                        )
                    ),
                }
            )

            log_agent(
                case_id,
                (
                    "Research Agent completed "
                    f"in {duration} seconds. "
                    "LLM status: "
                    f"{research_result.get('llm_status')}"
                ),
            )

        except Exception as exc:
            duration = round(
                perf_counter()
                - agent_started,
                2,
            )

            execution_log.append(
                {
                    "agent": (
                        "research_agent"
                    ),
                    "status": "FAILED",
                    "duration_seconds": (
                        duration
                    ),
                    "error": str(exc),
                }
            )

            log_agent(
                case_id,
                (
                    "Research Agent failed: "
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            )

            raise

    else:
        log_agent(
            case_id,
            (
                "Research Agent skipped because "
                "it was not selected."
            ),
        )

    # ----------------------------------
    # EVIDENCE
    # ----------------------------------

    agent_started = perf_counter()

    log_agent(
        case_id,
        "Evidence validation started.",
    )

    evidence_result = (
        evidence_store.validate(
            case_id
        )
    )

    duration = round(
        perf_counter()
        - agent_started,
        2,
    )

    execution_log.append(
        {
            "agent": (
                "evidence_verifier"
            ),
            "status": "COMPLETED",
            "duration_seconds": duration,
            "result_status": (
                evidence_result.get(
                    "status"
                )
            ),
        }
    )

    log_agent(
        case_id,
        (
            "Evidence validation completed. "
            f"Status: "
            f"{evidence_result.get('status')}"
        ),
    )

    # ----------------------------------
    # RED TEAM
    # ----------------------------------

    agent_started = perf_counter()

    log_agent(
        case_id,
        "Black Swan Red Team started.",
    )

    try:
        red_team_result = (
            await run_red_team(
                classification=(
                    classification
                ),
                research_result=(
                    research_result
                ),
                evidence_result=(
                    evidence_result
                ),
                analysis_result=(
                    analysis_result
                ),
            )
        )

        duration = round(
            perf_counter()
            - agent_started,
            2,
        )

        execution_log.append(
            {
                "agent": (
                    "black_swan_red_team"
                ),
                "status": "COMPLETED",
                "duration_seconds": (
                    duration
                ),
                "llm_status": (
                    red_team_result.get(
                        "llm_status"
                    )
                ),
            }
        )

        log_agent(
            case_id,
            (
                "Black Swan Red Team "
                f"completed in {duration} seconds. "
                "LLM status: "
                f"{red_team_result.get('llm_status')}"
            ),
        )

    except Exception as exc:
        duration = round(
            perf_counter()
            - agent_started,
            2,
        )

        execution_log.append(
            {
                "agent": (
                    "black_swan_red_team"
                ),
                "status": "FAILED",
                "duration_seconds": (
                    duration
                ),
                "error": str(exc),
            }
        )

        log_agent(
            case_id,
            (
                "Black Swan Red Team failed: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        )

        raise

    # ----------------------------------
    # COMMITTEE
    # ----------------------------------

    agent_started = perf_counter()

    log_agent(
        case_id,
        "Decision Committee started.",
    )

    try:
        committee_result = (
            await generate_committee_decision(
                classification=(
                    classification
                ),
                evidence_result=(
                    evidence_result
                ),
                red_team_result=(
                    red_team_result
                ),
                research_result=(
                    research_result
                ),
                analysis_result=(
                    analysis_result
                ),
            )
        )

        duration = round(
            perf_counter()
            - agent_started,
            2,
        )

        execution_log.append(
            {
                "agent": "committee",
                "status": "COMPLETED",
                "duration_seconds": (
                    duration
                ),
                "llm_status": (
                    committee_result.get(
                        "llm_status"
                    )
                ),
                "decision": (
                    committee_result.get(
                        "decision"
                    )
                ),
            }
        )

        log_agent(
            case_id,
            (
                "Decision Committee completed "
                f"in {duration} seconds. "
                "Decision: "
                f"{committee_result.get('decision')}"
            ),
        )

    except Exception as exc:
        duration = round(
            perf_counter()
            - agent_started,
            2,
        )

        execution_log.append(
            {
                "agent": "committee",
                "status": "FAILED",
                "duration_seconds": (
                    duration
                ),
                "error": str(exc),
            }
        )

        log_agent(
            case_id,
            (
                "Decision Committee failed: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        )

        raise

    # ----------------------------------
    # MEMORY
    # ----------------------------------

    memory_store.remember(
        case_id=case_id,
        agent="committee",
        insight=str(
            committee_result.get(
                "decision",
                "DEFER",
            )
        ),
        confidence=float(
            committee_result.get(
                "confidence",
                0.0,
            )
        ),
    )

    memory_entries = (
        memory_store.get_case_memory(
            case_id
        )
    )

    executed_agents = [
        item["agent"]
        for item in execution_log
        if item["status"]
        == "COMPLETED"
    ]

    total_duration = round(
        perf_counter()
        - orchestration_started,
        2,
    )

    log_agent(
        case_id,
        (
            "Orchestration completed "
            f"in {total_duration} seconds."
        ),
    )

    return {
        "status": "COMPLETED",
        "case_id": case_id,
        "duration_seconds": total_duration,
        "executed_agents": (
            executed_agents
        ),
        "research": research_result,
        "evidence": evidence_result,
        "red_team": red_team_result,
        "committee": committee_result,
        "memory": memory_entries,
        "execution_log": execution_log,
    }