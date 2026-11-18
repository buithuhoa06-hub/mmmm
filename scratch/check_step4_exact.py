with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

start_needle = '<!-- ========================================================= -->\n            <!-- STEP 4: EXECUTIVE DASHBOARD & EXECUTIVE REPORT            -->\n            <!-- ========================================================= -->'
end_needle = '</section>\n\n          </main>'

pos_start = html.find(start_needle)
pos_end = html.find(end_needle, pos_start)
if pos_end == -1:
    pos_end = html.find('</section>', pos_start + 1000)

print("Found end at:", pos_end)
print("Snippet around end:\n", html[pos_end-200:pos_end+50])
