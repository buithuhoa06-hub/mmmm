with open("static/app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(1470, min(1570, len(lines))):
    print(f"{i+1}: {lines[i]}", end="")
