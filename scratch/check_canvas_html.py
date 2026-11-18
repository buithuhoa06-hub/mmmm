with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

pos = html.find("reportEmbedChartCanvas")
print(html[pos-200:pos+300])
