with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

pos = text.find('"column_metadata"')
print(text[pos-200:pos+800])
