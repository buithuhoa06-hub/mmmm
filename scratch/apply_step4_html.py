step4_new_html = """<!-- ========================================================= -->
            <!-- STEP 4: EXECUTIVE DASHBOARD & EXECUTIVE REPORT            -->
            <!-- ========================================================= -->
            <section id="panelStep4" class="step-panel">
              <!-- Minimalist, Clean Executive Report & Dashboard -->
              <div class="demodata-report-container">
                
                <!-- Title & Meta Banner -->
                <div class="demodata-header">
                  <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:14px;">
                    <div>
                      <h1 class="demodata-title" id="repMainTitle">Báo cáo Phân tích Kinh doanh & Vận hành</h1>
                      <div class="demodata-subtitle" id="repSubtitle">
                        <span id="repSubDomain">Bán lẻ đa kênh</span> · 
                        <span id="repSubDatasets">1 bộ dữ liệu</span> · 
                        <span id="repSubRows">0 dòng đã phân tích</span>
                      </div>
                    </div>
                    <div class="demodata-top-actions">
                      <button type="button" class="btn-demodata-sm" onclick="toggleStep4AdjustDrawer()" style="background:#e0f2fe; color:#0369a1; border-color:#bae6fd; font-weight:700;" title="Yêu cầu AI điều chỉnh lại nội dung phân tích">✏️ AI Phân tích lại</button>
                      <button type="button" class="btn-demodata-sm" onclick="window.print()" title="In hoặc lưu PDF">🖨️ In / Xuất PDF</button>
                      <button type="button" class="btn-demodata-sm" onclick="downloadCleanedCSV()" title="Tải file CSV đã làm sạch">⬇ Tải CSV sạch</button>
                      <button type="button" class="btn-demodata-sm" onclick="resetWorkspace()" title="Bắt đầu phiên phân tích mới">🔄 Phiên mới</button>
                    </div>
                  </div>

                  <!-- STEP 4 MODE SWITCHER: DASHBOARD VS REPORT (SEPARATE TOP-LEVEL VIEWS) -->
                  <div class="step4-mode-switcher">
                    <button type="button" id="btnModeDashboard" class="step4-mode-btn active" onclick="switchStep4Mode('dashboard')">
                      <span class="mode-icon">📊</span>
                      <span>Dashboard Điều Hành (BI Dashboard)</span>
                    </button>
                    <button type="button" id="btnModeReport" class="step4-mode-btn" onclick="switchStep4Mode('report')">
                      <span class="mode-icon">📄</span>
                      <span>Báo Cáo Chiến Lược (Executive Report)</span>
                    </button>
                  </div>

                  <!-- STEP 4 AI ADJUSTMENT DRAWER -->
                  <div id="step4AdjustDrawer" class="hidden" style="margin:16px 0; background:#f0f9ff; border:1.5px solid #0284c7; border-radius:12px; padding:16px; box-shadow:0 4px 16px rgba(2,132,199,0.08);">
                    <div style="font-weight:700; color:#0369a1; font-size:13.5px; margin-bottom:4px; display:flex; align-items:center; gap:8px;">
                      <span>🤖 Yêu cầu AI điều chỉnh lại Báo cáo & Đề xuất:</span>
                    </div>
                    <p style="font-size:12.5px; color:#475569; margin-bottom:12px;">
                      Nhập lệnh bạn muốn AI làm lại (Ví dụ: <em>"phần giải pháp ngắn gọn hơn"</em>, <em>"tập trung vào cắt giảm chi phí"</em>, <em>"rút ngắn chu kỳ tồn kho"</em>, <em>"phân bổ theo 3 giai đoạn"</em>...)
                    </p>
                    <div style="display:flex; gap:10px; flex-wrap:wrap;">
                      <input type="text" id="step4FeedbackInput" placeholder="Nhập lệnh điều chỉnh cho AI tại đây..." style="flex:1; min-width:260px; padding:9px 14px; border:1.5px solid #93c5fd; border-radius:8px; font-size:13px; outline:none; background:#ffffff;" onkeydown="if(event.key==='Enter') runStep4ReAnalysis()" />
                      <button type="button" class="btn-primary" onclick="runStep4ReAnalysis()" style="background:#0284c7; color:#fff; font-weight:700; padding:9px 20px; border-radius:8px; border:none; cursor:pointer; font-size:13px;">
                        ⚡ AI Cập nhật Ngay
                      </button>
                    </div>
                  </div>
                </div>

                <!-- ======================================================= -->
                <!-- VIEW 1: EXECUTIVE BI DASHBOARD (INDEPENDENT VIEW)       -->
                <!-- ======================================================= -->
                <div id="step4DashboardView">
                  <div class="demodata-card" style="margin-top:0;">
                    <div class="demodata-card-header-flex">
                      <div>
                        <h2 class="demodata-card-title">Trung tâm Chỉ số KPI & Bộ Lọc Tương Tác</h2>
                        <div class="demodata-kpi-sub" id="dashKpiSubMeta">Tháng 04/2026 · 0 dòng · Bán lẻ mẫu</div>
                      </div>
                      <div class="demodata-slicers-wrap">
                        <div class="demodata-slicer-box">
                          <label>Bộ dữ liệu (Sheet)</label>
                          <select id="demodataSlicerDataset" onchange="filterDemodataDashboard()"></select>
                        </div>
                        <div class="demodata-slicer-box">
                          <label>Kỳ báo cáo (Thời gian)</label>
                          <select id="demodataSlicerPeriod" onchange="filterDemodataDashboard()"></select>
                        </div>
                      </div>
                    </div>

                    <!-- 4 Clean KPI Cards -->
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

                    <!-- Interactive Charts Grid -->
                    <div class="demodata-charts-grid" style="margin-top:20px;">
                      <div class="demodata-chart-card">
                        <div class="demodata-chart-head">
                          <strong id="demodataChart1Title">Doanh thu theo Phân loại / Kênh</strong>
                        </div>
                        <div style="height:260px; position:relative;">
                          <canvas id="demodataChart1Canvas"></canvas>
                        </div>
                      </div>
                      <div class="demodata-chart-card">
                        <div class="demodata-chart-head">
                          <strong id="demodataChart2Title">Xu hướng Biến động theo Thời gian</strong>
                        </div>
                        <div style="height:260px; position:relative;">
                          <canvas id="demodataChart2Canvas"></canvas>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- ======================================================= -->
                <!-- VIEW 2: EXECUTIVE STRATEGIC REPORT (INDEPENDENT VIEW)   -->
                <!-- ======================================================= -->
                <div id="step4ReportView" class="hidden">
                  <!-- 4 Clean Underlined Tabs -->
                  <div class="demodata-tabs-row" id="demodataTabsRow">
                    <button type="button" class="demodata-tab active" onclick="jumpToReportSection('secTomTat', this)">1. Tóm tắt & Bối cảnh</button>
                    <button type="button" class="demodata-tab" onclick="jumpToReportSection('secChiSo', this)">2. Chỉ số chính & Biểu đồ</button>
                    <button type="button" class="demodata-tab" onclick="jumpToReportSection('secChuyenDe', this)">3. Phân tích chuyên đề</button>
                    <button type="button" class="demodata-tab" onclick="jumpToReportSection('secDeXuat', this)">4. Kết luận và đề xuất</button>
                  </div>

                  <!-- CARD 1: TÓM TẮT ĐIỀU HÀNH & BỐI CẢNH DOANH NGHIỆP -->
                  <div class="demodata-card" id="secTomTat">
                    <h2 class="demodata-card-title">1. Tóm tắt điều hành & Bối cảnh Doanh nghiệp</h2>
                    <!-- Context Summary Box -->
                    <div class="context-summary-box" id="demodataContextSummaryBox">
                      <div class="context-summary-info">
                        <div class="context-summary-title" id="ctxSummaryCompany">
                          🏢 Doanh nghiệp: Công ty Cổ phần Thiên Minh
                        </div>
                        <div class="context-summary-desc" id="ctxSummaryDesc">
                          🎯 Lĩnh vực kinh doanh: <strong>Bán lẻ đa kênh</strong> · Mục tiêu phân tích: <strong>Tối ưu doanh thu, tinh gọn chi phí và cải thiện biên lợi nhuận ròng</strong>.
                        </div>
                      </div>
                      <span class="context-summary-tag" id="ctxSummaryScope">Dữ liệu nội bộ · Đã làm sạch HITL</span>
                    </div>

                    <div class="demodata-card-body" id="demodataExecSummaryBody">
                      <p style="color:#64748b;">Đang tải tóm tắt điều hành...</p>
                    </div>
                  </div>

                  <!-- CARD 2: CHỈ SỐ KPI CHÍNH & BIỂU ĐỒ PHÂN TÍCH NHÚNG -->
                  <div class="demodata-card" id="secChiSo">
                    <h2 class="demodata-card-title">2. Chỉ số KPI Cốt lõi & Biểu đồ Phân tích Trực quan</h2>
                    
                    <!-- KPI Summary Strip in Report -->
                    <div class="report-kpi-summary-strip" id="reportKpiStrip">
                      <!-- Rendered by app.js -->
                    </div>

                    <!-- Embedded Chart from Dashboard for In-depth Narrative -->
                    <div class="report-chart-embed-box">
                      <div class="report-chart-embed-header">
                        <div class="report-chart-embed-title" id="reportEmbedChartTitle">
                          📊 Biểu đồ Phân tích Trọng điểm (Nhúng trực tiếp từ Dashboard)
                        </div>
                        <span style="font-size:12px; color:#0284c7; font-weight:600; background:#e0f2fe; padding:3px 9px; border-radius:6px;">Trực quan hóa Dữ liệu</span>
                      </div>
                      <div style="height:260px; position:relative; margin-bottom:12px;">
                        <canvas id="reportEmbedChartCanvas"></canvas>
                      </div>
                      <div class="report-chart-commentary" id="reportEmbedChartCommentary">
                        <!-- AI commentary on the embedded chart -->
                      </div>
                    </div>
                  </div>

                  <!-- CARD 3: PHÂN TÍCH CHUYÊN ĐỀ -->
                  <div class="demodata-card" id="secChuyenDe">
                    <h2 class="demodata-card-title">3. Phân tích chuyên đề sâu</h2>
                    <div class="demodata-card-body" id="demodataThematicBody">
                      <p style="color:#64748b;">Đang tải nội dung phân tích chuyên đề...</p>
                    </div>
                  </div>

                  <!-- CARD 4: KẾT LUẬN VÀ ĐỀ XUẤT -->
                  <div class="demodata-card" id="secDeXuat">
                    <h2 class="demodata-card-title">4. Kết luận chiến lược & Đề xuất hành động (SMART Matrix)</h2>
                    <div class="demodata-card-body" id="demodataProposalBody">
                      <p style="color:#64748b;">Đang tải ma trận đề xuất hành động...</p>
                    </div>
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

with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

start_needle = '<!-- ========================================================= -->\n            <!-- STEP 4: EXECUTIVE DASHBOARD & EXECUTIVE REPORT            -->\n            <!-- ========================================================= -->'
pos_start = html.find(start_needle)
end_needle = '</section>'
pos_end = html.find(end_needle, pos_start + 100) + len(end_needle)

new_html = html[:pos_start] + step4_new_html + html[pos_end:]

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(new_html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(new_html)

print("Updated static/index.html and index.html successfully!")
