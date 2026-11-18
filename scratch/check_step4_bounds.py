with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

start_needle = '<!-- ========================================================= -->\n            <!-- STEP 4: EXECUTIVE DASHBOARD & EXECUTIVE REPORT            -->\n            <!-- ========================================================= -->'
end_needle = '</main>'

pos_start = html.find(start_needle)
pos_end = html.find(end_needle, pos_start)

print("Start pos:", pos_start, "End pos:", pos_end)
print("Section snippet:\n", html[pos_start:pos_start+400])
