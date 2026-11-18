with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

pos3 = js.find("function renderStep3Feedback")
pos4 = js.find("function renderStep4DashboardAndReport")
block = js[pos3:pos4]
import re
for m in re.finditer(r'function\s+([A-Za-z0-9_]+)', block):
    print("Function in block:", m.group(1))
