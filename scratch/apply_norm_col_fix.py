with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

pos_detect = js.find("function detectDatasetDimensions(rows, step3Data) {")
pos_switch = js.find("function switchStep4Mode(mode = \"dashboard\") {")

print("Found detectDatasetDimensions pos:", pos_detect, "switchStep4Mode pos:", pos_switch)

new_detect_code = """function normCol(str) {
  return String(str || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/đ/g, "d")
    .replace(/Đ/g, "D")
    .toLowerCase()
    .replace(/[\s\-_]+/g, "_");
}

function detectDatasetDimensions(rows, step3Data) {
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
  let valCol = numericCandidates.find(c => /doanh_thu|revenue|sales|ngan_sach|budget|thanh_tien|tong_tien|tien|amount|gia_tri/i.test(normCol(c))) || "";

  // 2. Volume / Orders / Quantity (Số đơn / Số lượng / Volume)
  let volCol = numericCandidates.find(c => /so_don|so_luong|quantity|qty|volume|orders|don_hang|so_luot/i.test(normCol(c))) || "";

  // 3. Cost / COGS (Chi phí / Giá vốn)
  let costCol = numericCandidates.find(c => /chi_phi|cost|cogs|gia_von|expense/i.test(normCol(c))) || "";

  // 4. Profit (Lợi nhuận)
  let profitCol = numericCandidates.find(c => /loi_nhuan|profit|lai|margin/i.test(normCol(c))) || "";

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
    if (/ma_|id|code|stt|so_thu_tu/i.test(normCol(c))) return false;
    return true;
  });

  let catCol = catCandidates.find(c => /kenh|channel|san_pham|product|danh_muc|category|khu_vuc|region|loai|phong_ban/i.test(normCol(c))) || "";

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
    return /thang|month|ky|period|quy|quarter|ngay|date|nam|year/i.test(normCol(c));
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

"""

js = js[:pos_detect] + new_detect_code + js[pos_switch:]

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)

print("Applied normCol in detectDatasetDimensions successfully!")
