from app.engines import financial_metrics, monte_carlo, dependency_analysis
from app.schemas import Assumptions, DependencyNode, DependencyEdge

def test_finance():
    out=financial_metrics(100,[30,30,30,30,30],.1)
    assert out["roi"] == .5 and "npv" in out

def test_monte_carlo_reproducible():
    a=Assumptions(initial_investment=30,annual_cash_flows=[10]*5,discount_rate=.1,annual_revenue=40,annual_cost=30,years=5,revenue_shock_low=-.2,revenue_shock_high=.1,cost_shock_low=0,cost_shock_high=.2)
    assert monte_carlo(a,100,7)==monte_carlo(a,100,7)

def test_dependency():
    nodes=[DependencyNode(id="a",label="Supplier",single_source=True),DependencyNode(id="b",label="Plant"),DependencyNode(id="c",label="Customer")]
    edges=[DependencyEdge(source="a",target="b"),DependencyEdge(source="b",target="c")]
    out=dependency_analysis(nodes,edges)
    assert out["downstream_impact_count"]["a"]==2
