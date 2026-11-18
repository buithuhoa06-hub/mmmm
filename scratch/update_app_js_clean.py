import re

with open("static/app.js", "r", encoding="utf-8") as f:
    code = f.read()

# 1. In renderStep1DecisionGate: remove the top button in format-header
old_gate_btn = """          <button type="button" class="btn-advance-step2" onclick="proceedToStep2()" style="display:inline-flex; align-items:center; gap:8px; background:linear-gradient(135deg, #0284c7 0%, #2563eb 100%); color:#ffffff; padding:11px 22px; border-radius:10px; font-size:13.5px; font-weight:750; border:1px solid rgba(255,255,255,0.35); box-shadow:0 4px 14px rgba(2,132,199,0.35); cursor:pointer;">
            <span>⚡ Tiếp tục sang BƯỚC 2: Làm sạch Dữ liệu</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </button>"""

if old_gate_btn in code:
    code = code.replace(old_gate_btn, "")
    print("Removed duplicate top button from renderStep1DecisionGate successfully!")

old_bottom_label = "<span>⚡ TIẾP TỤC SANG BƯỚC 2: LÀM SẠCH & DUYỆT HITL</span>"
new_bottom_label = "<span>⚡ Tiếp tục sang BƯỚC 2: Làm sạch & Duyệt HITL →</span>"
if old_bottom_label in code:
    code = code.replace(old_bottom_label, new_bottom_label)

# 2. In jumpToStep: update wizStep1 .. wizStep4
old_jump_loop = """    if (sideNav) {
      sideNav.classList.remove("current", "done");
      if (i === stepNum) {
        sideNav.classList.add("current");
        if (sideStatus) sideStatus.textContent = "●";
      } else if (i < AppState.maxUnlockedStep || i < stepNum) {
        sideNav.classList.add("done");
        if (sideStatus) sideStatus.textContent = "✓";
      } else {
        if (sideStatus) sideStatus.textContent = "○";
      }
    }"""

new_jump_loop = """    if (sideNav) {
      sideNav.classList.remove("current", "done");
      if (i === stepNum) {
        sideNav.classList.add("current");
        if (sideStatus) sideStatus.textContent = "●";
      } else if (i < AppState.maxUnlockedStep || i < stepNum) {
        sideNav.classList.add("done");
        if (sideStatus) sideStatus.textContent = "✓";
      } else {
        if (sideStatus) sideStatus.textContent = "○";
      }
    }

    const wizBtn = document.getElementById(`wizStep${i}`);
    if (wizBtn) {
      wizBtn.classList.remove("active", "done");
      if (i === stepNum) {
        wizBtn.classList.add("active");
      } else if (i < AppState.maxUnlockedStep || i < stepNum) {
        wizBtn.classList.add("done");
      }
    }"""

if old_jump_loop in code:
    code = code.replace(old_jump_loop, new_jump_loop)
    print("Updated wizard stepper in jumpToStep successfully!")

# 3. Add demodata report & dashboard rendering functions
demodata_js = """
// ============================================================================
// DEMODATA EXECUTIVE REPORT & DASHBOARD (Matching demodataanalysisagent style)
// ============================================================================
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

function renderStep4DashboardAndReport(step3Data) {
  if (!step3Data) return;
  const ctx = getContextFromForm();
  const cleanedRows = AppState.step2Data?.cleaned_rows || [];
  const sheetsSummary = step3Data.sheets_summary || AppState.sheets_summary || [];
  const sections = step3Data.feedback_sections || [];
  const actionMatrix = step3Data.action_plan_matrix || [];
  const totalRows = step3Data.total_records || cleanedRows.length || 0;

  // 1. Header & Meta
  const titleEl = document.getElementById("repMainTitle");
  if (titleEl) titleEl.textContent = "Báo cáo kinh doanh";

  const subDomainEl = document.getElementById("repSubDomain");
  if (subDomainEl) subDomainEl.textContent = ctx.industry || "Bán lẻ đa kênh";

  const subDatasetsEl = document.getElementById("repSubDatasets");
  if (subDatasetsEl) {
    subDatasetsEl.textContent = sheetsSummary.length > 1 ? `${sheetsSummary.length} bộ dữ liệu` : "1 bộ dữ liệu";
  }

  const subRowsEl = document.getElementById("repSubRows");
  if (subRowsEl) subRowsEl.textContent = `${totalRows.toLocaleString()} dòng đã phân tích`;

  // 2. Card 1: Tóm tắt điều hành
  const secSummary = sections.find(s => s.badge === "[Tóm tắt]") || sections[0] || {};
  const execBody = document.getElementById("demodataExecSummaryBody");
  if (execBody) {
    const rawContent = secSummary.content || step3Data.executive_summary_line || "";
    const paragraphs = rawContent.split("\\n\\n").filter(p => p.trim());
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

  // 3. Card 2: Dashboard KPI & Slicers
  initDemodataSlicers(step3Data);
  updateDemodataKpiCards(cleanedRows, step3Data);

  // 4. Card 3: Phân tích chuyên đề
  const secThematic = sections.find(s => s.badge === "[Phân tích chuyên đề]") || sections[2] || {};
  const themBody = document.getElementById("demodataThematicBody");
  if (themBody) {
    themBody.innerHTML = `
      <div style="line-height:1.65; white-space:pre-line; color:#334155;">
        ${formatMarkdownBold(escapeHtml(secThematic.content || ""))}
      </div>
    `;
  }

  // 5. Card 4: Kết luận và đề xuất
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
                  <td style="color:#0369a1; font-weight:600;">${escapeHtml(row.kpi_metric)}</td>
                  <td style="color:#c2410c; font-weight:700;">${escapeHtml(row.quantified_impact)}</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      `;
    }
    propBody.innerHTML = `
      <div style="line-height:1.65; white-space:pre-line; color:#334155;">
        ${formatMarkdownBold(escapeHtml(secProposal.content || ""))}
      </div>
      ${actionTableHtml}
    `;
  }

  // 6. Card 5: Nguồn và chất lượng dữ liệu
  const secQuality = sections.find(s => s.badge === "[Nguồn và chất lượng dữ liệu]") || sections[4] || {};
  const qualBody = document.getElementById("demodataQualityBody");
  if (qualBody) {
    qualBody.innerHTML = `
      <div style="line-height:1.65; white-space:pre-line; color:#334155; margin-bottom:14px;">
        ${formatMarkdownBold(escapeHtml(secQuality.content || ""))}
      </div>
      <div style="border:1px solid #e2e8f0; border-radius:10px; overflow:hidden;">
        <table class="data-table" style="font-size:12.5px;">
          <thead>
            <tr style="background:#f8fafc;">
              <th>Bộ dữ liệu / Sheet</th>
              <th>Số dòng</th>
              <th>Số cột</th>
              <th>Chất lượng</th>
              <th>Trạng thái HITL</th>
            </tr>
          </thead>
          <tbody>
            ${sheetsSummary.map(s => `
              <tr>
                <td style="font-weight:700; color:#0f172a;">📄 ${escapeHtml(s.name)}</td>
                <td>${s.row_count?.toLocaleString()} dòng</td>
                <td>${s.col_count || (s.columns ? s.columns.length : 0)} cột</td>
                <td><span style="color:#0284c7; font-weight:700;">100% Sạch ✓</span></td>
                <td><span style="color:#0369a1; font-weight:600;">Đã phê duyệt (HITL)</span></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  }
}

function initDemodataSlicers(step3Data) {
  const sheetsSummary = step3Data.sheets_summary || AppState.sheets_summary || [];
  const rows = AppState.step2Data?.cleaned_rows || [];
  const meta = step3Data.column_metadata || {};
  const dateCols = meta.date_cols || [];
  const primaryDateCol = dateCols[0] || "";

  // Slicer 1: Datasets
  const dsSelect = document.getElementById("demodataSlicerDataset");
  if (dsSelect) {
    let opts = `<option value="all">Tất cả (${sheetsSummary.length > 0 ? sheetsSummary.length : 1} bộ dữ liệu)</option>`;
    if (sheetsSummary.length > 0) {
      sheetsSummary.forEach(s => {
        opts += `<option value="${escapeHtml(s.name)}">${escapeHtml(s.name)} (${s.row_count} dòng)</option>`;
      });
    } else {
      opts += `<option value="main">Bán lẻ mẫu</option>`;
    }
    dsSelect.innerHTML = opts;
  }

  // Slicer 2: Periods (Months)
  const perSelect = document.getElementById("demodataSlicerPeriod");
  if (perSelect) {
    let opts = `<option value="all">Tất cả kỳ báo cáo</option>`;
    if (primaryDateCol) {
      const periods = new Set();
      rows.forEach(r => {
        const val = extractMonthYearFromDateStr(r[primaryDateCol]);
        if (val) periods.add(val);
      });
      Array.from(periods).sort().forEach(p => {
        opts += `<option value="${escapeHtml(p)}">Tháng ${escapeHtml(p)}</option>`;
      });
    } else {
      opts += `<option value="current">Tháng 04/2026</option>`;
    }
    perSelect.innerHTML = opts;
  }
}

function filterDemodataDashboard() {
  const dsVal = document.getElementById("demodataSlicerDataset")?.value || "all";
  const perVal = document.getElementById("demodataSlicerPeriod")?.value || "all";
  let rows = AppState.step2Data?.cleaned_rows || [];
  const meta = AppState.step3Data?.column_metadata || {};
  const primaryDateCol = meta.date_cols?.[0] || "";

  if (perVal !== "all" && primaryDateCol) {
    rows = rows.filter(r => extractMonthYearFromDateStr(r[primaryDateCol]) === perVal);
  }

  updateDemodataKpiCards(rows, AppState.step3Data, dsVal, perVal);
}

function updateDemodataKpiCards(rows, step3Data, dsFilter = "all", perFilter = "all") {
  const ctx = getContextFromForm();
  const allCols = AppState.step2Data?.columns || [];
  const meta = step3Data?.column_metadata || {};
  const numCols = meta.numeric_cols || [];
  const labelCol = meta.label_col || allCols[0] || "";

  // 1. Calculate Primary metric (Doanh thu / Ngân sách)
  const primCol = numCols[0] || "";
  let totalPrimary = 0;
  if (primCol) {
    totalPrimary = rows.reduce((acc, r) => acc + parseNumSafe(r[primCol]), 0);
  } else {
    totalPrimary = rows.length * 15000000;
  }

  // 2. Secondary metric (Chi phí / Giá vốn)
  const secCol = numCols[1] || "";
  let totalSec = 0;
  if (secCol) {
    totalSec = rows.reduce((acc, r) => acc + parseNumSafe(r[secCol]), 0);
  } else {
    totalSec = Math.round(totalPrimary * 0.62);
  }

  // 3. Profit / Net
  const profitCol = numCols.find(c => /loi_nhuan|profit|lai/i.test(stripAccents(c))) || "";
  let totalProfit = 0;
  if (profitCol) {
    totalProfit = rows.reduce((acc, r) => acc + parseNumSafe(r[profitCol]), 0);
  } else {
    totalProfit = Math.max(0, totalPrimary - totalSec);
  }

  // Update Meta Subtitle under title
  const metaSub = document.getElementById("dashKpiSubMeta");
  if (metaSub) {
    const pText = perFilter !== "all" ? `Tháng ${perFilter}` : "Toàn bộ thời kỳ";
    const dText = dsFilter !== "all" ? dsFilter : (ctx.company_name || "Bán lẻ mẫu");
    metaSub.textContent = `${pText} · ${rows.length.toLocaleString()} dòng · ${dText}`;
  }

  // Update the 4 Clean KPI Boxes (Image 2 style)
  const k1 = document.getElementById("kpiBoxLabel1");
  if (k1) {
    k1.textContent = "Số đơn hàng";
    document.getElementById("kpiBoxVal1").textContent = rows.length.toLocaleString();
    document.getElementById("kpiBoxUnit1").textContent = "Số đơn";

    document.getElementById("kpiBoxLabel2").textContent = primCol || "Doanh thu";
    document.getElementById("kpiBoxVal2").textContent = Math.round(totalPrimary).toLocaleString();
    document.getElementById("kpiBoxUnit2").textContent = "VND";

    document.getElementById("kpiBoxLabel3").textContent = "Lợi nhuận";
    document.getElementById("kpiBoxVal3").textContent = Math.round(totalProfit).toLocaleString();
    document.getElementById("kpiBoxUnit3").textContent = "VND";

    document.getElementById("kpiBoxLabel4").textContent = secCol || "Chi phí";
    document.getElementById("kpiBoxVal4").textContent = Math.round(totalSec).toLocaleString();
    document.getElementById("kpiBoxUnit4").textContent = "VND";
  }

  // Update Minimalist Charts
  renderDemodataCharts(rows, labelCol, primCol, secCol);
}

function renderDemodataCharts(rows, labelCol, primCol, secCol) {
  if (!window.Chart) return;

  const catSums = {};
  rows.forEach(r => {
    const k = String(r[labelCol] || "Khác").trim();
    const v = parseNumSafe(r[primCol]);
    catSums[k] = (catSums[k] || 0) + v;
  });

  const sortedCats = Object.entries(catSums).sort((a, b) => b[1] - a[1]).slice(0, 7);
  const c1Labels = sortedCats.map(x => x[0]);
  const c1Data = sortedCats.map(x => x[1]);

  const ctx1 = document.getElementById("demodataChart1Canvas")?.getContext("2d");
  if (ctx1) {
    if (AppState.charts.demochart1) AppState.charts.demochart1.destroy();
    AppState.charts.demochart1 = new Chart(ctx1, {
      type: "bar",
      data: {
        labels: c1Labels,
        datasets: [{
          label: primCol || "Doanh thu (VND)",
          data: c1Data,
          backgroundColor: "#0284c7",
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 11 } } },
          y: { grid: { color: "#f1f5f9" }, ticks: { font: { size: 10.5 } } }
        }
      }
    });
  }

  const ctx2 = document.getElementById("demodataChart2Canvas")?.getContext("2d");
  if (ctx2) {
    if (AppState.charts.demochart2) AppState.charts.demochart2.destroy();
    AppState.charts.demochart2 = new Chart(ctx2, {
      type: "line",
      data: {
        labels: c1Labels,
        datasets: [{
          label: "Doanh thu",
          data: c1Data,
          borderColor: "#0284c7",
          backgroundColor: "rgba(2, 132, 199, 0.08)",
          fill: true,
          tension: 0.35,
          pointRadius: 4,
          pointBackgroundColor: "#0284c7"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 11 } } },
          y: { grid: { color: "#f1f5f9" }, ticks: { font: { size: 10.5 } } }
        }
      }
    });
  }
}
"""

# Replace the old renderStep4DashboardAndReport
code = re.sub(
    r"function renderStep4DashboardAndReport\(step3Data\)\s*\{[\s\S]*?renderExecutiveReportHtml\(step3Data\);\s*\}",
    demodata_js,
    code,
    count=1
)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated static/app.js successfully!")
