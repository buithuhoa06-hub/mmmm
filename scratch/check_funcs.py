import re

with open("static/app.js", "r", encoding="utf-8") as f:
    content = f.read()

# Check for all functions defined
funcs = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', content)
print(f"Total functions defined in static/app.js: {len(funcs)}")
required_funcs = [
    "switchPage", "startAnalysisWorkflow", "tryJumpToStep", "validateBusinessContext",
    "quickDemoSample", "jumpToStep", "runStep1Validation", "proceedToStep2",
    "renderStep1DecisionGate", "runStep2Cleaning", "renderStep2View",
    "runStep3Analysis", "renderStep4DashboardAndReport", "jumpToReportSection",
    "filterDemodataDashboard", "updateDemodataKpiCards", "renderDemodataCharts"
]

missing = [fn for fn in required_funcs if fn not in funcs]
if missing:
    print("MISSING FUNCTIONS:", missing)
else:
    print("All required functions are defined in static/app.js!")
