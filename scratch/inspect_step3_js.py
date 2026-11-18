with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

pos = js.find("function renderStep3Feedback")
print(js[pos:pos+2500])
