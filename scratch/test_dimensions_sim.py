import pandas as pd
import io
import re
import unicodedata

def norm_col(str_val):
    s = unicodedata.normalize("NFD", str(str_val or ""))
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = s.replace("đ", "d").replace("Đ", "D").lower()
    return re.sub(r"[\s\-_]+", "_", s)

raw_csv = """Mã dòng,Tháng,Kênh bán,Khu vực,Sản phẩm,Số đơn,Doanh thu (VND)
DS-001,2026-07,Website,Miền Bắc,Áo thun,92,22540000
DS-002,2026-07,Website,Miền Trung,Sơ mi,85,35615000
DS-003,2026-07,Website,Miền Nam,Quần jeans,,37554000
DS-004,2026-07,Website,Miền Bắc,Túi tote,55,8525000
DS-005,2026-07,Cửa hàng,Miền Trung,Áo thun,69,16905000
"""

df = pd.read_csv(io.StringIO(raw_csv))
rows = df.to_dict(orient="records")
cols = list(df.columns)

numeric_candidates = [c for c in cols if c in ("Số đơn", "Doanh thu (VND)")]
cat_candidates = [c for c in cols if c not in ("Mã dòng", "Tháng", "Số đơn", "Doanh thu (VND)")]

val_col = next((c for c in numeric_candidates if re.search(r"doanh_thu|revenue|sales|ngan_sach|budget|tien", norm_col(c))), "")
vol_col = next((c for c in numeric_candidates if re.search(r"so_don|so_luong|quantity|qty|volume", norm_col(c))), "")
cat_col = next((c for c in cat_candidates if re.search(r"kenh|channel|san_pham|product|khu_vuc", norm_col(c))), "")
date_col = next((c for c in cols if re.search(r"thang|month|ky|period|date|ngay", norm_col(c))), "")

print("val_col:", val_col)
print("vol_col:", vol_col)
print("cat_col:", cat_col)
print("date_col:", date_col)

# Chart 1: Group by cat_col
cat_sums = {}
for r in rows:
    k = str(r.get(cat_col, "Khác"))
    try:
        v = float(r.get(val_col, 0) or 0)
    except:
        v = 0.0
    cat_sums[k] = cat_sums.get(k, 0.0) + v

print("\nChart 1 Grouping (Kênh bán -> Doanh thu):")
for k, v in cat_sums.items():
    print(f"  {k}: {v:,.0f} VND")

assert val_col == "Doanh thu (VND)"
assert vol_col == "Số đơn"
assert cat_col == "Kênh bán"
assert date_col == "Tháng"
assert cat_sums["Website"] == 104234000
assert cat_sums["Cửa hàng"] == 16905000
print("\n>>> ALL CHECKS PASSED WITH 100% ACCURACY! <<<")
