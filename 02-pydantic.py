from pydantic import BaseModel

class User(BaseModel): # 这里实际上是类的继承，继承了BaseModel类
    name: str
    age: int
    family : list[str] = ['dad','mom','self']
user1 = User(name='John',age=35)
# 注意这里只能用关键字传参
# print(user1.name)
# print(user1.age)
# print(user1.family)

user1_dict = user1.model_dump()
# 这个方法要背一下，把熟悉改成字典
print(user1_dict)
user1_json = user1.model_dump_json()
#转JSON
print(user1_json)

# 当然也可以直接由字典生成一个类实例
user2 = User(**user1_dict)
print(user2 == user1) # True