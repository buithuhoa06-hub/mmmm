import urllib.request

req = urllib.request.urlopen("http://127.0.0.1:8000/")
html = req.read().decode("utf-8")
print("Status: 200 OK, length:", len(html))
print("pageHome in HTML:", 'id="pageHome"' in html)
print("pageStudio in HTML:", 'id="pageStudio"' in html)
print("navTabHome in HTML:", 'id="navTabHome"' in html)
print("navTabStudio in HTML:", 'id="navTabStudio"' in html)
print("switchPage in HTML:", 'switchPage' in html)

req_css = urllib.request.urlopen("http://127.0.0.1:8000/static/styles.css")
css = req_css.read().decode("utf-8")
print("CSS Status: 200 OK, length:", len(css))
print("btn-advance-step2 in CSS:", 'btn-advance-step2' in css)
print("input-required-pulse in CSS:", 'input-required-pulse' in css)
print("page-container in CSS:", 'page-container' in css)

req_js = urllib.request.urlopen("http://127.0.0.1:8000/static/app.js")
js = req_js.read().decode("utf-8")
print("JS Status: 200 OK, length:", len(js))
print("switchPage in JS:", 'switchPage' in js)
print("validateBusinessContext in JS:", 'validateBusinessContext' in js)
print("btn-advance-step2-full in JS:", 'btn-advance-step2-full' in js)
