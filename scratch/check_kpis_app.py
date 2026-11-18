with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

pos = text.find('kpi_cards')
print("=== kpi_cards in app.py ===")
print(text[pos-100:pos+1500])
