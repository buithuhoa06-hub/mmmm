with open("static/app.js", "r", encoding="utf-8") as f:
    text = f.read()

# Fix the broken split
text = text.replace('rawContent.split("\n\n")', 'rawContent.split("\\n\\n")')
text = text.replace('rawContent.split("\r\n\r\n")', 'rawContent.split("\\n\\n")')
# Also check if it was split across lines
import re
text = re.sub(r'rawContent\.split\("\s*\n\s*"\)', 'rawContent.split("\\\\n\\\\n")', text)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed rawContent.split in static/app.js")
