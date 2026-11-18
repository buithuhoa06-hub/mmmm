with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# 1. Update handleManualCellEdit & renderEditableCleanedTable
old_edit_fn = """function handleManualCellEdit(rowIdx, colName, newValue) {
  if (!AppState.step2Data || !AppState.step2Data.cleaned_rows[rowIdx]) return;
  AppState.step2Data.cleaned_rows[rowIdx][colName] = newValue.trim();
}"""

new_edit_fn = """function handleManualCellEdit(rowIdx, colName, newValue, tdElem) {
  if (!AppState.step2Data || !AppState.step2Data.cleaned_rows[rowIdx]) return;
  const oldVal = AppState.step2Data.cleaned_rows[rowIdx][colName];
  const trimmed = (newValue || "").trim();
  AppState.step2Data.cleaned_rows[rowIdx][colName] = trimmed;
  if (tdElem) {
    tdElem.classList.add("cell-cleaned");
    tdElem.title = `Đã sửa thủ công: "${oldVal}" → "${trimmed}"`;
  }
  showToast(`Đã lưu chỉnh sửa ô [Dòng ${rowIdx + 1}, Cột ${colName}]`, "info");
}"""

if old_edit_fn in js:
    js = js.replace(old_edit_fn, new_edit_fn)
    print("Replaced handleManualCellEdit successfully")
else:
    print("WARNING: old_edit_fn not found")

# Replace onblur in renderEditableCleanedTable
old_blur = 'onblur="handleManualCellEdit(${rIdx}, this.getAttribute(\'data-col\'), this.innerText)"'
new_blur = 'onblur="handleManualCellEdit(${rIdx}, this.getAttribute(\'data-col\'), this.innerText, this)"'
if old_blur in js:
    js = js.replace(old_blur, new_blur)
    print("Replaced onblur in renderEditableCleanedTable successfully")
else:
    print("WARNING: old_blur not found")

# 2. Update renderStep3Feedback, confirmStep3AndGoStep4, switchStep4Mode, renderStep4DashboardAndReport, renderReportEmbeddedChart
pos_step3 = js.find("function renderStep3Feedback(data) {")
pos_step4_end = js.find("function initDemodataSlicers(step3Data) {")

if pos_step3 != -1 and pos_step4_end != -1:
    print(f"Found step3 to initDemodataSlicers region ({pos_step3} to {pos_step4_end})")
    
    new_step3_and_step4_logic = """function renderStep3Feedback(data) {
  document.getElementById("step3SummaryHint").textContent = data.executive_summary_line || "";
  const sections = data.feedback_sections || [];
  const actionMatrix = data.action_plan_matrix || [];
  const container = document.getElementById("step3FeedbackContainer");

  // Per user instruction: Keep Step 3 lean, crisp, and focused strictly on Key Problems & Proposed Solutions + Action Matrix!
  const secProblem = sections.find(s => s.badge === "[Phân tích chuyên đề]") || sections[2] || sections[0] || {};
  const secSolution = sections.find(s => s.badge === "[Kết luận và đề xuất]") || sections[3] || sections[1] || {};

  const problemsHtml = `
    <div class="feedback-card" style="border-left: 4px solid #ef4444;">
      <span class="feedback-badge" style="background:#fee2e2; color:#b91c1c;">🔍 Vấn đề Phát hiện Từ Dữ liệu</span>
      <h4>1. Các Điểm Nghẽn & Thách Thức Vận Hành Cần Giải Quyết</h4>
      <div class="feedback-body" style="line-height:1.65; color:#1e293b; font-size:13.5px;">
        ${formatMarkdownBold(escapeHtml(secProblem.content || data.executive_summary_line || ""))}
      </div>
    </div>
  `;

  const solutionsHtml = `
    <div class="feedback-card" style="border-left: 4px solid #0284c7;">
      <span class="feedback-badge" style="background:#e0f2fe; color:#0369a1;">💡 Đề xuất Giải pháp Cốt lõi</span>
      <h4>2. Định Hướng Giải Pháp Chiến Lược & Tối Ưu Hóa</h4>
      <div class="feedback-body" style="line-height:1.65; color:#1e293b; font-size:13.5px;">
        ${formatMarkdownBold(escapeHtml(secSolution.content || ""))}
      </div>
    </div>
  `;

  const matrixHtml = actionMatrix.length > 0 ? `
    <div style="grid-column: 1 / -1; background:#ffffff; border:1.5px solid #0284c7; border-radius:10px; overflow:hidden; margin-top:8px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
      <div style="background:#0284c7; color:#ffffff; padding:12px 18px; font-size:0.95rem; font-weight:700; display:flex; justify-content:space-between; align-items:center;">
        <span>🎯 MA TRẬN GIẢI PHÁP & KẾ HOẠCH HÀNH ĐỘNG SMART (MEASURABLE ACTION PLAN)</span>
        <span style="font-size:0.75rem; background:rgba(255,255,255,0.22); padding:3px 10px; border-radius:99px; font-weight:600;">Đo lường bằng KPI định lượng</span>
      </div>
      <div class="table-scroll-wrapper" style="max-height:none;">
        <table class="data-table" style="white-space:normal; font-size:12.5px;">
          <thead>
            <tr>
              <th style="width:15%; background:#f8fafc; color:#0f172a; border-bottom:2px solid #cbd5e1;">Hạng mục Giải pháp</th>
              <th style="width:25%; background:#f8fafc; color:#0f172a; border-bottom:2px solid #cbd5e1;">Vấn đề Thực tế từ Dữ liệu</th>
              <th style="width:26%; background:#f8fafc; color:#0f172a; border-bottom:2px solid #cbd5e1;">Giải pháp Triển khai Cụ thể</th>
              <th style="width:18%; background:#f8fafc; color:#0f172a; border-bottom:2px solid #cbd5e1;">Chỉ số Đo lường (KPI Target)</th>
              <th style="width:16%; background:#f8fafc; color:#0f172a; border-bottom:2px solid #cbd5e1;">Tác động Dự kiến</th>
            </tr>
          </thead>
          <tbody>
            ${actionMatrix.map(row => `
              <tr>
                <td style="vertical-align:top; font-weight:700; color:#0369a1;">
                  <span style="display:inline-block; background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:4px; font-size:0.75rem; margin-bottom:4px;">${escapeHtml(row.code || "ACT")}</span><br/>
                  ${escapeHtml(row.area || "")}
                </td>
                <td style="vertical-align:top; color:#334155;">${formatMarkdownBold(escapeHtml(row.problem || ""))}</td>
                <td style="vertical-align:top; color:#0f172a; font-weight:500;">${formatMarkdownBold(escapeHtml(row.solution || ""))}</td>
                <td style="vertical-align:top; color:#166534; font-weight:600; background:#f0fdf4;">${escapeHtml(row.kpi_metric || "")}</td>
                <td style="vertical-align:top; color:#c2410c; font-weight:700; background:#fff7ed;">${escapeHtml(row.quantified_impact || "")}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    </div>
  ` : "";

  container.innerHTML = problemsHtml + solutionsHtml + matrixHtml;

  // Reveal Step 3 confirmation gate
  document.getElementById("step3HitlGateBox")?.classList.remove("hidden");
}

function toggleStep3AdjustBox() {
  const box = document.getElementById("step3AdjustBox");
  box.classList.toggle("hidden");
  if (!box.classList.contains("hidden")) {
    box.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
}

async function runStep3ReAnalysis() {
  const fb = document.getElementById("step3FeedbackInput").value.trim();
  if (!fb) {
    alert("Vui lòng nhập nội dung điều chỉnh / phản hồi cho AI.");
    return;
  }
  await runStep3Analysis(fb);
}

function confirmStep3AndGoStep4(initialMode = "dashboard") {
  AppState.maxUnlockedStep = 4;
  jumpToStep(4, true);
  if (AppState.step3Data) {
    renderStep4DashboardAndReport(AppState.step3Data);
  }
  switchStep4Mode(initialMode);
}

// ============================================================================
// STEP 4: SEPARATE VIEWS FOR DASHBOARD & EXECUTIVE REPORT
// ============================================================================
function switchStep4Mode(mode = "dashboard") {
  const dashView = document.getElementById("step4DashboardView");
  const repView = document.getElementById("step4ReportView");
  const btnDash = document.getElementById("btnModeDashboard");
  const btnRep = document.getElementById("btnModeReport");

  if (mode === "dashboard") {
    if (dashView) dashView.classList.remove("hidden");
    if (repView) repView.classList.add("hidden");
    if (btnDash) btnDash.classList.add("active");
    if (btnRep) btnRep.classList.remove("active");
    
    // Re-render dashboard charts for proper canvas sizing
    if (AppState.step3Data) {
      const rows = AppState.step2Data?.cleaned_rows || [];
      const meta = AppState.step3Data.column_metadata || {};
      renderDemodataCharts(rows, meta.cat_col, meta.prim_col, meta.sec_col);
    }
  } else {
    if (dashView) dashView.classList.add("hidden");
    if (repView) repView.classList.remove("hidden");
    if (btnDash) btnDash.classList.remove("active");
    if (btnRep) btnRep.classList.add("active");

    // Render embedded chart inside Report
    if (AppState.step3Data) {
      renderReportEmbeddedChart(AppState.step3Data);
    }
    jumpToReportSection("secTomTat");
  }
}

function switchStep4View(mode) {
  switchStep4Mode(mode);
}

function jumpToReportSection(secId, tabEl) {
  if (tabEl) {
    document.querySelectorAll(".demodata-tab").forEach(t => t.classList.remove("active"));
    tabEl.classList.add("active");
  }
  const el = document.getElementById(secId);
  if (el) {
    el.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function toggleStep4AdjustDrawer() {
  const drawer = document.getElementById("step4AdjustDrawer");
  if (!drawer) return;
  drawer.classList.toggle("hidden");
  if (!drawer.classList.contains("hidden")) {
    document.getElementById("step4FeedbackInput")?.focus();
  }
}

async function runStep4ReAnalysis() {
  const inp = document.getElementById("step4FeedbackInput");
  const fb = (inp?.value || "").trim();
  if (!fb) {
    alert("Vui lòng nhập lệnh bạn muốn AI điều chỉnh (ví dụ: 'phần giải pháp ngắn gọn hơn').");
    inp?.focus();
    return;
  }
  
  const originalVal = inp.value;
  inp.value = "⏳ AI đang điều chỉnh lại toàn bộ nội dung phân tích & giải pháp...";
  inp.disabled = true;

  try {
    await runStep3Analysis(fb);
    if (AppState.step3Data) {
      renderStep4DashboardAndReport(AppState.step3Data);
    }
    jumpToReportSection("secDeXuat");
  } finally {
    inp.disabled = false;
    inp.value = originalVal;
  }
}

function renderReportEmbeddedChart(step3Data) {
  if (!window.Chart || !step3Data) return;
  const canvas = document.getElementById("reportEmbedChartCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const rows = AppState.step2Data?.cleaned_rows || [];
  const meta = step3Data.column_metadata || {};
  const labelCol = meta.cat_col || Object.keys(rows[0] || {})[1] || "Kênh bán";
  const primCol = meta.prim_col || meta.monetary_cols?.[0] || Object.keys(rows[0] || {})[2] || "Doanh thu";

  const catSums = {};
  rows.forEach(r => {
    const k = String(r[labelCol] || "Khác").trim();
    const v = parseNumSafe(r[primCol]);
    catSums[k] = (catSums[k] || 0) + v;
  });

  const sortedCats = Object.entries(catSums).sort((a, b) => b[1] - a[1]).slice(0, 6);
  const labels = sortedCats.map(x => x[0]);
  const data = sortedCats.map(x => x[1]);
  const total = data.reduce((a, b) => a + b, 0);

  const colors = [
    "#0284c7", "#0ea5e9", "#38bdf8", "#7dd3fc", "#bae6fd", "#94a3b8"
  ];

  if (AppState.charts.reportEmbedChart) {
    AppState.charts.reportEmbedChart.destroy();
  }

  AppState.charts.reportEmbedChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: colors.slice(0, labels.length),
        borderWidth: 2,
        borderColor: "#ffffff"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "right",
          labels: { boxWidth: 14, font: { size: 12 } }
        },
        tooltip: {
          callbacks: {
            label: function(item) {
              const val = item.raw || 0;
              const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
              return ` ${item.label}: ${Math.round(val).toLocaleString()} VND (${pct}%)`;
            }
          }
        }
      },
      cutout: "60%"
    }
  });

  // Analytical commentary
  const commEl = document.getElementById("reportEmbedChartCommentary");
  if (commEl && sortedCats.length > 0) {
    const top1 = sortedCats[0];
    const topPct = total > 0 ? ((top1[1] / total) * 100).toFixed(1) : 0;
    commEl.innerHTML = `
      <strong>💡 Phân tích từ Biểu đồ Nhúng:</strong> Nhóm <em>"${escapeHtml(top1[0])}"</em> đang chiếm tỷ trọng đóng góp lớn nhất với <strong>${topPct}%</strong> tổng ${escapeHtml(primCol)} (${Math.round(top1[1]).toLocaleString()} VND). Sự chênh lệch tỷ trọng giữa các nhóm chỉ ra cơ hội tối ưu danh mục và đa dạng hóa nguồn thu để phân tán rủi ro.
    `;
  }
}

function renderStep4DashboardAndReport(step3Data) {
  if (!step3Data) {
    step3Data = AppState.step3Data;
  }
  if (!step3Data) return;
  const ctx = getContextFromForm();
  
  // Extract rows robustly
  let cleanedRows = AppState.step2Data?.cleaned_rows || [];
  if (!cleanedRows.length && AppState.sheets && AppState.sheets.length > 0) {
    cleanedRows = AppState.sheets.flatMap(s => s.step2Data?.cleaned_rows || s.cleaned_rows || []);
  }
  if (!cleanedRows.length && AppState.step1Data?.preview_rows) {
    cleanedRows = AppState.step1Data.preview_rows;
  }
  
  const sheetsSummary = step3Data.sheets_summary || AppState.sheets_summary || [];
  const sections = step3Data.feedback_sections || [];
  const actionMatrix = step3Data.action_plan_matrix || [];
  const totalRows = step3Data.total_records || cleanedRows.length || 0;

  // 1. Header & Meta
  const titleEl = document.getElementById("repMainTitle");
  if (titleEl) titleEl.textContent = "Báo cáo Phân tích Kinh doanh & Vận hành";

  const subDomainEl = document.getElementById("repSubDomain");
  if (subDomainEl) subDomainEl.textContent = ctx.industry || "Bán lẻ đa kênh";

  const subDatasetsEl = document.getElementById("repSubDatasets");
  if (subDatasetsEl) {
    subDatasetsEl.textContent = sheetsSummary.length > 1 ? `${sheetsSummary.length} bộ dữ liệu` : "1 bộ dữ liệu";
  }

  const subRowsEl = document.getElementById("repSubRows");
  if (subRowsEl) subRowsEl.textContent = `${totalRows.toLocaleString()} dòng đã phân tích`;

  // 2. View 1 (Dashboard): Slicers & KPI Cards & Charts
  initDemodataSlicers(step3Data);
  updateDemodataKpiCards(cleanedRows, step3Data);

  // 3. View 2 (Report):
  // 3.1 Business Context Box
  const compName = ctx.company || "Công ty Cổ phần Thiên Minh";
  const industry = ctx.industry || "Bán lẻ đa kênh";
  const goal = ctx.goal || "Tối ưu doanh thu, chi phí và biên lợi nhuận ròng";
  
  const compEl = document.getElementById("ctxSummaryCompany");
  if (compEl) compEl.innerHTML = `🏢 Doanh nghiệp: <strong>${escapeHtml(compName)}</strong>`;

  const descEl = document.getElementById("ctxSummaryDesc");
  if (descEl) descEl.innerHTML = `🎯 Lĩnh vực kinh doanh: <strong>${escapeHtml(industry)}</strong> · Mục tiêu chiến lược: <strong>${escapeHtml(goal)}</strong>`;

  const scopeEl = document.getElementById("ctxSummaryScope");
  if (scopeEl) scopeEl.textContent = `${totalRows.toLocaleString()} dòng dữ liệu · Đã qua kiểm định HITL`;

  // 3.2 Executive Summary Body
  const secSummary = sections.find(s => s.badge === "[Tóm tắt]") || sections[0] || {};
  const execBody = document.getElementById("demodataExecSummaryBody");
  if (execBody) {
    const rawContent = secSummary.content || step3Data.executive_summary_line || "";
    const paragraphs = rawContent.split(/\\n\\s*\\n/).filter(p => p.trim());
    if (paragraphs.length > 0) {
      execBody.innerHTML = paragraphs.map(p => `
        <p style="margin-bottom:12px; line-height:1.65; color:#1e293b; font-size:13.5px;">
          ${formatMarkdownBold(escapeHtml(p))}
        </p>
      `).join("");
    } else {
      execBody.innerHTML = `<p>${formatMarkdownBold(escapeHtml(rawContent))}</p>`;
    }
  }

  // 3.3 Report KPI Strip
  const kpiStrip = document.getElementById("reportKpiStrip");
  if (kpiStrip) {
    const kpi1L = document.getElementById("kpiBoxLabel1")?.textContent || "Số đơn hàng";
    const kpi1V = document.getElementById("kpiBoxVal1")?.textContent || "0";
    const kpi1U = document.getElementById("kpiBoxUnit1")?.textContent || "";

    const kpi2L = document.getElementById("kpiBoxLabel2")?.textContent || "Doanh thu";
    const kpi2V = document.getElementById("kpiBoxVal2")?.textContent || "0";
    const kpi2U = document.getElementById("kpiBoxUnit2")?.textContent || "";

    const kpi3L = document.getElementById("kpiBoxLabel3")?.textContent || "Lợi nhuận";
    const kpi3V = document.getElementById("kpiBoxVal3")?.textContent || "0";
    const kpi3U = document.getElementById("kpiBoxUnit3")?.textContent || "";

    const kpi4L = document.getElementById("kpiBoxLabel4")?.textContent || "Chi phí";
    const kpi4V = document.getElementById("kpiBoxVal4")?.textContent || "0";
    const kpi4U = document.getElementById("kpiBoxUnit4")?.textContent || "";

    kpiStrip.innerHTML = `
      <div class="report-kpi-strip-item">
        <div class="report-kpi-strip-label">${escapeHtml(kpi1L)}</div>
        <div class="report-kpi-strip-val">${escapeHtml(kpi1V)} <span style="font-size:12px; font-weight:500; color:#64748b;">${escapeHtml(kpi1U)}</span></div>
        <div class="report-kpi-strip-note">Tổng sản lượng / Đơn hàng</div>
      </div>
      <div class="report-kpi-strip-item">
        <div class="report-kpi-strip-label">${escapeHtml(kpi2L)}</div>
        <div class="report-kpi-strip-val">${escapeHtml(kpi2V)} <span style="font-size:12px; font-weight:500; color:#64748b;">${escapeHtml(kpi2U)}</span></div>
        <div class="report-kpi-strip-note">Quy mô dòng tiền vào</div>
      </div>
      <div class="report-kpi-strip-item">
        <div class="report-kpi-strip-label">${escapeHtml(kpi3L)}</div>
        <div class="report-kpi-strip-val">${escapeHtml(kpi3V)} <span style="font-size:12px; font-weight:500; color:#64748b;">${escapeHtml(kpi3U)}</span></div>
        <div class="report-kpi-strip-note">Hiệu quả sinh lời ròng</div>
      </div>
      <div class="report-kpi-strip-item">
        <div class="report-kpi-strip-label">${escapeHtml(kpi4L)}</div>
        <div class="report-kpi-strip-val">${escapeHtml(kpi4V)} <span style="font-size:12px; font-weight:500; color:#64748b;">${escapeHtml(kpi4U)}</span></div>
        <div class="report-kpi-strip-note">Giá vốn & Chi phí vận hành</div>
      </div>
    `;
  }

  // 3.4 Embedded Chart inside Report
  renderReportEmbeddedChart(step3Data);

  // 3.5 Thematic Analysis
  const secThematic = sections.find(s => s.badge === "[Phân tích chuyên đề]") || sections[2] || {};
  const themBody = document.getElementById("demodataThematicBody");
  if (themBody) {
    themBody.innerHTML = `
      <div style="line-height:1.65; white-space:pre-line; color:#334155; font-size:13.5px;">
        ${formatMarkdownBold(escapeHtml(secThematic.content || ""))}
      </div>
    `;
  }

  // 3.6 Strategic Proposal & SMART Action Plan
  const secProposal = sections.find(s => s.badge === "[Kết luận và đề xuất]") || sections[3] || {};
  const propBody = document.getElementById("demodataProposalBody");
  if (propBody) {
    let actionTableHtml = "";
    if (actionMatrix.length > 0) {
      actionTableHtml = `
        <div style="border:1px solid #e2e8f0; border-radius:10px; overflow:hidden; margin-top:16px;">
          <table class="data-table" style="white-space:normal; font-size:12.5px;">
            <thead>
              <tr style="background:#f8fafc;">
                <th style="width:16%; color:#0f172a;">Hạng mục</th>
                <th style="width:24%; color:#0f172a;">Vấn đề Thực tế</th>
                <th style="width:26%; color:#0f172a;">Giải pháp Triển khai</th>
                <th style="width:18%; color:#0f172a;">Chỉ số Đo lường (KPI)</th>
                <th style="width:16%; color:#0f172a;">Tác động Định lượng</th>
              </tr>
            </thead>
            <tbody>
              ${actionMatrix.map(row => `
                <tr>
                  <td style="font-weight:700; color:#0369a1;">${escapeHtml(row.area)}</td>
                  <td>${formatMarkdownBold(escapeHtml(row.problem))}</td>
                  <td>${formatMarkdownBold(escapeHtml(row.solution))}</td>
                  <td style="color:#166534; font-weight:600; background:#f0fdf4;">${escapeHtml(row.kpi_metric)}</td>
                  <td style="color:#c2410c; font-weight:700; background:#fff7ed;">${escapeHtml(row.quantified_impact)}</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      `;
    }
    propBody.innerHTML = `
      <div style="line-height:1.65; white-space:pre-line; color:#334155; font-size:13.5px;">
        ${formatMarkdownBold(escapeHtml(secProposal.content || ""))}
      </div>
      ${actionTableHtml}
    `;
  }
}
"""

    js = js[:pos_step3] + new_step3_and_step4_logic + js[pos_step4_end:]
    print("Replaced step3 to step4 logic successfully!")

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)

print("Saved static/app.js successfully!")
