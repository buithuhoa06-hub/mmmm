with open("static/styles.css", "r", encoding="utf-8") as f:
    css = f.read()

if "report-kpi-summary-strip" not in css:
    extra_css = """
/* KPI strip inside Report mode */
.report-kpi-summary-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin: 14px 0 18px 0;
}
.report-kpi-strip-item {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px 14px;
}
.report-kpi-strip-label {
  font-size: 12px;
  color: #64748b;
  font-weight: 600;
  margin-bottom: 4px;
}
.report-kpi-strip-val {
  font-size: 18px;
  font-weight: 800;
  color: #0284c7;
}
.report-kpi-strip-note {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}
.report-chart-commentary {
  background: #f8fafc;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 13px;
  color: #334155;
  line-height: 1.55;
  border-left: 3.5px solid #0284c7;
}
"""
    with open("static/styles.css", "a", encoding="utf-8") as f:
        f.write(extra_css)
    print("Added report-kpi-summary-strip to static/styles.css")
else:
    print("Already in styles.css")
