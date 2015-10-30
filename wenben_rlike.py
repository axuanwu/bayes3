# coding=utf-8
import math

__author__ = '01053185'
import numpy as np
import os
import time
from pro_estimate2 import Pro_estimate


class most_like():

    def __init__(self):
        self.data_dir = 'E:\\gitshell\\tianchi2'
        # 词组
        self.word_num = 0
        self.dict_word = {}
        self.top_k_word = 20000  # 详细计算前20000的词组
        self.word_M = np.zeros((1000000, 2))  # 第一列 记录word_id  第二列 记录 概率对数
        self.word_item_array = [""] * 1000000  # 每个词被哪些商品使用
        self.word_word = np.zeros((3, 3))
        # 需要预测的词组
        self.r_word_num = 0
        self.r_dict_word = {}
        self.r_word_M = np.zeros((80000, 2))
        self.test_item = []
        # 商品
        self.dict_item = {}
        self.item_M = np.zeros((600000, 2), int)  # item_id  类别编号
        self.item_word_array = [""] * 600000
        self.item_num = 0
        # 类别
        self.class_M = np.zeros((3000000, 2))  # 类别id  类别商品计数/ 概率对数
        self.dict_class = {}
        self.class_num = 0
        self.class_class = np.zeros((2, 2))
        # 原始人工经验
        # self.matrix_item = np.zeros((10000000,3))
        # 概率优化模块
        self.pro_guji = Pro_estimate()
        # 只考虑 最热的 6万 商品
        self.item_top_k = 60000
        # 原始的搭配概率
        self.p_match = 0.0006  # 任意随机商品 搭配的概率
        pass

    def read_txt(self, filename="dim_items.txt"):
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
            # 录入分类信息
            class_id = int(my_str[1])
            class_ind = self.dict_class.get(class_id, -1)
            if class_ind == -1:
                self.dict_class[class_id] = self.class_num
                self.class_M[self.class_num, :] = [class_id, 1]
                self.class_num += 1
            else:
                self.class_M[class_ind, 1] += 1
        self.class_M = self.class_M[0:self.class_num, :]
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
        self.word_M[:, 1] = np.log(self.word_M[:, 1] / sum_word_num)
        # 转化word_M 第2 列 为概率对数：
        sum_class_num = sum(self.class_M[:, 1])
        self.class_M[:, 1] = np.log(self.class_M[:, 1] / sum_class_num)

    def result_word(self, file_name='test_items2.txt'):
        # 找出需要计算的词汇
        file_name = os.path.join(self.data_dir, file_name)
        r_stream = open(file_name, 'r')
        for line_i in r_stream:
            item_id = int(line_i.strip())
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
                break
        self.r_word_num = i_record
        self.r_word_M = self.r_word_M[0:i_record, :]

    # 返回一个词的所有 商品
    def get_item_array(self, word_id):
        word_ind = self.dict_word.get(word_id, -1)
        item_array = []
        if word_ind == -1:
            return item_array
        else:
            item_str = self.word_item_array[word_ind].split(',')
            for item in item_str:
                item_array.append(int(item))
        return item_array

     # 统计 类类 关系
    def my_tongji2(self):
        # 统计结果由 sql sever 完成后存为txt 这里直接读取 # 检查完毕
        r_path = os.path.join(self.data_dir, "class_class.txt")
        r_stream = open(r_path, 'r')
        self.class_class = np.zeros((self.class_num, self.class_num))
        for line in r_stream:
            my_str = line.strip().split('\t')
            class_ind1 = self.dict_class[int(my_str[0])]
            class_ind2 = self.dict_class[int(my_str[1])]
            num = int(my_str[2])
            self.class_class[class_ind1, class_ind2] += num
        r_stream.close()
        row_sum = self.class_class.sum(1)  # 按照行求和
        # all_num = 6 # 商品总数
        # self.class_class[class_ind1, class_ind2] 存储 id1 类别 后面搭配 id2 类别的概率
        w_path1 = open(os.path.join(self.data_dir, "class_class1.txt"), 'w')
        w_path2 = open(os.path.join(self.data_dir, "class_class2.txt"), 'w')
        w_path3 = open(os.path.join(self.data_dir, "class_class3.txt"), 'w')
        for ind1 in xrange(0, self.class_num):
            p_pre = np.exp(self.class_M[ind1, 1])  # 原假设： ind2 发生的概率
            w_path3.writelines(str(p_pre) + '\t')
            for ind2 in xrange(0, self.class_num):
                p_pre = np.exp(self.class_M[ind2, 1])  # 原假设： ind2 发生的概率
                if ind2 == self.class_num - 1:
                    w_path1.writelines(str(self.class_class[ind1, ind2]) + '\n')
                else:
                    w_path1.writelines(str(self.class_class[ind1, ind2]) + '\t')
                self.class_class[ind1, ind2] = self.pro_guji.get_pro_r(p_pre,
                                                                       self.class_class[ind1, ind2],
                                                                       row_sum[ind1])  # ind1 条件下 ind2 的概率
                if ind2 == self.class_num - 1:
                    w_path2.writelines(str(self.class_class[ind1, ind2]) + '\n')
                else:
                    w_path2.writelines(str(self.class_class[ind1, ind2]) + '\t')
        w_path1.close()
        w_path2.close()
        w_path3.close()

    # 统计词词关系 new 基于sql sever 处理过的文件开始统计 简化代码
    def my_tongji3(self):
        split_ss = self.r_word_num
        temp_array = np.zeros((self.r_word_num + 1, self.top_k_word + 1))
        p_remain = sum(np.exp(self.word_M[self.top_k_word:, 1]))  # 残余项原始概率
        i_file = 0
        file_name = "word_word_pro"
        r_path = os.path.join(self.data_dir, "wordstr_wordstr.txt")
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
        # 求概率
        temp_array_sum = temp_array.sum(1)  # 按照行进行求和
        (row_num, col_num) = temp_array.shape
        for i_col in xrange(0, col_num):
            if i_col % 200 == 0:
                print i_col, time.time()
            if i_col == self.top_k_word:
                p_pre = p_remain
            else:
                p_pre = np.exp(self.word_M[i_col, 1])
            for i_row in xrange(0, row_num):
                temp_array[i_row, i_col] = \
                    self.pro_guji.get_pro_r(p_pre,
                                            temp_array[i_row, i_col],
                                            temp_array_sum[i_row])  # p n m
        # 静态存储
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
        path = os.path.join(self.data_dir, 'dim_items2.txt')
        nums_array = np.array([0] * self.item_num)
        r_stream = open(path, 'r')
        for line_i in r_stream:
            my_str = line_i.strip().split(' ')
            item_id = int(my_str[0])
            nums = int(my_str[3])
            item_ind = self.dict_item[item_id]
            nums_array[item_ind] = nums
        r_stream.close()
        a = np.argsort(-nums_array)
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


    # 搭配算法 主进程
    def da_pei(self):
        file_name = os.path.join(self.data_dir, 'fm_submissions2_tag.txt')
        w_stream = open(file_name, 'w')
        iii = -1
        for item_id in self.test_item:
            iii += 1
            if iii % 100 == 0:
                print time.time(), iii
            item_ind = self.dict_item[item_id]
            word_str = self.item_word_array[item_ind]
            class_id = self.item_M[item_ind, 1]  # 类别编号
            class_ind = self.dict_class[class_id]  # 类别索引
            # item_id == self.class_M[item_ind,0]
            temp_result_array = np.zeros((self.item_num, 2))  # 第一列记录词组的意见，第二列记录类别的意见 概率乘 化作 加
            class_pro = np.log(self.class_class[class_ind, :])  # 搭配时 该商品类别到各个类别的概率
            class_pro2 = self.class_M[:, 1]  # 不搭配时 该商品类别到各个类别的概率
            temp_word_pro = np.array([0.0] * (self.top_k_word + 1))  # 该商品词组到各个词组的概率
            word_num = 0
            word_str_array = word_str.split(',')
            # 获得该商品后 其他商品的输出概率
            for word_id in word_str_array:
                try:
                    word_id2i = int(word_id)
                except:
                    continue
                word_ind1 = self.r_dict_word.get(word_id2i, -1)
                if word_ind1 == -1:
                    continue  # 非统计对象
                word_ind1 = min(word_ind1, self.r_word_num)
                temp_word_pro += np.log(self.word_word[word_ind1, :])  # word_word 记录的是 真实概率
                word_num += 1
            if word_num == 0:
                temp_word_pro = self.word_M[:, 1]
            else:
                temp_word_pro *= (1.0 / word_num)  # 搭配 平均词意见
            temp_word_pro2 = self.word_M[:, 1]  # 不搭配 意见
            for item_ind in xrange(0, self.item_top_k):
                word_str = self.item_word_array[item_ind]
                class_id = self.item_M[item_ind, 1]
                class_ind00 = self.dict_class[int(class_id)]
                temp_result_array[item_ind, 1] = class_pro[class_ind00] - class_pro2[class_ind00]  # 其exp 为搭配是 不搭配的倍数
                if word_str == "":
                    continue
                word_str = word_str.split(',')
                word_num2 = 0
                for word_id2 in word_str:
                    word_ind2 = self.dict_word.get(int(word_id2), -1)
                    if word_ind2 == -1:
                        continue
                    word_ind2 = min(word_ind2, self.top_k_word)
                    temp_result_array[item_ind, 0] += temp_word_pro[word_ind2] - temp_word_pro2[word_ind2]
                    word_num2 += 1
                if word_num2 == 0:
                    temp_result_array[item_ind, 0] = 0
                else:
                    temp_result_array[item_ind, 0] *= (1.0 / word_num2)
            a = temp_result_array[:, 0] + temp_result_array[:, 1]  # 类别的意见， 加上词的意见
            my_order = np.argsort(-a)  # 降序排序 并输出
            # 找出前6百个 按照热度进行排名 将 前 200 个 写入文件
            top_top_k = 400  # 重要参数
            temp_rrr = np.zeros((top_top_k, 2))
            for i in xrange(0, top_top_k):
                temp_rrr[i, :] = [self.item_M[my_order[i], 0], my_order[i]]
            my_order = np.argsort(temp_rrr[:, 1])  # 按照序号排名  即热度
            result_str = str(item_id) + ' ' + str(int(temp_rrr[my_order[0], 0]))
            for i in xrange(1, 200):
                result_str += ',' + str(int(temp_rrr[my_order[i], 0]))
            w_stream.writelines(result_str + '\n')
        pass

    # 仅仅计算出所有结果前6万商品的搭配结果
    # 加入了 原始的搭配概率 0.006，在 搭配中由于这一直大家相同，所以无关紧要。
    # 这次会计算出前6万的搭配概率，供 my_python2 做 进一步筛查
    def da_pei2(self):
        file_name = os.path.join(self.data_dir, 'fm_submissions2_tag_m.txt')
        w_stream = open(file_name, 'w')
        iii = -1
        for item_id in self.test_item:
            iii += 1
            if iii % 100 == 0:
                print time.time(), iii
            item_ind = self.dict_item[item_id]
            word_str = self.item_word_array[item_ind]
            class_id = self.item_M[item_ind, 1]  # 类别编号
            class_ind = self.dict_class[class_id]  # 类别索引
            # item_id == self.class_M[item_ind,0]
            temp_result_array = np.zeros((self.item_num, 2))  # 第一列记录词组的意见，第二列记录类别的意见 概率乘 化作 加
            class_pro = np.log(self.class_class[class_ind, :])  # 搭配时 该商品类别到各个类别的概率
            class_pro2 = self.class_M[:, 1]  # 不搭配时 该商品类别到各个类别的概率对数
            temp_word_pro = np.array([0.0] * (self.top_k_word + 1))  # 该商品词组发生后各个词组的概率
            word_num = 0
            word_str_array = word_str.split(',')
            # 获得该商品后 其他商品的输出概率
            for word_id in word_str_array:
                try:
                    word_id2i = int(word_id)
                except:
                    continue
                word_ind1 = self.r_dict_word.get(word_id2i, -1)
                if word_ind1 == -1:
                    continue  # 非统计对象
                word_ind1 = min(word_ind1, self.r_word_num)
                temp_word_pro += np.log(self.word_word[word_ind1, :])  # word_word 记录的是 真实概率
                word_num += 1
            if word_num == 0:
                temp_word_pro = self.word_M[:, 1]
            else:
                temp_word_pro *= (1.0 / word_num)  # 搭配 平均词意见
            temp_word_pro2 = self.word_M[:, 1]  # 不搭配 意见
            for item_ind in xrange(0, self.item_top_k):
                word_str = self.item_word_array[item_ind]
                class_id = self.item_M[item_ind, 1]
                class_ind00 = self.dict_class[int(class_id)]
                temp_result_array[item_ind, 1] = class_pro[class_ind00] - class_pro2[class_ind00]  # 其exp 为搭配是 不搭配发生的倍数
                if word_str == "":
                    continue
                word_str = word_str.split(',')
                word_num2 = 0
                for word_id2 in word_str:
                    word_ind2 = self.dict_word.get(int(word_id2), -1)
                    if word_ind2 == -1:
                        continue
                    word_ind2 = min(word_ind2, self.top_k_word)
                    temp_result_array[item_ind, 0] += temp_word_pro[word_ind2] - temp_word_pro2[word_ind2]
                    word_num2 += 1
                if word_num2 == 0:
                    temp_result_array[item_ind, 0] = 0
                else:
                    temp_result_array[item_ind, 0] *= (1.0 / word_num2)
            a = temp_result_array[:, 0] + temp_result_array[:, 1]  # 类别的意见， 加上词的意见 a元素 中存储的是
            pro_a = self.p_match * np.exp(a) / (self.p_match * np.exp(a) + (1 - self.p_match) * 1)  # 得到各个商品 的概率
            # my_str00 = ""
            w_stream.writelines(str(item_id) + '\t')
            for item_ind in xrange(0, self.item_top_k):
                if item_ind != (self.item_top_k - 1):
                    w_stream.writelines(str(round(pro_a[item_ind], 9)) + '\t')
                else:
                    w_stream.writelines(str(round(pro_a[item_ind], 9)) + '\n')
        w_stream.close()


if __name__ == "__main__":
    a = most_like()
    a.read_txt()
    a.result_word()
    print 1
    a.my_tongji2()  # 统计 类类 关系
    # # a.my_tongji3()  # 统计 词词 关系
    # a.read_word_word()
    # print 2
    # a.my_tongji2()  # 统计 类类 关系
    # a.read_item_hot()
    # a.da_pei2()  #
    # print 3
    # # a.get_item_array(171811)

