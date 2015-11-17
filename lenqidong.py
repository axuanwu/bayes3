# coding=utf-8
import os
import numpy as np
import time
import gl

"""
由于购买记录访问比较频繁，本模块旨在录入商品并做进一步映射，实现更快的访问
用户id映射为 2000000+i(存储索引) 记为user_id'
商品id映射为 1000000+i(存储索引) 记为item_id'
同时也增加了 从 item_id 到 user 的快速访问通道
"""


class known_information():
    def __init__(self):
        self.user_num = 100
        self.item_num = 100
        self.record_num = 100
        self.userid_dict = {}  # 用户id 转化的映射字典
        self.itemid_dict = {}  # 商品id 转化字典
        self.user_item_array = np.zeros((self.record_num, 3), int)  # 第一列记录item_id'   第二列购买次数 第三列记录最后一次购买时间差(与第一天相比)
        self.item_user_array = np.zeros((self.record_num, 2), int)  # 第一列记录user_id'  第二列购买次数
        self.user_array = np.zeros((self.user_num, 2), int)  # 第一列user_item_array中的结束位置 第二列用户购买总数
        self.item_array = np.zeros((self.item_num, 4), int)  # 第一列item_user_array中的结束位置 第二列商品被数量 第三列为class_id 第四列 item_id
        self.item_word_list = []  # 按照 item_id' 存放数据
        pass

    def read_history(self):
        # 返回用户商品购买信息
        # 读取原始信息 并且构造商品、用户的映射字典
        # step1: 读取原始信息
        r_stream = open(gl.BoughtHistoryFile, 'r')
        temp_history_array = np.zeros((15000000, 3), int)  # 用户 商品 时间
        i_line = 0
        for line in r_stream:
            my_str = line.rstrip().split(",")
            for i in xrange(0, 3):
                temp_history_array[i_line, i] = int(my_str[i])
            i_line += 1
            if i_line == 10000:
                break
        r_stream.close()
        print time.time()
        temp_history_array = temp_history_array[0:i_line, ]
        # step2 : 构造用户 映射字典
        # 按照用户商品时间排序
        temp_history_array = sorted(temp_history_array, key=lambda l: [l[0], l[1]])
        # 统计用户购买次数
        temp_user_array = np.zeros((150*10000, 2), int)  # user_id , 购买商品数
        temp_user_array[0, ] = [temp_history_array[0, 0], 1]
        temp_dict = {}
        user_num = 1  # 用户数
        for i_num in xrange(1, i_line):
            if temp_history_array[i_num, 0] == temp_history_array[i_num - 1, 0]:
                # 用户相同
                if temp_history_array[i_num, 1] != temp_history_array[i_num - 1, 1]:
                    # 商品不同
                    temp_user_array[user_num-1, 1] += 1  # 购买+1
            else:
                temp_user_array[user_num, ] = [temp_history_array[i_num,0], 1]
                user_num += 1  # user数+1
        # 按照购买次数降序排序 用户id 重新映射
        temp_user_array = sorted(temp_user_array[0:user_num, ], key=lambda l: -l[1])
        for x in xrange(0, user_num):
            temp_dict[temp_user_array[x, 0]] = gl.userIdStart + x  # 现有item_id到 item_id' 映射
        self.userid_dict = temp_dict
        del temp_dict
        #  step3： 构造商品 映射字典
        #  按照商品 用户排序
        temp_history_array = sorted(temp_history_array, key=lambda l: [l[1], l[0]])
        temp_item_array = np.zeros((150*10000, 2), int)  # item_id , 购买用户数
        temp_dict = {}
        item_num = 1
        temp_item_array[0, ] = [temp_history_array[0, 1], 1]
        for i_num in xrange(1, i_line):
            if temp_history_array[i_num, 1] == temp_history_array[i_num-1, 1]:
                # 商品相同
                if temp_history_array[i_num, 0] != temp_history_array[i_num-1, 0]:
                    # 用户不同
                    temp_item_array[item_num-1] += 1  # 购买用户+1
            else:
                temp_item_array[item_num, ] = [temp_history_array[i_num, 1], 1]
                item_num += 1
        temp_item_array = sorted(temp_item_array[0:item_num, ], key=lambda l: -l[1])
        for x in xrange(0,item_num):
            temp_dict[temp_item_array[x, 0]] = x + gl.itemIDStart
        self.itemid_dict = temp_dict
        return temp_history_array

    def map(self):
        # 映射购买历史
        temp_history_array = self.read_history()
        (m, n) = temp_history_array.shape
        for x in xrange(0, m):
            temp_history_array[x,] = [self.userid_dict[temp_history_array[x, 0]],
                                      self.itemid_dict[temp_history_array[x, 1]],
                                      temp_history_array[x,2]]
        # 索引用户信息
        temp_history_array = sorted(temp_history_array, key=lambda l: [l[0], l[2]])  # 用户 时间 排序

        # 索引商品信息




if __name__ == "__main__":
    a = known_information()
    a.read_history
