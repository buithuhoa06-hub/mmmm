with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# Let's inspect renderReportEmbeddedChart and renderStep4DashboardAndReport
pos_embed = js.find("function renderReportEmbeddedChart")
pos_step4 = js.find("function renderStep4DashboardAndReport")
pos_slicers = js.find("function initDemodataSlicers")
print("pos_embed:", pos_embed, "pos_step4:", pos_step4, "pos_slicers:", pos_slicers)
