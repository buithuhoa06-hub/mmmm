with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

pos = text.find('"column_metadata"')
print("=== column_metadata in app.py ===")
print(text[pos-100:pos+800])
