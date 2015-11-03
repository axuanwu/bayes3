# coding=utf-8
__author__ = '01053185'
"""
该代码实现功能：
1.测试集 与 学习集合的划分
2.测试集的输入文件构造
3.构造学习集的输入文件
"""
import os
import random

class StepOne():
    def __init__(self):
        self.data_dir_in = 'E:\\gitshell\\tianchi2'  # 输入文件夹
        self.data_dir_out = 'E:\\gitshell\\tianchi3'  # 输出文件夹

    # 搭配关系重新表示
    def my_ShangPinGuanLian(self):
        # 两个ID， id1 原文件中表示所在行编号  id2 表示以;分割所在的顺序号
        # 所以 id1相同 id2不同 表示配对商品
        path = os.path.join(self.data_dir_in, "dim_fashion_matchsets.txt")
        opath = os.path.join(self.data_dir_out, "dim_fashion_matchsets2.txt")
        read_stream = open(path, 'r')
        write_stream = open(opath, 'w')
        for line in read_stream:
            aaa = line.rstrip().split(' ')
            key = int(aaa[0])
            item_list = aaa[1].rstrip().split(';')
            for i in xrange(0, len(item_list)):
                temp_str = str(key) + '\t' + str(i) + '\t'
                item_list2 = item_list[i].split(',')
                for temp_item in item_list2:
                    write_stream.writelines(temp_str + temp_item + '\n')
        read_stream.close()
        write_stream.close()

    def data_partition(self, file1="dim_fashion_matchsets2.txt"):
        # 以0.03的概率随机抽取测试样本
        read_stream = open(os.path.join(self.data_dir_out, file1), 'r')
        learn_set_stream = open(os.path.join(self.data_dir_out, 'learn_set.txt'), 'w')
        test_set_stream = open(os.path.join(self.data_dir_out, 'test_set.txt'), 'w')
        random.seed("I LOVE U")
        for line in read_stream:
            if random.random() < 0.03:
                test_set_stream.write(line)
            else:
                learn_set_stream.write(line)
        test_set_stream.close()
        learn_set_stream.close()

    # 词组搭配的学习文本构建
    def data_partition2(self, file1="wordstr_wordstr0.txt"):
        read_stream = open(os.path.join(self.data_dir_in, file1), 'r')  # 需要分割的文件
        test_set_stream = open(os.path.join(self.data_dir_out, 'test_set.txt'), 'r')  # 需要过滤掉的测试集合文件
        learn_set_stream = open(os.path.join(self.data_dir_out, 'learn_wordstr_wordstr0.txt'), 'w')  # 目标结果文件
        test_dic = {}
        for line in test_set_stream:
            my_line = line.rstrip().split('\t')
            test_dic[int(my_line[-1])] = 1  # 最后一个为商品id
        test_set_stream.close()
        for line in read_stream:
            my_line = line.rstrip('\r').rstrip('\n').split('\t')
            if test_dic.get(int(my_line[0]), 0)+test_dic.get(int(my_line[1]), 0) == 0:  # 都不在测试集中
                learn_set_stream.write(my_line[4]+'\t'+my_line[5]+'\t1\n')
        read_stream.close()
        learn_set_stream.close()

    #  构造需要测试集的商品对应用户输入文件
    def file_to_test(self):
        test_set_stream = open(os.path.join(self.data_dir_out, 'test_set.txt'), 'r')  # 需要过滤掉的测试集合文件
        test_dic ={}
        for line in test_set_stream:
            my_line = line.rstrip().split('\t')
            test_dic[int(my_line[-1])] = 1  # 最后一个为商品id
        test_set_stream.close()
        # 过滤用户购买历史
        bought_history = open(os.path.join(self.data_dir_in, "user_bought_history1.txt"),'r')
        item_user = []
        for line in bought_history:
            my_line = line.strip().split(',')
            if 0 != test_dic.get(int(my_line[1]), 0):
                item_user.append((my_line[1], my_line[0]))
        bought_history.close()
        item_user = sorted(item_user, key=lambda x:x[0])
        test_file = open(os.path.join(self.data_dir_out, "test_file.txt"), 'w')
        for x in item_user:
            test_file.write(x[0]+'\t'+x[1]+'\n')
        test_file.close()

if __name__ == "__main__":
    a = StepOne()
    a.my_ShangPinGuanLian()
    a.data_partition()
    a.data_partition2()
    a.file_to_test()

