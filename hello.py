# 输入输出
# name = input("请输入你的名字：")
# print("你好，" + name)
# age = int(input("请输入你的年龄："))
# print("我的年龄是：" ,age)


#if语句
# score = 85 
# if score >= 90:
#     print("优秀")
# elif score >= 60:
#     print("及格")
# else:
#     print("不及格")


# for循环（左闭右开）
# for i in range(5):
#     print(i)


# #练习1
# num1 = float(input("请输入第一个数："))
# num2 = float(input("请输入第二个数："))
# symbol = input("请输入运算符：")
# if symbol == "+":
#     print("结果是：", num1+num2)
# elif symbol == "-":
#     print("结果是：", num1-num2)
# elif symbol == "*":
#     print("结果是：", num1*num2)
# elif symbol == "/":
#     if num2 == 0:
#         print("不支持除法")
#     else:
#         print("结果是：", num1/num2)
# else:
#    print("不支持的运算符")


# #练习2
# num = 7
# i = 1
# while i == 1:
#     m = int(input("猜一个数字："))
#     if m == num:
#         i = 0
#         print("猜对了！")
#     elif m > num:
#         print("大了")
#     else:
#         print("小了")

##练习2 （版本二更好的写法）
# num = 7
# while True:
#     m = int(input("猜一个数字："))
#     if m == num:
#         print("猜对了！")
#         break          # 直接跳出循环
#     elif m > num:
#         print("大了")
#     else:
#         print("小了")
    

# #练习3


    
for i in range(1, 10):
    for j in range(1,i+1):
        print(f"{j} * {i} = {j * i}",end = "\t")
    print()

