with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

pos = js.find("function renderStep4DashboardAndReport")
print(js[pos:pos+3000])
