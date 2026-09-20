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
        