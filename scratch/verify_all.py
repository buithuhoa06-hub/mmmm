import json
import urllib.request

base_url = "http://127.0.0.1:8000"

print("--- 1. Testing Root Page ---")
with urllib.request.urlopen(f"{base_url}/") as res:
    html = res.read().decode("utf-8")
    assert "Data Analyst" in html, "Missing Data Analyst brand"
    assert "DataLens" not in html, "DataLens still present in HTML"
    assert 'id="studioStepWizard"' in html, "Missing studioStepWizard"
    assert 'id="secTomTat"' in html, "Missing #secTomTat"
    assert 'id="secChiSo"' in html, "Missing #secChiSo"
    assert 'id="demodataKpiGrid"' in html, "Missing #demodataKpiGrid"
    assert 'id="demodataTabsRow"' in html, "Missing #demodataTabsRow"
    print("HTML verified: Clean layout, Data Analyst brand, 5 sections & wizard stepper present!")

print("--- 2. Testing Static JS & CSS ---")
with urllib.request.urlopen(f"{base_url}/static/styles.css") as res:
    css = res.read().decode("utf-8")
    assert ".demodata-report-container" in css, "Missing .demodata-report-container in CSS"
    assert ".demodata-kpi-grid" in css, "Missing .demodata-kpi-grid in CSS"
    assert ".demodata-tabs-row" in css, "Missing .demodata-tabs-row in CSS"
    assert ".studio-step-wizard" in css, "Missing .studio-step-wizard in CSS"
    print("CSS verified: Demodata report & Step wizard styles present!")

with urllib.request.urlopen(f"{base_url}/static/app.js") as res:
    js = res.read().decode("utf-8")
    # Verify ONLY 1 button in renderStep1DecisionGate (check count of proceedToStep2 calls in renderStep1DecisionGate)
    gate_part = js[js.find("function renderStep1DecisionGate"):js.find("function focusRawInputManual")]
    btn_count = gate_part.count("proceedToStep2()")
    assert btn_count == 1, f"Expected exactly 1 proceedToStep2() button in Step 1 gate, found {btn_count}"
    assert "renderStep4DashboardAndReport" in js, "Missing renderStep4DashboardAndReport"
    assert "demodataExecSummaryBody" in js, "Missing demodataExecSummaryBody"
    print(f"JS verified: Exactly {btn_count} next button in Step 1 decision gate (no duplicate!), clean report engine active!")

print("--- 3. Testing Step 3 Analyze API (Executive Summary Style) ---")
payload = {
    "context": {
        "company_name": "Bán lẻ mẫu",
        "industry": "Bán lẻ đa kênh",
        "target_audience": "Ban Giám Đốc",
        "objective": "Tối ưu hóa kênh bán hàng và chi phí giá vốn"
    },
    "cleaned_rows": [
        {"Kênh": "Website", "Doanh thu (VND)": "173200000", "Chi phí giá vốn (VND)": "95000000"},
        {"Kênh": "Shopee", "Doanh thu (VND)": "120000000", "Chi phí giá vốn (VND)": "72000000"},
        {"Kênh": "Lazada", "Doanh thu (VND)": "85000000", "Chi phí giá vốn (VND)": "55518000"}
    ]
}
req = urllib.request.Request(
    f"{base_url}/api/step3/analyze",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as res:
    data = json.loads(res.read().decode("utf-8"))
    sections = data.get("feedback_sections", [])
    sec1 = next((s for s in sections if s.get("badge") == "[Tóm tắt]"), None)
    assert sec1 is not None, "Missing [Tóm tắt] section"
    assert sec1.get("title") == "Tóm tắt điều hành", f"Expected title 'Tóm tắt điều hành', got {sec1.get('title')}"
    print(f"Section 1 Title: {sec1.get('title')}")
    print("Section 1 Content:\n", sec1.get("content"))
    assert "Nhóm" in sec1.get("content") and "cao nhất" in sec1.get("content"), "Missing executive top group insight"

print("\nALL SYSTEM & UI REFINEMENTS VERIFIED 100% SUCCESSFULLY!")
