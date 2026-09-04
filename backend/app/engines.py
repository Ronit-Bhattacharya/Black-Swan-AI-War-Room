from collections import defaultdict, deque
from random import Random
from statistics import mean


def financial_metrics(initial: float, cash_flows: list[float], rate: float):
    npv = -initial + sum(cf / ((1 + rate) ** year) for year, cf in enumerate(cash_flows, 1))
    roi = (sum(cash_flows) - initial) / initial
    cumulative = -initial
    payback = None
    for year, cf in enumerate(cash_flows, 1):
        before = cumulative
        cumulative += cf
        if cumulative >= 0 and payback is None:
            payback = (year - 1) + ((-before / cf) if cf else 0)
    return {"npv": round(npv, 2), "roi": round(roi, 6), "payback_years": None if payback is None else round(payback, 3)}


def monte_carlo(a, iterations=3000, seed=42):
    rng = Random(seed)
    values=[]
    for _ in range(iterations):
        revenue = a.annual_revenue * (1 + rng.uniform(a.revenue_shock_low, a.revenue_shock_high))
        cost = a.annual_cost * (1 + rng.uniform(a.cost_shock_low, a.cost_shock_high))
        cf = revenue - cost
        npv = -a.initial_investment + sum(cf / ((1+a.discount_rate)**y) for y in range(1, a.years+1))
        values.append(npv)
    values.sort()
    pick=lambda p: values[int((len(values)-1)*p)]
    return {"iterations":iterations,"seed":seed,"mean_npv":round(mean(values),2),"p05_npv":round(pick(.05),2),"median_npv":round(pick(.5),2),"p95_npv":round(pick(.95),2),"probability_negative_npv":round(sum(x<0 for x in values)/len(values),6)}


def dependency_analysis(nodes, edges):
    ids={n.id for n in nodes}
    adj=defaultdict(list); indeg=defaultdict(int)
    for e in edges:
        if e.source not in ids or e.target not in ids:
            raise ValueError("Dependency edge references an unknown node")
        adj[e.source].append(e.target); indeg[e.target]+=1
    critical=[]; impacts={}
    for n in nodes:
        degree=len(adj[n.id])+indeg[n.id]
        if degree >= 2 or n.single_source:
            critical.append({"id":n.id,"label":n.label,"degree":degree,"single_source":n.single_source})
        seen={n.id}; q=deque([n.id])
        while q:
            current=q.popleft()
            for nxt in adj[current]:
                if nxt not in seen: seen.add(nxt); q.append(nxt)
        impacts[n.id]=len(seen)-1
    critical.sort(key=lambda x:(x["single_source"],x["degree"]), reverse=True)
    return {"critical_nodes":critical,"downstream_impact_count":impacts}


def black_swan_scenario(dep):
    critical=dep.get("critical_nodes", [])
    if critical:
        node=critical[0]
        return {"title":f"Compound disruption around {node['label']}","classification":"HYPOTHETICAL","trigger":f"Failure or restriction affecting {node['label']}","transmission_path":"Supply constraint -> cost increase -> operational delay -> lower utilization -> cash-flow pressure","early_warnings":["lead-time increase","supplier concentration increase","cost variance","service-level deterioration"],"mitigations":["qualify alternate suppliers","stage investment","hold liquidity reserve","define stop-loss milestones"]}
    return {"title":"Demand and financing compound shock","classification":"HYPOTHETICAL","trigger":"Demand softening combined with financing-cost increase","transmission_path":"Lower utilization -> weaker cash flow -> slower payback","early_warnings":["utilization decline","financing spread increase"],"mitigations":["pilot before scale","stage-gate capital release"]}
