contacts = {
    "张三": "1381525",
    "李四": "1399565"
}


while True:
    print("1. 查看全部")
    print("2. 添加联系人")
    print("3. 查找联系人")
    print("4. 删除联系人")
    print("5. 退出")
    num = int(input("请输入数字选择你的操作:"))
    
    if num == 1:
        for name in contacts: 
            print(f"{name}:{contacts[name]}")
            
    elif num == 2:
        name = input("请输入联系人姓名:")
        if name in contacts:
            choice = int(input("联系人已存在是否覆盖，是请输入1，否请输入2："))           
            if choice == 1:
                phone= input("请输入联系人电话:")
                contacts[name] = phone
                print("添加成功")
            elif choice == 2:
                print("未覆盖原有联系人")
            else:
                print("指令不正确")
        else:
            print("联系人不存在可以添加")
            phone= input("请输入联系人电话:")
            contacts[name] = phone
            print("添加成功")
    elif num == 3:
        name = input("请输入联系人姓名:")
        if name in contacts:
            print(f"查找成功{name}:{contacts[name]}")
        else:
            print("该联系人不存在")
    elif num == 4:
        name = input("请输入联系人姓名:")
        if name in contacts:
            del contacts[name]
            print("删除成功")
        else:
            print("该联系人不存在")
    elif num == 5:
        print("退出成功")
        break
    else:
        print("请输入1~5的数字在进行操作")


    
