# coding=utf-8
import numpy
import time
from item_bought_history import *

t1 = time.time()
if False:
    a = items()
    a.set_information()
    a.save_history()
    f = open(gl.pickle_file, 'wb')
    pick = pickle.Pickler(f)
    pick.dump(a)
    f.close()
    del a
    del pick
f = open(gl.pickle_file, 'rb')
pick = pickle.Unpickler(f)
a = pick.load()
f.close()
del pick
a.load_history()
print 1,time.time()
b = a.user2item(12058626, False)
print a.itemid_dict[32567] in b[:, 0]  # 12068626 买的商品中是否有 32567
b = a.item2user(32567, False)
print a.userid_dict[12058626] in b[:, 0]  # 买了 32567的用户中是否有  用户 12068626
b = a.word2item(123950, False)  #
print a.itemid_dict[32567] in b[:, 0]  # 词123950的商品中 是否有 32567
print len(b) == 32
print len(a.class2item(311, False)) == 8895  # 类别311中是否有 8895 个商品
b = a.class2itemArray(311, False)
print b[a.itemid_dict[782028] - gl.itemIDStart]  # 782028 是否在 类别 311 中
