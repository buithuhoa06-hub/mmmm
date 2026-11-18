import re
import shutil

# ==============================================================================
# 1. UPDATE static/styles.css
# ==============================================================================
with open("static/styles.css", "r", encoding="utf-8") as f:
    css = f.read()

demodata_css = """

/* ========================================================================== */
/* STEP WIZARD BAR (Clean Step Separation)                                    */
/* ========================================================================== */
.studio-step-wizard {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: #ffffff;
  border: 1px solid #e0f2fe;
  border-radius: 14px;
  padding: 8px 16px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(2, 132, 199, 0.04);
  overflow-x: auto;
}

.wizard-step-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 9999px;
  background: transparent;
  border: 1px solid transparent;
  color: #64748b;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.wizard-step-btn:hover {
  background: #f0f7ff;
  color: #0284c7;
}

.wizard-step-btn.active {
  background: #e0f2fe !important;
  border-color: #bae6fd !important;
  color: #0284c7 !important;
  font-weight: 750 !important;
  box-shadow: 0 1px 4px rgba(2, 132, 199, 0.15) !important;
}

.wizard-step-btn.done {
  color: #0369a1;
}

.wiz-num {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #f1f5f9;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 750;
}

.wizard-step-btn.active .wiz-num {
  background: #0284c7;
  color: #ffffff;
}

.wizard-step-btn.done .wiz-num {
  background: #bae6fd;
  color: #0369a1;
}

.wiz-label {
  font-size: 12px;
}

.wiz-arrow {
  color: #cbd5e1;
  font-size: 16px;
  font-weight: 700;
}

/* ========================================================================== */
/* DEMODATA REPORT & DASHBOARD (Clean, Uncluttered Executive Look)             */
/* ========================================================================== */
.demodata-report-container {
  max-width: 1040px;
  margin: 0 auto;
  padding: 10px 0 30px;
}

.demodata-header {
  margin-bottom: 22px;
}

.demodata-title {
  font-family: var(--font-heading);
  font-size: 28px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.025em;
  line-height: 1.2;
}

.demodata-subtitle {
  font-size: 13.5px;
  color: #475569;
  font-weight: 500;
  margin-top: 6px;
  margin-bottom: 18px;
}

.demodata-top-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-demodata-sm {
  padding: 7px 14px;
  border-radius: 8px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #334155;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-demodata-sm:hover {
  background: #f8fafc;
  border-color: #0284c7;
  color: #0284c7;
}

.demodata-tabs-row {
  display: flex;
  align-items: center;
  gap: 22px;
  border-bottom: 1.5px solid #e2e8f0;
  padding-bottom: 0;
  overflow-x: auto;
}

.demodata-tab {
  padding: 10px 2px 12px;
  font-size: 13.5px;
  font-weight: 600;
  color: #64748b;
  background: none;
  border: none;
  border-bottom: 2.5px solid transparent;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.demodata-tab:hover {
  color: #0284c7;
}

.demodata-tab.active {
  color: #0284c7 !important;
  border-bottom-color: #0284c7 !important;
  font-weight: 750 !important;
}

.demodata-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 22px 24px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.demodata-card-title {
  font-family: var(--font-heading);
  font-size: 16px;
  font-weight: 750;
  color: #0f172a;
  margin-bottom: 14px;
}

.demodata-card-body {
  font-size: 13.5px;
  color: #334155;
  line-height: 1.65;
}

.demodata-card-body p {
  margin-bottom: 12px;
}

.demodata-card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 18px;
}

.demodata-kpi-sub {
  font-size: 12px;
  color: #64748b;
  margin-top: 3px;
}

.demodata-slicers-wrap {
  display: flex;
  align-items: center;
  gap: 14px;
}

.demodata-slicer-box {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.demodata-slicer-box label {
  font-size: 10.5px;
  font-weight: 600;
  color: #64748b;
}

.demodata-slicer-box select {
  min-width: 140px;
  padding: 7px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #ffffff;
  font-size: 12.5px;
  font-weight: 600;
  color: #1e293b;
  cursor: pointer;
  outline: none;
  transition: all 0.15s ease;
}

.demodata-slicer-box select:focus {
  border-color: #0284c7;
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
}

.demodata-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-top: 14px;
}

@media (max-width: 768px) {
  .demodata-kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.demodata-kpi-box {
  background: #ffffff;
  border: 1.5px solid #0284c7;
  border-radius: 12px;
  padding: 16px 18px;
  text-align: left;
  transition: all 0.2s ease;
}

.demodata-kpi-box:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.15);
}

.kpi-box-label {
  font-size: 12px;
  font-weight: 600;
  color: #475569;
}

.kpi-box-val {
  font-family: var(--font-heading);
  font-size: 26px;
  font-weight: 800;
  color: #0284c7;
  letter-spacing: -0.02em;
  margin: 6px 0 2px;
  line-height: 1.15;
}

.kpi-box-unit {
  font-size: 12.5px;
  font-weight: 700;
  color: #0284c7;
}

.demodata-charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 820px) {
  .demodata-charts-grid {
    grid-template-columns: 1fr;
  }
}

.demodata-chart-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
}

.demodata-chart-head {
  font-size: 13px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 12px;
}

.demodata-bottom-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 18px;
  border-top: 1px solid #e2e8f0;
}

.btn-demodata-action {
  padding: 10px 18px;
  border-radius: 10px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #334155;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-demodata-action:hover {
  background: #f1f5f9;
  border-color: #0284c7;
  color: #0284c7;
}

.btn-demodata-action.btn-demodata-primary {
  background: linear-gradient(135deg, #0284c7, #2563eb);
  color: #ffffff;
  border: none;
  font-weight: 700;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35);
}

.btn-demodata-action.btn-demodata-primary:hover {
  transform: translateY(-1.5px);
  box-shadow: 0 6px 18px rgba(2, 132, 199, 0.45);
}
"""

if ".demodata-report-container" not in css:
    css += demodata_css
    with open("static/styles.css", "w", encoding="utf-8") as f:
        f.write(css)
    print("Updated static/styles.css with demodata styles!")
else:
    print("static/styles.css already contains demodata styles")
