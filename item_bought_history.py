# coding=utf-8
"""
功能：
1、有购买历史的商品的关联购买
2、无购买历史的商品的关联购买序列（冷启动）
"""
from information import known_information
import pickle
import numpy as np

# 继承information.known_information 类的信息
class items(known_information):


    def __init__(self):
        known_information.__init__(self)
        self.item_hot_pro = np.array([0.0] * 10)  # 商品购买热度
        self.item_relate = np.array([0.0] * 10)  # 商品购买数

    def set_information(self):
        self.map()
        self.map_word()

    def count_relate_num(self, item_id_bar, item_array):
        # 代完成
        """

        :rtype : self.item_num_history 长度的向量
        """
        a = np.array([0]*self.item_num_history)
        return a

    def item_relate_item(self, item_id, bar_mark=True):
        if not bar_mark:
            item_id = self.itemid_dict[item_id]
        a = np.array([0]*self.item_num_history)  # 有购买历史的商品的长度
        user_array = self.item2user(item_id, True)  #
        for user_id in user_array:
            item_array = self.user2item(user_id, True)
            a += self.count_relate_num(item_id, item_array)
        return a
