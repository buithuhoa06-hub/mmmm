with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

pos3 = js.find("function renderStep3Feedback")
pos4 = js.find("function renderStep4DashboardAndReport")
print(js[pos3:pos4])
