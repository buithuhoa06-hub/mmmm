with open("static/app.js", "r", encoding="utf-8") as f:
    text = f.read()

# Let's check for broken lines in text
lines = text.splitlines()
print(f"Total lines: {len(lines)}")
for i in range(1215, min(1235, len(lines))):
    print(f"{i+1}: {repr(lines[i])}")
