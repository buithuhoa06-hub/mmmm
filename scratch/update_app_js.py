with open("static/app.js", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add switchPage, startAnalysisWorkflow, tryJumpToStep, validateBusinessContext
helper_funcs = """// ============================================================================
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
    alert("⚠️ BẮT BUỘC NHẬP BỐI CẢNH DOANH NGHIỆP:\\nVui lòng nhập 'Tên Doanh nghiệp / Dự án' ở Bước 1A trước khi tiếp tục!");
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
    alert("⚠️ BẮT BUỘC NHẬP MỤC TIÊU PHÂN TÍCH:\\nVui lòng nhập 'Bối cảnh & Mục tiêu Phân tích' ở Bước 1A để AI nắm rõ bài toán kinh doanh!");
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

"""

# Prepend helpers before quickDemoSample or at top of file
if "function quickDemoSample()" in code:
    code = code.replace("function quickDemoSample()", helper_funcs + "function quickDemoSample()")

# 2. Update quickDemoSample to call switchPage('studio')
old_demo = """function quickDemoSample() {
  document.getElementById("ctxCompany").value = "Tập đoàn Đầu tư & Công nghệ Alpha";"""

new_demo = """function quickDemoSample() {
  switchPage("studio");
  jumpToStep(1, true);
  document.getElementById("ctxCompany").value = "Tập đoàn Đầu tư & Công nghệ Alpha";"""

if old_demo in code:
    code = code.replace(old_demo, new_demo)

# 3. Update jumpToStep to check context when stepNum >= 2
old_jump = """function jumpToStep(stepNum, force = false) {
  if (!force && stepNum > AppState.maxUnlockedStep) {
    return;
  }"""

new_jump = """function jumpToStep(stepNum, force = false) {
  if (stepNum >= 2 && !force) {
    if (!validateBusinessContext()) {
      return;
    }
  }
  if (!force && stepNum > AppState.maxUnlockedStep) {
    return;
  }"""

if old_jump in code:
    code = code.replace(old_jump, new_jump)

# 4. Update runStep1Validation to use validateBusinessContext
old_val = """async function runStep1Validation() {
  const company = document.getElementById("ctxCompany").value.trim();
  const objective = document.getElementById("ctxObjective").value.trim();
  const rawInput = document.getElementById("rawInputText").value.trim();

  if (!company) {
    alert("⚠️ Vui lòng nhập 'Tên Doanh nghiệp / Dự án' ở Bước 1A trước khi phân tích.");
    const compInput = document.getElementById("ctxCompany");
    compInput.focus();
    compInput.classList.add("input-required-pulse");
    setTimeout(() => compInput.classList.remove("input-required-pulse"), 1500);
    return;
  }

  if (!objective) {
    alert("⚠️ Vui lòng nhập 'Bối cảnh & Mục tiêu Phân tích' ở Bước 1A để AI nắm rõ mục tiêu bài toán.");
    const objInput = document.getElementById("ctxObjective");
    objInput.focus();
    objInput.classList.add("input-required-pulse");
    setTimeout(() => objInput.classList.remove("input-required-pulse"), 1500);
    return;
  }"""

new_val = """async function runStep1Validation() {
  if (!validateBusinessContext()) {
    return;
  }
  const rawInput = document.getElementById("rawInputText").value.trim();"""

if old_val in code:
    code = code.replace(old_val, new_val)

# 5. Update proceedToStep2 to use validateBusinessContext
old_proceed = """async function proceedToStep2() {
  const company = document.getElementById("ctxCompany").value.trim();
  const objective = document.getElementById("ctxObjective").value.trim();

  if (!company) {
    alert("⚠️ Vui lòng nhập 'Tên Doanh nghiệp / Dự án' ở Bước 1A trước khi chuyển sang Bước 2.");
    const compInput = document.getElementById("ctxCompany");
    compInput.focus();
    compInput.classList.add("input-required-pulse");
    setTimeout(() => compInput.classList.remove("input-required-pulse"), 1500);
    return;
  }

  if (!objective) {
    alert("⚠️ Vui lòng nhập 'Bối cảnh & Mục tiêu Phân tích' ở Bước 1A để AI làm sạch và phân tích chính xác.");
    const objInput = document.getElementById("ctxObjective");
    objInput.focus();
    objInput.classList.add("input-required-pulse");
    setTimeout(() => objInput.classList.remove("input-required-pulse"), 1500);
    return;
  }

  AppState.maxUnlockedStep = Math.max(AppState.maxUnlockedStep, 2);
  jumpToStep(2, true);
  await runStep2Cleaning("");
}"""

new_proceed = """async function proceedToStep2() {
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
}"""

if old_proceed in code:
    code = code.replace(old_proceed, new_proceed)

# 6. Update renderStep1DecisionGate to render bulletproof buttons
old_render_gate = """          <button type="button" class="btn-advance-step2" onclick="proceedToStep2()">
            ⚡ Tiếp tục sang BƯỚC 2: Làm sạch Dữ liệu →
          </button>
        </div>

        <div style="display:grid; grid-template-columns: 1fr 1.5fr; gap:14px; margin-top:12px;">"""

new_render_gate = """          <button type="button" class="btn-advance-step2" onclick="proceedToStep2()" style="display:inline-flex; align-items:center; gap:8px; background:linear-gradient(135deg, #0284c7 0%, #2563eb 100%); color:#ffffff; padding:11px 22px; border-radius:10px; font-size:13.5px; font-weight:750; border:1px solid rgba(255,255,255,0.35); box-shadow:0 4px 14px rgba(2,132,199,0.35); cursor:pointer;">
            <span>⚡ Tiếp tục sang BƯỚC 2: Làm sạch Dữ liệu</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </button>
        </div>

        <div style="display:grid; grid-template-columns: 1fr 1.5fr; gap:14px; margin-top:12px;">"""

if old_render_gate in code:
    code = code.replace(old_render_gate, new_render_gate)

old_bottom_button = """        <div style="margin-top:14px; padding-top:12px; border-top:1px solid #e2e8f0; display:flex; justify-content:flex-end;">
          <button type="button" class="btn-advance-step2-full" onclick="proceedToStep2()">
            ⚡ Tiếp tục sang BƯỚC 2: Làm sạch Dữ liệu & Duyệt kết quả (HITL) →
          </button>
        </div>"""

new_bottom_button = """        <div class="format-footer-action" style="margin-top:18px; padding-top:16px; border-top:1.5px dashed #bae6fd; display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap;">
          <div class="footer-action-note" style="display:flex; align-items:center; gap:8px; font-size:13px; font-weight:600; color:#0369a1;">
            <span class="pulse-beacon"></span>
            <span><strong>Dữ liệu chuẩn:</strong> Bấm nút bên phải để AI bắt đầu quét lỗi & chuẩn hóa dữ liệu:</span>
          </div>
          <button type="button" class="btn-advance-step2-full" onclick="proceedToStep2()" style="display:inline-flex; align-items:center; justify-content:center; gap:10px; background:linear-gradient(135deg, #0284c7 0%, #1d4ed8 100%); color:#ffffff; padding:14px 28px; border-radius:12px; font-size:14.5px; font-weight:800; border:1px solid rgba(255,255,255,0.35); box-shadow:0 6px 22px rgba(2,132,199,0.45); cursor:pointer;">
            <span>⚡ TIẾP TỤC SANG BƯỚC 2: LÀM SẠCH & DUYỆT HITL</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </button>
        </div>"""

if old_bottom_button in code:
    code = code.replace(old_bottom_button, new_bottom_button)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated static/app.js successfully!")
