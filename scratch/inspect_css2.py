with open("static/styles.css", "r", encoding="utf-8") as f:
    css = f.read()

pos = css.find("report-chart-embed-box")
print(css[pos:pos+1000])
