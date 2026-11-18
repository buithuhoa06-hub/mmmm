import re
import shutil

# ==============================================================================
# 1. UPDATE static/index.html
# ==============================================================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Add Studio Step Wizard inside workbench-canvas right before panelStep1
wizard_html = """          <!-- Main Workspace Canvas -->
          <main class="workbench-canvas">

            <!-- Horizontal Step Wizard Bar (Step Separation & Clarity) -->
            <div class="studio-step-wizard" id="studioStepWizard">
              <button type="button" class="wizard-step-btn active" id="wizStep1" onclick="jumpToStep(1, true)">
                <span class="wiz-num">1</span>
                <span class="wiz-label">Tiếp nhận & Bối cảnh</span>
              </button>
              <span class="wiz-arrow">›</span>
              <button type="button" class="wizard-step-btn" id="wizStep2" onclick="tryJumpToStep(2)">
                <span class="wiz-num">2</span>
                <span class="wiz-label">Làm sạch & Duyệt HITL</span>
              </button>
              <span class="wiz-arrow">›</span>
              <button type="button" class="wizard-step-btn" id="wizStep3" onclick="tryJumpToStep(3)">
                <span class="wiz-num">3</span>
                <span class="wiz-label">Nhận định BI</span>
              </button>
              <span class="wiz-arrow">›</span>
              <button type="button" class="wizard-step-btn" id="wizStep4" onclick="tryJumpToStep(4)">
                <span class="wiz-num">4</span>
                <span class="wiz-label">Dashboard & Báo cáo</span>
              </button>
            </div>"""

if 'id="studioStepWizard"' not in html:
    html = html.replace('<!-- Main Workspace Canvas -->\n          <main class="workbench-canvas">', wizard_html)

# Replace panelStep4 contents with clean demodata structure
old_step4_pattern = r'<section id="panelStep4" class="step-panel">[\s\S]*?</section>'
new_step4 = """<section id="panelStep4" class="step-panel">
              <!-- Minimalist, Clean Executive Report & Dashboard (Matching demodataanalysisagent style) -->
              <div class="demodata-report-container">
                
                <!-- Title & Meta Banner -->
                <div class="demodata-header">
                  <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:14px;">
                    <div>
                      <h1 class="demodata-title" id="repMainTitle">Báo cáo kinh doanh</h1>
                      <div class="demodata-subtitle" id="repSubtitle">
                        <span id="repSubDomain">Bán lẻ đa kênh</span> · 
                        <span id="repSubDatasets">1 bộ dữ liệu</span> · 
                        <span id="repSubRows">0 dòng đã phân tích</span>
                      </div>
                    </div>
                    <div class="demodata-top-actions">
                      <button type="button" class="btn-demodata-sm" onclick="window.print()" title="In hoặc lưu PDF">🖨️ In / Xuất PDF</button>
                      <button type="button" class="btn-demodata-sm" onclick="downloadCleanedCSV()" title="Tải file CSV đã làm sạch">⬇ Tải CSV sạch</button>
                      <button type="button" class="btn-demodata-sm" onclick="resetWorkspace()" title="Bắt đầu phiên phân tích mới">🔄 Phiên mới</button>
                    </div>
                  </div>

                  <!-- 5 Clean Underlined Tabs (Image 2 style) -->
                  <div class="demodata-tabs-row" id="demodataTabsRow">
                    <button type="button" class="demodata-tab active" onclick="jumpToReportSection('secTomTat', this)">Tóm tắt</button>
                    <button type="button" class="demodata-tab" onclick="jumpToReportSection('secChiSo', this)">Chỉ số chính</button>
                    <button type="button" class="demodata-tab" onclick="jumpToReportSection('secChuyenDe', this)">Phân tích chuyên đề</button>
                    <button type="button" class="demodata-tab" onclick="jumpToReportSection('secDeXuat', this)">Kết luận và đề xuất</button>
                    <button type="button" class="demodata-tab" onclick="jumpToReportSection('secChatLuong', this)">Nguồn và chất lượng dữ liệu</button>
                  </div>
                </div>

                <!-- CARD 1: TÓM TẮT ĐIỀU HÀNH -->
                <div class="demodata-card" id="secTomTat">
                  <h2 class="demodata-card-title">Tóm tắt điều hành</h2>
                  <div class="demodata-card-body" id="demodataExecSummaryBody">
                    <p style="color:#64748b;">Đang tải tóm tắt điều hành...</p>
                  </div>
                </div>

                <!-- CARD 2: DASHBOARD KPI KINH DOANH -->
                <div class="demodata-card" id="secChiSo">
                  <div class="demodata-card-header-flex">
                    <div>
                      <h2 class="demodata-card-title">Dashboard KPI kinh doanh</h2>
                      <div class="demodata-kpi-sub" id="dashKpiSubMeta">Tháng 04/2026 · 0 dòng · Bán lẻ mẫu</div>
                    </div>
                    <div class="demodata-slicers-wrap">
                      <div class="demodata-slicer-box">
                        <label>Bộ dữ liệu</label>
                        <select id="demodataSlicerDataset" onchange="filterDemodataDashboard()"></select>
                      </div>
                      <div class="demodata-slicer-box">
                        <label>Kỳ báo cáo</label>
                        <select id="demodataSlicerPeriod" onchange="filterDemodataDashboard()"></select>
                      </div>
                    </div>
                  </div>

                  <!-- 4 Clean KPI Cards matching Image 2 -->
                  <div class="demodata-kpi-grid" id="demodataKpiGrid">
                    <div class="demodata-kpi-box">
                      <div class="kpi-box-label" id="kpiBoxLabel1">Số đơn hàng</div>
                      <div class="kpi-box-val" id="kpiBoxVal1">0</div>
                      <div class="kpi-box-unit" id="kpiBoxUnit1">Số đơn</div>
                    </div>
                    <div class="demodata-kpi-box">
                      <div class="kpi-box-label" id="kpiBoxLabel2">Doanh thu</div>
                      <div class="kpi-box-val" id="kpiBoxVal2">0</div>
                      <div class="kpi-box-unit" id="kpiBoxUnit2">VND</div>
                    </div>
                    <div class="demodata-kpi-box">
                      <div class="kpi-box-label" id="kpiBoxLabel3">Lợi nhuận</div>
                      <div class="kpi-box-val" id="kpiBoxVal3">0</div>
                      <div class="kpi-box-unit" id="kpiBoxUnit3">VND</div>
                    </div>
                    <div class="demodata-kpi-box">
                      <div class="kpi-box-label" id="kpiBoxLabel4">Chi phí</div>
                      <div class="kpi-box-val" id="kpiBoxVal4">0</div>
                      <div class="kpi-box-unit" id="kpiBoxUnit4">VND</div>
                    </div>
                  </div>

                  <!-- Minimalist Clean Charts Grid -->
                  <div class="demodata-charts-grid" style="margin-top:20px;">
                    <div class="demodata-chart-card">
                      <div class="demodata-chart-head">
                        <strong id="demodataChart1Title">Doanh thu theo Kênh / Nhóm</strong>
                      </div>
                      <div style="height:250px; position:relative;">
                        <canvas id="demodataChart1Canvas"></canvas>
                      </div>
                    </div>
                    <div class="demodata-chart-card">
                      <div class="demodata-chart-head">
                        <strong id="demodataChart2Title">Phân bổ Doanh thu theo Kỳ / Thời gian</strong>
                      </div>
                      <div style="height:250px; position:relative;">
                        <canvas id="demodataChart2Canvas"></canvas>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- CARD 3: PHÂN TÍCH CHUYÊN ĐỀ -->
                <div class="demodata-card" id="secChuyenDe">
                  <h2 class="demodata-card-title">Phân tích chuyên đề</h2>
                  <div class="demodata-card-body" id="demodataThematicBody">
                    <p style="color:#64748b;">Đang tải nội dung phân tích chuyên đề...</p>
                  </div>
                </div>

                <!-- CARD 4: KẾT LUẬN VÀ ĐỀ XUẤT -->
                <div class="demodata-card" id="secDeXuat">
                  <h2 class="demodata-card-title">Kết luận và đề xuất</h2>
                  <div class="demodata-card-body" id="demodataProposalBody">
                    <p style="color:#64748b;">Đang tải ma trận đề xuất hành động...</p>
                  </div>
                </div>

                <!-- CARD 5: NGUỒN VÀ CHẤT LƯỢNG DỮ LIỆU -->
                <div class="demodata-card" id="secChatLuong">
                  <h2 class="demodata-card-title">Nguồn và chất lượng dữ liệu</h2>
                  <div class="demodata-card-body" id="demodataQualityBody">
                    <p style="color:#64748b;">Đang tải kiểm định chất lượng dữ liệu...</p>
                  </div>
                </div>

                <!-- Bottom Actions -->
                <div class="demodata-bottom-actions">
                  <button type="button" class="btn-demodata-action" onclick="window.print()">
                    🖨️ In Báo cáo / Lưu PDF
                  </button>
                  <button type="button" class="btn-demodata-action" onclick="downloadCleanedCSV()">
                    ⬇ Tải file CSV đã làm sạch
                  </button>
                  <button type="button" class="btn-demodata-action btn-demodata-primary" onclick="resetWorkspace()">
                    🔄 Tạo phiên phân tích mới
                  </button>
                </div>

              </div>
            </section>"""

html = re.sub(old_step4_pattern, new_step4, html, count=1)

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Updated static/index.html and root index.html successfully!")
