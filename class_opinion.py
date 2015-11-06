# coding=utf-8
import os
import numpy as  np
import time

class class_gailv():

    def __init__(self):
        self.data_dir = 'E:\\gitshell\\tianchi3'

        # 类别
        self.dict_class = {}
        self.class_num = 0
        self.class_class = np.zeros((2, 2))

    def read_txt(self, filename="dim_items.txt"):
        # 读取商品的类别信息表
        r_path = os.path.join(self.data_dir, filename)
        r_stream = open(r_path, 'r')
        self.item_num = 0
        for line_i in r_stream:
            # if self.item_num % 100000 == 0:
            #     print self.item_num, time.time()
            my_str = line_i.strip('\n').split(" ")
            # 录入分类信息
            self.item_num += 1
            class_id = int(my_str[1])
            class_ind = self.dict_class.get(class_id, -1)
            if class_ind == -1:
                self.dict_class[class_id] = self.class_num
                self.class_num += 1

     # 统计 类类 关系
    def my_tongji2(self):
        # 统计过程由 sql sever 完成后存为class_class.txt 这里直接读取 # 检查完毕
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
        self.class_class[:, :] += 1.0 / self.class_num  #  加上一个较小的数 不会除零
        row_sum = self.class_class.sum(1)  # 按照行求和
        for ind1 in xrange(0, self.class_num):
            for ind2 in xrange(0, self.class_num):
                a = int(self.class_class[ind1, ind2])
                self.class_class[ind1, ind2] = self.class_class[ind1, ind2]/ row_sum[ind1]  # ind1 条件下 ind2 的概率

    def get_gailv(self, class_id1, class_id2):
        ind1 = self.dict_class.get(int(class_id1), -1)
        ind2 = self.dict_class.get(int(class_id2), -1)
        if ind1 == -1 or ind2 == -1:
            print "warning : something unexpected "
            return 0
        else:
            return self.class_class[ind1, ind2]
if __name__ == "__main__":
    a = class_gailv()
    a.read_txt()
    a.my_tongji2()
    a.get_gailv(288,516)