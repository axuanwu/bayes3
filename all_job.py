# coding=utf-8
__author__ = '01053185'
from wenben_rlike import most_like
from my_python2 import READ_Bought_History
import time

a = most_like()
a.read_txt()
a.result_word()
print 1
# a.my_tongji3()  # 统计 词词 关系
a.read_word_word()
print 2
a.my_tongji2()  # 统计 类类 关系
a.read_item_hot()
a.da_pei2()  #
del a

a = READ_Bought_History()
a.set_weight()
a.my_test()
print time.time(), 0
a.read_history()
print time.time(), 1
# a.item_hot()
a.item_hot2()  # 保证排序和wenben_rlike相同，热度降序
print time.time(), 2
a.read_class_id()
print time.time(), 3
# a.class_item_hot()  # 商品顺序改变 或者 第一次计算  需要运行
a.read_write_class_item_hot('r')  # 运行class_item_hot 时，无参数 自动记录，否则 填写 ‘r’ 为参数读取之前的结果
print time.time(), 4
print time.time(), 5
a.calculate_all2()
print time.time(), 6