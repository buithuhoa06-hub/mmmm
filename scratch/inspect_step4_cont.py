with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

pos4 = html.find('id="panelStep4"')
print(html[pos4+3500:pos4+8000])
