import os
import re

files_to_update = [
    "static/index.html",
    "index.html",
    "static/styles.css",
    "static/app.js",
    "app.py"
]

for fp in files_to_update:
    if not os.path.exists(fp):
        continue
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace DataLens Studio -> Data Analyst
    content = content.replace("DataLens Studio", "Data Analyst")
    content = content.replace("DataLens", "Data Analyst")
    content = content.replace("datalens", "data-analyst")
    content = content.replace("DATALENS", "DATA ANALYST")

    # Specific logo badge replacement if needed
    content = content.replace('<span class="brand-main">Data Analyst <span class="brand-accent">Studio</span></span>', '<span class="brand-main">Data <span class="brand-accent">Analyst</span></span>')

    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {fp}")
