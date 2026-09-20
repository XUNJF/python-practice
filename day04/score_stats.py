
#练习1 成绩统计
scores = []
num = int(input("一共几个成绩："))
for i in range(num):
    score = float(input(f"请输入第{i+1}个成绩:"))
    scores.append(score)

print("平均分：", sum(scores)/len(scores)) 
print("最高分：", max(scores))
print("最低分：", min(scores))

