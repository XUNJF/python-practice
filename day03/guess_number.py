# 第 3 天 · 练习 2：猜数字
# 程序想一个数字，让用户一直猜，直到猜对

num = 7

while True:
    m = int(input("猜一个数字："))
    if m == num:
        print("猜对了！")
        break
    elif m > num:
        print("大了")
    else:
        print("小了")
