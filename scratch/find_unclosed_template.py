with open("static/app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

in_template = False
open_line = 0

for idx, line in enumerate(lines, 1):
    # Remove escaped backticks
    clean_line = line.replace('\\`', '')
    cnt = clean_line.count('`')
    if cnt % 2 != 0:
        in_template = not in_template
        if in_template:
            open_line = idx
            print(f"Template opened at line {idx}: {repr(line.strip())[:60]}")
        else:
            print(f"Template closed at line {idx}: {repr(line.strip())[:60]}")

print("Final in_template status:", in_template)
if in_template:
    print(f"Unclosed template opened at line {open_line}")
