with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

pos_kpi = js.find("function updateDemodataKpiCards")
pos_next_fn = js.find("function extractMonthYearFromDateStr")

print(f"Replacing region from updateDemodataKpiCards ({pos_kpi}) to extractMonthYearFromDateStr ({pos_next_fn})")

new_kpi_and_charts_code = """function updateDemodataKpiCards(rows, step3Data, dsFilter = "all", perFilter = "all") {
  if (!step3Data) step3Data = AppState.step3Data || {};
  const ctx = getContextFromForm();
  
  if (!rows || rows.length === 0) {
    if (AppState.step2Data?.cleaned_rows?.length) {
      rows = AppState.step2Data.cleaned_rows;
    } else if (AppState.sheets && AppState.sheets.length > 0) {
      rows = AppState.sheets.flatMap(s => s.step2Data?.cleaned_rows || s.cleaned_rows || []);
    } else if (AppState.step1Data?.preview_rows) {
      rows = AppState.step1Data.preview_rows;
    }
  }

  const dims = detectDatasetDimensions(rows, step3Data);

  // Update Meta Subtitle
  const metaSub = document.getElementById("dashKpiSubMeta");
  if (metaSub) {
    const pText = perFilter !== "all" ? `Tháng ${perFilter}` : "Toàn bộ thời kỳ";
    const dText = dsFilter !== "all" ? dsFilter : (ctx.company || "Dữ liệu kinh doanh");
    metaSub.textContent = `${pText} · ${rows.length.toLocaleString()} dòng · ${dText}`;
  }

  // Update the 4 Clean KPI Boxes in Dashboard
  const k1 = document.getElementById("kpiBoxLabel1");
  if (k1) {
    // Box 1: Volume / Số đơn
    k1.textContent = dims.volCol || "Số đơn hàng";
    document.getElementById("kpiBoxVal1").textContent = Math.round(dims.totalVolume).toLocaleString();
    document.getElementById("kpiBoxUnit1").textContent = dims.volCol ? "Đơn" : "Bản ghi";

    // Box 2: Doanh thu
    document.getElementById("kpiBoxLabel2").textContent = dims.valCol || "Tổng Doanh thu";
    document.getElementById("kpiBoxVal2").textContent = Math.round(dims.totalRevenue).toLocaleString();
    document.getElementById("kpiBoxUnit2").textContent = "VND";

    // Box 3: Lợi nhuận
    document.getElementById("kpiBoxLabel3").textContent = dims.profitCol || "Lợi nhuận ước tính";
    document.getElementById("kpiBoxVal3").textContent = Math.round(dims.totalProfit).toLocaleString();
    document.getElementById("kpiBoxUnit3").textContent = "VND";

    // Box 4: Chi phí
    document.getElementById("kpiBoxLabel4").textContent = dims.costCol || "Chi phí & Giá vốn";
    document.getElementById("kpiBoxVal4").textContent = Math.round(dims.totalCost).toLocaleString();
    document.getElementById("kpiBoxUnit4").textContent = "VND";
  }

  // Update Dashboard Charts
  renderDemodataCharts(rows, dims);
}

function renderDemodataCharts(rows, dims) {
  if (!window.Chart) return;
  if (!rows || rows.length === 0) {
    rows = AppState.step2Data?.cleaned_rows || [];
  }
  if (!dims) {
    dims = detectDatasetDimensions(rows, AppState.step3Data);
  }

  const catCol = dims.catCol || Object.keys(rows[0] || {})[1] || "Phân loại";
  const valCol = dims.valCol || Object.keys(rows[0] || {})[Object.keys(rows[0] || {}).length - 1] || "Doanh thu";
  const dateCol = dims.dateCol || "";

  // 1. Group by catCol for Chart 1 (Bar Chart)
  const catSums = {};
  rows.forEach(r => {
    const k = String(r[catCol] || "Khác").trim() || "Khác";
    const v = parseNumSafe(r[valCol]);
    catSums[k] = (catSums[k] || 0) + v;
  });

  const sortedCats = Object.entries(catSums).sort((a, b) => b[1] - a[1]).slice(0, 7);
  const c1Labels = sortedCats.map(x => x[0]);
  const c1Data = sortedCats.map(x => x[1]);

  // Update Chart 1 Header Title
  const title1 = document.getElementById("demodataChart1Title");
  if (title1) title1.textContent = `${valCol} theo ${catCol}`;

  const ctx1 = document.getElementById("demodataChart1Canvas")?.getContext("2d");
  if (ctx1) {
    if (AppState.charts.demochart1) AppState.charts.demochart1.destroy();
    AppState.charts.demochart1 = new Chart(ctx1, {
      type: "bar",
      data: {
        labels: c1Labels.length > 0 ? c1Labels : ["Không có dữ liệu"],
        datasets: [{
          label: valCol || "Doanh thu (VND)",
          data: c1Data.length > 0 ? c1Data : [0],
          backgroundColor: "#0284c7",
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (item) => ` ${item.label}: ${Math.round(item.raw || 0).toLocaleString()} VND`
            }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 11, weight: "600" }, color: "#475569" } },
          y: {
            grid: { color: "#f1f5f9" },
            ticks: {
              font: { size: 10.5 },
              callback: (v) => formatVietnameseBigNumber(v)
            }
          }
        }
      }
    });
  }

  // 2. Group by dateCol (or secondary category if no date) for Chart 2 (Line/Trend Chart)
  const timeGroupingCol = dateCol || (Object.keys(rows[0] || {}).find(c => c !== catCol && c !== valCol && !/ma_|id/i.test(stripAccents(c))) || catCol);
  const timeSums = {};
  rows.forEach(r => {
    let k = String(r[timeGroupingCol] || "").trim();
    if (dateCol) k = extractMonthYearFromDateStr(k) || k;
    if (!k) k = "Khác";
    const v = parseNumSafe(r[valCol]);
    timeSums[k] = (timeSums[k] || 0) + v;
  });

  const sortedTime = Object.entries(timeSums).sort((a, b) => a[0].localeCompare(b[0]));
  const c2Labels = sortedTime.map(x => x[0]);
  const c2Data = sortedTime.map(x => x[1]);

  // Update Chart 2 Header Title
  const title2 = document.getElementById("demodataChart2Title");
  if (title2) title2.textContent = `Xu hướng ${valCol} theo ${timeGroupingCol}`;

  const ctx2 = document.getElementById("demodataChart2Canvas")?.getContext("2d");
  if (ctx2) {
    if (AppState.charts.demochart2) AppState.charts.demochart2.destroy();
    AppState.charts.demochart2 = new Chart(ctx2, {
      type: "line",
      data: {
        labels: c2Labels.length > 0 ? c2Labels : ["Kỳ hiện tại"],
        datasets: [{
          label: valCol || "Doanh thu",
          data: c2Data.length > 0 ? c2Data : [0],
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
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (item) => ` ${item.label}: ${Math.round(item.raw || 0).toLocaleString()} VND`
            }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 11, weight: "600" }, color: "#475569" } },
          y: {
            grid: { color: "#f1f5f9" },
            ticks: {
              font: { size: 10.5 },
              callback: (v) => formatVietnameseBigNumber(v)
            }
          }
        }
      }
    });
  }
}

"""

js = js[:pos_kpi] + new_kpi_and_charts_code + js[pos_next_fn:]

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)

print("Applied new updateDemodataKpiCards and renderDemodataCharts successfully!")
