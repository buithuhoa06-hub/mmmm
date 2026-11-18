with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

pos_init = js.find("function initDemodataSlicers")
print("initDemodataSlicers pos:", pos_init)
pos_charts = js.find("function renderDemodataCharts")
print("renderDemodataCharts pos:", pos_charts)
pos_filter = js.find("function filterDemodataDashboard")
print("filterDemodataDashboard pos:", pos_filter)
