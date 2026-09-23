import requests
import time


def Format(data):
    print(data["hitokoto"])
    num = len(data["hitokoto"]) * 2
    for i in range(num):
        print(" ", end='')
    if data['from_who'] is None:
        print(f"——{data['from']} {'佚名'}")
    else:
        print(f"——{data['from']} {data['from_who']}")


for _ in range(10):
    url = f"https://v1.hitokoto.cn/?t={time.time()}"
    response = requests.get(url, timeout=10)
    status = response.status_code
    if status == 200:
        data = response.json()
        Format(data)
        time.sleep(0.3)
    else:
        print(f"请求失败：{status}")


# ============================================================
# 下面这段是「缓存诊断」代码，留着以后排查用，不参与正常运行。
#
# 用途：怀疑接口返回的是缓存旧数据时，跑一下看看响应头。
#   重点看两个：
#     cf-cache-status: HIT  —— 命中缓存了，拿到的不是新内容
#     Age: 1                —— 这份缓存已经放了 1 秒
#
# 解法：请求时给网址加个变化的时间戳，让缓存认不出是同一个请求：
#     url = f"https://v1.hitokoto.cn/?t={time.time()}"
# ============================================================
# url = "https://v1.hitokoto.cn/"
#
# for i in range(3):
#     r = requests.get(url, timeout=10)
#     print(f"第 {i+1} 次：{r.json()['hitokoto'][:30]}")
#
# print()
# print("=== 响应头里的缓存相关信息 ===")
# for k, v in r.headers.items():
#     if 'cache' in k.lower() or 'age' in k.lower() or 'expire' in k.lower():
#         print(f"{k}: {v}")
