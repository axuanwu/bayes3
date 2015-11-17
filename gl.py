# coding=utf-8
"""
全局变量
"""
import os
dataDir = "E:\\gitshell\\tianchi3"
userIdStart = 3000000  # 用户以2000000开始编号
itemIDStart = 2000000  # 商品以1000000开始编号
wordIdStart = 1000000
itemClassWordFile = os.path.join(dataDir, "dim_items.txt")  # 商品的类别，词组信息文件
BoughtHistoryFile = os.path.join(dataDir, "user_bought_history_o.txt")  # 购买记录
