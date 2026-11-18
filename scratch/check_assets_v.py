with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

import re
matches = re.findall(r'(?:href|src)=["\']([^"\']+\.(?:css|js)[^"\']*)["\']', html)
print("Asset links in HTML:")
for m in matches:
    print(" ", m)
