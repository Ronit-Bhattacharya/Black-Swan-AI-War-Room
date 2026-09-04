from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# =====================================================
# Case Creation
# =====================================================

class CaseCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=200,
    )

    decision: str = Field(
        min_length=10,
        max_length=10000,
    )

    context: str = Field(
        default="",
        max_length=10000,
    )


# =====================================================
# Classification
# =====================================================

class ClassificationRequest(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=200,
    )

    decision: str = Field(
        min_length=10,
        max_length=10000,
    )

    context: str = Field(
        default="",
        max_length=10000,
    )


class ClassificationResult(BaseModel):
    domain: str
    industry: str
    decision_type: str

    region: str | None = None

    objective: str
    summary: str

    confidence: float = Field(
        ge=0,
        le=1,
    )

    required_agents: list[str]
    missing_inputs: list[str]
    research_questions: list[str]
    risk_dimensions: list[str]

    requires_financial_analysis: bool
    requires_live_research: bool

    classification_reason: str
    classification_method: str

    classification_warning: str | None = None


# =====================================================
# Investigation Plan
# =====================================================

class InvestigationStep(BaseModel):
    step: int
    agent: str
    title: str
    purpose: str
    status: str


class InvestigationPlan(BaseModel):
    summary: dict[str, Any]

    investigation_steps: list[
        InvestigationStep
    ]

    missing_inputs: list[str]

    research_questions: list[str]

    risk_dimensions: list[str]

    estimated_complexity: str

    estimated_effort: str

    requires_live_research: bool

    requires_financial_analysis: bool

    plan_version: str


# =====================================================
# Analysis Inputs
# =====================================================

class Assumptions(BaseModel):
    initial_investment: float = Field(
        gt=0,
        le=1e15,
    )

    annual_cash_flows: list[float] = Field(
        min_length=1,
        max_length=30,
    )

    discount_rate: float = Field(
        gt=-0.99,
        le=2,
    )

    annual_revenue: float = Field(
        gt=0,
        le=1e15,
    )

    annual_cost: float = Field(
        ge=0,
        le=1e15,
    )

    years: int = Field(
        ge=1,
        le=30,
    )

    revenue_shock_low: float = Field(
        ge=-0.95,
        le=2,
    )

    revenue_shock_high: float = Field(
        ge=-0.95,
        le=2,
    )

    cost_shock_low: float = Field(
        ge=-0.95,
        le=5,
    )

    cost_shock_high: float = Field(
        ge=-0.95,
        le=5,
    )


class DependencyNode(BaseModel):
    id: str = Field(
        min_length=1,
        max_length=100,
    )

    label: str = Field(
        min_length=1,
        max_length=200,
    )

    single_source: bool = False


class DependencyEdge(BaseModel):
    source: str = Field(
        min_length=1,
        max_length=100,
    )

    target: str = Field(
        min_length=1,
        max_length=100,
    )


class AnalysisRequest(BaseModel):
    assumptions: Assumptions

    nodes: list[DependencyNode] = Field(
        default_factory=list,
        max_length=100,
    )

    edges: list[DependencyEdge] = Field(
        default_factory=list,
        max_length=300,
    )


# =====================================================
# Orchestration
# =====================================================

class OrchestrationRequest(BaseModel):
    case_id: str


class OrchestrationResult(BaseModel):
    status: str

    executed_agents: list[str]

    research: dict[str, Any] | None = None

    evidence: dict[str, Any] | None = None

    red_team: dict[str, Any] | None = None

    committee: dict[str, Any] | None = None

    memory: list[dict[str, Any]] = Field(
        default_factory=list
    )

    execution_log: list[
        dict[str, Any]
    ] = Field(
        default_factory=list
    )


# =====================================================
# API Views
# =====================================================

class CaseView(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    title: str
    decision: str
    status: str

    assumptions: dict[str, Any]

    result: dict[str, Any]


class AuditView(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    case_id: str
    agent: str
    event_type: str
    summary: str
    created_at: Any