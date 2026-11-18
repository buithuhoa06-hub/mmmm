with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

pos = js.find("function updateDemodataCharts")
if pos != -1:
    print(js[pos:pos+1500])
else:
    print("Not found updateDemodataCharts, searching for Chart...")
    import re
    for m in re.finditer(r'new Chart\(', js):
        p = m.start()
        print("Chart instantiated around line:", js[:p].count("\n")+1)
        print(js[p-100:p+300])
        print("---")
