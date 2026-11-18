with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

pos_init = js.find("function initDemodataSlicers")
pos_charts = js.find("function renderDemodataCharts")
end_charts = js.find("// ============================================================================", pos_charts)
print("=== Region from initDemodataSlicers to end of renderDemodataCharts ===")
print("Length:", end_charts - pos_init)
print(js[pos_charts:end_charts])
