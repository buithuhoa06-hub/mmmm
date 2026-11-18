with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

funcs_to_find = [
    "handleManualCellEdit",
    "renderEditableCleanedTable",
    "renderStep3Feedback",
    "confirmStep3AndGoStep4",
    "switchStep4View",
    "renderStep4DashboardAndReport"
]

for fn in funcs_to_find:
    pos = js.find(f"function {fn}")
    print(f"=== {fn} ===")
    if pos != -1:
        print(js[pos:pos+500])
    else:
        print("NOT FOUND")
