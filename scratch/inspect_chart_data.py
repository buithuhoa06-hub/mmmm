with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

import re
pos = js.find("function renderDemodataCharts")
print("=== renderDemodataCharts ===")
print(js[pos:pos+1500])

pos2 = js.find("function updateDemodataKpiCards")
print("\n=== updateDemodataKpiCards ===")
print(js[pos2:pos2+1500])
