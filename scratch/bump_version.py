for path in ["static/index.html", "index.html"]:
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()
    c = c.replace("/static/styles.css?v=20261117_06", "/static/styles.css?v=20261118_09")
    c = c.replace("/static/app.js?v=20261117_06", "/static/app.js?v=20261118_09")
    with open(path, "w", encoding="utf-8") as f:
        f.write(c)

print("Bumped asset version query to v=20261118_09 successfully in both HTML files!")
