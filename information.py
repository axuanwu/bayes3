# coding=utf-8
import os
import numpy as np
import time
import datetime
import gl
import pickle
# import StringIO
"""
由于购买记录访问比较频繁，本模块旨在录入商品并做进一步映射，实现更快的访问
用户id映射为 2000000+i(存储索引) 记为user_id'
商品id映射为 1000000+i(存储索引) 记为item_id'
同时也增加了 从 item_id 到 user 的快速访问通道
"""


def datediff(a, b):
    a1 = time.strptime(str(a), "%Y%m%d")
    b1 = time.strptime(str(b), "%Y%m%d")
    a1 = datetime.datetime(*a1[0:3])
    b1 = datetime.datetime(*b1[0:3])
    return (b1 - a1).days


class known_information():

    def __init__(self):
        self.user_num = 100
        self.item_num = 100
        self.item_num_history = 100 # 购买历史中 商品数
        self.record_num = 100
        self.userid_dict = {}  # 用户id 转化的映射字典
        self.itemid_dict = {}  # 商品id 转化字典
        self.user_item_array = np.zeros((self.record_num, 2), int)  # 第一列记录item_id'   第二列记录购买时间差(与第一天相比)
        self.item_user_array = np.zeros((self.record_num, 2), int)  # 第一列记录user_id'  第二列购买次数
        self.user_array = np.zeros((self.user_num, 2), int)  # 第一列user_item_array中的结束位置 第二列用户购买商品数
        self.item_array = np.zeros((self.item_num, 4),int)  # 第一列item_user_array中的结束位置 第二列商品购买用户数量 第三列为class_id 第四列 item_id
        self.item_word_list = []  # 按照 item_id' 存放数据 (item_id',word_str)
        # 词组  的 相关变量
        self.word_num = 100  # 词的数量
        self.record_word = 100  # 商品-词组对 的数量
        self.wordid_dict = {}
        self.word_array = np.zeros((self.word_num, 3), int)  # word_id ,结束位置, 商品数
        self.word_item_array = np.zeros((self.record_word, 1), int)  # itemid’
        # 类别 的 相关信息
        self.class_num = 100
        self.classid_dict = {}  # 词id的映射表
        self.class_array = np.zeros((self.class_num, 3), int)  # 存储结束位置 商品个数 购买用户数（按商品去重）
        self.class_item_array = np.zeros((self.item_num, 1), int)  # itemid’

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
            # if line == 100000:
            #     break
        self.record_num = i_line
        r_stream.close()
        print time.time()
        temp_history_array = temp_history_array[0:i_line, ]
        # step2 : 构造用户 映射字典
        # 按照用户商品排序
        a = np.argsort(temp_history_array[:, 1])  # np.argsort 是一个稳定排序算法
        temp_history_array = temp_history_array[a, ]
        a = np.argsort(temp_history_array[:, 0], kind='mergesort')
        temp_history_array = temp_history_array[a, ]
        # temp_history_array = sorted(temp_history_array, key=lambda l: [l[0], l[1]])
        # 统计用户购买次数
        temp_user_array = np.zeros((150 * 10000, 2), int)  # user_id , 购买商品数
        temp_user_array[0, ] = [temp_history_array[0, 0], 1]
        temp_dict = {}
        user_num = 1  # 用户数
        for i_num in xrange(1, i_line):
            if temp_history_array[i_num, 0] == temp_history_array[i_num - 1, 0]:
                # 用户相同
                if temp_history_array[i_num, 1] == temp_history_array[i_num - 1, 1]:
                    # 商品不同
                    pass
                temp_user_array[user_num - 1, 1] += 1  # 购买+1
            else:
                temp_user_array[user_num,] = [temp_history_array[i_num, 0], 1]
                user_num += 1  # user数+1
        # 按照购买次数降序排序 用户id 重新映射
        self.user_num = user_num
        a = np.argsort(-temp_user_array[:, 1])
        temp_user_array = temp_user_array[a, ]
        for x in xrange(0, user_num):
            temp_dict[temp_user_array[x, 0]] = gl.userIdStart + x  # 现有item_id到 item_id' 映射
        self.userid_dict = temp_dict
        del temp_dict
        # step3： 构造商品 映射字典
        #  按照商品 用户排序
        a = np.argsort(temp_history_array[:, 0])
        temp_history_array = temp_history_array[a, ]
        a = np.argsort(temp_history_array[:, 1], kind='mergesort')
        temp_history_array = temp_history_array[a, ]
        # temp_history_array = sorted(temp_history_array, key=lambda l: [l[1], l[0]])
        temp_item_array = np.zeros((150 * 10000, 2), int)  # item_id , 购买用户数
        temp_dict = {}
        item_num = 1
        temp_item_array[0, ] = [temp_history_array[0, 1], 1]
        for i_num in xrange(1, i_line):
            if temp_history_array[i_num, 1] == temp_history_array[i_num - 1, 1]:
                # 商品相同
                if temp_history_array[i_num, 0] != temp_history_array[i_num - 1, 0]:
                    # 用户不同
                    temp_item_array[item_num - 1, 1] += 1  # 购买用户+1
            else:
                temp_item_array[item_num, ] = [temp_history_array[i_num, 1], 1]
                item_num += 1
        self.item_num = item_num
        self.item_num_history = item_num
        a = np.argsort(- temp_item_array[0:item_num, 1])
        temp_item_array = temp_item_array[a, ]
        # temp_item_array = sorted(temp_item_array[0:item_num, ], key=lambda l: -l[1])
        for x in xrange(0, item_num):
            temp_dict[temp_item_array[x, 0]] = x + gl.itemIDStart
        self.itemid_dict = temp_dict
        return temp_history_array

    def map(self):
        """
        物品索引
        用户索引
        购买时间转化
        商品的用户去重
        """
        # 映射购买历史
        temp_history_array = self.read_history()
        (m, n) = temp_history_array.shape
        for x in xrange(0, m):
            temp_history_array[x, ] = [self.userid_dict[temp_history_array[x, 0]],
                                      self.itemid_dict[temp_history_array[x, 1]],
                                      temp_history_array[x, 2]]
        # 索引用户信息
        a = np.argsort(temp_history_array[:, 2])
        temp_history_array = temp_history_array[a, ]
        a = np.argsort(temp_history_array[:, 0], kind='mergesort')  # 稳定排序
        temp_history_array = temp_history_array[a, ]
        # temp_history_array = sorted(temp_history_array, key=lambda l: [l[0], l[2]])  # 用户 时间 排序
        self.user_array = np.zeros((self.user_num, 2), int)
        self.user_item_array = np.zeros((self.record_num, 2), int)  # 第一列记录item_id'    第二列记录购买时间差(与第一次购买相比)
        user_before = temp_history_array[0, 0]
        day_start = temp_history_array[0, 2]
        i_num = 1
        self.user_item_array[0, ] = [temp_history_array[0, 1], 0]
        for i_record in xrange(1, self.record_num):
            if temp_history_array[i_record, 0] == user_before:
                i_num += 1
            else:
                self.user_array[user_before - gl.userIdStart,] = [i_record, i_num]
                day_start = temp_history_array[i_record, 2]
                user_before = temp_history_array[i_record, 0]
                i_num = 1
            self.user_item_array[i_record, ] = [temp_history_array[i_record, 1],
                                                datediff(day_start, temp_history_array[i_record, 2])]
        self.user_array[user_before - gl.userIdStart,] = [self.record_num, i_num]
        # 索引商品信息
        a = np.argsort(temp_history_array[:, 0])
        temp_history_array = temp_history_array[a, ]
        a = np.argsort(temp_history_array[:, 1], kind='mergesort')
        temp_history_array = temp_history_array[a, ]
        # temp_history_array = sorted(temp_history_array[:, 0:2], key=lambda l: [l[1], l[0]])  # 商品 用户 排序
        self.item_user_array = np.zeros((self.record_num, 2), int)  # 第一列记录user_id'  第二列购买次数
        self.item_array = np.zeros((100*10000, 4), int)  # 第一列item_user_array中的结束位置 第二列商品被数量 第三列为class_id 第四列 item_id
        temp_array = sorted(self.itemid_dict.iteritems(), key=lambda l: l[1])  # 按照映射位置对字典排序
        item_before = temp_history_array[0, 1]
        user_before = temp_history_array[0, 0]
        self.item_user_array[0,] = [temp_history_array[0, 0], 1]
        i_num = 1
        i_record_num = 1
        for i_record in xrange(1, self.record_num):
            if temp_history_array[i_record, 1] == item_before:
                if temp_history_array[i_record, 0] != user_before:
                    user_before = temp_history_array[i_record, 0]
                    i_num += 1
                    i_record_num += 1
                    self.item_user_array[i_record_num - 1, 0] = temp_history_array[i_record, 0]
                self.item_user_array[i_record_num - 1, 1] += 1  # 购买次数+1
            else:
                ind = item_before - gl.itemIDStart
                self.item_array[ind, 0:4] = [i_record_num, i_num, 0, temp_array[ind][0]]
                i_num = 1
                i_record_num += 1
                [user_before, item_before] = temp_history_array[i_record, 0:2]
                self.item_user_array[i_record_num - 1, ] = [temp_history_array[i_record, 0], 1]
        ind = item_before - gl.itemIDStart
        self.item_array[ind, 0:4] = [i_record_num, i_num, 0, temp_array[ind][0]]
        self.item_user_array = self.item_user_array[0:i_record_num, ]
        # item_array 中 加入类别、词组信息 以及 历史中不存在的商品
        read_stream = open(gl.itemClassWordFile, 'r')  # 商品的类别，词组信息文件
        temp_word_list = []
        for line in read_stream:
            my_str = line.rstrip().split(" ")
            item_id = int(my_str[0])
            class_id = int(my_str[1])
            if self.itemid_dict.get(item_id, -1) == -1:
                itemid_bar = self.item_num + gl.itemIDStart
                self.itemid_dict[item_id] = itemid_bar
                self.item_array[self.item_num, 0:4] = [i_record_num, 0, class_id, item_id]
                self.item_num += 1
                temp_word_list.append((itemid_bar, my_str[2]))
            else:
                itemid_bar = self.itemid_dict[item_id]
                self.item_array[itemid_bar - gl.itemIDStart, 2] = class_id
                temp_word_list.append((itemid_bar, my_str[2]))
        read_stream.close()
        self.item_array = self.item_array[0:self.item_num, ]
        self.item_word_list = sorted(temp_word_list, key=lambda l: l[0])

    def map_word(self):
        # 索引词组到商品的信息
        # step1：拆分商品 词组 记录
        temp_array = np.zeros((1000*10000, 2), int)  # 商品词的记录
        i_num = 0
        for tuple in self.item_word_list:
            item_id_bar = tuple[0]
            word_str_array = tuple[1].split(',')
            if len(word_str_array) < 2:
                continue
            for word_id in word_str_array:
                temp_array[i_num, ] = [item_id_bar, int(word_id)]
                i_num += 1
        temp_array = temp_array[0:i_num, ]
        self.record_word = i_num
        a = np.argsort(temp_array[:, 1])  # 按照词组排序
        temp_array = temp_array[a, ]
        # step2： 统计词组的热度 并编制映射关系
        word_array = np.zeros((500*10000, 2), int)  # 词关系 记录  word_id,item, num
        i_word_num = 1
        word_array[i_word_num-1, 0:2] = [temp_array[0, 1], 1]
        for x in xrange(1, i_num):
            if word_array[i_word_num-1, 0] == temp_array[x, 1]:
                word_array[i_word_num-1, 1] += 1
            else:
                i_word_num += 1
                word_array[i_word_num-1, ] = [temp_array[x, 1], 1]
        word_array = word_array[0:i_word_num, ]
        a = np.argsort(- word_array[:, 1])  # 按照次序降序排列
        word_array = word_array[a, ]
        x = 0
        for x in xrange(0, i_word_num):
            # if word_array[x, 1]==1:
            #     break  # 不映射只有一个商品的词
            self.wordid_dict[word_array[x, 0]] = x
        self.word_num = i_word_num  # 收录词的个数
        # step3： 重新映射 词组 商品数据
        for x in xrange(0, self.record_word):
            temp_array[x, 1] = self.wordid_dict[temp_array[x, 1]]
        a = np.argsort(temp_array[:, 1])
        temp_array = temp_array[a, ]  # 重新排序
        # 索引词
        self.word_item_array = np.zeros((self.record_word, 1), int)
        self.word_array = np.zeros((self.word_num, 3), int)
        word_dict_array = sorted(self.wordid_dict.iteritems(),key=lambda l: l[1])
        word_before = temp_array[0, 1]
        i_num = 1
        for i_record in xrange(1, self.record_word):
            if temp_array[i_record, 1] == word_before:
                # 词相同
                i_num += 1
            else:
                self.word_array[word_before, 0:3] = [word_dict_array[word_before][0], i_record, i_num]   # word_id ,结束位置, 商品数
                i_num = 1
                word_before = temp_array[i_record, 1]
        self.word_array[word_before, 0:3] = [word_dict_array[word_before][0], self.record_word, i_num]
        self.word_item_array[0:self.record_word,0] = temp_array[:, 0]

    def map_class(self):
        temp_array = np.zeros((self.item_num, 2), int)  # 第2列class_id 第1列 item_id'
        temp_array[:, 0] = np.arange(0, self.item_num) + gl.itemIDStart
        temp_array[:, 1] = self.item_array[:, 2]  # class_id
        a = np.argsort(temp_array[:, 1], kind='mergesort')  # 稳定排序
        temp_array[:, :] = temp_array[a, ]
        self.class_array = np.zeros((500, 3), int)  # 类别的结束位置 类别的商品数 类别的购买数
        class_before = temp_array[0, 1]
        i_num = 1
        i_num2 = self.item_array[temp_array[0, 0]-gl.itemIDStart, 1]  # 用户数
        self.class_num = 1
        self.classid_dict[class_before] = self.class_num - 1
        for x in xrange(1, self.item_num):
            if class_before == temp_array[x, 1]:
                i_num += 1
                i_num2 += self.item_array[temp_array[x, 0]-gl.itemIDStart, 1]  # 用户数
            else:
                self.class_array[self.class_num-1, ] = [x, i_num, i_num2]
                class_before = temp_array[x, 1]  # 类别变更
                i_num = 1  # 重新计数
                i_num2 = self.item_array[temp_array[x, 0]-gl.itemIDStart, 1]  # 用户数
                self.class_num += 1  # 类别数 +1
                self.classid_dict[class_before] = self.class_num -1  # 映射类别
        self.class_array[self.class_num-1, ] = [class_before, i_num, i_num2]
        self.class_array = self.class_array[0:self.class_num, ]
        self.class_item_array = np.zeros((self.item_num, 1), int)
        self.class_item_array[:, 0] = temp_array[:, 0]  # 赋值

    def class2item(self, class_id, bar_mark=True):
        if not bar_mark:
            class_id = self.classid_dict.get(class_id,-1)
            if class_id == -1:
                return []
        temp = self.class_array[class_id]
        return np.reshape(self.class_item_array[(temp[0]-temp[1]):temp[0], 0], (temp[1], 1))

    def class2itemArray(self, class_id, bar_mark=True):
        #  返回某一个类别的商品 0,1 bool向量组，并去除没有购买历史的商品
        a = np.array([False]*self.item_num_history)
        if not bar_mark:
            class_id = self.classid_dict.get(class_id, -1)
            if class_id == -1:
                return a
        temp = self.class_array[class_id]
        b = self.class_item_array[(temp[0]-temp[1]):temp[0], 0]  # 所有商品
        for x in b:
            item_ind = x - gl.itemIDStart
            if item_ind < self.item_num_history:
                a[item_ind] = True  # 有购买历史的商品
        return a

    def word2item(self, word_id, bar_mark=True):
        #  返回某一个词组的 所有商品 item_id'
        if not bar_mark:
            word_id = self.wordid_dict.get(word_id, -1)
            if word_id == -1:
                print "非录入词组"
                return []
        temp = self.word_array[word_id]
        return np.reshape(self.word_item_array[(temp[1]-temp[2]):temp[1], 0],(temp[2],1))

    def word2itemArray(self,word_id, bar_mark=True):
        #  返回某一个词组的商品 0,1 向量组，并去除没有购买历史的商品
        a = np.array([False]*self.item_num_history)
        if not bar_mark:
            word_id = self.wordid_dict.get(word_id, -1)
            if word_id == -1:
                print "非录入词组"
                return a
        temp = self.word_array[word_id]
        for x in xrange(temp[1]-temp[2],temp[1]):
            item_ind = self.word_item_array[x, 0] - gl.itemIDStart
            if item_ind < self.item_num_history:
                a[item_ind] = True
        return a

    def item2user(self, item_id, bar_mark=True):
        """
        根据商品id 返回购买用户

        :type item_id: 可以为 item_id_bar的向量， 或者单个的 item_id 或者 item_id_bar
        """
        try:
            b = len(item_id)
            if b == 1:
                item_id = item_id[0]
        except:
            pass
        try:
            b = len(item_id)  # item_id_bar 数组
            temp = self.item_array[item_id-gl.itemIDStart, ]
            m = sum(temp[:, 1])
            temp_iua = np.zeros((m,2), int)
            i_start = 0
            for x in xrange(0, temp.shape[0]):
                temp_iua[i_start:(i_start + temp[x, 1]), 0:2] = self.item_user_array[(temp[x, 0]-temp[x, 1]):temp[x, 0], 0:2]
                i_start += temp[x, 1]
            a = np.argsort(temp_iua[:, 0])
            temp_iua = temp_iua[a, ]
            i_temp = 0
            i_temp2 = 1
            while i_temp2 < m:
                if temp_iua[i_temp2,0] == temp_iua[i_temp, 0]:
                    temp_iua[i_temp, 1] += temp_iua[i_temp2,1]
                    i_temp2 += 1
                else:
                    i_temp += 1
                    temp_iua[i_temp, ] = temp_iua[i_temp2, ]
                    i_temp2 += 1
            return temp_iua[0:(i_temp+1), ]
        except:
            if not bar_mark:
                item_id = self.itemid_dict.get(item_id, -1)
                if item_id == -1:
                    print "非录入商品"
                    return []
            temp = self.item_array[item_id-gl.itemIDStart, ]
            if temp[1] == 0:
                return []
            else:
                return self.item_user_array[(temp[0]-temp[1]):temp[0], ]

    def item2class(self, item_id, bar_mark=True):
        # 返回商品类别 class_id_bar
        if not bar_mark:
            item_id = self.itemid_dict.get(item_id, -1)
            if item_id == -1:
                print "非录入商品"
                return []
        class_id_nobar = self.item_array[item_id-gl.itemIDStart, 2]
        return class_id_nobar

    def item2word(self, item_id, bar_mark = True):
        # 返回wordid_bar的数组
        if not bar_mark:
            item_id = self.itemid_dict.get(item_id, -1)
            if item_id == -1:
                print "非录入商品"
                return []
        word_str = self.item_word_list[item_id-gl.itemIDStart][1]
        word_str = word_str.split(',')
        length = len(word_str)
        word_array = np.array([0]* length)
        for x in xrange(0, length):
            word_array[x] = self.wordid_dict[int(word_str[x])]
        return word_array

    def item_inverse(self,item_id):
        # 从item_id'逆转换到 原始的 item_id
        return self.item_array[item_id-gl.itemIDStart, 3]

    def user2item(self,user_id, bar_mark = True):
        if not bar_mark:
            user_id = self.userid_dict.get(user_id, -1)
            if user_id == -1:
                print "非录入用户"
                return[]
        temp = self.user_array[user_id-gl.userIdStart]
        return self.user_item_array[(temp[0]-temp[1]):temp[0],]

    def save_history(self):
        # 写 user_item_array
        o_stream = open(gl.user_item_array_file, 'w')
        (m, n) = self.user_item_array.shape
        for i in xrange(0, m):
            o_stream.write(str(self.user_item_array[i, 0])+'\t'+str(self.user_item_array[i,1])+'\n')
        o_stream.close()
        self.user_item_array = np.zeros((2, 2), int)
        #  写item_user_array_file
        (m, n) = self.item_user_array.shape
        o_stream = open(gl.item_user_array_file, 'w')
        for i in xrange(0, m):
            o_stream.write(str(self.item_user_array[i, 0])+'\t'+str(self.item_user_array[i,1])+'\n')
        o_stream.close()
        self.item_user_array = np.zeros((2, 2), int)

    def load_history(self):
        # user_item_array
        o_stream = open(gl.user_item_array_file, 'r')
        self.user_item_array = np.zeros((self.record_num,2), int)
        i_line = 0
        for line in o_stream:
            my_str = line.rstrip().split("\t")
            self.user_item_array[i_line, ] = [int(my_str[0]), int(my_str[1])]
            i_line += 1
        o_stream.close()
        self.user_item_array = self.user_item_array[0:i_line, ]
        #  item_user_array
        o_stream = open(gl.item_user_array_file, 'r')
        self.item_user_array = np.zeros((self.record_num, 2), int)
        i_line = 0
        for line in o_stream:
            my_str = line.rstrip().split("\t")
            self.item_user_array[i_line, ] = [int(my_str[0]), int(my_str[1])]
            i_line += 1
        o_stream.close()
        self.item_user_array = self.item_user_array[0:i_line, ]


if __name__ == "__main__":
    t1 = time.time()
    a = known_information()
    a.map()  # 商品信息 购买历史 信息完成录入并 映射
    print time.time()
    a.map_word()
    print time.time()
    a.map_class()
    print time.time()
    print time.time() - t1
    # 以下为几个简单的测试
    b = a.user2item(12058626, False)
    print a.itemid_dict[32567] in b[:, 0]  # 12068626 买的商品中是否有 32567
    b = a.item2user(32567, False)
    print a.userid_dict[12058626] in b[:, 0]  # 买了 32567的用户中是否有  用户 12068626
    b = a.word2item(123950, False)  #
    print a.itemid_dict[32567] in b[:, 0]  # 词123950的商品中 是否有 32567
    print len(a.class2item(311,False)) == 8918  # 类别311中是否有 8918个商品
    b = a.class2itemArray(311, False)
    print b[a.itemid_dict[782028] - gl.itemIDStart]  # 782028 是否在 类别 311 中
    # 持久存储。dumps
    a.save_history()
    f = open(gl.pickle_file, 'wb')
    pick = pickle.Pickler(f)
    pick.dump(a)
    f.close()
    pick.clear_memo()
    del pick
    del a

    # 读取 pickle
    f = open(gl.pickle_file, 'rb')
    pick = pickle.Unpickler(f)
    a = pick.load()
    f.close()
    del pick
    a.load_history()
    # 以下为几个简单的测试
    b = a.user2item(12058626, False)
    print a.itemid_dict[32567] in b[:, 0]  # 12068626 买的商品中是否有 32567
    b = a.item2user(32567, False)
    print a.userid_dict[12058626] in b[:, 0]  # 买了 32567的用户中是否有  用户 12068626
    b = a.word2item(123950, False)  #
    print a.itemid_dict[32567] in b[:, 0]  # 词123950的商品中 是否有 32567
    print time.time()-t1
