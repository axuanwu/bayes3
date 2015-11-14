# coding=utf-8
import os
import numpy as np
import time

"""
对前两百的命中数进行统计
"""
__author__ = '01053185'
# 该部分的主要是直接使用达人的匹配数据进行关联结果
class score_txt():
    def __init__(self):
        self.matrix_item = np.zeros((90000, 3), int)
        self.data_dir = 'E:\\gitshell\\tianchi3'
        self.item_dict = {}
        self.ind1_dict = {}
        # 用于有无购买历史的划分
        self.history_dict = {}
        self.item_array = np.zeros((600000, 2))
        self.top_k_da = 100000
        self.item_dict2 = {}

    def read_jingyan(self):
        opath = "E:\\gitshell\\tianchi3\\dim_fashion_matchsets2.txt"
        Read_stream = open(opath, "r")
        i_record = 0
        pre_ind1 = -1
        for line_i in Read_stream:
            my_str = line_i.split("\t")
            # 商品 主序号  次序号
            self.matrix_item[i_record, :] = [int(my_str[2]), int(my_str[0]), int(my_str[1])]
            ind_str = self.item_dict.get(int(my_str[2]), '-1')
            #  商品字典
            if ind_str == '-1':
                self.item_dict[int(my_str[2])] = str(i_record)
            else:
                self.item_dict[int(my_str[2])] = ind_str + ',' + str(i_record)
            i_record += 1
            #  ind1 字典
            if i_record == 1:
                self.ind1_dict[int(my_str[0])] = 0
                pre_ind1 = int(my_str[0])
            elif pre_ind1 != int(my_str[0]):
                self.ind1_dict[int(my_str[0])] = i_record - 1
                pre_ind1 = int(my_str[0])

    def read_some(self):
        r_stream = open(os.path.join(self.data_dir, 'test_file.txt'), 'r')
        for line in r_stream:
            my_str = line.split('\t')
            self.history_dict[int(my_str[0])] = 1
        r_stream.close()
    # 输入item_id  输出搭配商品
    def associated_items(self, item_id):
        ind_str = self.item_dict.get(item_id, '')
        if len(ind_str) == 0:
            return []
        else:
            asso_array = []
            ind_str = ind_str.split(',')
            for ind in ind_str:
                ind2 = int(ind)
                temp_item = self.matrix_item[ind2, :]
                if temp_item[0] != item_id:
                    print
                id1 = temp_item[1]
                id2 = temp_item[2]
                start_i = self.ind1_dict[id1]
                while (self.matrix_item[start_i, 1] == id1):
                    if self.matrix_item[start_i, 2] != id2:
                        asso_array.append(self.matrix_item[start_i, 0])
                    start_i += 1
            return set(asso_array)  # 去重

    # 统计结果
    def score_it(self, result_file="fm_submissions21.txt"):
        self.read_jingyan()
        score_array = [0]*20  # 存储总的
        score_array1 = [0]*20  # 存储无购买历史的商品结果
        sum1 = 0
        i1 = 0
        score_array2 = [0]*20  # 存储有购买历史的商品结果
        sum2 = 0
        i2 = 0
        test_file = open(os.path.join(self.data_dir,result_file), 'r')
        i = 0
        sum0 = 0
        for line in test_file:
            i += 1
            my_str = line.strip().split(' ')
            item_id = int(my_str[0])
            relate_set = self.associated_items(item_id)
            sum0 += len(relate_set)
            iii = 0
            if self.history_dict.get(item_id,-1) == -1:
                i2 += 1
                sum2 += len(relate_set)
            else:
                i1 += 1
                sum1 += len(relate_set)
            my_str2 = my_str[1].split(',')
            for x in my_str2:
                if int(x) in relate_set:
                    score_array[int(iii/10)] += 1
                    if self.history_dict.get(item_id,-1) == -1:
                        score_array2[int(iii/10)] += 1
                    else:
                        score_array1[int(iii/10)] += 1
                iii += 1
        # print i, sum0, sum(score_array)
        print i, sum0, sum(score_array), score_array
        print i1, sum1, sum(score_array1), score_array1
        print i2, sum2, sum(score_array2), score_array2

        return score_array

    def item_hot2(self):
        # 读取文本分析中存储的商品顺序 确保商品存储位置完全一致
        r_stream = open(os.path.join(self.data_dir, 'my_item_hot.txt'), 'r')
        self.item_num = -1

        for line in r_stream:
            my_str = line.strip().split('\t')
            self.item_num += 1
            self.item_array[self.item_num, :] = [int(my_str[0]), int(my_str[1])]
        self.item_array = self.item_array[0:(self.item_num + 1), ]
        self.item_array[:, 1] = self.item_array[:, 1] / sum(self.item_array[:, 1])  # 记录次数 转为 记录概率
        for x in xrange(0, self.item_num + 1):
            self.item_dict2[int(self.item_array[x, 0])] = x

    def score_it2(self, result_file="fm_submissions2_tag_w.txt"):
        self.item_hot2()
        self.read_jingyan()
        score_array = [0] * 2000  # 存储总的
        score_array1 = [0] * 2000  # 存储无购买历史的商品结果
        sum1 = 0
        i1 = 0
        score_array2 = [0] * 2000  # 存储有购买历史的商品结果
        sum2 = 0
        i2 = 0
        test_file = open(os.path.join(self.data_dir, result_file), 'r')
        i = 0
        sum0 = 0
        step = 500
        a = 0  # 记录热度在10万以外的搭配商品数
        for line_s in test_file:
            if i % 100 == 0:
                print i, time.time()
            my_str = line_s.split('\t')
            item_id = int(my_str[0])
            pro_da_pei = np.array([0.0] * self.top_k_da)
            for x in xrange(1, self.top_k_da + 1):
                try:
                    pro_da_pei[x - 1] = float(my_str[x])
                except:
                    pro_da_pei[x - 1] = 0
            i += 1
            # orders = np.argsort() #降排序
            rank_0 = np.argsort(np.argsort(-pro_da_pei))
            relate_set = self.associated_items(item_id)
            sum0 += len(relate_set)
            if self.history_dict.get(item_id, -1) == -1:
                i2 += 1
                sum2 += len(relate_set)
            else:
                i1 += 1
                sum1 += len(relate_set)

            for item_id2 in relate_set:
                ind = self.item_dict2.get(item_id2, -1)
                if ind == -1 or ind >= self.top_k_da:
                    a += 1
                    continue  # 不在命中外围
                score_array[int(rank_0[ind] - 1) / step] += 1
                if self.history_dict.get(item_id, -1) == -1:
                    score_array2[int(rank_0[ind] - 1) / step] += 1
                else:
                    score_array1[int(rank_0[ind] - 1) / step] += 1
        # print i, sum0, sum(score_array)
        aaa = int(self.top_k_da/step)
        print i, sum0, sum(score_array), score_array[0:aaa]
        print i1, sum1, sum(score_array1), score_array1[0:aaa]
        print i2, sum2, sum(score_array2), score_array2[0:aaa]
        print a
        return score_array

if __name__ == "__main__":
    b = score_txt()
    b.read_some()
    b.score_it2("fm_submissions2_tag_w.txt")