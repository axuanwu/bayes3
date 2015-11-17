# coding=utf-8
import math
import numpy as np
import os
import time
from pro_estimate2 import Pro_estimate
import sys


class WordOpinion():
    def __init__(self):
        self.data_dir = 'E:\\gitshell\\tianchi3'
        self.my_matrix = np.zeros((2, 2))  # 记录词到商品的概率对数
        # 词组
        self.word_num = 0
        self.dict_word = {}
        self.top_k_word = 15000  # 详细计算前20000的词组
        self.word_M = np.zeros((1000000, 2))  # 第一列 记录word_id  第二列 记录 概率
        self.word_item_array = [""] * 1000000  # 每个词被哪些商品使用
        self.word_word = np.zeros((3, 3))  # 统一记录真实概率
        # 需要预测的词组
        self.r_word_num = 0
        self.r_dict_word = {}
        self.r_word_M = np.zeros((80000, 2))  # 第一列词 第二列词的次数
        self.test_item = []
        # 商品
        self.dict_item = {}
        self.item_M = np.zeros((600000, 2), int)  # item_id  类别编号
        self.item_word_array = [""] * 600000
        self.item_num = 0
        # 概率优化模块
        self.pro_guji = Pro_estimate()
        # 只考虑 最热的 6万 商品
        self.item_top_k = 100000
        # 原始的搭配概率
        self.p_match = 0.0006  # 任意随机商品 搭配的概率
        self.num_word2 = 800

        pass

    def read_txt(self, filename="dim_items.txt"):
        # 读取商品的类别信息表
        r_path = os.path.join(self.data_dir, filename)
        r_stream = open(r_path, 'r')
        self.item_num = 0
        for line_i in r_stream:
            if self.item_num % 100000 == 0:
                print self.item_num, time.time()
            # 录入商品
            my_str = line_i.strip('\n').split(" ")
            self.dict_item[int(my_str[0])] = self.item_num
            self.item_M[self.item_num, :] = [my_str[0], int(my_str[1])]
            self.item_word_array[self.item_num] = my_str[2]
            self.item_num += 1
            # 录入不同的词组
            my_str2 = my_str[2].split(',')
            for x_word in my_str2:
                try:
                    word_id = int(x_word)
                except:
                    continue
                word_ind = self.dict_word.get(word_id, -1)
                if word_ind == -1:
                    self.dict_word[word_id] = self.word_num
                    self.word_M[self.word_num, :] = [word_id, 1]
                    # self.word_item_array[self.word_num] = my_str[0]  # 商品
                    self.word_num += 1
                else:
                    self.word_M[word_ind, 1] += 1
                    # self.word_item_array[word_ind] += ',' + my_str[0]  # 商品

        self.word_M = self.word_M[0:self.word_num, :]
        self.item_M = self.item_M[0:self.item_num, :]
        self.item_word_array = self.item_word_array[0:self.item_num]
        # self.word_item_array = self.word_item_array[0:self.word_num]
        # 根据热度排行对词进行重新排序
        order = np.argsort(-self.word_M[:, 1])
        self.word_M = self.word_M[order, :]
        # temp_a = self.word_item_array
        # for x in xrange(0, len(order)):
        # self.word_item_array[x] = temp_a[order[x]]
        for x in xrange(0, self.word_num):
            self.dict_word[int(self.word_M[x, 0])] = x
        r_stream.close()
        # # 转化word_M 第2 列 为概率对数：
        sum_word_num = sum(self.word_M[:, 1])
        self.word_M[:, 1] = self.word_M[:, 1] / sum_word_num


    def result_word(self, file_name='test_set.txt'):
        # 只对需要预测的商品进行计算 找出需要计算的词汇
        file_name = os.path.join(self.data_dir, file_name)
        r_stream = open(file_name, 'r')
        for line_i in r_stream:
            item_id = int(line_i.strip().split('\t')[-1])
            self.test_item.append(item_id)
            item_ind = self.dict_item.get(item_id, -1)
            if item_ind == -1:
                continue
            word_array = self.item_word_array[item_ind].split(',')
            for word_id in word_array:
                word_id = int(word_id)
                word_ind = self.r_dict_word.get(word_id, -1)
                if word_ind == -1:
                    self.r_dict_word[word_id] = self.r_word_num
                    self.r_word_M[self.r_word_num, :] = [word_id, 1]
                    self.r_word_num += 1
                else:
                    self.r_word_M[word_ind, 1] += 1
        r_stream.close()
        order = np.argsort(-self.r_word_M[0:self.r_word_num, 1])
        self.r_word_M = self.r_word_M[order, :]
        i_record = self.r_word_num
        for i in xrange(0, self.r_word_num):
            if self.r_word_M[i, 1] == 1:
                i_record = i
                print i_record
                break
        self.r_word_num = i_record
        self.r_word_M = self.r_word_M[0:i_record, :]


    # 统计词词关系 new 基于sql sever 处理过的文件开始统计 简化代码
    def my_tongji3(self):
        # split_ss = self.r_word_num
        temp_array = np.zeros((self.r_word_num + 1, self.top_k_word + 1))
        p_remain = sum(self.word_M[self.top_k_word:, 1])  # 残余项原始概率
        i_file = 0
        file_name = "word_word_pro"
        r_path = os.path.join(self.data_dir, "learn_wordstr_wordstr0.txt")
        r_stream = open(r_path, 'r')
        for wor_str in r_stream:
            my_str = wor_str.strip().split('\t')
            if my_str[0] == '' or my_str[1] == '':
                continue
            word_p = my_str[0].split(',')
            word_s = my_str[1].split(',')
            num = int(my_str[2])
            for word_id1 in word_p:
                word_ind1 = self.r_dict_word.get(int(word_id1), -1)  # 行号
                if word_ind1 == -1:
                    continue  # 非统计对象
                word_ind1 = min(word_ind1, self.r_word_num)
                for word_id2 in word_s:
                    word_ind2 = self.dict_word.get(int(word_id2), -1)
                    if word_ind2 == -1:
                        continue  # 非录入词
                    word_ind2 = min(word_ind2, self.top_k_word)
                    temp_array[word_ind1, word_ind2] += num  # word_ind 指示的词发生后其关联商品 为 含word_ind2的词 次数+1
        r_stream.close()
        for x in xrange(0, self.top_k_word):
            temp_array[:, x] += self.word_M[x, 1]  # 增加 一个未知事件 保证没有概率为0 的情况
        temp_array[:, self.top_k_word] += sum(self.word_M[self.top_k_word:, 1])
        # 求概率
        temp_array_sum = temp_array.sum(1)  # 按照行进行求和
        (row_num, col_num) = temp_array.shape
        o_stream = open(os.path.join(self.data_dir, "ceshi_tongji3.txt"), 'w')
        for i_col in xrange(0, col_num):
            if i_col % 200 == 0:
                print i_col, time.time()
            if i_col == self.top_k_word:
                p_pre = p_remain
            else:
                p_pre = self.word_M[i_col, 1]
            for i_row in xrange(0, row_num):
                a = temp_array[i_row, i_col]
                # temp_array[i_row, i_col] = temp_array[i_row, i_col]/temp_array_sum[i_row]
                temp_array[i_row, i_col] = self.pro_guji.get_pro_r(p_pre,
                                                                   temp_array[i_row, i_col],
                                                                   temp_array_sum[i_row])  # p n m
                if i_row == 1:
                    o_stream.write(str(p_pre) + '\t' + str(temp_array[i_row, i_col])
                                   + '\t' + str(a) + '\t' + str(temp_array_sum[i_row]) + '\n')
        # 静态存储
        o_stream.close()
        w_file = os.path.join(self.data_dir, file_name + str(i_file) + '.txt')
        w_stream = open(w_file, 'w')
        for i_row in xrange(0, row_num):
            my_str = ''
            for i_col in xrange(0, col_num - 1):
                my_str += str(math.log(temp_array[i_row, i_col])) + ','
            my_str += str(math.log(temp_array[i_row, col_num - 1])) + '\n'
            w_stream.writelines(my_str)
        w_stream.close()
        self.word_word = temp_array

    # 读取之前计算的词词关系
    def read_word_word(self):
        self.word_word = np.zeros((self.r_word_num + 1, self.top_k_word + 1))
        o_stream = open(os.path.join(self.data_dir, "word_word_pro0.txt"), 'r')
        i_line = 0
        for line in o_stream:
            my_str = line.strip().split(',')
            for x in xrange(0, self.top_k_word + 1):
                self.word_word[i_line, x] = math.exp(float(my_str[x]))  # 真概率
            i_line += 1
        o_stream.close()
        if i_line == (self.r_word_num + 1):
            print time.time(), "good"

    # 根据热度重组商品矩阵
    def read_item_hot(self, write=True):
        path = os.path.join(self.data_dir, 'my_item_hot.txt')
        nums_array = np.array([0] * self.item_num)
        r_stream = open(path, 'r')
        for line_i in r_stream:
            my_str = line_i.strip().split('\t')
            item_id = int(my_str[0])
            nums = int(my_str[-1])
            item_ind = self.dict_item[item_id]
            nums_array[item_ind] = nums
        r_stream.close()
        a = np.argsort(-nums_array)  # 降序排列
        self.item_M = self.item_M[a, :]
        for x in xrange(0, self.item_num):
            self.dict_item[int(self.item_M[x, 0])] = x
        # 记录商品热度
        if write:
            w_stream = open(os.path.join(self.data_dir, 'my_item_hot.txt'), 'w')
            nums_array = nums_array[a]
            for x in xrange(0, self.item_num):
                w_stream.writelines(str(int(self.item_M[x, 0])) + '\t' + str(nums_array[x]) + '\n')
            w_stream.close()

    # 对2000个词来 进行构造矩阵
    def dapei(self):
        # 每一个词后面 各个商品的发生几率
        self.my_matrix = np.zeros((self.num_word2, self.item_top_k))
        for word_ind1 in xrange(0, self.num_word2):
            temp_word = self.r_word_M[word_ind1,]
            print word_ind1
            # word_id1 = int(temp_word[0])
            self.my_matrix[word_ind1,] = self.get_pro_1(word_ind1,False)

    # 返回某一个词对每个 商品的搭配意见
    def get_pro_1(self, word_ind1, ab=True):
        if word_ind1 < self.num_word2 and ab:
            return self.my_matrix[word_ind1,]
        else:
            array0 = np.array([0.0] * (self.item_top_k))
            temp_word_pro2 = np.log(self.word_M[0:self.top_k_word + 1, 1])
            temp_word_pro2[self.top_k_word] = sum(self.word_M[self.top_k_word:, 1])
            temp_word_pro = np.log(self.word_word[word_ind1,])
            for item_ind in xrange(0, self.item_top_k):
                word_str = self.item_word_array[item_ind]
                if word_str == "":  # 没有任何词语
                    continue
                word_str = word_str.split(',')
                word_num2 = 0
                for word_id2 in word_str:
                    word_ind2 = self.dict_word.get(int(word_id2), -1)
                    if word_ind2 == -1:
                        continue
                    word_ind2 = min(word_ind2, self.top_k_word)
                    array0[item_ind] += temp_word_pro[word_ind2] - temp_word_pro2[word_ind2]
                    word_num2 += 1
                array0[item_ind] = array0[item_ind]/word_num2
            return array0

    # 得到某一个词的搭配商品
    def get(self, item_id):
        yyy = np.array([0.0] * self.item_top_k)
        item_ind = self.dict_item[item_id]
        word_str = self.item_word_array[item_ind]
        if len(word_str) == 0:
            return yyy
        word_str_array = word_str.split(',')
        aaa = 1
        for word_id in word_str_array:
            try:
                word_id2i = int(word_id)
            except:
                continue
            word_ind1 = self.r_dict_word.get(word_id2i, -1)
            if word_ind1 == -1:
                continue  # 非统计对象
            word_ind1 = min(word_ind1, self.r_word_num)
            yyy += self.get_pro_1(word_ind1)  # word_word 记录的是 真实概率
            aaa += 1
        yyy = yyy/aaa
        b = max(yyy)
        yyy = np.exp(yyy - b)  # 最大值化为一
        return yyy

    def write_result(self):
        file_name1 = os.path.join(self.data_dir, 'fm_submissions2_tag_w.txt')  # word 意见
        w_stream1 = open(file_name1, 'w')
        iii = -1
        t_b = time.time()
        for item_id in self.test_item:
            iii += 1
            if iii % 100 == 0 or time.time() - t_b > 100:
                t_b = time.time()
                print iii, t_b
            pro_gailv = self.get(item_id)
            w_stream1.writelines(str(item_id) + '\t')
            for item_ind in xrange(0, self.item_top_k - 1):
                w_stream1.writelines(str(pro_gailv[item_ind]) + '\t')
            w_stream1.writelines(str(pro_gailv[self.item_top_k - 1]) + '\n')
        w_stream1.close()


if __name__ == "__main__":
    a = WordOpinion()
    a.read_txt()
    a.result_word()
    print 1
    # a.my_tongji3()  # 统计 词词 关系
    a.read_word_word()
    print 2
    a.read_item_hot()
    print 3
    a.dapei()  #
    print 4
    a.write_result()

