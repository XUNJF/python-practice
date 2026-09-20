# fruits = ["苹果", "香蕉", "橙子"]
# numbers = [3, 1, 4, 1, 5]
# mixed = ["张三", 25, 3.14, True]


# fruits = ["苹果", "香蕉", "橙子"]
# print(fruits[0])
# print(fruits[1])
# print(fruits[2]) 
# print(fruits[-1])    #-1是最后一个，-2是倒数第二个...


# fruits = ["苹果", "香蕉"]
# fruits.append("橙子")        # 往后加一个 → ["苹果", "香蕉", "橙子"]
# fruits.remove("香蕉")        # 删掉指定的 → ["苹果", "橙子"]
# print(len(fruits))           # 2，长度
# print("苹果" in fruits)      # True，判断在不在里面
# print(fruits[0])             # 取第一个
# fruits[0] = "梨"             # 直接改

# for fruit in fruits:    #遍历
#     print(fruit)

# for i in range(len(fruits)):
#     print(i, fruits[i])



# #练习1 成绩统计
# scores = []
# num = float(input("一共几个成绩："))
# for i in range(num):
#     score = int(input(f"请输入第{i+1}个成绩:"))
#     scores.append(score)

# print("平均分：", sum(scores)/num)  #num 最好改正len(scores)
# print("最高分：", max(scores))
# print("最低分：", min(scores))



#练习2 购物清单
things = ["香蕉","pingguo"]

while True:
    print("1. 查看清单")
    print("2. 添加商品")
    print("3. 删除商品")
    print("4. 退出")
    i = int(input("选择操作："))
    if i == 1:
        for j in range(len(things)):
            print(f"{j+1}.{things[j]}")
        print()
    elif i == 2:
        thing = input("请输入商品名：")
        things.append(thing)
    elif i == 3:
        thing = input("请输入要删除的商品名：")
        if thing in things:
            things.remove(thing)
            print("删除成功")
        else:
            print("列表没有该商品")
    elif i == 4:
        print("退出成功")
        break
    else:
        print("请输入1~4")
        

