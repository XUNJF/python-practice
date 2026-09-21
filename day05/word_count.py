#练习一
counts = {}
words = input("请输入一句话：").split()

for word in words:
    if word in counts:
        counts[word] += 1
    else:
        counts[word] = 1

for key, value in counts.items():
    print(f"{key}:{value}")
        
