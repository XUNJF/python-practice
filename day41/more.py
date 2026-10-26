import asyncio
import time

print("=" * 62)
print("  1. 什么时候【不能】gather —— 有依赖关系")
print("=" * 62)


async def fetch_user():
    await asyncio.sleep(0.5)
    return "user Xiaoming"

async def fetch_orders(user):
    await asyncio.sleep(0.5)
    return f"orders of {user}"

async def with_dependency():
    start = time.time()
    user = await fetch_user()
    orders = await fetch_orders(user)
    print(f"    串行（有依赖）：{time.time()-start:.2f}秒 → {orders}")

async def no_dependency():
    start = time.time()
    a, b = await asyncio.gather(fetch_user(), fetch_user())
    print(f"    并发（无依赖）:{time.time()-start:.2f}秒")


async def main1():
    await with_dependency()
    await no_dependency()
    print()
    print("    * 有依赖的必须串行（后面的要用前面的结果）")
    print("    * 没依赖的才该并发")


asyncio.run(main1())

print()
print("=" * 62)
print("  2. timeout")
print("=" * 62)


async def slow_api():
    await asyncio.sleep(10)
    return "finally done"

async def main2():
    start = time.time()
    try:
        r = await asyncio.wait_for(slow_api(), timeout=2)
        print(f"    result: {r}")
    except asyncio.TimeoutError:
        print(f"    超时了！({time.time()-start:.1f} 秒就放弃了，没等到 10 秒)")

asyncio.run(main2())

print()
print("=" * 62)
print("  3. 阻塞函数怎么救")
print("=" * 62)

def blocking_task():
    time.sleep(1)
    return "finished"

async def main3():
    start = time.time()
    r = await asyncio.gather(
        asyncio.to_thread(blocking_task),
        asyncio.to_thread(blocking_task),
        asyncio.to_thread(blocking_task),
    )
    print(f"    三个阻塞函数并发：{time.time()-start:.2f} 秒  →  {r}")
    print("    ★ 不改原函数，也能变并发（靠线程）")


asyncio.run(main3())