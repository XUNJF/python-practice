def max_of_two(a,b):
    return max(a,b)

print(max_of_two(3, 7))  

def average(numbers):
    return sum(numbers)/len(numbers)

print(average([85, 92, 78])) 

def is_even(n):
    if n % 2 == 1:
        return False
    elif n % 2 == 0:
        return True
    else:
        return "不是整数"

print(is_even(4))               
print(is_even(7))   