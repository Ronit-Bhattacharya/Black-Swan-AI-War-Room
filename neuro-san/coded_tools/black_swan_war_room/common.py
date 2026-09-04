import json
def parse(value): return value if isinstance(value,(list,dict)) else json.loads(value)
def output(data): return json.dumps(data,indent=2)
