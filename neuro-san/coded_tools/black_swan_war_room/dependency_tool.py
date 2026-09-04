from typing import Any, Dict
from collections import defaultdict,deque
from neuro_san.interfaces.coded_tool import CodedTool
from common import parse,output
class DependencyTool(CodedTool):
    def invoke(self,args:Dict[str,Any],sly_data:Dict[str,Any]):
        g=parse(args["graph_json"]); ids={n["id"] for n in g["nodes"]}; adj=defaultdict(list); indeg=defaultdict(int)
        for e in g["edges"]:
            if e["source"] not in ids or e["target"] not in ids: raise ValueError("Unknown dependency node")
            adj[e["source"]].append(e["target"]);indeg[e["target"]]+=1
        critical=[]
        for n in g["nodes"]:
            d=len(adj[n["id"]])+indeg[n["id"]]
            if d>=2 or n.get("single_source"):critical.append({"id":n["id"],"label":n.get("label",n["id"]),"degree":d,"single_source":bool(n.get("single_source"))})
        return output({"critical_nodes":sorted(critical,key=lambda x:(x["single_source"],x["degree"]),reverse=True)})
