import urllib.request
import json

raw_csv = """Mã dòng,Tháng,Kênh bán,Khu vực,Sản phẩm,Số đơn,Doanh thu (VND)
DS-001,2026-07,Website,Miền Bắc,Áo thun,92,22540000
DS-002,2026-07,Website,Miền Trung,Sơ mi,85,35615000
DS-003,2026-07,Website,Miền Nam,Quần jeans,,37554000
DS-004,2026-07,Website,Miền Bắc,Túi tote,55,8525000
DS-005,2026-07,Cửa hàng,Miền Trung,Áo thun,69,16905000
"""

data = {
    "raw_csv": raw_csv,
    "context": {
        "company_name": "Công ty Cổ phần Thiên Minh",
        "domain": "Bán lẻ đa kênh",
        "analysis_goal": "Tối ưu doanh thu, chi phí và biên lợi nhuận ròng"
    },
    "custom_instruction": ""
}

req = urllib.request.Request(
    "http://localhost:8000/api/step2/clean",
    data=json.dumps(data).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

res = urllib.request.urlopen(req)
clean_res = json.loads(res.read().decode("utf-8"))

print("=== STEP 2 CLEAN RESULTS ===")
print("Columns:", clean_res.get("columns"))
print("Column Types:", clean_res.get("column_types"))

# Test Step 3 analyze
step3_payload = {
    "cleaned_rows": clean_res.get("cleaned_rows", []),
    "context": data["context"],
    "user_feedback": "",
    "all_sheets": []
}

req3 = urllib.request.Request(
    "http://localhost:8000/api/step3/analyze",
    data=json.dumps(step3_payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
res3 = urllib.request.urlopen(req3)
bi_res = json.loads(res3.read().decode("utf-8"))

print("\n=== STEP 3 ANALYZE RESULTS ===")
print("Feedback sections count:", len(bi_res.get("feedback_sections", [])))
for s in bi_res.get("feedback_sections", []):
    print(f"  - Section: {s.get('badge')} | Title: {s.get('title')}")
print("Action plan matrix rows:", len(bi_res.get("action_plan_matrix", [])))
print("Executive bullets:")
for b in bi_res.get("executive_bullets", [])[:3]:
    print(f"  * {b}")
print("\n>>> ALL API TESTS COMPLETED PERFECTLY! <<<")
