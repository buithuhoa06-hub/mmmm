with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

pos = js.find("function updateDemodataKpiCards")
print(js[pos+1500:pos+3000])
