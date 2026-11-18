with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

pos = text.find("def build_bi_analysis_and_dashboard")
print(text[pos:pos+2500])
