with open("static/styles.css", "r", encoding="utf-8") as f:
    css = f.read()

pos = css.find("report-kpi-summary-strip")
print(css[pos-100:pos+1000])
