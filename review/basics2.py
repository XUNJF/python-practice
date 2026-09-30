import json

# ============================================================
# 任务 1：读 key 文件
# 要求：读 key_sf.txt，打印前 8 个字符
# ============================================================

with open("key_sf.txt", "r", encoding="utf-8") as f:
    key = f.read().strip()

print(key[:8])


# ============================================================
# 任务 2：存 JSON
# 要求：把下面的字典存成 data.json，中文不变形，缩进 2 格
# ============================================================

data = {"名字": "小明", "年龄": 25}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================
# 任务 3：average 函数
# 要求：传入一个数字列表，返回平均值
# 例：average([85, 92, 78]) → 85.0
# ============================================================

def average(nums):
    return sum(nums) / len(nums)


print(average([85, 92, 78]))


# ============================================================
# 任务 4：longest 函数
# 要求：传入一个字符串列表，返回最长的那个
# 例：longest(["cat", "elephant", "dog"]) → "elephant"
# 提示：先假设第一个最长，再一个一个比
# ============================================================

def longest(words):
    result = words[0]
    for w in words:
        if len(w) > len(result):
            result = w
    return result


print(longest(["cat", "elephant", "dog"]))


# ============================================================
# 任务 5：Counter 类
# 要求：
#   创建时接收一个名字
#   有个 count 属性，初始是 0
#   add()   → count 加 1
#   reset() → count 归零
#   show()  → 打印 "名字: 数字"
# ============================================================

class Counter:
    def __init__(self, name):
        self.name = name
        self.count = 0

    def add(self):
        self.count += 1

    def reset(self):
        self.count = 0

    def show(self):
        print(f"{self.name}: {self.count}")


# ============================================================
# 测试（上面的写完了再跑这一段）
# ============================================================

c = Counter("番茄")
c.add()
c.add()
c.show()          # 应该打印：番茄: 2

c.reset()
c.show()          # 应该打印：番茄: 0