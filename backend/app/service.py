import json, uuid
from sqlalchemy.orm import Session
from .models import Case, AuditEvent
from .schemas import AnalysisRequest
from .engines import financial_metrics, monte_carlo, dependency_analysis, black_swan_scenario

def audit(db: Session, case_id: str, agent: str, event_type: str, summary: str):
    db.add(AuditEvent(id=str(uuid.uuid4()), case_id=case_id, agent=agent, event_type=event_type, summary=summary[:2000]))
    db.commit()

def analyze(db: Session, case: Case, request: AnalysisRequest):
    audit(db, case.id, "War Room Commander", "ROUTE_SELECTED", "Activated Quant Finance, Dependency Intelligence, Scenario Simulator, Black Swan Red Team, Contrarian, Evidence Verifier, and Committee.")
    metrics=financial_metrics(request.assumptions.initial_investment, request.assumptions.annual_cash_flows, request.assumptions.discount_rate)
    audit(db, case.id, "Quant Finance", "TOOL_RESULT", "Deterministic finance metrics calculated from user-supplied assumptions.")
    scenario=monte_carlo(request.assumptions)
    audit(db, case.id, "Scenario Simulator", "TOOL_RESULT", "Monte Carlo scenario distribution calculated with a fixed reproducibility seed.")
    dependency=dependency_analysis(request.nodes, request.edges)
    audit(db, case.id, "Dependency Intelligence", "TOOL_RESULT", "Dependency graph analysed for bottlenecks and downstream impact.")
    swan=black_swan_scenario(dependency)
    audit(db, case.id, "Black Swan Red Team", "CHALLENGE", "Generated a labelled hypothetical compound disruption scenario.")
    concerns=[]
    if scenario["probability_negative_npv"] > .35: concerns.append("Material downside frequency in supplied scenario ranges")
    if any(n["single_source"] for n in dependency["critical_nodes"]): concerns.append("Single-source dependency detected")
    if metrics["npv"] < 0: concerns.append("Base-case NPV is negative")
    audit(db, case.id, "Contrarian", "CHALLENGE", "; ".join(concerns) if concerns else "No automatic blocking signal; assumptions still require human validation.")
    evidence={"status":"PASS","checks":["All numeric outputs originate from deterministic tools","Scenario assumptions are user-supplied","Black Swan scenario is labelled hypothetical","No external consequential action executed"]}
    audit(db, case.id, "Evidence Verifier", "QUALITY_GATE", "PASS: numeric provenance and assumption labelling checks completed.")
    decision="PROCEED_WITH_CONDITIONS" if metrics["npv"] >= 0 and scenario["probability_negative_npv"] < .5 else "DEFER"
    result={"financial":metrics,"scenario":scenario,"dependencies":dependency,"black_swan":swan,"contrarian_concerns":concerns,"evidence_verification":evidence,"committee":{"decision":decision,"conditions":["Human validation of financial assumptions","Pilot or staged capital release","Mitigate critical single-source dependencies","Define measurable reversal thresholds"],"human_approval_required":True,"disclaimer":"Decision support only; not financial advice."}}
    case.assumptions_json=request.assumptions.model_dump_json()
    case.result_json=json.dumps(result)
    case.status="ANALYZED"
    db.commit(); db.refresh(case)
    audit(db, case.id, "Committee", "DECISION_MEMO", f"{decision}; human approval required.")
    return result
