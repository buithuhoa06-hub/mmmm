with open("static/app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(max(0, 2615), min(len(lines), 2645)):
    print(f"{i+1}: {lines[i]}", end="")
