
def calculate(a, b, symbol):
    if symbol == "+":
        return a + b
    elif symbol == "-":
        return a - b
    elif symbol == "*":
        return a * b
    elif symbol == "/":
        if b == 0:
            return None 
        else:
            return a / b
    else:
        return None


r1 = calculate(7,6,"%")   
if r1 is not None:
    print(f"结果是：{r1}")   
else:
     print("计算出错了")


results = []
for i in range(3):
    r = calculate(10, i, "/")
    if r is not None:
        results.append(r)
print(results)