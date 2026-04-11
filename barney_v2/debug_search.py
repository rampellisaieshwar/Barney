from core.tools import web_search
import json

res = web_search("weather in Hyderabad today")
print(json.dumps(res, indent=2))
