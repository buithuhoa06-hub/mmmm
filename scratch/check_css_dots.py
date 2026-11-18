with open("static/styles.css", "r", encoding="utf-8") as f:
    css = f.read()

pos = css.find("step4-mode-switcher")
print(css[pos-50:pos+1500])
