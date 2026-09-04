from typing import Any


AGENT_DESCRIPTIONS = {
    "case_understanding": {
        "title": "Case Understanding",
        "purpose": "Understand the decision, objectives and context.",
    },
    "research_agent": {
        "title": "Research Agent",
        "purpose": "Identify evidence required to investigate the decision.",
    },
    "market_intelligence": {
        "title": "Market Intelligence",
        "purpose": "Assess market size, growth and competitive dynamics.",
    },
    "competition_intelligence": {
        "title": "Competition Intelligence",
        "purpose": "Evaluate competitors and substitute offerings.",
    },
    "technology_assessment": {
        "title": "Technology Assessment",
        "purpose": "Assess technical feasibility and implementation complexity.",
    },
    "financial_impact": {
        "title": "Financial Impact",
        "purpose": "Estimate financial outcomes and business value.",
    },
    "quant_finance": {
        "title": "Quantitative Finance",
        "purpose": "Perform financial modelling and scenario calculations.",
    },
    "operations_analysis": {
        "title": "Operations Analysis",
        "purpose": "Analyse operational impact and delivery considerations.",
    },
    "supply_chain_analysis": {
        "title": "Supply Chain Analysis",
        "purpose": "Assess supplier and logistics risks.",
    },
    "cyber_risk": {
        "title": "Cyber Risk",
        "purpose": "Assess cybersecurity threats and vulnerabilities.",
    },
    "regulatory_risk": {
        "title": "Regulatory Risk",
        "purpose": "Identify compliance and regulatory considerations.",
    },
    "policy_analysis": {
        "title": "Policy Analysis",
        "purpose": "Evaluate government and policy implications.",
    },
    "stakeholder_analysis": {
        "title": "Stakeholder Analysis",
        "purpose": "Understand stakeholder interests and concerns.",
    },
    "environmental_risk": {
        "title": "Environmental Risk",
        "purpose": "Assess environmental consequences and sustainability risks.",
    },
    "reputation_risk": {
        "title": "Reputation Risk",
        "purpose": "Assess brand and reputational exposure.",
    },
    "dependency_intelligence": {
        "title": "Dependency Intelligence",
        "purpose": "Evaluate critical dependencies and bottlenecks.",
    },
    "scenario_simulator": {
        "title": "Scenario Simulator",
        "purpose": "Explore uncertainty using multiple future scenarios.",
    },
    "black_swan_red_team": {
        "title": "Black Swan Red Team",
        "purpose": "Challenge assumptions with low-probability high-impact events.",
    },
    "contrarian": {
        "title": "Contrarian Challenge",
        "purpose": "Challenge consensus assumptions and recommendations.",
    },
    "evidence_verifier": {
        "title": "Evidence Verifier",
        "purpose": "Validate evidence quality and traceability.",
    },
    "committee": {
        "title": "Decision Committee",
        "purpose": "Produce final recommendation and decision memo.",
    },
}


def estimate_complexity(
    classification: dict[str, Any]
) -> str:
    """
    Simple complexity estimation.
    """

    score = 0

    score += len(
        classification.get(
            "required_agents",
            [],
        )
    )

    score += len(
        classification.get(
            "research_questions",
            [],
        )
    )

    score += len(
        classification.get(
            "missing_inputs",
            [],
        )
    )

    if score <= 8:
        return "LOW"

    if score <= 15:
        return "MEDIUM"

    return "HIGH"


def estimate_effort(
    classification: dict[str, Any]
) -> str:
    """
    Rough effort estimate for investigation depth.
    """

    agent_count = len(
        classification.get(
            "required_agents",
            [],
        )
    )

    if agent_count <= 5:
        return "LIGHT"

    if agent_count <= 10:
        return "MODERATE"

    return "EXTENSIVE"


def create_agent_step(
    step_number: int,
    agent_name: str,
) -> dict[str, Any]:
    """
    Convert an agent identifier into
    a readable investigation step.
    """

    metadata = AGENT_DESCRIPTIONS.get(
        agent_name,
        {
            "title": agent_name.replace(
                "_",
                " "
            ).title(),
            "purpose": "Execute investigation activity.",
        },
    )

    return {
        "step": step_number,
        "agent": agent_name,
        "title": metadata["title"],
        "purpose": metadata["purpose"],
        "status": "PENDING",
    }


def build_investigation_plan(
    classification: dict[str, Any]
) -> dict[str, Any]:
    """
    Build a dynamic investigation plan
    from the classifier output.
    """

    required_agents = classification.get(
        "required_agents",
        [],
    )

    investigation_steps: list[dict[str, Any]] = []

    step_number = 1

    for agent in required_agents:

        investigation_steps.append(
            create_agent_step(
                step_number,
                agent,
            )
        )

        step_number += 1

    summary = {
        "domain": classification.get(
            "domain"
        ),
        "industry": classification.get(
            "industry"
        ),
        "decision_type": classification.get(
            "decision_type"
        ),
        "region": classification.get(
            "region"
        ),
        "confidence": classification.get(
            "confidence"
        ),
    }

    return {
        "summary": summary,
        "investigation_steps": investigation_steps,
        "missing_inputs": classification.get(
            "missing_inputs",
            [],
        ),
        "research_questions": classification.get(
            "research_questions",
            [],
        ),
        "risk_dimensions": classification.get(
            "risk_dimensions",
            [],
        ),
        "estimated_complexity": estimate_complexity(
            classification
        ),
        "estimated_effort": estimate_effort(
            classification
        ),
        "requires_live_research": classification.get(
            "requires_live_research",
            False,
        ),
        "requires_financial_analysis": classification.get(
            "requires_financial_analysis",
            False,
        ),
        "plan_version": "1.0",
    }