with open("static/styles.css", "r", encoding="utf-8") as f:
    css = f.read()

pos = css.find("step4-mode-switcher")
if pos != -1:
    print(css[pos:pos+1500])
else:
    print("Not found step4-mode-switcher in styles.css")
