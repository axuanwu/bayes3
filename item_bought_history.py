# coding=utf-8
"""
功能：
1、有购买历史的商品的关联购买
2、无购买历史的商品的关联购买序列（冷启动）
"""
from imformation import known_information
import pickle
import numpy as np

# 继承information.known_information 类的信息
class items(known_information):
    def __init__(self):
        known_information.__init__(self)
        self.item_hot_pro = np.array([0.0] * 10)  # 商品购买热度
        self.item_relate = np.array([0.0] * 10)  # 商品购买数