# coding=utf-8
"""
全局变量
"""
import os
dataDir = "E:\\gitshell\\tianchi3"
userIdStart = 2000000  # 用户以2000000开始编号
itemIDStart = 1000000  # 商品以1000000开始编号
wordIdStart = 4000000
itemClassWordFile = os.path.join(dataDir, "dim_items.txt")  # 商品的类别，词组信息文件
BoughtHistoryFile = os.path.join(dataDir, "user_bought_history_o.txt")  # 购买记录
pickle_file = os.path.join(dataDir, "information.pkl")  # 商品的类别，词组信息文件
weight_path = os.path.join(dataDir, "次序关联.txt".decode("utf8"))  # 权重文件
testFile = os.path.join(dataDir, 'test_set.txt')  # 记录待预测商品的文件
resultFile = os.path.join(dataDir, 'fm_submissions21.txt')