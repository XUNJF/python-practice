import time


def down_load(name, s):
    time.sleep(s)
    return f"{name} 完成（用了{s}秒"

start = time.time()

print(down_load("A", 1))
print(down_load("B", 1))
print(down_load("C", 1))

print(f"\n总共用了： {time.time() - start:.2f}秒")