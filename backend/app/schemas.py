from typing import Any, Literal
from pydantic import BaseModel, Field, ConfigDict

class CaseCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    decision: str = Field(min_length=10, max_length=10000)

class Assumptions(BaseModel):
    initial_investment: float = Field(gt=0, le=1e15)
    annual_cash_flows: list[float] = Field(min_length=1, max_length=30)
    discount_rate: float = Field(gt=-0.99, le=2)
    annual_revenue: float = Field(gt=0, le=1e15)
    annual_cost: float = Field(ge=0, le=1e15)
    years: int = Field(ge=1, le=30)
    revenue_shock_low: float = Field(ge=-0.95, le=2)
    revenue_shock_high: float = Field(ge=-0.95, le=2)
    cost_shock_low: float = Field(ge=-0.95, le=5)
    cost_shock_high: float = Field(ge=-0.95, le=5)

class DependencyNode(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    label: str = Field(min_length=1, max_length=200)
    single_source: bool = False

class DependencyEdge(BaseModel):
    source: str
    target: str

class AnalysisRequest(BaseModel):
    assumptions: Assumptions
    nodes: list[DependencyNode] = Field(default_factory=list, max_length=100)
    edges: list[DependencyEdge] = Field(default_factory=list, max_length=300)

class CaseView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    decision: str
    status: str
    assumptions: dict[str, Any]
    result: dict[str, Any]

class AuditView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    case_id: str
    agent: str
    event_type: str
    summary: str
    created_at: Any
