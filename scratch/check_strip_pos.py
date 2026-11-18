with open("static/styles.css", "r", encoding="utf-8") as f:
    css = f.read()

pos = css.find("report-kpi-summary-strip")
print("Found report-kpi-summary-strip at pos:", pos)
if pos != -1:
    print(css[pos:pos+500])
