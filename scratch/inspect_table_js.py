with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

pos = js.find("function renderEditableCleanedTable")
print(js[pos:pos+1500])
