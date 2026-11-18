with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

import re
for m in re.finditer(r'kpi_cards', text):
    p = m.start()
    print("Found kpi_cards around line:", text[:p].count("\n")+1)
    print(text[p-50:p+300])
    print("---")
