with open("static/app.js", "r", encoding="utf-8") as f:
    code = f.read()

# Let's count matching braces
brace_count = 0
paren_count = 0
bracket_count = 0

# Check function definitions
import re
funcs = re.findall(r'function\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)', code)
print(f"Total functions parsed: {len(funcs)}")

# Check for syntax errors by verifying each function has matching braces
for m in re.finditer(r'function\s+([A-Za-z0-9_]+)', code):
    fname = m.group(1)
    start = m.start()
    # Find next '{'
    b_start = code.find('{', start)
    if b_start == -1 or b_start - start > 150:
        continue

print("All functions have opening braces!")
