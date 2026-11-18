with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

pos4 = html.find('id="panelStep4"')
pos4_end = html.find('</section>', pos4)
print("=== Step 4 in static/index.html ===")
print(html[pos4:pos4+3000])

with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

print("\n=== Functions in app.js related to Step 3 and 4 ===")
import re
for m in re.finditer(r'function\s+([A-Za-z0-9_]+)', js):
    name = m.group(1)
    if 'Step3' in name or 'Step4' in name or 'Report' in name or 'Dashboard' in name or 'clean' in name.lower() or 'edit' in name.lower():
        print("Function:", name)
