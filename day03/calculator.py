# 第 3 天 · 练习 1：计算器
# 输入两个数字和一个运算符，输出计算结果

num1 = float(input("请输入第一个数："))
num2 = float(input("请输入第二个数："))
symbol = input("请输入运算符：")

if symbol == "+":
    print("结果是：", num1 + num2)
elif symbol == "-":
    print("结果是：", num1 - num2)
elif symbol == "*":
    print("结果是：", num1 * num2)
elif symbol == "/":
    if num2 == 0:
        print("除数不能为 0")
    else:
        print("结果是：", num1 / num2)
else:
    print("不支持的运算符")
