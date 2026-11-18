import re

with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Pattern for the unwanted features section + landing footer
unwanted_pattern = r'</main>\s*<!-- HIGHLIGHT FEATURES GRID -->[\s\S]*?</footer>\s*</main>'

if re.search(unwanted_pattern, html):
    html = re.sub(unwanted_pattern, '</main>', html, count=1)
    print("Removed features section and landing footer successfully!")
else:
    # Alternative direct replacement
    old_block = """    </div>
  </section>
  </main>

    <!-- HIGHLIGHT FEATURES GRID -->
    <section class="home-features-section">
      <div class="features-grid">
        <div class="feature-card">
          <div class="feat-icon">📑</div>
          <h3>Xử lý Đa Sheet Đồng Bộ</h3>
          <p>Tự động phân tích tất cả các sheet trong cùng 1 file Excel hoặc liên kết Google Sheet trực tiếp, gom dữ liệu thông minh và tổng hợp báo cáo toàn diện.</p>
        </div>
        <div class="feature-card">
          <div class="feat-icon">🛡️</div>
          <h3>Làm sạch Minh bạch HITL</h3>
          <p>Cơ chế Human-in-the-Loop: Tự động phát hiện kiểu ngày tháng, tỷ lệ chiết khấu, số tiền sai định dạng và cho phép bạn duyệt ĐẠT hoặc sửa thủ công.</p>
        </div>
        <div class="feature-card">
          <div class="feat-icon">📊</div>
          <h3>Dashboard & Báo cáo 5 phần</h3>
          <p>Xuất biểu đồ tương tác kèm slicer bộ lọc phong cách Power BI và tạo Báo cáo điều hành chuẩn 5 phần: Tóm tắt, Chỉ số, Chuyên đề, Đề xuất, Nguồn dữ liệu.</p>
        </div>
      </div>
    </section>

    <!-- LANDING FOOTER -->
    <footer class="landing-footer">
      <div class="landing-footer-container">
        <span>🔒 Dữ liệu được bảo mật và phân tích an toàn trong phiên làm việc của bạn</span>
        <button type="button" class="btn-footer-launch" onclick="startAnalysisWorkflow()">
          Mở Không gian Phân tích →
        </button>
      </div>
    </footer>
  </main>"""

    new_block = """    </div>
  </section>
  </main>"""

    if old_block in html:
        html = html.replace(old_block, new_block)
        print("Replaced old_block directly!")
    else:
        print("Warning: could not find exact block to remove")

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Updated static/index.html and root index.html successfully!")
