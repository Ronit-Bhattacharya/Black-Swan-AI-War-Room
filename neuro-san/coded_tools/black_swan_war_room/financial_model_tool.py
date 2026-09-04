from typing import Any, Dict
from neuro_san.interfaces.coded_tool import CodedTool
from common import parse, output
class FinancialModelTool(CodedTool):
    def invoke(self,args:Dict[str,Any],sly_data:Dict[str,Any]):
        initial=float(args["initial_investment"]); flows=[float(x) for x in parse(args["cash_flows_json"])]; rate=float(args["discount_rate"])
        npv=-initial+sum(cf/((1+rate)**y) for y,cf in enumerate(flows,1)); roi=(sum(flows)-initial)/initial
        cumulative=-initial; payback=None
        for y,cf in enumerate(flows,1):
            before=cumulative;cumulative+=cf
            if cumulative>=0 and payback is None: payback=(y-1)+(-before/cf if cf else 0)
        return output({"npv":round(npv,2),"roi":round(roi,6),"payback_years":None if payback is None else round(payback,3),"provenance":"deterministic_tool"})
