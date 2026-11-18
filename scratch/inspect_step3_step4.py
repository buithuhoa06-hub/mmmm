with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

pos3 = html.find('id="panelStep3"')
pos4 = html.find('id="panelStep4"')
print("=== Step 3 in HTML ===")
print(html[pos3:pos4])

print("\n=== Remainder of Step 4 in HTML ===")
print(html[pos4:pos4+4000])
