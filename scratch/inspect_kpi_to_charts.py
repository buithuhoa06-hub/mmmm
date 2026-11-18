with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# Let's inspect updateDemodataKpiCards
pos_kpi = js.find("function updateDemodataKpiCards")
pos_charts = js.find("function renderDemodataCharts")
print("updateDemodataKpiCards to renderDemodataCharts length:", pos_charts - pos_kpi)
print(js[pos_kpi:pos_kpi+800])
