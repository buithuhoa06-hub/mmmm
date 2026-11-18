with open("static/app.js", "r", encoding="utf-8") as f:
    text = f.read()

# Replace any raw split with regex split which is 100% safe
text = text.replace('rawContent.split("\n\n")', 'rawContent.split(/\\n\\s*\\n/)')
text = text.replace('rawContent.split("\\n\\n")', 'rawContent.split(/\\n\\s*\\n/)')

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated with regex split in static/app.js")
