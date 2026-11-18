with open("static/styles.css", "r", encoding="utf-8") as f:
    css = f.read()

old_block = """/* KPI strip inside Report mode */
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
}"""

new_block = """/* KPI strip inside Report mode - Modern Card Grid */
.report-kpi-summary-strip {
  display: grid !important;
  grid-template-columns: repeat(4, 1fr) !important;
  gap: 16px !important;
  margin: 18px 0 24px 0 !important;
}
@media (max-width: 992px) {
  .report-kpi-summary-strip {
    grid-template-columns: repeat(2, 1fr) !important;
  }
}
@media (max-width: 580px) {
  .report-kpi-summary-strip {
    grid-template-columns: 1fr !important;
  }
}
.report-kpi-strip-item {
  background: #ffffff !important;
  border: 1.5px solid #e0f2fe !important;
  border-radius: 12px !important;
  padding: 16px 18px !important;
  box-shadow: 0 2px 10px rgba(2, 132, 199, 0.05) !important;
  transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
.report-kpi-strip-item:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 16px rgba(2, 132, 199, 0.12) !important;
  border-color: #7dd3fc !important;
}
.report-kpi-strip-label {
  font-size: 12px !important;
  color: #64748b !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
  margin-bottom: 6px !important;
}
.report-kpi-strip-val {
  font-size: 22px !important;
  font-weight: 800 !important;
  color: #0369a1 !important;
  display: flex !important;
  align-items: baseline !important;
  gap: 6px !important;
}
.report-kpi-strip-val span {
  font-size: 13px !important;
  font-weight: 600 !important;
  color: #0284c7 !important;
}
.report-kpi-strip-note {
  font-size: 11.5px !important;
  color: #94a3b8 !important;
  margin-top: 4px !important;
  font-weight: 500 !important;
}

/* Embedded chart in report section */
.report-chart-embed-box {
  background: #ffffff !important;
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 14px !important;
  padding: 22px !important;
  margin: 20px 0 !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
}
.report-chart-embed-header {
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  margin-bottom: 16px !important;
  padding-bottom: 12px !important;
  border-bottom: 1px solid #f1f5f9 !important;
}
.report-chart-embed-title {
  font-size: 15px !important;
  font-weight: 800 !important;
  color: #0f172a !important;
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
}
.report-chart-commentary {
  background: #f0f9ff !important;
  border-radius: 10px !important;
  padding: 14px 18px !important;
  font-size: 13.5px !important;
  color: #1e293b !important;
  line-height: 1.6 !important;
  border-left: 4px solid #0284c7 !important;
  margin-top: 14px !important;
}"""

if old_block in css:
    css = css.replace(old_block, new_block)
    with open("static/styles.css", "w", encoding="utf-8") as f:
        f.write(css)
    print("Replaced CSS block successfully!")
else:
    print("Old block not found, appending new block...")
    css += "\n" + new_block
    with open("static/styles.css", "w", encoding="utf-8") as f:
        f.write(css)
    print("Appended CSS block successfully!")
