with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

pos = js.find('k1.textContent = "Số bản ghi";')
print(js[pos:pos+1000])
