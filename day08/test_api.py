# 探测哪些接口能通
# 国内国外能访问的网站不同，实测最准

import requests

candidates = [
    ("一言",      "https://v1.hitokoto.cn/"),
    ("vvhan天气", "https://api.vvhan.com/api/weather"),
    ("oioweb天气","https://api.oioweb.cn/api/weather/weatherInfo"),
    ("国际天气",   "https://wttr.in/Chengdu?format=j1"),
    ("GitHub",    "https://api.github.com"),
]

for name, url in candidates:
    print(f"--- {name} ---")
    print(f"    {url}")
    try:
        r = requests.get(url, timeout=8)
        print(f"    状态码：{r.status_code}")
        if r.status_code == 200:
            print(f"    返回前 150 字：{r.text[:150]}")
    except Exception as e:
        print(f"    失败：{type(e).__name__} - {e}")
    print()
