def full_name(first_name : str, last_name :str):
    full_name = first_name.title() + " " + last_name.title()
    return full_name

def name_with_age(name : str, age : int):
    result = name + "is this old" + str(age)
    return result

# from typing import List,Any,Tuple,Set,Dict
# python 3.10 以上，这些东西都没必要再从typing库里导入了，直接用原生的
# Any除外

# list[int | float]即可，tuple要逐个指定类型，dict传两个参数
def get_items( items : tuple[float | int ,...] ):
    for i in items:
        print(i**2)
lst = (2,4,6,9,2.5,1.5,7)
get_items(lst)

# 下面的例子告诉我们，类也可以作为类型提示
class Person:
    def __init__(self, name: str):
        self.name = name

def get_person_name(one_person: Person):
    return one_person.name

p = Person('John')
print(get_person_name(p))
