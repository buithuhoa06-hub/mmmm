import re

with open("static/styles.css", "r", encoding="utf-8") as f:
    css = f.read()

# 1. Update :root variables
root_pattern = r":root\s*\{[^}]+\}"
new_root = """:root {
  color-scheme: light;
  --font-heading: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-body: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --text: #0f172a;
  --text-dark: #0f172a;
  --muted: #475569;
  --subtle: #64748b;
  --line: #e2e8f0;
  --line-dark: #cbd5e1;
  --blue-primary: #0284c7;
  --blue-deep: #0369a1;
  --blue-soft: #f0f7ff;
  --blue-subtle: #e0f2fe;
  --blue-vibrant: #2563eb;
  --blue-border: #bae6fd;
  --green: #0284c7;
  --green-deep: #0369a1;
  --mint: #e0f2fe;
  --mint-dark: #bae6fd;
  --emerald: #0284c7;
  --blue: #2563eb;
  --blue-light: #f0f7ff;
  --orange: #ea580c;
  --orange-light: #fff7ed;
  --red: #dc2626;
  --red-light: #fef2f2;
  --bg-card: #ffffff;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 14px rgba(2, 132, 199, 0.08);
  --shadow-lg: 0 12px 32px rgba(2, 132, 199, 0.12);
  --shadow-window: 0 36px 64px -22px rgba(2, 132, 199, 0.22), 0 12px 28px -12px rgba(2, 132, 199, 0.14), 0 0 0 5px rgba(255, 255, 255, 0.65);
}"""
css = re.sub(root_pattern, new_root, css, count=1)

# 2. Update body background
body_pattern = r"body\s*\{[^}]*background:[^}]*\}"
new_body = """body {
  min-height: 100vh;
  color: var(--text);
  font-family: var(--font-body);
  background: radial-gradient(ellipse at 15% 10%, #dbeafe 0%, transparent 60%),
              radial-gradient(ellipse at 85% 90%, #e0f2fe 0%, transparent 55%),
              linear-gradient(135deg, #f0f7ff 0%, #e8f3fc 100%);
  background-attachment: fixed;
  overflow-x: hidden;
}"""
css = re.sub(body_pattern, new_body, css, count=1)

# 3. Replace color hexes
replacements = {
    "#08785f": "#0284c7",
    "#10b981": "#0284c7",
    "#059669": "#0369a1",
    "#065f46": "#075985",
    "#00644e": "#075985",
    "#16a34a": "#0284c7",
    "#15803d": "#0369a1",
    "#166534": "#0369a1",
    "#dcf4e8": "#dbeafe",
    "#e8f5ee": "#f0f7ff",
    "#dff2e8": "#e0f2fe",
    "#cce8da": "#bae6fd",
    "#0c604b": "#0369a1",
    "#047857": "#0284c7",
    "#a7f3d0": "#bae6fd",
    "#ecfdf5": "#f0f7ff",
    "#bbf7d0": "#bae6fd",
    "rgba(16, 185, 129,": "rgba(2, 132, 199,",
    "rgba(8, 120, 95,": "rgba(2, 132, 199,",
    "rgba(22, 163, 74,": "rgba(2, 132, 199,",
    "rgba(11, 119, 87,": "rgba(2, 132, 199,",
    "rgba(23, 43, 40,": "rgba(2, 132, 199,",
    "rgba(38, 75, 71,": "rgba(2, 132, 199,",
}

for old, new in replacements.items():
    css = css.replace(old, new)

# 4. Append comprehensive CSS rules for:
# - 2-Page separation (.page-container, .island-link.active, .home-features-section, etc.)
# - Step 1 Result Decision Gate (.format-box, .format-header, .btn-advance-step2, .btn-advance-step2-full)
# - Input validation pulse (.input-required-pulse)
# - Topbar tools and actions
additional_css = """

/* ========================================================================== */
/* 2-PAGE ARCHITECTURE (Page 1: Home / Landing · Page 2: Studio Workbench)   */
/* ========================================================================== */
.page-container {
  display: block;
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.page-container.hidden-page {
  display: none !important;
}

.page-container.active {
  display: block !important;
  animation: pageFadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes pageFadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Island Nav Tab Switcher */
.island-link {
  cursor: pointer;
  border: none;
  background: transparent;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
  border-radius: 9999px;
  font-size: 12.5px;
  font-weight: 600;
  color: #475569;
  transition: all 0.2s ease;
}

.island-link:hover {
  color: #0284c7;
  background: #e0f2fe;
}

.island-link.active {
  color: #ffffff !important;
  background: linear-gradient(135deg, #0284c7, #2563eb) !important;
  box-shadow: 0 3px 10px rgba(2, 132, 199, 0.35) !important;
}

.tab-icon {
  font-size: 13px;
}

/* Home Landing Page Feature Highlights Grid */
.home-features-section {
  max-width: 1200px;
  margin: 0 auto 36px;
  padding: 0 16px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

@media (max-width: 860px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
}

.feature-card {
  background: #ffffff;
  border: 1.5px solid #e0f2fe;
  border-radius: 20px;
  padding: 24px 22px;
  box-shadow: 0 4px 18px rgba(2, 132, 199, 0.05);
  transition: all 0.25s ease;
  text-align: left;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(2, 132, 199, 0.12);
  border-color: #bae6fd;
}

.feature-card .feat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #f0f7ff;
  border: 1px solid #bae6fd;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  margin-bottom: 14px;
}

.feature-card h3 {
  font-family: var(--font-heading);
  font-size: 15.5px;
  font-weight: 750;
  color: #0f172a;
  margin-bottom: 8px;
}

.feature-card p {
  font-size: 12.8px;
  color: #475569;
  line-height: 1.6;
}

/* Landing Page Footer Banner */
.landing-footer {
  max-width: 1200px;
  margin: 0 auto 60px;
  padding: 0 16px;
}

.landing-footer-container {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border: 1px solid #e0f2fe;
  border-radius: 18px;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #475569;
  font-size: 12.5px;
  flex-wrap: wrap;
  gap: 12px;
}

.btn-footer-launch {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #0284c7, #2563eb);
  color: #ffffff;
  padding: 9px 20px;
  border-radius: 9999px;
  font-weight: 700;
  font-size: 12.5px;
  border: none;
  cursor: pointer;
  box-shadow: 0 3px 12px rgba(2, 132, 199, 0.3);
  transition: all 0.2s ease;
}

.btn-footer-launch:hover {
  transform: translateY(-1.5px);
  box-shadow: 0 6px 18px rgba(2, 132, 199, 0.45);
}

/* Studio Window Topbar Right Tools */
.window-right-tools {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-topbar-tool {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 11.5px;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-topbar-tool:hover {
  background: #e2e8f0;
  color: #0f172a;
}

/* ========================================================================== */
/* STEP 1 RESULT BOX & ADVANCE TO STEP 2 BUTTONS (BULLETPROOF STYLING)        */
/* ========================================================================== */
.decision-container {
  margin-top: 20px;
}

.format-box {
  border-radius: 16px;
  padding: 22px;
  box-shadow: 0 6px 24px rgba(2, 132, 199, 0.08);
  transition: all 0.3s ease;
  margin-top: 14px;
}

.format-box.valid {
  background: linear-gradient(180deg, #f0f7ff 0%, #ffffff 100%) !important;
  border: 1.5px solid #bae6fd !important;
}

.format-box.invalid {
  background: linear-gradient(180deg, #fff1f2 0%, #ffffff 100%) !important;
  border: 1.5px solid #fecdd3 !important;
}

.format-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0f2fe;
  flex-wrap: wrap;
}

.format-badge-valid {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px;
  background: #e0f2fe;
  color: #0284c7;
  border: 1px solid #7dd3fc;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 750;
  letter-spacing: 0.3px;
}

.format-badge-invalid {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px;
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fca5a5;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 750;
}

/* Prominent button in Header */
.btn-advance-step2 {
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
  color: #ffffff !important;
  padding: 11px 22px !important;
  border-radius: 10px !important;
  font-size: 13.5px !important;
  font-weight: 750 !important;
  text-decoration: none !important;
  border: 1px solid rgba(255, 255, 255, 0.35) !important;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35) !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
  white-space: nowrap !important;
}

.btn-advance-step2:hover {
  background: linear-gradient(135deg, #0369a1 0%, #1d4ed8 100%) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 22px rgba(2, 132, 199, 0.5) !important;
}

/* Prominent Full Banner in Footer */
.format-footer-action {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1.5px dashed #bae6fd;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.footer-action-note {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #0369a1;
}

.btn-advance-step2-full {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 10px !important;
  background: linear-gradient(135deg, #0284c7 0%, #1d4ed8 100%) !important;
  color: #ffffff !important;
  padding: 14px 28px !important;
  border-radius: 12px !important;
  font-size: 14.5px !important;
  font-weight: 800 !important;
  letter-spacing: 0.3px !important;
  border: 1px solid rgba(255, 255, 255, 0.35) !important;
  box-shadow: 0 6px 22px rgba(2, 132, 199, 0.45) !important;
  cursor: pointer !important;
  transition: all 0.25s ease !important;
}

.btn-advance-step2-full:hover {
  background: linear-gradient(135deg, #0369a1 0%, #1e40af 100%) !important;
  transform: translateY(-2px) scale(1.01) !important;
  box-shadow: 0 10px 28px rgba(2, 132, 199, 0.55) !important;
}

/* Pulsing red border when context fields are missing */
.input-required-pulse {
  animation: requiredPulse 0.5s ease 3 !important;
  border-color: #ef4444 !important;
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.25) !important;
}

@keyframes requiredPulse {
  0%, 100% { border-color: #ef4444; box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.25); }
  50% { border-color: #dc2626; box-shadow: 0 0 0 7px rgba(239, 68, 68, 0.45); }
}
"""

css += additional_css

with open("static/styles.css", "w", encoding="utf-8") as f:
    f.write(css)

print("Updated static/styles.css successfully!")
