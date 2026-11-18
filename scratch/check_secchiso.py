with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

pos = html.find('id="secChiSo"')
print(html[pos:pos+1200])
