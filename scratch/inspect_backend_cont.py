with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

pos = text.find("# 2. Extract truly NUMERIC columns")
print(text[pos:pos+2500])
