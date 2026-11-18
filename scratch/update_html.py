import re
import shutil

with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace header navigation
old_nav_pattern = r'<nav class="island-nav-links"[^>]*>[\s\S]*?</nav>'
new_nav = """<nav class="island-nav-links" aria-label="Điều hướng 2 trang chính">
        <button type="button" id="navTabHome" class="island-link active" onclick="switchPage('home')">
          <span class="tab-icon">🏠</span> <span>Trang chủ</span>
        </button>
        <button type="button" id="navTabStudio" class="island-link" onclick="switchPage('studio')">
          <span class="tab-icon">📊</span> <span>Không gian Phân tích</span>
        </button>
      </nav>"""
html = re.sub(old_nav_pattern, new_nav, html, count=1)

# Replace brand link href
html = html.replace('href="#heroSection" class="brand-identity"', 'href="javascript:void(0)" onclick="switchPage(\'home\')" class="brand-identity"')

# Replace hero flow cards onclicks to use tryJumpToStep
old_flow = """      <!-- 4 Studio Flow Cards -->
      <div class="hero-flow-grid">
        <div class="flow-pill-card" onclick="jumpToStep(1)">
          <span class="flow-step-num">01</span>
          <div class="flow-step-content">
            <strong>Tiếp nhận & Bối cảnh</strong>
            <small>Đọc đa Sheet, link Google Sheet, CSV</small>
          </div>
        </div>
        <div class="flow-pill-card" onclick="jumpToStep(2)">
          <span class="flow-step-num">02</span>
          <div class="flow-step-content">
            <strong>Làm sạch & Duyệt HITL</strong>
            <small>Sửa Ngày/Số/Tỷ lệ chiết khấu, duyệt ĐẠT</small>
          </div>
        </div>
        <div class="flow-pill-card" onclick="jumpToStep(3)">
          <span class="flow-step-num">03</span>
          <div class="flow-step-content">
            <strong>Phân tích Đa Sheet</strong>
            <small>Tổng hợp chung, Pareto 80/20 & SLA</small>
          </div>
        </div>
        <div class="flow-pill-card" onclick="jumpToStep(4)">
          <span class="flow-step-num">04</span>
          <div class="flow-step-content">
            <strong>Dashboard & Báo cáo</strong>
            <small>Power BI slicers & Báo cáo 5 phần</small>
          </div>
        </div>
      </div>"""

new_flow = """      <!-- 4 Studio Flow Cards -->
      <div class="hero-flow-grid">
        <div class="flow-pill-card" onclick="switchPage('studio'); jumpToStep(1, true);" title="Bước 1: Tiếp nhận dữ liệu & Bối cảnh">
          <span class="flow-step-num">01</span>
          <div class="flow-step-content">
            <strong>Tiếp nhận & Bối cảnh</strong>
            <small>Đọc đa Sheet, link Google Sheet, CSV</small>
          </div>
        </div>
        <div class="flow-pill-card" onclick="tryJumpToStep(2)" title="Bước 2: Quét lỗi & Làm sạch dữ liệu">
          <span class="flow-step-num">02</span>
          <div class="flow-step-content">
            <strong>Làm sạch & Duyệt HITL</strong>
            <small>Sửa Ngày/Số/Tỷ lệ chiết khấu, duyệt ĐẠT</small>
          </div>
        </div>
        <div class="flow-pill-card" onclick="tryJumpToStep(3)" title="Bước 3: Nhận định & Tổng hợp đa bảng">
          <span class="flow-step-num">03</span>
          <div class="flow-step-content">
            <strong>Phân tích Đa Sheet</strong>
            <small>Tổng hợp chung, Pareto 80/20 & SLA</small>
          </div>
        </div>
        <div class="flow-pill-card" onclick="tryJumpToStep(4)" title="Bước 4: Dashboard Power BI & Báo cáo 5 phần">
          <span class="flow-step-num">04</span>
          <div class="flow-step-content">
            <strong>Dashboard & Báo cáo</strong>
            <small>Power BI slicers & Báo cáo 5 phần</small>
          </div>
        </div>
      </div>"""

html = html.replace(old_flow, new_flow)

# Replace hero action row buttons
old_actions = """      <!-- Action Row -->
      <div class="hero-actions-row">
        <a href="#analysisStudio" class="cta-primary-btn">
          <span>📥 Bắt đầu Phân tích Ngay</span>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </a>
        <button type="button" class="cta-secondary-btn" onclick="quickDemoSample()">
          <span>⚡ Chạy thử Dữ liệu Mẫu (Demo)</span>
        </button>
      </div>"""

new_actions = """      <!-- Action Row -->
      <div class="hero-actions-row">
        <button type="button" class="cta-primary-btn" onclick="startAnalysisWorkflow()">
          <span>📥 Bắt đầu Phân tích Ngay</span>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </button>
        <button type="button" class="cta-secondary-btn" onclick="quickDemoSample()">
          <span>⚡ Chạy thử Dữ liệu Mẫu (Demo)</span>
        </button>
      </div>"""

html = html.replace(old_actions, new_actions)

# Now wrap hero-showcase + features grid + footer in pageHome:
hero_start = '  <section class="hero-showcase" id="heroSection">'
new_hero_start = """  <!-- =================================================================== -->
  <!-- PAGE 1: TRANG CHỦ (LANDING PAGE)                                    -->
  <!-- =================================================================== -->
  <main id="pageHome" class="page-container active">
    <section class="hero-showcase" id="heroSection">"""

html = html.replace(hero_start, new_hero_start)

# End of hero-showcase: append feature cards + landing footer, then close pageHome and open pageStudio
hero_end = '  </section>\n\n  <!-- =================================================================== -->\n  <!-- ANALYSIS WORKBENCH WINDOW (From demodataanalysisagent.vercel.app)    -->\n  <!-- =================================================================== -->\n  <section class="studio-section" id="analysisStudio">'

new_page_split = """  </section>

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
  </main>

  <!-- =================================================================== -->
  <!-- PAGE 2: KHÔNG GIAN PHÂN TÍCH (DATALENS STUDIO WORKBENCH)            -->
  <!-- =================================================================== -->
  <main id="pageStudio" class="page-container hidden-page">
    <section class="studio-section" id="analysisStudio">"""

html = html.replace(hero_end, new_page_split)

# Close pageStudio right after studio-section ends
studio_end = '    </div>\n  </section>'
new_studio_end = '    </div>\n  </section>\n  </main>'
html = html.replace(studio_end, new_studio_end)

# Also update the window-topbar in studio to add 'Quay lại Trang chủ' button
old_topbar = """        <div class="window-topbar">
          <div class="macos-lights">
            <i class="dot-red" title="Đóng"></i>
            <i class="dot-yellow" title="Thu nhỏ"></i>
            <i class="dot-green" title="Toàn màn hình"></i>
          </div>
          <div class="window-title-badge">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <rect x="2" y="3" width="20" height="14" rx="2"/>
              <line x1="8" y1="21" x2="16" y2="21"/>
              <line x1="12" y1="17" x2="12" y2="21"/>
            </svg>
            <span>Không gian Phân tích Dữ liệu · DataLens Studio</span>
          </div>
          <div class="window-actions-right">
            <button class="btn-window-action" onclick="resetWorkspace()" title="Làm mới toàn bộ không gian làm việc">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
              <span>Phiên mới</span>
            </button>
          </div>
        </div>"""

new_topbar = """        <div class="window-topbar">
          <div class="macos-lights">
            <i class="dot-red" title="Đóng" onclick="switchPage('home')"></i>
            <i class="dot-yellow" title="Thu nhỏ"></i>
            <i class="dot-green" title="Toàn màn hình"></i>
          </div>
          <div class="window-title-badge">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <rect x="2" y="3" width="20" height="14" rx="2"/>
              <line x1="8" y1="21" x2="16" y2="21"/>
              <line x1="12" y1="17" x2="12" y2="21"/>
            </svg>
            <span>Không gian Phân tích Dữ liệu · DataLens Studio</span>
          </div>
          <div class="window-right-tools">
            <button type="button" class="btn-topbar-tool" onclick="switchPage('home')" title="Quay lại Trang chủ">
              🏠 Trang chủ
            </button>
            <button type="button" class="btn-topbar-tool" onclick="resetWorkspace()" title="Bắt đầu phiên làm việc mới">
              🔄 Phiên mới
            </button>
          </div>
        </div>"""

html = html.replace(old_topbar, new_topbar)

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Updated static/index.html and root index.html successfully!")
