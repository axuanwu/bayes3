# coding=utf-8
import os
import numpy as np
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
        pass

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
    def score_it(self, result_file="fm_submissions.txt"):
        self.read_jingyan()
        score_array = [0]*20
        test_file = open(os.path.join(self.data_dir,result_file), 'r')
        for line in test_file:
            my_str = line.strip().split(' ')
            item_id = int(my_str[0])
            relate_set = self.associated_items(item_id)
            iii = 0
            my_str2 = my_str[1].split(',')
            for x in my_str2:
                if int(x) in relate_set:
                    score_array[int(iii/10)] += 1
                iii += 1
        return score_array

if __name__ == "__main__":
    b = score_txt()
    print b.score_it('fm_submissions21.txt')