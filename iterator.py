class itermodel:
    def __init__(self,a):
        self.a = a
    def __iter__(self):
        return self
    def __next__(self):
        if (self.a > 100):
            raise StopIteration
        self.a += 1
        return self.a
it = itermodel(66)
for i in it:
    print(i)
# 这个itermodel是一个迭代器类，it是迭代器，也是可迭代对象
# 在for i in it的时候会首先调用一下__iter__方法，获得返回值(可迭代对象)
# 然后再不断进行调用__next__