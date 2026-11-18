// ============================================================================
// BI AI AGENT — FRONTEND CONTROLLER (4-STEP HUMAN-IN-THE-LOOP WORKFLOW)
// ============================================================================

if (window.ChartDataLabels) {
  Chart.register(window.ChartDataLabels);
}

const AppState = {
  currentStep: 1,
  maxUnlockedStep: 1,
  normalizedCsv: "",
  sheets: [],
  activeSheetIdx: 0,
  step1Data: null,
  step2Data: null,
  step3Data: null,
  charts: {
    aging: null,
    workingCapital: null,
    pnl: null
  }
};

// Initialize clean workspace on page load
window.addEventListener("DOMContentLoaded", () => {
  resetWorkspace();
});

function resetWorkspace() {
  document.getElementById("ctxCompany").value = "";
  document.getElementById("ctxIndustry").value = "";
  document.getElementById("ctxAudience").value = "";
  document.getElementById("ctxObjective").value = "";
  document.getElementById("rawInputText").value = "";
  const fileEl = document.getElementById("fileUploadInput");
  if (fileEl) fileEl.value = "";
  const gsheetInput = document.getElementById("gsheetUrlInput");
  if (gsheetInput) gsheetInput.value = "";
  const gsheetStatus = document.getElementById("gsheetStatusMsg");
  if (gsheetStatus) {
    gsheetStatus.className = "gsheet-status-msg hidden";
    gsheetStatus.innerHTML = "";
  }
  ["multiSheetSelectorBar", "step2ExcelTabBar"].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.classList.add("hidden");
      el.innerHTML = "";
    }
  });

  AppState.currentStep = 1;
  AppState.maxUnlockedStep = 1;
  AppState.normalizedCsv = "";
  AppState.sheets = [];
  AppState.activeSheetIdx = 0;
  AppState.step1Data = null;
  AppState.step2Data = null;
  AppState.step3Data = null;

  document.getElementById("step1ResultBox").classList.add("hidden");
  document.getElementById("step1ResultBox").innerHTML = "";
  document.getElementById("step2HitlGateBox")?.classList.add("hidden");
  document.getElementById("step2TableQuickActions")?.classList.add("hidden");
  document.getElementById("step3HitlGateBox")?.classList.add("hidden");
  updateSidebarSourceStatus();
  jumpToStep(1, true);
}

function getContextFromForm() {
  return {
    company_name: document.getElementById("ctxCompany").value.trim() || "Doanh nghiệp của bạn",
    industry: document.getElementById("ctxIndustry").value.trim() || "Đa ngành (Business Intelligence)",
    target_audience: document.getElementById("ctxAudience").value.trim() || "Ban Giám đốc (CEO / CFO)",
    objective: document.getElementById("ctxObjective").value.trim() || "Phân tích số liệu BI & Tối ưu hiệu quả hoạt động"
  };
}

// Initialize Loaded Sheets from Excel / Google Sheets
function initLoadedSheets(sheets, rawInput, rowCount, colCount, columns) {
  if (sheets && sheets.length > 0) {
    AppState.sheets = sheets.map(s => ({
      name: s.name,
      row_count: s.row_count || 0,
      col_count: s.col_count || (s.columns ? s.columns.length : 0),
      columns: s.columns || [],
      csv: s.csv || "",
      step1Data: null,
      step2Data: null,
      step3Data: null
    }));
  } else {
    AppState.sheets = [{
      name: "Sheet 1",
      row_count: rowCount || 0,
      col_count: colCount || (columns ? columns.length : 0),
      columns: columns || [],
      csv: rawInput || "",
      step1Data: null,
      step2Data: null,
      step3Data: null
    }];
  }

  AppState.activeSheetIdx = 0;
  const rawArea = document.getElementById("rawInputText");
  if (rawArea) {
    rawArea.value = AppState.sheets[0].csv || rawInput || "";
  }
  renderAllExcelTabBars();
  updateSidebarSourceStatus();
}

// Render Excel Sheet Tabs only for Step 1 and Step 2
// (Step 3 & 4 provide unified analysis across all sheets without tab fragmentation)
function renderAllExcelTabBars() {
  renderExcelTabBarForContainer("multiSheetSelectorBar", 1);
  renderExcelTabBarForContainer("step2ExcelTabBar", 2);
}

function renderExcelTabBarForContainer(elementId, stepNum) {
  const bar = document.getElementById(elementId);
  if (!bar) return;

  if (!AppState.sheets || AppState.sheets.length <= 1) {
    bar.classList.add("hidden");
    bar.innerHTML = "";
    return;
  }

  let html = `
    <span class="excel-sheet-tabs-label">📑 Các Sheet (${AppState.sheets.length}):</span>
  `;

  AppState.sheets.forEach((s, idx) => {
    const isActive = (idx === AppState.activeSheetIdx);
    html += `
      <button type="button" class="excel-sheet-tab ${isActive ? 'active' : ''}" onclick="switchExcelSheet(${idx}, ${stepNum})">
        <span class="excel-sheet-tab-icon">📑</span>
        <span class="excel-sheet-tab-title">${escapeHtml(s.name)}</span>
        <span class="excel-sheet-tab-count">${(s.row_count || 0).toLocaleString()} dòng</span>
      </button>
    `;
  });

  bar.innerHTML = html;
  bar.classList.remove("hidden");
}

async function switchExcelSheet(targetIdx, fromStep) {
  if (targetIdx < 0 || targetIdx >= AppState.sheets.length) return;
  AppState.activeSheetIdx = targetIdx;
  const currentSheet = AppState.sheets[targetIdx];
  renderAllExcelTabBars();

  if (fromStep === 1 || AppState.currentStep === 1) {
    const rawArea = document.getElementById("rawInputText");
    if (rawArea) {
      rawArea.value = currentSheet.csv || "";
      rawArea.classList.add("flash-highlight");
      setTimeout(() => rawArea.classList.remove("flash-highlight"), 600);
    }
    runStep1Validation();
  } else if (fromStep === 2 || AppState.currentStep === 2) {
    if (currentSheet.step2Data) {
      AppState.step2Data = currentSheet.step2Data;
      renderStep2View(currentSheet.step2Data);
    } else {
      await runStep2Cleaning("");
    }
  } else if (fromStep === 3 || AppState.currentStep === 3) {
    if (currentSheet.step3Data) {
      AppState.step3Data = currentSheet.step3Data;
      renderStep3Feedback(currentSheet.step3Data);
    } else {
      if (!currentSheet.step2Data) {
        await runStep2Cleaning("");
      }
      await runStep3Analysis("");
    }
  } else if (fromStep === 4 || AppState.currentStep === 4) {
    if (!currentSheet.step3Data) {
      if (!currentSheet.step2Data) {
        await runStep2Cleaning("");
      }
      await runStep3Analysis("");
    }
    renderStep4DashboardAndReport(currentSheet.step3Data || AppState.step3Data);
  }
}

// Backward compatibility alias for any existing click handlers
function selectSheetMode(idx) {
  switchExcelSheet(Number(idx) || 0, AppState.currentStep);
}

// Handle file upload (.csv, .xlsx, .json)
async function handleFileUpload(event) {
  const file = event.target.files?.[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  showGSheetStatus("loading", `⏳ Đang đọc dữ liệu từ file '${file.name}'...`);

  try {
    const res = await fetch("/api/upload-file", {
      method: "POST",
      body: formData
    });
    if (!res.ok) {
      const err = await res.json();
      showGSheetStatus("error", `❌ ${err.detail || "Không thể đọc file."}`);
      return;
    }
    const data = await res.json();
    initLoadedSheets(data.sheets || [], data.raw_input || "", data.row_count || 0, data.col_count || 0, data.columns || []);
    if (data.message) {
      showGSheetStatus("success", `✅ ${data.message}`);
    }
    runStep1Validation();
  } catch (e) {
    showGSheetStatus("error", "❌ Lỗi tải file: " + e.message);
  }
}

// Import Google Sheet direct link
async function importGoogleSheet() {
  const input = document.getElementById("gsheetUrlInput");
  const btn = document.getElementById("btnImportGSheet");
  const url = (input?.value || "").trim();

  if (!url) {
    showGSheetStatus("error", "⚠️ Vui lòng dán link Google Sheets của bạn vào ô trên.");
    input?.focus();
    return;
  }

  // Update UI to loading
  if (btn) btn.disabled = true;
  const originalBtnText = btn ? btn.innerHTML : "⚡ Nạp dữ liệu";
  if (btn) btn.innerHTML = `⏳ Đang tải...`;
  showGSheetStatus("loading", "⏳ Đang kết nối và tải tất cả các Sheet từ Google Sheet...");

  try {
    const res = await fetch("/api/import-gsheet", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });

    const data = await res.json();
    if (!res.ok) {
      showGSheetStatus("error", `❌ ${data.detail || "Không thể tải Google Sheet."}`);
      return;
    }

    initLoadedSheets(data.sheets || [], data.raw_input || "", data.row_count || 0, data.col_count || 0, data.columns || []);

    const rawArea = document.getElementById("rawInputText");
    if (rawArea) {
      rawArea.classList.add("flash-highlight");
      setTimeout(() => rawArea.classList.remove("flash-highlight"), 1200);
    }

    showGSheetStatus("success", `✅ ${data.message || `Đã nạp ${data.row_count} dòng, ${data.col_count} cột thành công!`}`);

    // Automatically trigger Step 1 Validation
    runStep1Validation();
  } catch (err) {
    showGSheetStatus("error", `❌ Lỗi kết nối: ${err.message || "Không thể liên lạc với máy chủ."}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = originalBtnText;
    }
  }
}

function showGSheetStatus(type, htmlMsg) {
  const msgBox = document.getElementById("gsheetStatusMsg");
  if (!msgBox) return;
  msgBox.className = `gsheet-status-msg ${type}`;
  msgBox.innerHTML = htmlMsg;
  msgBox.classList.remove("hidden");
}

// Update Sidebar Source Telemetry Status
function updateSidebarSourceStatus() {
  const fileNameEl = document.getElementById("sideSourceFileName");
  const detailsEl = document.getElementById("sideSourceDetails");
  const dotEl = document.getElementById("sideSourceDot");
  if (!fileNameEl || !detailsEl) return;

  const currentSheet = AppState.sheets[AppState.activeSheetIdx];
  const sheetCount = AppState.sheets?.length || 0;
  const rowCount = AppState.step2Data?.summary?.rows_after || currentSheet?.row_count || 0;
  const colCount = AppState.step2Data?.summary?.total_columns || currentSheet?.col_count || 0;

  if (sheetCount > 0 || rowCount > 0) {
    fileNameEl.textContent = currentSheet?.name ? `Sheet: ${currentSheet.name}` : "Dữ liệu sẵn sàng";
    detailsEl.textContent = `${rowCount.toLocaleString()} dòng • ${colCount} cột • ${sheetCount} Sheet`;
    if (dotEl) dotEl.className = "status-indicator-dot connected";
  } else {
    fileNameEl.textContent = "Chưa nạp dữ liệu";
    detailsEl.textContent = "0 dòng • 0 cột • 0 Sheet";
    if (dotEl) dotEl.className = "status-indicator-dot";
  }
}

// Quick Sample Data Loader (For instant 1-click enterprise demo)
// ============================================================================
// PAGE SWITCHING & BUSINESS CONTEXT VALIDATION (2-Page Architecture)
// ============================================================================
function switchPage(pageId) {
  const pageHome = document.getElementById("pageHome");
  const pageStudio = document.getElementById("pageStudio");
  const navTabHome = document.getElementById("navTabHome");
  const navTabStudio = document.getElementById("navTabStudio");

  if (pageId === "home") {
    if (pageHome) {
      pageHome.classList.add("active");
      pageHome.classList.remove("hidden-page");
    }
    if (pageStudio) {
      pageStudio.classList.remove("active");
      pageStudio.classList.add("hidden-page");
    }
    if (navTabHome) navTabHome.classList.add("active");
    if (navTabStudio) navTabStudio.classList.remove("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  } else {
    // pageId === "studio"
    if (pageHome) {
      pageHome.classList.remove("active");
      pageHome.classList.add("hidden-page");
    }
    if (pageStudio) {
      pageStudio.classList.add("active");
      pageStudio.classList.remove("hidden-page");
    }
    if (navTabHome) navTabHome.classList.remove("active");
    if (navTabStudio) navTabStudio.classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

function startAnalysisWorkflow() {
  switchPage("studio");
  jumpToStep(1, true);
  const companyInput = document.getElementById("ctxCompany");
  if (companyInput && !companyInput.value.trim()) {
    companyInput.focus();
    companyInput.classList.add("input-required-pulse");
    setTimeout(() => companyInput.classList.remove("input-required-pulse"), 1800);
  }
}

function tryJumpToStep(stepNum) {
  if (stepNum >= 2) {
    if (!validateBusinessContext()) {
      return;
    }
  }
  switchPage("studio");
  jumpToStep(stepNum, true);
}

function validateBusinessContext() {
  const company = document.getElementById("ctxCompany")?.value?.trim() || "";
  const objective = document.getElementById("ctxObjective")?.value?.trim() || "";

  if (!company) {
    alert("⚠️ BẮT BUỘC NHẬP BỐI CẢNH DOANH NGHIỆP:\nVui lòng nhập 'Tên Doanh nghiệp / Dự án' ở Bước 1A trước khi tiếp tục!");
    switchPage("studio");
    jumpToStep(1, true);
    const compInput = document.getElementById("ctxCompany");
    if (compInput) {
      compInput.scrollIntoView({ behavior: "smooth", block: "center" });
      compInput.focus();
      compInput.classList.add("input-required-pulse");
      setTimeout(() => compInput.classList.remove("input-required-pulse"), 2000);
    }
    return false;
  }

  if (!objective) {
    alert("⚠️ BẮT BUỘC NHẬP MỤC TIÊU PHÂN TÍCH:\nVui lòng nhập 'Bối cảnh & Mục tiêu Phân tích' ở Bước 1A để AI nắm rõ bài toán kinh doanh!");
    switchPage("studio");
    jumpToStep(1, true);
    const objInput = document.getElementById("ctxObjective");
    if (objInput) {
      objInput.scrollIntoView({ behavior: "smooth", block: "center" });
      objInput.focus();
      objInput.classList.add("input-required-pulse");
      setTimeout(() => objInput.classList.remove("input-required-pulse"), 2000);
    }
    return false;
  }

  return true;
}

function quickDemoSample() {
  switchPage("studio");
  jumpToStep(1, true);
  document.getElementById("ctxCompany").value = "Tập đoàn Đầu tư & Công nghệ Alpha";
  document.getElementById("ctxIndustry").value = "Công nghệ thông tin & Bán lẻ B2B";
  document.getElementById("ctxAudience").value = "Ban Giám đốc (CEO, CFO, Giám đốc Vận hành)";
  document.getElementById("ctxObjective").value = "Phân tích quy mô ngân sách dự án, tối ưu hóa chu kỳ phê duyệt hợp đồng và cân đối năng lực đội ngũ theo vùng miền.";

  const sampleCsv = `Project_ID,Project_Name,Department,Client_Name,Budget,Discount_Rate,Request_Date,Proposal_Deadline
PRJ-2026-001,Triển khai ERP Cloud,Công nghệ,Tập đoàn Mai Linh,850000000,0.08,01/01/2026,15/01/2026
PRJ-2026-002,Hệ thống CRM Omnichannel,Kinh doanh,Bán lẻ Vinmart,1200000000,0.12,05/01/2026,20/01/2026
PRJ-2026-003,Nâng cấp Hạ tầng Cloud,Hạ tầng,Ngân hàng Techcombank,2400000000,0.05,08/01/2026,28/01/2026
PRJ-2026-004,Phần mềm Quản lý Kho WMS,Vận hành,Shopee Express,650000000,0.10,10/01/2026,18/01/2026
PRJ-2026-005,Tích hợp Thanh toán Tự động,Tài chính,Ví Momo,450000000,0.00,12/01/2026,22/01/2026
PRJ-2026-006,Xây dựng BI Dashboard,Phân tích dữ liệu,Masan Group,1500000000,0.15,15/01/2026,30/01/2026
PRJ-2026-007,Ứng dụng Loyalty App,Marketing,Highlands Coffee,780000000,0.05,18/01/2026,25/01/2026
PRJ-2026-008,Bảo mật Hệ thống SOC,An ninh mạng,Viettel Post,1900000000,0.08,20/01/2026,05/02/2026`;

  document.getElementById("rawInputText").value = sampleCsv;

  // Scroll smoothly to studio workbench
  const studioEl = document.getElementById("analysisStudio");
  if (studioEl) {
    studioEl.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // Flash highlight on raw input
  const rawArea = document.getElementById("rawInputText");
  if (rawArea) {
    rawArea.classList.add("flash-highlight");
    setTimeout(() => rawArea.classList.remove("flash-highlight"), 800);
  }

  // Trigger step 1 validation automatically
  runStep1Validation();
}

// Navigation between steps
function jumpToStep(stepNum, force = false) {
  if (stepNum >= 2 && !force) {
    if (!validateBusinessContext()) {
      return;
    }
  }
  if (!force && stepNum > AppState.maxUnlockedStep) {
    return;
  }
  AppState.currentStep = stepNum;
  for (let i = 1; i <= 4; i++) {
    const panel = document.getElementById(`panelStep${i}`);
    const wf = document.getElementById(`wfStep${i}`);
    const status = document.getElementById(`wfStatus${i}`);
    const sideNav = document.getElementById(`sideNavStep${i}`);
    const sideStatus = document.getElementById(`sideNavStatus${i}`);

    if (panel) panel.classList.toggle("active", i === stepNum);

    if (wf) {
      wf.classList.remove("active", "done");
      if (i === stepNum) {
        wf.classList.add("active");
        if (status) status.textContent = "Đang thực hiện";
      } else if (i < AppState.maxUnlockedStep || i < stepNum) {
        wf.classList.add("done");
        if (status) status.textContent = "Hoàn tất ✓";
      } else {
        if (status) status.textContent = "Chờ";
      }
    }

    if (sideNav) {
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
    }
  }

  updateSidebarSourceStatus();
  renderAllExcelTabBars();

  if (stepNum === 2) {
    if (AppState.step2Data) {
      renderStep2View(AppState.step2Data);
    } else {
      runStep2Cleaning("");
    }
  } else if (stepNum === 3) {
    if (AppState.step3Data) {
      renderStep3Feedback(AppState.step3Data);
    } else {
      runStep3Analysis("");
    }
  } else if (stepNum === 4) {
    if (AppState.step3Data) {
      renderStep4DashboardAndReport(AppState.step3Data);
    }
  }

  // Smooth scroll to studio workbench if moving beyond step 1
  if (stepNum > 1) {
    const studioEl = document.getElementById("analysisStudio");
    if (studioEl) {
      studioEl.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }
}

// ============================================================================
// STEP 1: CONTEXT ANALYSIS & FORMAT CHECK
// ============================================================================
async function runStep1Validation() {
  if (!validateBusinessContext()) {
    return;
  }
  const rawInput = document.getElementById("rawInputText").value.trim();

  if (!rawInput) {
    alert("Vui lòng nhập hoặc dán dữ liệu của bạn (hoặc tải file CSV/Excel/JSON lên) trước khi phân tích.");
    document.getElementById("rawInputText").focus();
    return;
  }

  const context = getContextFromForm();
  const resultBox = document.getElementById("step1ResultBox");
  resultBox.classList.remove("hidden");
  resultBox.innerHTML = `<div class="card"><p>⏳ AI đang phân tích bối cảnh doanh nghiệp và kiểm tra định dạng dữ liệu của bạn...</p></div>`;

  try {
    const res = await fetch("/api/step1/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ context, raw_input: rawInput })
    });
    const data = await res.json();
    AppState.step1Data = data;
    renderStep1DecisionGate(data);
  } catch (e) {
    resultBox.innerHTML = `<div class="card"><p style="color:#dc2626;">Lỗi kiểm tra định dạng: ${e.message}</p></div>`;
  }
}

function renderStep1DecisionGate(data) {
  const resultBox = document.getElementById("step1ResultBox");
  const ctxInfo = data.context_analysis || {};

  if (data.is_valid) {
    AppState.normalizedCsv = data.normalized_csv || document.getElementById("rawInputText").value;
    resultBox.innerHTML = `
      <div class="format-box valid">
        <div class="format-header">
          <div>
            <span class="format-badge-valid">✓ ĐÚNG ĐỊNH DẠNG (${escapeHtml(data.format_type)} • Độ tin cậy ${data.confidence}%)</span>
            <h3 style="margin-top:8px; color:#0369a1;">Dữ liệu đạt chuẩn cấu trúc bảng (${data.row_count} dòng × ${data.column_count} cột)</h3>
            <p style="font-size:12px; color:#475569; margin-top:2px;">Bối cảnh doanh nghiệp và cấu trúc cột đã được xác thực thành công.</p>
          </div>

        </div>

        <div style="display:grid; grid-template-columns: 1fr 1.5fr; gap:14px; margin-top:12px;">
          <div style="background:#ffffff; border:1px solid #bfdbfe; border-radius:10px; padding:14px; font-size:0.85rem;">
            <div style="font-weight:700; color:#0369a1; margin-bottom:6px;">🧠 AI Phân tích Bối cảnh Doanh nghiệp:</div>
            <p><strong>Doanh nghiệp:</strong> ${escapeHtml(ctxInfo.company_name)}</p>
            <p><strong>Ngành nghề:</strong> ${escapeHtml(ctxInfo.detected_domain)}</p>
            <p><strong>Mục tiêu:</strong> ${escapeHtml(ctxInfo.objective)}</p>
            <p style="margin-top:8px; font-weight:600; color:#1e293b;">Các trường dữ liệu phát hiện:</p>
            <ul style="margin-left:18px; margin-top:4px; color:#334155; line-height:1.5;">
              ${(ctxInfo.recommended_kpis || []).map(k => `<li>${escapeHtml(k)}</li>`).join("")}
            </ul>
          </div>

          <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; overflow:hidden;">
            <div style="background:#f1f5f9; padding:8px 12px; font-size:11.5px; font-weight:700; color:#1e293b; border-bottom:1px solid #e2e8f0;">
              Xem trước cấu trúc cột (${data.columns.length} cột): ${data.columns.slice(0, 8).join(", ")}${data.columns.length > 8 ? "..." : ""}
            </div>
            <div class="table-scroll-wrapper" style="max-height:175px;">
              ${buildSimplePreviewTable(data.columns, data.preview_rows.slice(0, 5))}
            </div>
          </div>
        </div>

        <div class="format-footer-action" style="margin-top:18px; padding-top:16px; border-top:1.5px dashed #bae6fd; display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap;">
          <div class="footer-action-note" style="display:flex; align-items:center; gap:8px; font-size:13px; font-weight:600; color:#0369a1;">
            <span class="pulse-beacon"></span>
            <span><strong>Dữ liệu chuẩn:</strong> Bấm nút bên phải để AI bắt đầu quét lỗi & chuẩn hóa dữ liệu:</span>
          </div>
          <button type="button" class="btn-advance-step2-full" onclick="proceedToStep2()" style="display:inline-flex; align-items:center; justify-content:center; gap:10px; background:linear-gradient(135deg, #0284c7 0%, #1d4ed8 100%); color:#ffffff; padding:14px 28px; border-radius:12px; font-size:14.5px; font-weight:800; border:1px solid rgba(255,255,255,0.35); box-shadow:0 6px 22px rgba(2,132,199,0.45); cursor:pointer;">
            <span>⚡ Tiếp tục sang BƯỚC 2: Làm sạch & Duyệt HITL →</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </button>
        </div>
      </div>
    `;
  } else {
    resultBox.innerHTML = `
      <div class="format-box invalid">
        <div class="format-header">
          <div>
            <span class="format-badge-invalid">✕ SAI ĐỊNH DẠNG (${escapeHtml(data.format_type)})</span>
            <h3 style="margin-top:8px; color:#991b1b;">Phát hiện lỗi cấu trúc định dạng dữ liệu đầu vào!</h3>
          </div>
        </div>

        <div class="error-list-box">
          <strong>⚠️ Chi tiết lỗi định dạng AI phát hiện:</strong>
          <ul>
            ${(data.errors || []).map(err => `<li>${escapeHtml(err)}</li>`).join("")}
          </ul>
        </div>

        <h4 style="font-size:0.92rem; color:#1e293b;">Vui lòng chọn 1 trong 2 phương án xử lý theo quy trình:</h4>
        <div class="two-options-grid">
          <!-- Option 1: Manual Re-entry -->
          <div class="option-card">
            <h4>✍️ Lựa chọn 1: Nhập lại / Chỉnh sửa thủ công</h4>
            <p>Tự chỉnh sửa lại văn bản dữ liệu thô, tách cột bằng dấu phẩy (CSV) chuẩn hoặc tải lên một file dữ liệu khác.</p>
            <button class="btn-outline-sm" onclick="focusRawInputManual()">
              👆 Nhập / Sửa lại thủ công tại ô Dữ liệu
            </button>
          </div>

          <!-- Option 2: AI Auto-Format Suggestion -->
          <div class="option-card option-ai">
            <h4>🤖 Lựa chọn 2: AI gợi ý điền / chuẩn hóa lại đúng định dạng</h4>
            <p>AI Agent sẽ tự động phân tích dữ liệu của bạn, tách các trường bị gộp, loại bỏ dòng ghi chú thừa và điền lại thành bảng chuẩn.</p>
            <div style="display:flex; gap:8px; margin-bottom:8px;">
              <input type="text" id="aiFormatHintInput" placeholder="Ghi chú thêm cho AI (tùy chọn)..." style="flex:1; padding:6px 10px; border:1px solid #fcd34d; border-radius:6px; font-size:0.8rem;" />
              <button class="btn-primary" onclick="runStep1AiReformat()">
                ✨ AI Gợi Ý & Điền Lại Đúng Định Dạng
              </button>
            </div>
          </div>
        </div>

        <div id="aiReformatPreviewContainer" class="hidden" style="margin-top:16px;"></div>
      </div>
    `;
  }
  resultBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function focusRawInputManual() {
  const rawEl = document.getElementById("rawInputText");
  rawEl.focus();
  rawEl.scrollIntoView({ behavior: "smooth", block: "center" });
}

async function runStep1AiReformat() {
  const context = getContextFromForm();
  const rawInput = document.getElementById("rawInputText").value;
  const userHint = document.getElementById("aiFormatHintInput")?.value || "";
  const container = document.getElementById("aiReformatPreviewContainer");
  container.classList.remove("hidden");
  container.innerHTML = `<p style="padding:12px; font-weight:600; color:#1565c0;">⏳ AI đang tái cấu trúc và điền lại bảng dữ liệu của bạn đúng định dạng...</p>`;

  try {
    const res = await fetch("/api/step1/ai-reformat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ context, raw_input: rawInput, user_hint: userHint })
    });
    const data = await res.json();
    AppState.normalizedCsv = data.reconstructed_csv;

    container.innerHTML = `
      <div class="ai-log-list">
        <strong>✅ AI đã chuẩn hóa và điền lại định dạng bảng thành công (${data.row_count} dòng × ${data.column_count} cột):</strong>
        <ul style="margin-left:18px; margin-top:6px;">
          ${(data.ai_actions_log || []).map(l => `<li>${escapeHtml(l)}</li>`).join("")}
        </ul>
      </div>
      <div style="background:#fff; border:1px solid #cbd5e1; border-radius:8px; overflow:hidden; margin-bottom:12px;">
        <div style="background:#1e3a5f; color:#fff; padding:7px 12px; font-size:0.8rem; font-weight:600;">
          Bản xem trước Dữ liệu sau khi AI điền lại đúng định dạng:
        </div>
        <div class="table-scroll-wrapper" style="max-height:220px;">
          ${buildSimplePreviewTable(data.columns, data.preview_rows)}
        </div>
      </div>
      <div style="display:flex; justify-content:flex-end; gap:10px;">
        <button class="btn-outline-sm" onclick="applyReformattedToTextarea()">📝 Cập nhật vào ô Dữ liệu gốc</button>
        <button class="btn-success btn-lg" onclick="applyReformattedAndGoStep2()">
          ✅ Xác nhận Định dạng AI Gợi ý & Sang BƯỚC 2 →
        </button>
      </div>
    `;
  } catch (e) {
    container.innerHTML = `<p style="color:#dc2626;">Lỗi chuẩn hóa định dạng: ${e.message}</p>`;
  }
}

function applyReformattedToTextarea() {
  if (AppState.normalizedCsv) {
    document.getElementById("rawInputText").value = AppState.normalizedCsv;
    runStep1Validation();
  }
}

function applyReformattedAndGoStep2() {
  if (AppState.normalizedCsv) {
    document.getElementById("rawInputText").value = AppState.normalizedCsv;
  }
  proceedToStep2();
}

async function proceedToStep2() {
  if (!validateBusinessContext()) {
    return;
  }
  const rawInput = document.getElementById("rawInputText")?.value?.trim() || "";
  if (!rawInput && !AppState.normalizedCsv && !AppState.uploadedMultiSheets) {
    alert("⚠️ Vui lòng nhập hoặc tải file dữ liệu ở Bước 1B trước khi tiếp tục!");
    document.getElementById("rawInputText")?.focus();
    return;
  }
  AppState.maxUnlockedStep = Math.max(AppState.maxUnlockedStep, 2);
  jumpToStep(2, true);
  await runStep2Cleaning("");
}

// ============================================================================
// STEP 2: DATA CLEANING & HUMAN-IN-THE-LOOP CONFIRMATION
// ============================================================================
async function runStep2Cleaning(customInstruction = "") {
  const context = getContextFromForm();
  const currentSheet = AppState.sheets[AppState.activeSheetIdx] || {};
  const rawCsv = currentSheet.csv || AppState.normalizedCsv || document.getElementById("rawInputText").value;

  // Hide confirmation gate & table actions while AI is still scanning/cleaning!
  document.getElementById("step2HitlGateBox")?.classList.add("hidden");
  document.getElementById("step2ReCleanBox")?.classList.add("hidden");
  document.getElementById("step2TableQuickActions")?.classList.add("hidden");
  document.getElementById("step2CustomRulesLog")?.classList.add("hidden");

  document.getElementById("step2ScoreBadges").innerHTML = "";
  document.getElementById("step2SummaryRow").innerHTML = "";
  document.getElementById("issueCountPill").textContent = "⏳ Đang quét...";

  const issuesContainer = document.getElementById("issuesListContainer");
  issuesContainer.innerHTML = `<p style="padding:16px; color:#1565c0; font-weight:600;">⏳ AI đang quét lỗi dữ liệu thô và thực hiện làm sạch...</p>`;

  const tableContainer = document.getElementById("cleanedTableContainer");
  if (tableContainer) {
    tableContainer.innerHTML = `<p style="padding:16px; color:#64748b; font-weight:500;">⏳ Đang chờ AI xử lý và chuẩn hóa dữ liệu...</p>`;
  }

  try {
    const res = await fetch("/api/step2/clean", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        context,
        raw_csv: rawCsv,
        custom_instruction: customInstruction
      })
    });
    const data = await res.json();
    if (!res.ok) {
      issuesContainer.innerHTML = `<p style="color:#dc2626; padding:14px;">❌ Lỗi làm sạch dữ liệu: ${escapeHtml(data.detail || "Không thể xử lý dữ liệu.")}</p>`;
      return;
    }
    AppState.step2Data = data;
    if (AppState.sheets[AppState.activeSheetIdx]) {
      AppState.sheets[AppState.activeSheetIdx].step2Data = data;
    }
    renderStep2View(data);
    renderAllExcelTabBars();
  } catch (e) {
    issuesContainer.innerHTML = `<p style="color:#dc2626; padding:14px;">❌ Lỗi làm sạch: ${escapeHtml(e.message)}</p>`;
  }
}

function renderStep2View(data) {
  const s = data.summary || {};
  document.getElementById("step2ScoreBadges").innerHTML = `
    <span class="step-pill" style="background:#64748b;">Chất lượng dữ liệu thô: ${s.quality_score_before}%</span>
    <span style="margin:0 6px; font-weight:700;">→</span>
    <span class="step-pill" style="background:#16a34a;">Sau khi AI làm sạch: ${s.quality_score_after}%</span>
  `;

  document.getElementById("step2SummaryRow").innerHTML = `
    <div class="clean-stat-card">
      <div class="clean-stat-label">Số bản ghi (Trước → Sau làm sạch)</div>
      <div class="clean-stat-val">${s.rows_before} → ${s.rows_after} dòng</div>
    </div>
    <div class="clean-stat-card">
      <div class="clean-stat-label">Tổng số lỗi phát hiện & xử lý</div>
      <div class="clean-stat-val" style="color:#ea580c;">${s.issues_count} lỗi dữ liệu</div>
    </div>
    <div class="clean-stat-card">
      <div class="clean-stat-label">Số trường chỉ số (Columns)</div>
      <div class="clean-stat-val">${s.total_columns} cột chuẩn</div>
    </div>
    <div class="clean-stat-card">
      <div class="clean-stat-label">Trạng thái Kiểm định</div>
      <div class="clean-stat-val" style="color:#16a34a; font-size:1.1rem;">Chờ bạn xác nhận ✓</div>
    </div>
  `;

  const customBanner = document.getElementById("step2CustomRulesLog");
  if (data.custom_rules_applied && data.custom_rules_applied.length > 0) {
    customBanner.classList.remove("hidden");
    customBanner.innerHTML = `
      <strong>✨ AI đã thực thi yêu cầu làm sạch tùy chỉnh của bạn:</strong>
      <ul style="margin-left:18px; margin-top:4px;">
        ${data.custom_rules_applied.map(r => `<li>${escapeHtml(r)}</li>`).join("")}
      </ul>
    `;
  } else {
    customBanner.classList.add("hidden");
  }

  document.getElementById("issueCountPill").textContent = `${(data.issues || []).length} lỗi đã sửa`;
  renderStep2IssuesList(data.issues || [], false);
  renderEditableCleanedTable(data, false);

  // Reveal confirmation gate & table quick actions AFTER AI has finished cleaning!
  document.getElementById("step2TableQuickActions")?.classList.remove("hidden");
  updateSidebarSourceStatus();
  const hitlGate = document.getElementById("step2HitlGateBox");
  if (hitlGate) {
    hitlGate.classList.remove("hidden");
  }
}

function renderStep2IssuesList(issues, showAll = false) {
  const issuesList = document.getElementById("issuesListContainer");
  if (!issuesList) return;
  if (!issues || issues.length === 0) {
    issuesList.innerHTML = `<div style="padding:18px; color:#166534; font-weight:600;">🎉 Dữ liệu của bạn không có lỗi định dạng số, ô trống hay trùng lặp nào! Bạn có thể bấm Xác nhận ĐẠT hoặc chỉnh sửa trực tiếp trên bảng bên phải.</div>`;
    return;
  }
  const MAX_ISSUES = 150;
  const slice = showAll ? issues : issues.slice(0, MAX_ISSUES);
  let html = slice.map((iss, idx) => `
    <div class="issue-item">
      <div class="issue-item-top">
        <span>#${idx + 1} • ${escapeHtml(iss.issue_type)}</span>
        <span>Dòng ${iss.row} | Cột: ${escapeHtml(iss.column)}</span>
      </div>
      <div class="issue-diff">
        <span class="val-raw">${escapeHtml(iss.raw_value)}</span>
        <span>→</span>
        <span class="val-clean">${escapeHtml(iss.cleaned_value)}</span>
      </div>
      <div class="issue-reason">💡 ${escapeHtml(iss.reason)}</div>
    </div>
  `).join("");

  if (!showAll && issues.length > MAX_ISSUES) {
    html += `
      <div style="text-align:center; padding:10px;">
        <button type="button" class="btn-outline-sm" onclick="renderStep2IssuesList(AppState.step2Data.issues, true)">
          🔽 Xem toàn bộ ${issues.length} lỗi đã làm sạch
        </button>
      </div>
    `;
  }
  issuesList.innerHTML = html;
}

function renderEditableCleanedTable(data, showAll = false) {
  const cols = data.columns || [];
  const rows = data.cleaned_rows || [];

  // O(1) lookup set for highlighted cells so large multi-sheet tables render instantly
  const cleanedCellSet = new Set((data.issues || []).map(iss => `${iss.row - 1}:${iss.column}`));
  const MAX_ROWS = 200;
  const visibleRows = showAll ? rows : rows.slice(0, MAX_ROWS);

  let html = `
    <table class="data-table" id="step2EditableGrid">
      <thead>
        <tr>
          <th>#</th>
          ${cols.map(c => `<th>${escapeHtml(c)}</th>`).join("")}
          <th>Thao tác</th>
        </tr>
      </thead>
      <tbody>
        ${visibleRows.map((r, rIdx) => `
          <tr data-row-idx="${rIdx}">
            <td style="font-weight:700; color:#64748b;">${rIdx + 1}</td>
            ${cols.map(c => {
              const isHighlighted = cleanedCellSet.has(`${rIdx}:${c}`);
              return `<td contenteditable="true"
                          class="${isHighlighted ? 'cell-cleaned' : ''}"
                          data-col="${escapeHtml(c)}"
                          onblur="handleManualCellEdit(${rIdx}, this.getAttribute('data-col'), this.innerText, this)">${escapeHtml(String(r[c] ?? ""))}</td>`;
            }).join("")}
            <td>
              <button class="btn-xs" style="color:#dc2626;" onclick="deleteRowStep2(${rIdx})" title="Xóa dòng này">✕</button>
            </td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;

  if (!showAll && rows.length > MAX_ROWS) {
    html += `
      <div style="text-align:center; padding:12px; background:#f8fafc; border-top:1px solid #e2e8f0;">
        <span style="font-size:0.8rem; color:#475569; margin-right:8px;">Đang hiển thị ${MAX_ROWS}/${rows.length} dòng đầu tiên để tối ưu tốc độ.</span>
        <button type="button" class="btn-outline-sm" onclick="renderEditableCleanedTable(AppState.step2Data, true)">
          🔽 Hiển thị toàn bộ ${rows.length} dòng
        </button>
      </div>
    `;
  }
  document.getElementById("cleanedTableContainer").innerHTML = html;
}

function handleManualCellEdit(rowIdx, colName, newValue, tdElem) {
  if (!AppState.step2Data || !AppState.step2Data.cleaned_rows[rowIdx]) return;
  const oldVal = AppState.step2Data.cleaned_rows[rowIdx][colName];
  const trimmed = (newValue || "").trim();
  AppState.step2Data.cleaned_rows[rowIdx][colName] = trimmed;
  if (tdElem) {
    tdElem.classList.add("cell-cleaned");
    tdElem.title = `Đã sửa thủ công: "${oldVal}" → "${trimmed}"`;
  }
  showToast(`Đã lưu chỉnh sửa ô [Dòng ${rowIdx + 1}, Cột ${colName}]`, "info");
}

function deleteRowStep2(rowIdx) {
  if (!AppState.step2Data) return;
  AppState.step2Data.cleaned_rows.splice(rowIdx, 1);
  AppState.step2Data.summary.rows_after = AppState.step2Data.cleaned_rows.length;
  renderStep2View(AppState.step2Data);
}

function addNewRowStep2() {
  if (!AppState.step2Data) return;
  const newRow = {};
  (AppState.step2Data.columns || []).forEach((c, idx) => {
    newRow[c] = idx === 0 ? "Kỳ mới" : "0";
  });
  AppState.step2Data.cleaned_rows.push(newRow);
  AppState.step2Data.summary.rows_after = AppState.step2Data.cleaned_rows.length;
  renderStep2View(AppState.step2Data);
}

function toggleStep2ReCleanBox() {
  const box = document.getElementById("step2ReCleanBox");
  box.classList.toggle("hidden");
  if (!box.classList.contains("hidden")) {
    box.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
}

function focusEditableTable() {
  const tbl = document.getElementById("cleanedTableContainer");
  tbl.scrollIntoView({ behavior: "smooth", block: "center" });
  const firstCell = tbl.querySelector('td[contenteditable="true"]');
  if (firstCell) firstCell.focus();
}

function setReCleanPrompt(text) {
  document.getElementById("customCleanInput").value = text;
}

async function runCustomAiReClean() {
  const instr = document.getElementById("customCleanInput").value.trim();
  if (!instr) {
    alert("Vui lòng nhập yêu cầu làm sạch lại cho AI.");
    return;
  }
  await runStep2Cleaning(instr);
}

async function confirmStep2AndGoStep3() {
  AppState.maxUnlockedStep = Math.max(AppState.maxUnlockedStep, 3);
  jumpToStep(3, true);
  await runStep3Analysis("");
}

// ============================================================================
// STEP 3: BI DATA ANALYSIS & FEEDBACK EVALUATION
// ============================================================================
async function runStep3Analysis(userFeedback = "") {
  const context = getContextFromForm();

  // Synthesize cleaned rows across ALL sheets if available
  const allSheetsPayload = (AppState.sheets && AppState.sheets.length > 0)
    ? AppState.sheets.map(s => ({
        name: s.name,
        row_count: s.step2Data?.cleaned_rows?.length || s.row_count || 0,
        col_count: s.step2Data?.columns?.length || s.col_count || 0,
        columns: s.step2Data?.columns || s.columns || [],
        cleaned_rows: s.step2Data?.cleaned_rows || []
      }))
    : [];

  let primaryCleanedRows = AppState.step2Data?.cleaned_rows || [];
  if (!primaryCleanedRows.length && allSheetsPayload.length > 0) {
    primaryCleanedRows = allSheetsPayload[0].cleaned_rows || [];
  }

  // Hide Step 3 confirmation gate while AI is analyzing!
  document.getElementById("step3HitlGateBox")?.classList.add("hidden");
  document.getElementById("step3AdjustBox")?.classList.add("hidden");
  document.getElementById("step3SummaryHint").textContent = "⏳ Đang tổng hợp nhận định BI chung cho tất cả các Sheet...";

  const container = document.getElementById("step3FeedbackContainer");
  container.innerHTML = `<div class="card"><p style="padding:16px; color:#1565c0; font-weight:600;">⏳ AI đang tổng hợp và phân tích dữ liệu chung cho toàn bộ các Sheet...</p></div>`;

  try {
    const res = await fetch("/api/step3/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        context,
        cleaned_rows: primaryCleanedRows,
        user_feedback: userFeedback,
        all_sheets: allSheetsPayload
      })
    });
    const data = await res.json();
    if (!res.ok) {
      container.innerHTML = `<div class="card"><p style="color:#dc2626; padding:14px;">❌ Lỗi phân tích Bước 3: ${escapeHtml(data.detail || "Không thể phân tích dữ liệu.")}</p></div>`;
      return;
    }
    AppState.step3Data = data;
    AppState.sheets_summary = data.sheets_summary || allSheetsPayload;
    renderStep3Feedback(data);
    renderAllExcelTabBars();
  } catch (e) {
    container.innerHTML = `<div class="card"><p style="color:#dc2626; padding:14px;">❌ Lỗi phân tích Bước 3: ${escapeHtml(e.message)}</p></div>`;
  }
}

function renderStep3Feedback(data) {
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
function normCol(str) {
  return String(str || "")
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
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
    const paragraphs = rawContent.split(/\n\s*\n/).filter(p => p.trim());
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

function stripAccents(str) {
  return String(str || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/đ/g, "d")
    .replace(/Đ/g, "D")
    .toLowerCase();
}

function updateDemodataKpiCards(rows, step3Data, dsFilter = "all", perFilter = "all") {
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

function extractMonthYearFromDateStr(val) {
  const s = String(val || "").trim();
  if (!s) return "";
  // Match YYYY-MM-DD or YYYY/MM/DD
  let m = s.match(/^(\d{4})[/\-\.](\d{1,2})[/\-\.]\d{1,2}$/);
  if (m) return `${m[2].padStart(2, "0")}/${m[1]}`;
  // Match DD/MM/YYYY or DD-MM-YYYY
  m = s.match(/^\d{1,2}[/\-\.](\d{1,2})[/\-\.](\d{4})$/);
  if (m) return `${m[1].padStart(2, "0")}/${m[2]}`;
  return s.slice(0, 10);
}

function parseNumSafe(val) {
  if (val === null || val === undefined) return 0;
  let s = String(val).trim();
  if (!s) return 0;
  s = s.replace(/[₫đ$€¥%]/gi, "").trim();
  if (/^\d{1,3}(\.\d{3})+(,\d+)?$/.test(s)) {
    s = s.replace(/\./g, "").replace(",", ".");
  } else if (/^\d{1,3}(,\d{3})+(\.\d+)?$/.test(s)) {
    s = s.replace(/,/g, "");
  } else if (s.includes(",") && !s.includes(".")) {
    s = s.replace(",", ".");
  }
  const n = parseFloat(s);
  return isNaN(n) ? 0 : n;
}

function formatVietnameseBigNumber(val) {
  if (val === null || val === undefined || isNaN(val)) return "0";
  const absV = Math.abs(val);
  const sign = val < 0 ? "-" : "";
  if (absV >= 1_000_000_000) {
    return `${sign}${(absV / 1_000_000_000).toFixed(2)} Tỷ`;
  }
  if (absV >= 1_000_000) {
    return `${sign}${(absV / 1_000_000).toFixed(2)} Triệu`;
  }
  if (absV >= 10_000) {
    return `${sign}${Math.round(absV).toLocaleString("en-US")}`;
  }
  return `${sign}${absV % 1 === 0 ? absV.toLocaleString("en-US") : absV.toFixed(2)}`;
}

function initDashboardSlicers(step3Data) {
  const rows = AppState.step2Data?.cleaned_rows || [];
  const allCols = AppState.step2Data?.columns || [];
  const meta = step3Data.column_metadata || {};

  const numCols = (meta.numeric_cols && meta.numeric_cols.length > 0)
    ? meta.numeric_cols
    : allCols.filter(c => rows.some(r => !isNaN(Number(r[c])) && String(r[c]).trim() !== ""));

  const dateCols = meta.date_cols || [];
  const primaryDateCol = dateCols[0] || "";

  // Pick categorical columns suitable for Slicers (2 to 50 unique values)
  const catCols = (meta.slicer_cols && meta.slicer_cols.length > 0)
    ? meta.slicer_cols
    : allCols.filter(c => !numCols.includes(c) && !dateCols.includes(c));

  const slicerCol1 = catCols[0] || "";
  const slicerCol2 = catCols[1] || "";

  AppState.dashConfig = {
    numCols,
    primaryDateCol,
    catCols,
    slicerCol1,
    slicerCol2,
    labelCol: meta.label_col || allCols[0] || ""
  };

  // Build unique Month/Year options if primaryDateCol exists
  let periodOptions = [];
  if (primaryDateCol) {
    const pSet = new Set();
    rows.forEach(r => {
      const p = extractMonthYearFromDateStr(r[primaryDateCol]);
      if (p) pSet.add(p);
    });
    periodOptions = Array.from(pSet).sort((a, b) => {
      const [ma, ya] = a.split("/");
      const [mb, yb] = b.split("/");
      return (Number(ya) * 100 + Number(ma)) - (Number(yb) * 100 + Number(mb));
    });
  }

  const getUniqueVals = (col) => {
    if (!col) return [];
    const s = new Set();
    rows.forEach(r => {
      const v = String(r[col] ?? "").trim();
      if (v) s.add(v);
    });
    return Array.from(s).slice(0, 40);
  };

  const s1Options = getUniqueVals(slicerCol1);
  const s2Options = getUniqueVals(slicerCol2);
  const groupColChoices = catCols.length > 0 ? catCols : [AppState.dashConfig.labelCol];

  const slicerBar = document.getElementById("execSlicerBar");
  slicerBar.innerHTML = `
    <div class="slicer-controls-left">
      <div class="slicer-group">
        <span class="slicer-label">📈 Chỉ số Phân tích chính (Metric)</span>
        <select class="slicer-select" id="slicerMetric" onchange="updateDashboardFromSlicers()">
          ${numCols.map((c, idx) => `<option value="${escapeHtml(c)}" ${idx === 0 ? "selected" : ""}>${escapeHtml(c)}</option>`).join("")}
        </select>
      </div>

      ${groupColChoices.length > 0 && groupColChoices[0] ? `
        <div class="slicer-group">
          <span class="slicer-label">📂 Nhóm Biểu đồ theo (Dimension)</span>
          <select class="slicer-select" id="slicerGroupBy" onchange="updateDashboardFromSlicers()">
            ${groupColChoices.map((c, idx) => `<option value="${escapeHtml(c)}" ${idx === 0 ? "selected" : ""}>${escapeHtml(c)}</option>`).join("")}
          </select>
        </div>
      ` : ""}

      ${primaryDateCol && periodOptions.length > 1 ? `
        <div class="slicer-group">
          <span class="slicer-label">📅 Kỳ thời gian (${escapeHtml(primaryDateCol)})</span>
          <select class="slicer-select" id="slicerPeriod" onchange="updateDashboardFromSlicers()">
            <option value="ALL">Tất cả các kỳ (${periodOptions.length} kỳ)</option>
            ${periodOptions.map(p => `<option value="${escapeHtml(p)}">Tháng ${escapeHtml(p)}</option>`).join("")}
          </select>
        </div>
      ` : ""}

      ${slicerCol1 && s1Options.length > 1 ? `
        <div class="slicer-group">
          <span class="slicer-label">🏷️ Lọc ${escapeHtml(slicerCol1)}</span>
          <select class="slicer-select" id="slicerCat1" onchange="updateDashboardFromSlicers()">
            <option value="ALL">Tất cả (${s1Options.length})</option>
            ${s1Options.map(v => `<option value="${escapeHtml(v)}">${escapeHtml(v.slice(0, 32))}</option>`).join("")}
          </select>
        </div>
      ` : ""}

      ${slicerCol2 && s2Options.length > 1 ? `
        <div class="slicer-group">
          <span class="slicer-label">🏢 Lọc ${escapeHtml(slicerCol2)}</span>
          <select class="slicer-select" id="slicerCat2" onchange="updateDashboardFromSlicers()">
            <option value="ALL">Tất cả (${s2Options.length})</option>
            ${s2Options.map(v => `<option value="${escapeHtml(v)}">${escapeHtml(v.slice(0, 32))}</option>`).join("")}
          </select>
        </div>
      ` : ""}
    </div>

    <div class="slicer-status-right">
      <span id="slicerCountBadge">Đang hiển thị: ${rows.length} / ${rows.length} bản ghi</span>
      <button class="btn-xs" onclick="resetDashboardSlicers()">↺ Xóa bộ lọc</button>
    </div>
  `;
}

function resetDashboardSlicers() {
  ["slicerPeriod", "slicerCat1", "slicerCat2"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = "ALL";
  });
  updateDashboardFromSlicers();
}

function updateDashboardFromSlicers() {
  const allRows = AppState.step2Data?.cleaned_rows || [];
  if (!allRows.length) return;

  const cfg = AppState.dashConfig || {};
  const primaryMetric = document.getElementById("slicerMetric")?.value || cfg.numCols?.[0] || "";
  const secondaryMetric = (cfg.numCols || []).find(c => c !== primaryMetric) || primaryMetric;
  const groupCol = document.getElementById("slicerGroupBy")?.value || cfg.slicerCol1 || cfg.labelCol || "";
  const periodFilter = document.getElementById("slicerPeriod")?.value || "ALL";
  const cat1Filter = document.getElementById("slicerCat1")?.value || "ALL";
  const cat2Filter = document.getElementById("slicerCat2")?.value || "ALL";

  // 1. Filter rows according to active Slicers
  const filteredRows = allRows.filter(r => {
    if (periodFilter !== "ALL" && cfg.primaryDateCol) {
      if (extractMonthYearFromDateStr(r[cfg.primaryDateCol]) !== periodFilter) return false;
    }
    if (cat1Filter !== "ALL" && cfg.slicerCol1) {
      if (String(r[cfg.slicerCol1] ?? "").trim() !== cat1Filter) return false;
    }
    if (cat2Filter !== "ALL" && cfg.slicerCol2) {
      if (String(r[cfg.slicerCol2] ?? "").trim() !== cat2Filter) return false;
    }
    return true;
  });

  const countBadge = document.getElementById("slicerCountBadge");
  if (countBadge) {
    countBadge.textContent = `Đang hiển thị: ${filteredRows.length} / ${allRows.length} bản ghi`;
  }

  const rowsToUse = filteredRows.length > 0 ? filteredRows : allRows;

  // 2. Compute Real Business KPIs on rowsToUse
  const primaryVals = rowsToUse.map(r => parseNumSafe(r[primaryMetric]));
  const secondaryVals = rowsToUse.map(r => parseNumSafe(r[secondaryMetric]));
  const totalPrimary = primaryVals.reduce((a, b) => a + b, 0);
  const avgPrimary = primaryVals.length ? totalPrimary / primaryVals.length : 0;
  const maxPrimary = primaryVals.length ? Math.max(...primaryVals) : 0;
  const totalSecondary = secondaryVals.reduce((a, b) => a + b, 0);

  const highValueRows = primaryVals.filter(v => v >= avgPrimary);
  const highValueSum = highValueRows.reduce((a, b) => a + b, 0);
  const paretoSharePct = totalPrimary > 0 ? (highValueSum / totalPrimary) * 100 : 0;

  // Sparkline sampled to max 20 points so it always looks smooth
  const sparkSample = sampleArray(primaryVals, 20);
  const sparkSample2 = sampleArray(secondaryVals, 20);

  const kpiCards = [
    {
      title: `Tổng ${primaryMetric}`,
      value: formatVietnameseBigNumber(totalPrimary),
      sub: `Chính xác: ${Math.round(totalPrimary).toLocaleString("en-US")} • ${rowsToUse.length} bản ghi`,
      color: "#1565c0",
      borderColor: "#1565c0",
      bg_tint: "rgba(21, 101, 192, 0.14)",
      sparkline: sparkSample
    },
    {
      title: secondaryMetric !== primaryMetric ? `Tổng ${secondaryMetric}` : `Quy mô Đỉnh (${primaryMetric})`,
      value: secondaryMetric !== primaryMetric ? formatVietnameseBigNumber(totalSecondary) : formatVietnameseBigNumber(maxPrimary),
      sub: secondaryMetric !== primaryMetric
        ? `Trung bình: ${formatVietnameseBigNumber(totalSecondary / Math.max(rowsToUse.length, 1))} / bản ghi`
        : `Gấp ${(maxPrimary / Math.max(avgPrimary, 1)).toFixed(1)} lần mức trung bình`,
      color: "#e05a47",
      borderColor: "#e05a47",
      bg_tint: "rgba(224, 90, 71, 0.14)",
      sparkline: sparkSample2
    },
    {
      title: `Trung bình ${primaryMetric} / Đơn`,
      value: formatVietnameseBigNumber(avgPrimary),
      sub: `Cao nhất: ${formatVietnameseBigNumber(maxPrimary)}`,
      color: "#00897b",
      borderColor: "#00897b",
      bg_tint: "rgba(0, 137, 123, 0.12)",
      sparkline: null
    },
    {
      title: `Tỷ trọng Nhóm Trọng điểm`,
      value: `${paretoSharePct.toFixed(1)} %`,
      sub: `${highValueRows.length}/${rowsToUse.length} hồ sơ (>= mức TB) chiếm ${paretoSharePct.toFixed(1)}% quy mô`,
      color: "#1e3a5f",
      borderColor: "#f59e0b",
      bg_tint: "rgba(245, 158, 11, 0.12)",
      sparkline: null
    }
  ];

  const kpiRow = document.getElementById("execKpiRow");
  kpiRow.innerHTML = kpiCards.map((kpi) => {
    const sparkSvg = kpi.sparkline ? buildAreaSparklineSvg(kpi.sparkline, kpi.bg_tint) : "";
    return `
      <div class="exec-kpi-card" style="border-top-color:${kpi.borderColor};">
        <div>
          <div class="exec-kpi-title">${escapeHtml(kpi.title)}</div>
          <div class="exec-kpi-value" style="color:${kpi.color};">${escapeHtml(kpi.value)}</div>
        </div>
        <div class="exec-kpi-sub">${escapeHtml(kpi.sub)}</div>
        ${sparkSvg}
      </div>
    `;
  }).join("");

  // 3. Aggregate by `groupCol` (Category Distribution — Top 8 Groups!)
  const catMap = new Map();
  rowsToUse.forEach(r => {
    const rawCat = String(r[groupCol] ?? "Khác").trim() || "Khác";
    // Clean trailing quantity if grouping by Equipment/Product text
    const cleanCat = rawCat.split(";")[0].replace(/\s*x\s*\d+.*$/i, "").trim().slice(0, 26) || "Khác";
    const cur = catMap.get(cleanCat) || { sum1: 0, sum2: 0, count: 0 };
    cur.sum1 += parseNumSafe(r[primaryMetric]);
    cur.sum2 += parseNumSafe(r[secondaryMetric]);
    cur.count += 1;
    catMap.set(cleanCat, cur);
  });

  const sortedCats = Array.from(catMap.entries()).sort((a, b) => b[1].sum1 - a[1].sum1);
  const top8Cats = sortedCats.slice(0, 8);
  const catLabels = top8Cats.map(e => e[0]);
  const catSum1 = top8Cats.map(e => Math.round(e[1].sum1 * 100) / 100);
  const catCountOrAvg = top8Cats.map(e => Math.round((e[1].sum1 / Math.max(e[1].count, 1)) * 100) / 100);

  // 4. Render 4 Clean Gauges based on aggregated stats
  const aboveAvgRate = Math.round((highValueRows.length / Math.max(rowsToUse.length, 1)) * 100);
  const top1CatShare = totalPrimary > 0 && top8Cats.length > 0 ? Math.round((top8Cats[0][1].sum1 / totalPrimary) * 100) : 0;
  const activeGroupsCount = sortedCats.length;

  const gauges = [
    {
      title: "Tỷ trọng Nhóm Trọng điểm",
      subtitle: `[Pareto >= Trung bình]`,
      value: Math.round(paretoSharePct),
      display_value: `${paretoSharePct.toFixed(1)}%`,
      min: 0,
      max: 100,
      color: "#1565c0"
    },
    {
      title: "Tỷ lệ Đơn Vượt Chuẩn TB",
      subtitle: `[${highValueRows.length} / ${rowsToUse.length} bản ghi]`,
      value: aboveAvgRate,
      display_value: `${aboveAvgRate}%`,
      min: 0,
      max: 100,
      color: "#f2a900"
    },
    {
      title: "Tỷ trọng Nhóm #1 Dẫn đầu",
      subtitle: `[${top8Cats[0]?.[0] || "Top 1"}]`,
      value: top1CatShare,
      display_value: `${top1CatShare}%`,
      min: 0,
      max: 100,
      color: "#ef5350"
    },
    {
      title: "Số Nhóm Phân Loại Hoạt Động",
      subtitle: `[Theo ${groupCol}]`,
      value: Math.min(activeGroupsCount, 30),
      display_value: `${activeGroupsCount} Nhóm`,
      min: 0,
      max: Math.max(30, activeGroupsCount),
      color: "#00a65a"
    }
  ];

  document.getElementById("execGaugeRow").innerHTML = gauges.map((g) => `
    <div class="exec-gauge-card">
      <div class="exec-gauge-header">
        <div class="exec-gauge-title">${escapeHtml(g.title)}</div>
        <div class="exec-gauge-subtitle">${escapeHtml(g.subtitle)}</div>
      </div>
      <div class="exec-gauge-svg-wrap">
        ${buildExecutiveGaugeSvg(g)}
      </div>
    </div>
  `).join("");

  // Render Chart 1 (Top-Right): Aggregated Category Bar Chart (Max 8 bars!)
  document.getElementById("agingChartTitle").textContent = `Phân bổ ${primaryMetric} theo ${groupCol}`;
  document.getElementById("agingChartSubtitle").textContent = `Top ${top8Cats.length} nhóm dẫn đầu (Đã gộp nhóm)`;
  renderAgingGroupedBarChart({
    x_axis_label: groupCol,
    labels: catLabels,
    series: [
      { name: `Tổng ${primaryMetric}`, color: "#24588e", data: catSum1 },
      { name: `Trung bình / Đơn (${primaryMetric})`, color: "#f44336", data: catCountOrAvg }
    ]
  });

  // 5. Render Chart 2 (Bottom-Left): Time-Series Trend by Month/Year (Max 12 periods!)
  let trendLabels = [];
  let trendSumSeries = [];
  let trendAvgSeries = [];

  if (cfg.primaryDateCol) {
    const timeMap = new Map();
    rowsToUse.forEach(r => {
      const ym = extractMonthYearFromDateStr(r[cfg.primaryDateCol]) || "Khác";
      const cur = timeMap.get(ym) || { sum: 0, count: 0 };
      cur.sum += parseNumSafe(r[primaryMetric]);
      cur.count += 1;
      timeMap.set(ym, cur);
    });
    const sortedTime = Array.from(timeMap.entries()).sort((a, b) => {
      const [ma, ya] = a[0].split("/");
      const [mb, yb] = b[0].split("/");
      return (Number(ya || 0) * 100 + Number(ma || 0)) - (Number(yb || 0) * 100 + Number(mb || 0));
    }).slice(-12);

    trendLabels = sortedTime.map(e => e[0]);
    trendSumSeries = sortedTime.map(e => Math.round(e[1].sum * 100) / 100);
    trendAvgSeries = sortedTime.map(e => Math.round((e[1].sum / Math.max(e[1].count, 1)) * 100) / 100);
    document.getElementById("wcChartTitle").textContent = `Xu hướng ${primaryMetric} theo Kỳ Thời Gian (${cfg.primaryDateCol})`;
    document.getElementById("wcChartSubtitle").textContent = `${trendLabels.length} kỳ thời gian`;
  } else {
    trendLabels = catLabels;
    trendSumSeries = catSum1;
    trendAvgSeries = catCountOrAvg;
    document.getElementById("wcChartTitle").textContent = `So sánh Tổng & Trung bình ${primaryMetric} theo ${groupCol}`;
    document.getElementById("wcChartSubtitle").textContent = `Top ${trendLabels.length} nhóm`;
  }

  renderWorkingCapitalLineChart({
    y_axis_label: primaryMetric,
    labels: trendLabels,
    series: [
      { name: `Tổng ${primaryMetric}`, color: "#24588e", data: trendSumSeries },
      { name: `Trung bình / Bản ghi`, color: "#f2b705", data: trendAvgSeries }
    ]
  });

  // 6. Render Chart 3 (Bottom-Right): Top 10 Ranking by Entity / Customer / Project or Secondary Category (Max 10 bars!)
  const rankCol = (cfg.labelCol && cfg.labelCol !== groupCol) ? cfg.labelCol : groupCol;
  const rankMap = new Map();
  rowsToUse.forEach(r => {
    const k = String(r[rankCol] ?? "Khác").trim().slice(0, 24) || "Khác";
    const cur = rankMap.get(k) || { sum1: 0, count: 0 };
    cur.sum1 += parseNumSafe(r[primaryMetric]);
    cur.count += 1;
    rankMap.set(k, cur);
  });

  const top10Rank = Array.from(rankMap.entries())
    .sort((a, b) => b[1].sum1 - a[1].sum1)
    .slice(0, 10);

  const rankLabels = top10Rank.map(e => e[0]);
  const rankSum1 = top10Rank.map(e => Math.round(e[1].sum1 * 100) / 100);
  const rankCount = top10Rank.map(e => e[1].count);

  document.getElementById("pnlChartTitle").textContent = `Top ${top10Rank.length} ${rankCol} có ${primaryMetric} lớn nhất & Số lượng đơn`;
  document.getElementById("pnlChartSubtitle").textContent = `Xếp hạng Top ${top10Rank.length} (Không vẽ chồng chéo)`;

  renderPnLComboChart({
    left_axis_label: `Tổng ${primaryMetric}`,
    right_axis_label: "Số lượng bản ghi (Count)",
    labels: rankLabels,
    stacked_series: [
      { name: `Tổng ${primaryMetric}`, color: "#24588e", data: rankSum1 }
    ],
    profit_loss_series: {
      name: "Số bản ghi / Đơn hàng",
      positive_color: "#f2a900",
      negative_color: "#f44336",
      data: rankCount
    }
  });
}

function sampleArray(arr, maxPoints = 20) {
  if (!arr || arr.length <= maxPoints) return arr || [];
  const step = arr.length / maxPoints;
  const res = [];
  for (let i = 0; i < maxPoints; i++) {
    res.push(arr[Math.floor(i * step)]);
  }
  return res;
}

function buildAreaSparklineSvg(values, fillColor) {
  if (!values || values.length < 2) return "";
  const w = 220;
  const h = 44;
  const minV = Math.min(...values) * 0.92;
  const maxV = Math.max(...values) * 1.02 || 1;
  const stepX = w / (values.length - 1);

  const pts = values.map((v, idx) => {
    const x = (idx * stepX).toFixed(1);
    const ratio = (v - minV) / Math.max(maxV - minV, 1);
    const y = (h - 4 - ratio * (h - 10)).toFixed(1);
    return `${x},${y}`;
  });

  const polygonPoints = `0,${h} ${pts.join(" ")} ${w},${h}`;
  return `
    <svg class="exec-kpi-spark-svg" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">
      <polygon points="${polygonPoints}" fill="${fillColor}" />
    </svg>
  `;
}

function buildExecutiveGaugeSvg(g) {
  const minVal = g.min ?? 0;
  const maxVal = g.max ?? 31;
  const rawVal = Math.max(minVal, Math.min(maxVal, Number(g.value) || 0));
  const ratio = (rawVal - minVal) / Math.max(maxVal - minVal, 1);

  const cx = 85;
  const cy = 78;
  const r = 54;
  const startAngle = 145;
  const totalSweep = 250;
  const endAngle = startAngle + totalSweep;
  const valAngle = startAngle + ratio * totalSweep;

  const trackPath = describeArc(cx, cy, r, startAngle, endAngle);
  const valuePath = ratio > 0.005 ? describeArc(cx, cy, r, startAngle, valAngle) : "";

  const needleRad = (valAngle * Math.PI) / 180;
  const tipX = cx + (r - 12) * Math.cos(needleRad);
  const tipY = cy + (r - 12) * Math.sin(needleRad);
  const baseLeftRad = needleRad - Math.PI / 2;
  const baseRightRad = needleRad + Math.PI / 2;
  const bRadius = 3.2;
  const bx1 = cx + bRadius * Math.cos(baseLeftRad);
  const by1 = cy + bRadius * Math.sin(baseLeftRad);
  const bx2 = cx + bRadius * Math.cos(baseRightRad);
  const by2 = cy + bRadius * Math.sin(baseRightRad);

  return `
    <svg width="170" height="148" viewBox="0 0 170 148">
      <path d="${trackPath}" fill="none" stroke="#e0e0e0" stroke-width="18" stroke-linecap="butt" />
      ${valuePath ? `<path d="${valuePath}" fill="none" stroke="${g.color}" stroke-width="18" stroke-linecap="butt" />` : ""}
      <polygon points="${tipX.toFixed(1)},${tipY.toFixed(1)} ${bx1.toFixed(1)},${by1.toFixed(1)} ${bx2.toFixed(1)},${by2.toFixed(1)}" fill="#616161" />
      <circle cx="${cx}" cy="${cy}" r="3.5" fill="#616161" />
      <text x="${cx}" y="119" text-anchor="middle" font-size="11.5" font-weight="700" fill="#1e293b">${escapeHtml(g.display_value)}</text>
      <text x="45" y="138" text-anchor="middle" font-size="10.5" font-weight="600" fill="#334155">${minVal}</text>
      <text x="125" y="138" text-anchor="middle" font-size="10.5" font-weight="600" fill="#334155">${maxVal}</text>
    </svg>
  `;
}

function polarToCartesian(cx, cy, r, angleInDegrees) {
  const angleInRadians = (angleInDegrees * Math.PI) / 180.0;
  return {
    x: cx + r * Math.cos(angleInRadians),
    y: cy + r * Math.sin(angleInRadians)
  };
}

function describeArc(cx, cy, r, startAngle, endAngle) {
  const start = polarToCartesian(cx, cy, r, startAngle);
  const end = polarToCartesian(cx, cy, r, endAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
  return ["M", start.x.toFixed(2), start.y.toFixed(2), "A", r, r, 0, largeArcFlag, 1, end.x.toFixed(2), end.y.toFixed(2)].join(" ");
}

function formatCompactMetric(val, withDollar = false) {
  if (val === null || val === undefined || isNaN(val)) return "";
  const absV = Math.abs(val);
  const prefix = withDollar ? "$" : "";
  let formatted = "";
  if (absV >= 1_000_000_000) {
    formatted = `${prefix}${(absV / 1_000_000_000).toFixed(2)}B`;
  } else if (absV >= 1_000_000) {
    formatted = `${prefix}${(absV / 1_000_000).toFixed(1)}M`;
  } else if (absV >= 1_000) {
    const kVal = absV / 1_000;
    formatted = `${prefix}${kVal % 1 === 0 ? kVal.toFixed(0) : kVal.toFixed(1)}K`;
  } else {
    formatted = `${prefix}${absV % 1 === 0 ? absV.toFixed(0) : absV.toFixed(1)}`;
  }
  return val < 0 ? `(${formatted})` : formatted;
}

function renderAgingGroupedBarChart(spec) {
  const ctx = document.getElementById("chartAging").getContext("2d");
  if (AppState.charts.aging) AppState.charts.aging.destroy();
  const showLabels = (spec.labels || []).length <= 10;

  AppState.charts.aging = new Chart(ctx, {
    type: "bar",
    data: {
      labels: spec.labels,
      datasets: spec.series.map((s) => ({
        label: s.name,
        data: s.data,
        backgroundColor: s.color,
        borderRadius: 4,
        barPercentage: 0.72,
        categoryPercentage: 0.68,
        datalabels: {
          display: showLabels,
          anchor: "end",
          align: "top",
          offset: 2,
          color: "#334155",
          font: { size: 9.5, weight: "600" },
          formatter: (v) => (v !== 0 ? formatCompactMetric(v) : "")
        }
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      layout: { padding: { top: 22 } },
      plugins: {
        legend: {
          position: "bottom",
          labels: { boxWidth: 12, font: { size: 11 } }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${Number(ctx.raw).toLocaleString("en-US")}`
          }
        }
      },
      scales: {
        x: {
          title: { display: true, text: spec.x_axis_label || "Danh mục", font: { size: 10.5, weight: "600" } },
          grid: { display: false },
          ticks: { font: { size: 10 }, maxRotation: 25 }
        },
        y: {
          beginAtZero: true,
          grid: { color: "#edf2f7" },
          ticks: {
            font: { size: 10 },
            callback: (v) => formatCompactMetric(v)
          }
        }
      }
    }
  });
}

function renderWorkingCapitalLineChart(spec) {
  const ctx = document.getElementById("chartWorkingCapital").getContext("2d");
  if (AppState.charts.workingCapital) AppState.charts.workingCapital.destroy();
  const showLabels = (spec.labels || []).length <= 12;

  AppState.charts.workingCapital = new Chart(ctx, {
    type: "line",
    data: {
      labels: spec.labels,
      datasets: spec.series.map((s, idx) => ({
        label: s.name,
        data: s.data,
        borderColor: s.color,
        backgroundColor: idx === 0 ? "rgba(36, 88, 142, 0.10)" : "transparent",
        fill: idx === 0,
        pointBackgroundColor: "#ffffff",
        pointBorderColor: s.color,
        pointBorderWidth: 2,
        pointRadius: 4,
        borderWidth: 2.2,
        tension: 0.25,
        datalabels: {
          display: showLabels && idx === 0,
          align: "top",
          offset: 5,
          color: "#1e293b",
          font: { size: 9.5, weight: "600" },
          formatter: (v) => formatCompactMetric(v)
        }
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      layout: { padding: { top: 24, bottom: 8, right: 16, left: 6 } },
      plugins: {
        legend: {
          position: "bottom",
          labels: { usePointStyle: true, boxWidth: 10, font: { size: 11 } }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${Number(ctx.raw).toLocaleString("en-US")}`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { size: 10 }, maxRotation: 25 }
        },
        y: {
          beginAtZero: true,
          title: { display: true, text: spec.y_axis_label || "Giá trị", font: { size: 10.5, weight: "600" } },
          grid: { color: "#edf2f7" },
          ticks: {
            font: { size: 10 },
            callback: (v) => formatCompactMetric(v)
          }
        }
      }
    }
  });
}

function renderPnLComboChart(spec) {
  const ctx = document.getElementById("chartPnL").getContext("2d");
  if (AppState.charts.pnl) AppState.charts.pnl.destroy();
  const showLabels = (spec.labels || []).length <= 10;

  const barDatasets = (spec.stacked_series || []).map((s) => ({
    type: "bar",
    label: s.name,
    data: s.data,
    backgroundColor: s.color,
    borderRadius: 4,
    yAxisID: "yLeft",
    barPercentage: 0.65,
    categoryPercentage: 0.7,
    datalabels: {
      display: showLabels,
      anchor: "end",
      align: "top",
      offset: 2,
      color: "#1e3a5f",
      font: { size: 9.5, weight: "600" },
      formatter: (v) => (v !== 0 ? formatCompactMetric(v) : "")
    }
  }));

  const plData = spec.profit_loss_series.data || [];

  const lineOrBarDataset = {
    type: "line",
    label: spec.profit_loss_series.name,
    data: plData,
    borderColor: "#e67e22",
    backgroundColor: "#ffffff",
    pointBackgroundColor: "#e67e22",
    pointRadius: 4,
    borderWidth: 2.2,
    tension: 0.2,
    yAxisID: "yRight",
    datalabels: {
      display: false
    }
  };

  AppState.charts.pnl = new Chart(ctx, {
    type: "bar",
    data: {
      labels: spec.labels,
      datasets: [...barDatasets, lineOrBarDataset]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      layout: { padding: { top: 22 } },
      plugins: {
        legend: {
          position: "bottom",
          labels: { boxWidth: 12, font: { size: 11 } }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${Number(ctx.raw).toLocaleString("en-US")}`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { size: 10 }, maxRotation: 25 }
        },
        yLeft: {
          type: "linear",
          position: "left",
          beginAtZero: true,
          title: { display: true, text: spec.left_axis_label || "Metrics", font: { size: 10.5, weight: "600" } },
          grid: { color: "#edf2f7" },
          ticks: {
            font: { size: 10 },
            callback: (v) => formatCompactMetric(v)
          }
        },
        yRight: {
          type: "linear",
          position: "right",
          stacked: false,
          title: { display: true, text: spec.right_axis_label || "Net", font: { size: 10.5 } },
          grid: { drawOnChartArea: false },
          ticks: {
            font: { size: 10 },
            callback: (v) => formatCompactMetric(v)
          }
        }
      }
    }
  });
}

function renderExecutiveReportHtml(step3Data) {
  const ctx = getContextFromForm();
  const dash = step3Data.dashboard || {};
  const sections = step3Data.feedback_sections || [];
  const actionMatrix = step3Data.action_plan_matrix || [];
  const cleanedRows = AppState.step2Data?.cleaned_rows || [];
  const cols = AppState.step2Data?.columns || [];
  const sheetsSummary = step3Data.sheets_summary || AppState.sheets_summary || [];

  const secSummary = sections.find(s => s.badge === "[Tóm tắt]") || sections[0] || {};
  const secKpi = sections.find(s => s.badge === "[Chỉ số chính]") || sections[1] || {};
  const secThematic = sections.find(s => s.badge === "[Phân tích chuyên đề]") || sections[2] || {};
  const secProposal = sections.find(s => s.badge === "[Kết luận và đề xuất]") || sections[3] || {};

  const html = `
    <div class="report-paper">
      <div class="report-header-banner">
        <div>
          <div style="font-size:0.78rem; font-weight:700; color:#1565c0; letter-spacing:0.6px;">EXECUTIVE BUSINESS INTELLIGENCE REPORT</div>
          <h2 style="font-size:1.5rem; color:#0f172a; margin-top:4px;">${escapeHtml(ctx.company_name)} — Báo cáo Phân tích & Đề xuất Điều hành</h2>
          <p style="font-size:0.86rem; color:#475569;">Ngành nghề: ${escapeHtml(ctx.industry)} | Mục tiêu: ${escapeHtml(ctx.objective)} | Đối tượng: ${escapeHtml(ctx.target_audience)}</p>
        </div>
        <div style="text-align:right; font-size:0.8rem; color:#64748b;">
          <div>Ngày xuất bản: ${new Date().toLocaleDateString("vi-VN")}</div>
          <div>Trạng thái: <strong>100% Đã làm sạch & Xác nhận (HITL Verified)</strong></div>
        </div>
      </div>

      <!-- MỤC 1: [Tóm tắt] -->
      <div class="report-section-block">
        <span class="report-sec-badge">[Tóm tắt]</span>
        <h3>I. TỔNG QUAN HOẠT ĐỘNG & BỐI CẢNH KINH DOANH</h3>
        <div class="report-text-body">${formatMarkdownBold(escapeHtml(secSummary.content || step3Data.executive_summary_line || ""))}</div>
      </div>

      <!-- MỤC 2: [Chỉ số chính] -->
      <div class="report-section-block">
        <span class="report-sec-badge">[Chỉ số chính]</span>
        <h3>II. HỆ THỐNG CHỈ SỐ HIỆU SUẤT CỐT LÕI (KEY PERFORMANCE INDICATORS)</h3>
        <div class="report-kpi-grid">
          ${(dash.kpi_cards || []).map(k => `
            <div class="report-kpi-card">
              <div class="rk-title">${escapeHtml(k.title)}</div>
              <div class="rk-val" style="color:${k.color};">${escapeHtml(k.value)}</div>
            </div>
          `).join("")}
        </div>
        <div class="report-text-body">${formatMarkdownBold(escapeHtml(secKpi.content || ""))}</div>
      </div>

      <!-- MỤC 3: [Phân tích chuyên đề] -->
      <div class="report-section-block">
        <span class="report-sec-badge">[Phân tích chuyên đề]</span>
        <h3>III. PHÂN TÍCH CHUYÊN ĐỀ SÂU TỪ DỮ LIỆU THỰC TẾ</h3>
        <div class="report-text-body">${formatMarkdownBold(escapeHtml(secThematic.content || ""))}</div>
      </div>

      <!-- MỤC 4: [Kết luận và đề xuất] -->
      <div class="report-section-block">
        <span class="report-sec-badge">[Kết luận và đề xuất]</span>
        <h3>IV. KẾT LUẬN CHIẾN LƯỢC & KẾ HOẠCH HÀNH ĐỘNG ĐO LƯỜNG ĐƯỢC (SMART ACTION PLAN)</h3>
        <div class="report-text-body" style="margin-bottom:14px;">${formatMarkdownBold(escapeHtml(secProposal.content || ""))}</div>
        ${actionMatrix.length > 0 ? `
          <div style="border:1px solid #cbd5e1; border-radius:6px; overflow:hidden; margin-top:12px;">
            <table class="data-table" style="white-space:normal;">
              <thead>
                <tr>
                  <th style="width:15%; background:#f1f5f9; color:#0f172a;">Hạng mục</th>
                  <th style="width:23%; background:#f1f5f9; color:#0f172a;">Vấn đề Thực tế</th>
                  <th style="width:26%; background:#f1f5f9; color:#0f172a;">Giải pháp Triển khai</th>
                  <th style="width:20%; background:#f1f5f9; color:#0f172a;">Chỉ số Đo lường (KPI)</th>
                  <th style="width:16%; background:#f1f5f9; color:#0f172a;">Tác động Định lượng</th>
                </tr>
              </thead>
              <tbody>
                ${actionMatrix.map(row => `
                  <tr>
                    <td style="vertical-align:top; font-weight:700; color:#1e3a5f;">
                      <span style="display:inline-block; background:#dbeafe; color:#1e40af; padding:1px 6px; border-radius:4px; font-size:0.7rem; margin-bottom:4px;">${escapeHtml(row.code)}</span><br/>
                      ${escapeHtml(row.area)}
                    </td>
                    <td style="vertical-align:top;">${formatMarkdownBold(escapeHtml(row.problem))}</td>
                    <td style="vertical-align:top; font-weight:500;">${formatMarkdownBold(escapeHtml(row.solution))}</td>
                    <td style="vertical-align:top; white-space:pre-line; color:#166534; font-weight:600; background:#f0fdf4;">${escapeHtml(row.kpi_metric)}</td>
                    <td style="vertical-align:top; color:#9a3412; font-weight:700; background:#fff7ed;">${escapeHtml(row.quantified_impact)}</td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
        ` : ""}
      </div>

      </div>
    </div>
  `;
  document.getElementById("executiveReportContainer").innerHTML = html;
}

function buildSimplePreviewTable(columns, rows) {
  if (!columns || !columns.length) return "";
  return `
    <table class="data-table">
      <thead>
        <tr>
          ${columns.map(c => `<th>${escapeHtml(c)}</th>`).join("")}
        </tr>
      </thead>
      <tbody>
        ${(rows || []).map(r => `
          <tr>
            ${columns.map(c => `<td>${escapeHtml(String(r[c] ?? ""))}</td>`).join("")}
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function downloadCleanedCSV() {
  const rows = AppState.step2Data?.cleaned_rows;
  const cols = AppState.step2Data?.columns;
  if (!rows || !cols) {
    alert("Chưa có dữ liệu làm sạch để tải xuống.");
    return;
  }
  const csvLines = [
    cols.join(","),
    ...rows.map(r => cols.map(c => `"${String(r[c] ?? "").replace(/"/g, '""')}"`).join(","))
  ];
  const blob = new Blob([csvLines.join("\n")], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "cleaned_bi_data.csv";
  a.click();
  URL.revokeObjectURL(url);
}

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatMarkdownBold(escapedStr) {
  return escapedStr
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/`([^`]+)`/g, "<code style='background:#e2e8f0;padding:1px 5px;border-radius:4px;font-size:0.8rem;'>$1</code>");
}

// ============================================================================
// FLOATING SMART AI BI CHATBOX CONTROLLER
// ============================================================================

function toggleAIChatbot(forceState) {
  const win = document.getElementById("aiChatWindow");
  if (!win) return;
  if (typeof forceState === "boolean") {
    win.classList.toggle("hidden", !forceState);
  } else {
    win.classList.toggle("hidden");
  }
  if (!win.classList.contains("hidden")) {
    const inp = document.getElementById("aiChatInput");
    setTimeout(() => inp?.focus(), 80);
  }
}

function clearAIChat() {
  const box = document.getElementById("aiChatMessages");
  if (!box) return;
  box.innerHTML = `
    <div class="ai-msg-row bot">
      <div class="ai-msg-bubble">
        👋 Đã làm mới hội thoại! Bạn muốn hỏi gì về dữ liệu các Sheet, thống kê hay giải pháp KPI?
      </div>
    </div>
  `;
}

function askQuickQuestion(questionText) {
  const inp = document.getElementById("aiChatInput");
  if (inp) inp.value = questionText;
  sendAIChatMessage();
}

function appendChatMessage(role, rawText) {
  const box = document.getElementById("aiChatMessages");
  if (!box) return;
  const row = document.createElement("div");
  row.className = `ai-msg-row ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "ai-msg-bubble";

  if (role === "bot") {
    const escaped = escapeHtml(rawText);
    bubble.innerHTML = formatMarkdownBold(escaped).replace(/\n/g, "<br/>");
  } else {
    bubble.textContent = rawText;
  }

  row.appendChild(bubble);
  box.appendChild(row);
  box.scrollTop = box.scrollHeight;
  return row;
}

async function sendAIChatMessage() {
  const inp = document.getElementById("aiChatInput");
  const msg = (inp?.value || "").trim();
  if (!msg) return;

  inp.value = "";
  appendChatMessage("user", msg);

  const loadingRow = appendChatMessage("bot", "⏳ AI đang phân tích dữ liệu...");

  try {
    const activeRows =
      AppState.step2Data?.cleaned_rows ||
      AppState.step1Data?.preview_rows ||
      [];
    const rawCsv =
      AppState.normalizedCsv ||
      document.getElementById("rawInputText")?.value ||
      "";

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: msg,
        context: getContextFromForm(),
        current_step: AppState.currentStep,
        sheets_meta: (AppState.sheets && AppState.sheets.length > 0) ? AppState.sheets : (AppState.sheetsMeta || []),
        dataset_rows: activeRows,
        raw_csv: rawCsv,
        issues_count: AppState.step2Data?.issues?.length || 0
      })
    });

    const data = await res.json();
    if (loadingRow) loadingRow.remove();

    if (!res.ok) {
      appendChatMessage("bot", `❌ Lỗi: ${data.detail || "Không thể xử lý câu hỏi."}`);
      return;
    }

    appendChatMessage("bot", data.reply || "Tôi đã ghi nhận yêu cầu của bạn.");

    // Update quick chips if returned
    if (Array.isArray(data.suggestions) && data.suggestions.length > 0) {
      const chipsContainer = document.getElementById("aiChatQuickChips");
      if (chipsContainer) {
        chipsContainer.innerHTML = data.suggestions
          .map(s => `<button type="button" class="ai-chip-btn" onclick="askQuickQuestion('${escapeHtml(s)}')">💬 ${escapeHtml(s)}</button>`)
          .join("");
      }
    }
  } catch (err) {
    if (loadingRow) loadingRow.remove();
    appendChatMessage("bot", `❌ Lỗi kết nối tới AI Agent: ${err.message}`);
  }
}
