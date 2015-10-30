# -*- coding: utf-8 -*-
# created by axuanwu 2015.1.25
# key word: hash  count
import numpy as np
import math


def getseed(str1):
    """

    :param str1: 词条的utf8形式
    :return: 词条的hash指纹 256的位随机数
    """
    h = 0
    for x in str1:
        if ord(x) > 256:
            h <<= 12
            h += ord(x)
        else:
            h <<= 6
            h += ord(x)
    while (h >> 256) > 0:
        h = (h & (2 ** 256 - 1)) ^ (h >> 256)  # 数字不能太大
    return h


class MCard():
    def __init__(self):
        self.M_num = 8
        self.N_max = 16777216
        self.nummax2 = 24
        self.MCARD = [0]
        self.Opath = ""
        self.index = [0] * 8
        self.__keys = ['first_NULL']
        self.i_key = 1  # 新增元素增加在位置 i_key 处
        self.index2 = [0] * 8

    def get_keys(self, iii=-1):
        if iii == -1:
            return self.__keys[1:]
        else:
            return self.__keys[iii]

    def getindex(self, str1, for_up=False):
        # 获取 词条的 8个随机位置
        seed = getseed(str1)
        for n in range(0, self.M_num):
            a = 0
            k = (n + 1)
            seed1 = seed
            if (seed >> 64) < 0:
                seed1 = seed * (n + 15048796327)
            while seed1 > 0:
                a ^= (seed1 & (self.N_max - 1)) + k
                a = ((a << k) & (self.N_max - 1)) | (a >> (self.nummax2 - k))  # 左循环移位
                seed1 >>= self.nummax2
            if for_up:
                self.index2[n] = a
            else:
                self.index[n] = a

    def update_card(self, str1, num=1):
        """
        :param str1: 词的utf-8编码形式
        :param num: 该词需要增加的value值
        """
        if self.read_card(str1, True) == 0:
            # 新词
            for iii in self.index:
                if self.MCARD[iii] == 0:
                    self.MCARD[iii] = self.i_key
            if self.i_key % 10000 == 0:
                print self.i_key
            self.i_key += 1
            self.__keys.append(str1)

    def read_card(self, str1, for_up=False):
        """
        :param str1: 词的utf-8编码形式
        :return: 输出该次条对应的value值
        """
        if for_up:
            for i in xrange(0, 10):  # 最多尝试10次
                i_str1 = str1 + str(i)
                if i > 5:
                    print i
                self.getindex(i_str1)
                aaa = min(self.MCARD[self.index])
                if aaa == 0:
                    return 0
            return -1
        else:
            for i in xrange(0, 10):  # 最多连续处理碰撞10次
                i_str1 = str1 + str(i)
                self.getindex(i_str1)
                aaa = max(self.MCARD[self.index])
                if aaa == 0:  # 不存在
                    return 0
                elif aaa < self.N_max:
                    if str1 == self.__keys[aaa]:
                        return aaa
            # print ("warning : bad case happened , card array maybe too short when update " + str1) # hash 桶太少
            return 0

    def setbase(self, num1=16777216, num2=8):
        """

        :param num1: 数组长度参数
        :param num2: 每个词条对应的hash位置数
        """
        self.nummax2 = int(math.ceil(math.log(num1, 2)))
        self.N_max = 2 ** self.nummax2  # self.nummax2 2的N次方
        self.M_num = num2
        self.index = [0] * num2
        self.index2 = [0] * num2

    def set_card(self, kk=-1, dd=8):
        """

        :param kk:  数组长度参数 -1表示取之前定义值
        """
        if -1 == kk:
            self.MCARD = np.repeat(0, self.N_max)
            return 0
            s1 = input('do you want to reset MCARD to zeros,all memory will be lost [y/n]:')
            if s1 == 'y':
                self.MCARD = np.repeat(0, self.N_max)
            else:
                print("no reset")
        else:
            self.setbase(kk, dd)
            self.MCARD = np.repeat(0, 2 ** self.nummax2)

    def record_num(self):

        """
        :return: 返回字典词条数量
        """
        return self.i_key - 1

    def card_test(self):
        """

        计算hash碰撞指数
        """
        aaa = self._record
        bbb = self.N_max
        ccc = 0
        for i in self.MCARD:
            ccc += int(i > 0)
        ddd = self.M_num
        print math.log(1.0 * ccc / bbb, 10) * ddd, math.log((1.0 * aaa * ddd - ccc) / ccc, 10) * ddd


