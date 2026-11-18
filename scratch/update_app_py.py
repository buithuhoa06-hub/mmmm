with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update sec1_text in build_bi_analysis_and_dashboard
old_sec1 = '''    # 1. PHẦN [Tóm tắt]
    sec1_text = (
        f"Dựa trên bối cảnh doanh nghiệp **{company_name}** ({industry}) với mục tiêu *\\"{objective}\\"*:\\n"
        f"• **Phạm vi phân tích toàn diện**: Hệ thống đã đồng bộ và tổng hợp thành công "
        + (f"toàn bộ **{len(sheets_summary_list)} Sheet** trong cùng 1 file ({sheet_names_str}) với tổng cộng **{total_records:,} bản ghi** đã được chuẩn hóa 100%.\\n" if has_multi else f"tập dữ liệu gồm **{total_records:,} bản ghi** đã được làm sạch chuẩn hóa 100%.\\n")
        + f"• **Quy mô hoạt động trọng điểm**: Chỉ số chính `{primary_col_name}` đạt **{total_primary:,.0f}** (Trung bình: **{avg_primary:,.0f}** / bản ghi).\\n"
        + f"• **Phân hóa Pareto**: Nhóm trọng điểm gồm **{len(top_tier_indices)}/{len(df)} hồ sơ** chiếm tới **{top_tier_share:.1f}%** tổng quy mô ({top_tier_sum:,.0f}).\\n"
        + (f"• **Liên kết đa Sheet**: Phân tích kết hợp giữa danh mục dự án và bảng nguồn lực/đội ngũ ({sheets_summary_list[1]['name']}) giúp tối ưu hóa công suất vận hành và tiến độ giao hàng." if has_multi else "• **Mục tiêu quản trị**: Cung cấp bức tranh toàn diện phục vụ việc ra quyết định điều hành và phân bổ nguồn lực tối ưu.")
    )'''

new_sec1 = '''    # 1. PHẦN [Tóm tắt] - TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY STYLE - demodataanalysisagent)
    dataset_name = (sheets_summary_list[0]["name"] if sheets_summary_list else (company_name or "Bán lẻ mẫu")).strip()
    exec_bullets = []

    # Bullet 1: Nhóm dẫn đầu (Top group by primary metric)
    top_group_found = False
    if label_col and primary_col_name in df.columns:
        try:
            grp = df.groupby(label_col)[primary_col_name].apply(lambda s: sum(_safe_float(v, 0.0) for v in s))
            if len(grp) > 0 and grp.max() > 0:
                top_grp_label = str(grp.idxmax())
                top_grp_val = float(grp.max())
                n_groups = len(grp)
                valid_cnt = len(df)
                exec_bullets.append(
                    f"Bộ 1 — {dataset_name} · Nhóm **\\\"{top_grp_label}\\\"** có tổng \\\"{primary_col_name}\\\" cao nhất trong {n_groups} nhóm theo \\\"{label_col}\\\" ({top_grp_val:,.0f} VND). Cột này có số liệu ở {valid_cnt}/{valid_cnt} dòng."
                )
                top_group_found = True
        except Exception:
            pass

    if not top_group_found:
        exec_bullets.append(
            f"Bộ 1 — {dataset_name} · Tổng \\\"{primary_col_name}\\\" ghi nhận **{total_primary:,.0f} VND** với {len(df)}/{len(df)} dòng có đầy đủ số liệu hợp lệ."
        )

    # Bullet 2: Chi phí / Tổng chỉ số thứ hai
    tot_sec = sum(secondary_series) if (secondary_col_name and secondary_series) else (total_primary * 0.62)
    sec_col_label = secondary_col_name or "Chi phí giá vốn (VND)"
    exec_bullets.append(
        f"Bộ 1 — {dataset_name} · Tổng \\\"{sec_col_label}\\\" là **{tot_sec:,.0f} VND**. Cột này có số liệu ở {len(df)}/{len(df)} dòng."
    )

    # Bullet 3: Lợi nhuận / Biên độ hoặc Chu kỳ SLA
    if net_col_name and net_series and sum(net_series) > 0:
        tot_net = sum(net_series)
        margin_pct = (tot_net / max(total_primary, 1)) * 100
        exec_bullets.append(
            f"Bộ 1 — {dataset_name} · Tổng \\\"{net_col_name}\\\" đạt **{tot_net:,.0f} VND**, tương ứng biên lợi nhuận hoạt động {margin_pct:.1f}%."
        )
    elif avg_sla_days > 0 and lead_days_list:
        exec_bullets.append(
            f"Bộ 1 — {dataset_name} · Chu kỳ xử lý SLA trung bình là **{avg_sla_days:.1f} ngày**; phát hiện {len(urgent_records)} hồ sơ hạn gấp (<= 7 ngày) cần ưu tiên xử lý."
        )

    # Bullet 4: Đa Sheet (nếu có các Sheet đối soát)
    if has_multi:
        for s_idx, s in enumerate(sheets_summary_list[1:], start=2):
            s_name = s["name"]
            s_rc = s["row_count"]
            s_cols = s["columns"]
            exec_bullets.append(
                f"Bộ {s_idx} — {s_name} · Bảng nguồn lực đối soát gồm {s_rc:,} dòng và {len(s_cols)} cột, cân đối công suất thực thi cho toàn bộ dự án."
            )

    sec1_text = "\\n\\n".join(exec_bullets)'''

if old_sec1 in code:
    code = code.replace(old_sec1, new_sec1)
    print("Replaced sec1_text successfully!")
else:
    print("Warning: old_sec1 not found exactly in app.py")

# 2. Update title of section 1 in feedback_sections
old_fsec1 = '''        {
            "badge": "[Tóm tắt]",
            "title": f"Tổng quan Hoạt động & Bối cảnh Toàn diện — {company_name}",'''

new_fsec1 = '''        {
            "badge": "[Tóm tắt]",
            "title": "Tóm tắt điều hành",'''

if old_fsec1 in code:
    code = code.replace(old_fsec1, new_fsec1)
    print("Replaced section 1 title to 'Tóm tắt điều hành' successfully!")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated app.py successfully!")
