def simple_wrapper(func):
    def inner():
        print("Before calling")
        print(func())
        print("After calling")
    return inner
def hello():
    return "Hi!"
'''我来解释一下这些代码
首先，simple_wrapper(func)这个函数，目的就是：它可以返回一个函数，让一个变量绑定这个函数！
如果不用simple_wrapper, 直接上inner，那
(1) hello = inner(hello)是获取确定的返回值
(2) hello = inner又没有传func的参。所以两者显然都不行
故而 def simple_wrapper是有必要的，里面再定义一个函数，就可以返回内部的函数，而内部的函数里调用了传给simple的函数
实现了对hello的装饰，这样再用hello = simple_wrapper(hello)对 hello 覆盖赋值，就完全实现了装饰
'''
# 手工装饰
hello = simple_wrapper(hello)
# hello()

# 这里就可以上装饰器了
@simple_wrapper
def hey():
    return "Hey!"
# hey()
# 实际上就是把hey变成装饰器里面那个函数，然后hey本身会被传到装饰器里作为参数

# 但是注意下面的例子又有一些不同
# 先写一个手动装饰
def wrapper(times,func):
    def inner(*args, **kwargs): # 注意哦，这里*args表示，先把所有参数打包成args元组，再用*解包
        print("Before calling")
        for i in range(times):
            print(f'that is {i}')
        result = func(*args, **kwargs)
        print("After calling")
        return result
    return inner

def f(a,b):
    return f'a+b = {a+b}'

f = wrapper(8,f)
# print(f(7,8))

# 这里是两层函数，但是如果要用装饰器的话就必须用三层函数
def outter_wrapper(times):
    def inner_wrapper(func):
        def inner(*args, **kwargs):
            print("Before calling")
            for i in range(times):
                print(f'that is {i}')
            result = func(*args, **kwargs)
            print("After calling")
            return result
        return inner
    return inner_wrapper

@outter_wrapper(times=3)
def f2(a,b):
    return f'a+b = {a+b}'
print(f2(10,20))

# 这里就必须用三层def来定义装饰器，其中第一层是用来

# 下面介绍一下多层装饰器
def deco1(func):
    print("deco1 包装")
    def wrapper1(*args, **kwargs):
        print("wrapper1 进入")
        result = func(*args, **kwargs)
        print("wrapper1 退出")
        return result
    return wrapper1

def deco2(func):
    print("deco2 包装")
    def wrapper2(*args, **kwargs):
        print("wrapper2 进入")
        result = func(*args, **kwargs)
        print("wrapper2 退出")
        return result
    return wrapper2

@deco1
@deco2
def target():
    print("执行 target")
target()
#这里target先变成内部又target的wrapper2，再变成内部有wrapper2的wrapper1

class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"第 {self.count} 次调用")
        return self.func(*args, **kwargs)

@CountCalls
def hi():
    print("Hi")

hi()
hi()
# 这里是类包装，相当于hi = CountCalls(hi)覆盖
# 学到这应该就够了