from typing import Any, Dict
from random import Random
from neuro_san.interfaces.coded_tool import CodedTool
from common import parse, output
class ScenarioTool(CodedTool):
    def invoke(self,args:Dict[str,Any],sly_data:Dict[str,Any]):
        base=parse(args["base_case_json"]); shocks=parse(args["shocks_json"]); n=max(100,min(int(args.get("iterations",2000)),50000)); rng=Random(42); values=[]
        for _ in range(n):
            rm=cm=1.0
            for s in shocks:
                draw=rng.uniform(float(s["low"]),float(s["high"])); rm*=1+draw if s["target"]=="revenue" else 1; cm*=1+draw if s["target"]=="cost" else 1
            cf=base["annual_revenue"]*rm-base["annual_cost"]*cm; values.append(-base["initial_investment"]+sum(cf/((1+base["discount_rate"])**y) for y in range(1,base["years"]+1)))
        values.sort(); pick=lambda p:values[int((n-1)*p)]
        return output({"iterations":n,"seed":42,"p05_npv":round(pick(.05),2),"median_npv":round(pick(.5),2),"p95_npv":round(pick(.95),2),"probability_negative_npv":round(sum(x<0 for x in values)/n,6)})
