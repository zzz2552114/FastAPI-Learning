def generator():
    a = 1
    b = 1
    while 1 :
        c = a
        a = b
        b = c + b
        yield a
# 这里要注意yield的妙用！可以暂停函数等下次再访问的时候从yield后面继续进行，已yield位置为周期起点
feb = generator()
for i in feb:
    if i > 10000:
        break
    print(i)
