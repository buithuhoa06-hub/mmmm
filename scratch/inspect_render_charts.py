with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

pos_charts = js.find("function renderDemodataCharts")
pos_next_fn = js.find("function extractMonthYearFromDateStr")
print("renderDemodataCharts block length:", pos_next_fn - pos_charts)
print(js[pos_charts:pos_next_fn])
