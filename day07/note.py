# # 写文件
# with open("note.txt", "a", encoding = "utf-8") as f:
#     f.write("hello\n")
#     f.write("world\n")

# # 读文件
# with open("note.txt", "r", encoding = "utf-8") as f:
#     content = f.read()

# print(content.strip())

import json
contacts = {"张三":"14234", "李四":"72737"}

with open("note.txt", "w", encoding="utf-8") as f:
    json.dump(contacts, f, ensure_ascii=False, indent=2)
with open("note.txt", "r", encoding="utf-8") as f:
    contacts = json.load(f)
print(contacts)


