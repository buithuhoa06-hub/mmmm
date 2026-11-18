with open("static/index.html", "r", encoding="utf-8") as f:
    c = f.read()
with open("index.html", "w", encoding="utf-8") as f:
    f.write(c)
print("Synced static/index.html to root index.html successfully!")
