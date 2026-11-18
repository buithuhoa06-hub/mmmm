with open("static/app.js", "r", encoding="utf-8") as f:
    js_code = f.read()

# Let's check bracket balancing and quotes
stack = []
in_single = False
in_double = False
in_template = False
escaped = False

errors = []
for line_no, line in enumerate(js_code.splitlines(), start=1):
    i = 0
    while i < len(line):
        ch = line[i]
        if escaped:
            escaped = False
            i += 1
            continue
        if ch == '\\':
            escaped = True
            i += 1
            continue

        # Handle comments
        if not in_single and not in_double and not in_template:
            if line[i:i+2] == '//':
                break

        if ch == "'" and not in_double and not in_template:
            in_single = not in_single
        elif ch == '"' and not in_single and not in_template:
            in_double = not in_double
        elif ch == '`' and not in_single and not in_double:
            in_template = not in_template
        i += 1

    if in_single:
        errors.append((line_no, "Unclosed single quote"))
        in_single = False
    if in_double:
        errors.append((line_no, "Unclosed double quote"))
        in_double = False

if errors:
    print(f"Found {len(errors)} string literal errors:")
    for l, err in errors[:10]:
        print(f"  Line {l}: {err}")
else:
    print("Zero single/double quote syntax errors found in static/app.js!")
print("Template string open at EOF:", in_template)
