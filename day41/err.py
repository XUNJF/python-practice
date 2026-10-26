import asyncio

print("=" * 62)
print(" 1. gather 里有一个失败，会怎样")
print("=" * 62)
print()

async def good_task():
    await asyncio.sleep(0.1)
    return "success"

async def bad_task():
    await asyncio.sleep(0.1)
    raise ValueError("这个接口挂了")

async def default_behavior():
    print("  默认（没加参数）：")
    try:
        r = await asyncio.gather(good_task(), bad_task(), good_task())
        print(f"    result: {r}")
    except ValueError as e:
        print(f"    ✗ 整个 gather 抛异常：{e}")
        print("    ★ 其他成功的任务结果【拿不到了】")

async def tolerant_mode():
    print("\n  加 return_exceptions=True：")
    r = await asyncio.gather(good_task(), bad_task(), good_task(), return_exceptions=True)
    for i, x in enumerate(r):
        if isinstance(x, Exception):
            print(f"    [{i}] X {type(x).__name__}: {x}")
        else:
              print(f"    [{i}] ok {x}")
    print("    ★ 成功的留下，失败的变成异常对象放在原位")
    
    
asyncio.run(default_behavior())
asyncio.run(tolerant_mode())