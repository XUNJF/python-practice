import asyncio
import time

async def down_load(name, s):
    await asyncio.sleep(s)
    return f"{name}完成用了{s}秒"

async def main():
    start = time.time()
    result = await asyncio.gather(
        down_load("A", 1),
        down_load("B", 1),
        down_load("C", 1),
    )
    for r in result:
        print(r)
    print(f"\n总共用了{time.time()-start:.2f}秒")

asyncio.run(main())
