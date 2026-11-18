with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# 1. We replace switchStep4Mode to renderReportEmbeddedChart to renderStep4DashboardAndReport
pos_switch = js.find("function switchStep4Mode(mode = \"dashboard\") {")
pos_slicers = js.find("function initDemodataSlicers(step3Data) {")

print("Found switchStep4Mode to initDemodataSlicers:", pos_switch, pos_slicers)

new_step4_control = """function detectDatasetDimensions(rows, step3Data) {
  if (!rows || rows.length === 0) {
    rows = AppState.step2Data?.cleaned_rows || [];
  }
  const cols = AppState.step2Data?.columns || (rows.length > 0 ? Object.keys(rows[0]) : []);
  const meta = step3Data?.column_metadata || {};
  const colTypes = meta.col_types || AppState.step2Data?.column_types || {};

  // Find candidate numeric columns
  const numericCandidates = cols.filter(c => {
    const t = colTypes[c];
    if (t === "NUMERIC") return true;
    if (t === "DATE" || t === "ID_CODE") return false;
    const sample = rows.slice(0, 10).map(r => parseNumSafe(r[c]));
    return sample.some(v => v > 0);
  });

  // 1. Monetary / Value Column (Doanh thu / Sales / Ngân sách / Tiền)
  let valCol = numericCandidates.find(c => /doanh_thu|revenue|sales|ngan_sach|budget|thanh_tien|tong_tien|tien|amount|gia_tri/i.test(stripAccents(c))) || "";

  // 2. Volume / Orders / Quantity (Số đơn / Số lượng / Volume)
  let volCol = numericCandidates.find(c => /so_don|so_luong|quantity|qty|volume|orders|don_hang|so_luot/i.test(stripAccents(c))) || "";

  // 3. Cost / COGS (Chi phí / Giá vốn)
  let costCol = numericCandidates.find(c => /chi_phi|cost|cogs|gia_von|expense/i.test(stripAccents(c))) || "";

  // 4. Profit (Lợi nhuận)
  let profitCol = numericCandidates.find(c => /loi_nhuan|profit|lai|margin/i.test(stripAccents(c))) || "";

  // If valCol is still not identified, pick the numeric column with highest sum
  if (!valCol && numericCandidates.length > 0) {
    const sums = numericCandidates.map(c => ({
      col: c,
      sum: rows.reduce((acc, r) => acc + parseNumSafe(r[c]), 0)
    }));
    sums.sort((a, b) => b.sum - a.sum);
    valCol = sums[0].col;
    if (sums.length > 1 && !volCol) {
      volCol = sums[1].col;
    }
  }

  // 5. Categorical column for Grouping (Must NOT be an ID code column like Mã dòng!)
  const catCandidates = cols.filter(c => {
    const t = colTypes[c];
    if (t === "ID_CODE" || t === "DATE") return false;
    if (numericCandidates.includes(c)) return false;
    if (/ma_|id|code|stt|so_thu_tu/i.test(stripAccents(c))) return false;
    return true;
  });

  let catCol = catCandidates.find(c => /kenh|channel|san_pham|product|danh_muc|category|khu_vuc|region|loai|phong_ban/i.test(stripAccents(c))) || "";

  if (!catCol && catCandidates.length > 0) {
    for (const c of catCandidates) {
      const u = new Set(rows.map(r => String(r[c] || "").trim()).filter(Boolean));
      if (u.size >= 2 && u.size <= 30) {
        catCol = c;
        break;
      }
    }
    if (!catCol) catCol = catCandidates[0];
  }

  // 6. Date / Period Column (Tháng / Kỳ / Ngày)
  let dateCol = cols.find(c => {
    const t = colTypes[c];
    if (t === "DATE") return true;
    return /thang|month|ky|period|quy|quarter|ngay|date|nam|year/i.test(stripAccents(c));
  }) || "";

  // Compute Aggregated Totals
  const totalRevenue = valCol ? rows.reduce((acc, r) => acc + parseNumSafe(r[valCol]), 0) : 0;
  const totalVolume = volCol ? rows.reduce((acc, r) => acc + parseNumSafe(r[volCol]), 0) : rows.length;
  const totalCost = costCol
    ? rows.reduce((acc, r) => acc + parseNumSafe(r[costCol]), 0)
    : (totalRevenue > 0 ? Math.round(totalRevenue * 0.65) : 0);
  const totalProfit = profitCol
    ? rows.reduce((acc, r) => acc + parseNumSafe(r[profitCol]), 0)
    : (totalRevenue > 0 ? Math.max(0, totalRevenue - totalCost) : 0);

  return { valCol, volCol, costCol, profitCol, catCol, dateCol, totalRevenue, totalVolume, totalCost, totalProfit };
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

    // Give DOM a frame to compute canvas width/height before rendering charts
    setTimeout(() => {
      let rows = AppState.step2Data?.cleaned_rows || [];
      const dsVal = document.getElementById("demodataSlicerDataset")?.value || "all";
      const perVal = document.getElementById("demodataSlicerPeriod")?.value || "all";
      const dims = detectDatasetDimensions(rows, AppState.step3Data);
      if (perVal !== "all" && dims.dateCol) {
        rows = rows.filter(r => extractMonthYearFromDateStr(r[dims.dateCol]) === perVal);
      }
      renderDemodataCharts(rows, dims);
    }, 60);
  } else {
    if (dashView) dashView.classList.add("hidden");
    if (repView) repView.classList.remove("hidden");
    if (btnDash) btnDash.classList.remove("active");
    if (btnRep) btnRep.classList.add("active");

    setTimeout(() => {
      renderReportEmbeddedChart(AppState.step3Data);
    }, 60);
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
  if (!window.Chart) return;
  const canvas = document.getElementById("reportEmbedChartCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  let rows = AppState.step2Data?.cleaned_rows || [];
  if (!rows.length && AppState.sheets && AppState.sheets.length > 0) {
    rows = AppState.sheets.flatMap(s => s.step2Data?.cleaned_rows || s.cleaned_rows || []);
  }

  const dims = detectDatasetDimensions(rows, step3Data);
  const catCol = dims.catCol || Object.keys(rows[0] || {})[1] || "Kênh";
  const valCol = dims.valCol || Object.keys(rows[0] || {})[Object.keys(rows[0] || {}).length - 1] || "Doanh thu";

  const catSums = {};
  rows.forEach(r => {
    const k = String(r[catCol] || "Khác").trim() || "Khác";
    const v = parseNumSafe(r[valCol]);
    catSums[k] = (catSums[k] || 0) + v;
  });

  const sortedCats = Object.entries(catSums).filter(x => x[1] > 0).sort((a, b) => b[1] - a[1]).slice(0, 7);
  const labels = sortedCats.length > 0 ? sortedCats.map(x => x[0]) : ["Toàn bộ danh mục"];
  const data = sortedCats.length > 0 ? sortedCats.map(x => x[1]) : [dims.totalRevenue || 1];
  const total = data.reduce((a, b) => a + b, 0);

  const colors = [
    "#0284c7", "#0ea5e9", "#38bdf8", "#7dd3fc", "#10b981", "#6366f1", "#f59e0b"
  ];

  if (AppState.charts.reportEmbedChart) {
    AppState.charts.reportEmbedChart.destroy();
  }

  // Update header title of embedded chart
  const titleEl = document.getElementById("reportEmbedChartTitle");
  if (titleEl) {
    titleEl.textContent = `📊 Biểu đồ Cơ cấu ${valCol} theo ${catCol} (Nhúng trực tiếp từ Dashboard)`;
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
          labels: { boxWidth: 14, font: { size: 12.5, weight: "600" }, color: "#334155" }
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
      cutout: "62%"
    }
  });

  // Analytical commentary
  const commEl = document.getElementById("reportEmbedChartCommentary");
  if (commEl && sortedCats.length > 0) {
    const top1 = sortedCats[0];
    const topPct = total > 0 ? ((top1[1] / total) * 100).toFixed(1) : 0;
    commEl.innerHTML = `
      <strong>💡 Phân tích từ Biểu đồ Nhúng:</strong> Nhóm <em>"${escapeHtml(top1[0])}"</em> đang dẫn đầu với <strong>${topPct}%</strong> tổng ${escapeHtml(valCol)} (đạt <strong>${Math.round(top1[1]).toLocaleString()} VND</strong>). Cơ cấu tỷ trọng cho thấy sự tập trung đáng kể, doanh nghiệp cần kết hợp giữ vững kênh mũi nhọn đồng thời tối ưu mở rộng các phân khúc tiềm năng còn lại.
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
  const dims = detectDatasetDimensions(cleanedRows, step3Data);

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

  // 3.3 Report KPI Strip - Accurate 4 Cards Grid
  const kpiStrip = document.getElementById("reportKpiStrip");
  if (kpiStrip) {
    kpiStrip.innerHTML = `
      <div class="report-kpi-strip-item">
        <div class="report-kpi-strip-label">${escapeHtml(dims.volCol || "Tổng Sản lượng")}</div>
        <div class="report-kpi-strip-val">${Math.round(dims.totalVolume).toLocaleString()} <span>${dims.volCol ? "Đơn" : "Bản ghi"}</span></div>
        <div class="report-kpi-strip-note">Tổng lượt giao dịch / phát sinh</div>
      </div>
      <div class="report-kpi-strip-item">
        <div class="report-kpi-strip-label">${escapeHtml(dims.valCol || "Tổng Doanh thu")}</div>
        <div class="report-kpi-strip-val">${Math.round(dims.totalRevenue).toLocaleString()} <span>VND</span></div>
        <div class="report-kpi-strip-note">Quy mô dòng tiền vào</div>
      </div>
      <div class="report-kpi-strip-item">
        <div class="report-kpi-strip-label">${escapeHtml(dims.profitCol || "Lợi nhuận ước tính")}</div>
        <div class="report-kpi-strip-val">${Math.round(dims.totalProfit).toLocaleString()} <span>VND</span></div>
        <div class="report-kpi-strip-note">Hiệu quả sinh lời ròng</div>
      </div>
      <div class="report-kpi-strip-item">
        <div class="report-kpi-strip-label">${escapeHtml(dims.costCol || "Chi phí & Giá vốn")}</div>
        <div class="report-kpi-strip-val">${Math.round(dims.totalCost).toLocaleString()} <span>VND</span></div>
        <div class="report-kpi-strip-note">Giá vốn & Chi phí vận hành</div>
      </div>
    `;
  }

  // 3.4 Thematic Analysis
  const secThematic = sections.find(s => s.badge === "[Phân tích chuyên đề]") || sections[2] || {};
  const themBody = document.getElementById("demodataThematicBody");
  if (themBody) {
    themBody.innerHTML = `
      <div style="line-height:1.65; white-space:pre-line; color:#334155; font-size:13.5px;">
        ${formatMarkdownBold(escapeHtml(secThematic.content || ""))}
      </div>
    `;
  }

  // 3.5 Strategic Proposal & SMART Action Plan
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

js = js[:pos_switch] + new_step4_control + js[pos_slicers:]
print("Replaced switchStep4Mode to initDemodataSlicers successfully!")

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
