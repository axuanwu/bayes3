# coding=utf-8
__author__ = '01053185'
import os
import time
import datetime
import math
from class_opinion import class_gailv
import numpy as np

import pro_estimate2 as pro_es2



class READ_Bought_History():
    def __init__(self):
        self.data_dir = 'E:\\gitshell\\tianchi3'
        # self.data_dir_new =
        self.user_dict = {}
        self.user_num = -1
        self.record_num = -1  # 记录最大编号 +1 为购买记录数
        self.user_array = np.zeros((2000000, 2), int)  # 记录 购买行为的 起末位置
        self.user_item_array = np.zeros((20000000, 2), int)
        # 商品热度统计数据
        self.item_num = -1  # 记录最大编号 +1为商品数
        self.item_dict = {}
        self.item_array = np.zeros((2000000, 2))  # 商品id， 商品数/概率
        self.item_user_list = []
        # 商品分类信息
        self.item_class = np.zeros([0] * 20)  # item_id 到 class_id 的映射
        self.class_dict = {}  # class_id 到 class_ind 的 映射
        self.class_num = -1  # 记录最大编号 +1为分类数
        # 热度排行初过滤参数  只对最畅销的 n 个商品进行精细计算
        self.top_k = 100000
        self.simple = True
        # 分类别关联性 商品热度统计
        self.num_k = 5  # 邻近的num_k个自身算第一个 被认为有关联
        self.like_matrix = np.zeros((10, 10), int)  # 存储不同分类下的
        # self.matrix = np.zeros((self.top_k+1,self.class_num+1), int)
        # 需要测试的数据组
        self.test_list = []
        # 关联商品的热度分布
        self.temp_item_array_hot = np.array([0] * 10)
        # 结果输出相关参数
        self.r_top_num = 200  # 取前200个商品
        # 购买次序相关的权重
        self.range = 10  # 购买次序的有效关联范围
        self.day_diff = 3  # 时间差 不超过3天
        self.order_weight = []
        # 达人的人工经验
        # self.peo_exp = exp_of_people()
        # self.peo_exp.read_jingyan()
        # 搭配概率
        self.top_k_da = 60000
        self.pro_da_pei = np.array([0.0] * self.top_k_da)
        # 原始的搭配概率
        self.p_match = 0.0006
        self.class_class = 0
        #  引入第一种提问方式的 类别意见
        self.my_cgailv = class_gailv()
        self.my_cgailv.read_txt()
        self.my_cgailv.my_tongji2()
        self.pre_class_gailv = []  # 记忆缓存
        self.pre_class_id = -1  # 记忆缓存


    def read_history(self):
        # 将购买物品
        read_path = os.path.join(self.data_dir, 'user_bought_history1.txt')
        read_stream = open(read_path, 'r')
        user_id_p = 0
        start_date = datetime.datetime(2012, 1, 1)
        i_line = 0
        for line_i in read_stream:
            i_line += 1
            if i_line % 1000000 == 0:
                print i_line, time.time()
            self.record_num += 1
            a = line_i.strip().split(',')
            item_id = int(a[1])
            user_id = int(a[0])
            t0 = a[2].split('-')
            date_now = datetime.datetime(int(t0[0]), int(t0[1]), int(t0[2]))
            if user_id_p != user_id:
                # di yi ci
                if self.record_num != 1:
                    self.user_array[self.user_num, 1] = self.record_num  # 记录上一个用户的末尾位置
                start_date = date_now
                user_id_p = user_id
                self.user_num += 1
                self.user_dict[user_id] = self.user_num
                self.user_array[self.user_num, 0] = self.record_num
                self.user_item_array[self.record_num, :] = np.array([item_id, 0])
            else:
                dt = (date_now - start_date).days
                self.user_item_array[self.record_num, :] = np.array([item_id, dt])
        self.user_array[self.user_num, 1] = self.record_num + 1
        self.user_array = self.user_array[0:(self.user_num + 1), ]
        self.user_item_array = self.user_item_array[0:(self.record_num + 1), ]
        read_stream.close()

    def item_hot2(self):
        # 读取文本分析中存储的商品顺序 确保商品存储位置完全一致
        r_stream = open(os.path.join(self.data_dir, 'my_item_hot.txt'), 'r')
        self.item_num = -1
        for line in r_stream:
            my_str = line.strip().split('\t')
            self.item_num += 1
            self.item_array[self.item_num, :] = [int(my_str[0]), int(my_str[1])]
        self.item_array = self.item_array[0:(self.item_num + 1), ]
        self.item_array[:, 1] = self.item_array[:, 1] / (self.record_num + 1)  # 记录次数 转为 记录概率
        for x in xrange(0, self.item_num + 1):
            self.item_dict[int(self.item_array[x, 0])] = x

    def read_class_id(self):
        # 读取每个类别的情况：
        read_path = os.path.join(self.data_dir, 'class_hot.txt')
        read_stream = open(read_path, 'r')
        class_index = 0
        for line_i in read_stream:
            my_str = line_i.split()
            if int(my_str[2]) == 1 or int(my_str[1]) <= 5:
                continue
            self.class_dict[int(my_str[0])] = class_index
            class_index += 1
        self.class_num = class_index - 1  # 最大编号  +1 位分类数
        # 读取每个商品的类别编号
        self.item_class = np.array([0] * (self.item_num + 1))
        read_path = os.path.join(self.data_dir, 'dim_items.txt')
        read_stream = open(read_path, 'r')
        for line_i in read_stream:
            aa = line_i.strip().split(' ')
            item_index = self.item_dict.get(int(aa[0]), -1)
            # 购买记录中存在该商品
            if item_index != -1:
                self.item_class[item_index] = int(aa[1])
                # 记录商品类别数目
                # if self.class_dict.get(int(aa[1]), -1) == -1:
                # self.class_num += 1
                # self.class_dict[int(aa[1])] = self.class_num  # 给类别分配编号
        read_stream.close()

    def set_top_k(self, a=20000):
        # 设置top_k
        self.top_k = a

    def class_item_hot(self):
        # 各类商品 关联商品热度 统计结果为购买某一类商品后 其他各个商品出现其后的概率
        self.like_matrix = np.zeros((self.top_k + 1, self.class_num + 1))  # 最后一行记录残余项
        # 关联数
        for i_user in xrange(0, self.user_num + 1):
            for i_record in xrange(self.user_array[i_user, 0], self.user_array[i_user, 1]):
                temp = self.user_item_array[i_record,]  # 商品id  时间差
                item_index0 = self.item_dict.get(temp[0], -1)  # 商品ind
                class_id0 = self.item_class[item_index0]
                class_index = self.class_dict.get(class_id0, -1)
                if class_index == -1:
                    continue
                # 向前看n个商品
                i_diff = 0
                while i_diff < self.range:
                    pre_ind = i_record - 1 - i_diff
                    if pre_ind >= self.user_array[i_user, 0]:  # 同一用户的记录范围内
                        temp_now = self.user_item_array[pre_ind, :]
                        if (temp[1] - temp_now[1]) <= self.day_diff:  # 时间范围内
                            item_index = self.item_dict.get(temp_now[0], -1)
                            item_index = min(item_index, self.top_k)  # top+1列存储其他所有
                            if item_index != -1:
                                self.like_matrix[item_index, class_index] += self.order_weight[i_diff]
                            else:
                                continue
                        else:
                            break
                        i_diff += 1
                    else:
                        break
                # 向后看n个商品
                i_diff = 0
                while i_diff < self.range:
                    suf_ind = i_record + 1 + i_diff
                    if suf_ind < self.user_array[i_user, 1]:  # 此处为 小于号
                        temp_now = self.user_item_array[suf_ind, :]
                        if (temp_now[1] - temp[1]) <= self.day_diff:  # 时间范围内
                            item_index = self.item_dict.get(temp_now[0], -1)
                            item_index = min(item_index, self.top_k)  # top+1列存储其他所有
                            if item_index != -1:
                                self.like_matrix[item_index, class_index] += self.order_weight[i_diff]
                            else:
                                continue
                        else:
                            break
                        i_diff += 1
                    else:
                        break
        # 将 like_matrix 直接转化为概率
        col_sum = self.like_matrix.sum(0)  # 按照列 求和
        # row_sum = self.like_matrix.sum(1)  # 按照行 求和
        pes = pro_es2.Pro_estimate()
        o_ceshi = open(os.path.join(self.data_dir, 'ceshi_class_p.txt'), 'w')
        for item_index in xrange(0, self.top_k + 1):
            # 前 top_k  个是商品 最后一项为残余项
            if item_index % 200 == 0:
                print item_index, time.time()
            if item_index == self.top_k:
                p_pre = 1 - sum(self.item_array[0:self.top_k, 1])
            else:
                p_pre = self.item_array[item_index, 1]
            for class_index in xrange(0, self.class_num + 1):
                a = self.like_matrix[item_index, class_index]
                self.like_matrix[item_index, class_index] = \
                    pes.get_pro_r(p_pre, self.like_matrix[item_index, class_index], col_sum[class_index])
                if class_index==1:
                    o_ceshi.write(str(p_pre) + '\t' + str(a) + '\t' + str(col_sum[class_index])
                                  + '\t' +str(self.like_matrix[item_index, class_index]) + '\n')
        o_ceshi.close()

    def read_write_class_item_hot(self, my_type="w", file="class_item_hot2.txt"):
        if my_type == "w":
            w_stream = open(os.path.join(self.data_dir, file), 'w')
            # 表头
            (m, n) = self.like_matrix.shape
            aaa = sorted(self.class_dict.iteritems(), key=lambda a: a[1])
            header = "item_id\t" + str(aaa[0][0])
            for class_index in xrange(1, n):
                header += ',' + str(aaa[class_index][0])
            w_stream.writelines(header + '\n')
            for item_index in xrange(0, m):
                item_id = self.item_array[item_index, 0]
                my_str = str(item_id) + '\t' + str(math.log(self.like_matrix[item_index, 0]))
                if item_index == (m - 1):  # 最后一项 为残余商品之和
                    my_str = 'remain\t' + str(math.log(self.like_matrix[item_index, 0]))
                for class_index in xrange(1, n):
                    my_str += ',' + str(math.log(self.like_matrix[item_index, class_index]))
                w_stream.writelines(my_str + '\n')
            w_stream.close()
        else:
            m = self.top_k + 1
            n = self.class_num + 1
            self.like_matrix = np.zeros((m, n), float)
            r_stream = open(os.path.join(self.data_dir, file), 'r')
            i_line = -1
            for line in r_stream:
                if i_line == -1:
                    i_line += 1
                    continue
                aaa = line.rstrip().split('\t')
                item_str_array = aaa[1].split(',')
                for i in xrange(0, n):
                    self.like_matrix[i_line, i] = math.exp(float(item_str_array[i]))
                i_line += 1
            r_stream.close()

    # 读取需要计算的商品
    def my_test(self, file_name="test_file.txt"):
        read_stream = open(os.path.join(self.data_dir, file_name), 'r')
        item_id = 0
        temp_str = ''
        first = True
        num_all = 0
        num_1 = 0
        for line_i in read_stream:
            a = line_i.strip().split('\t')
            # 增加 未有购买记录的商品处理方式
            if a[1] == 'None':
                a[1] = -1
                num_1 += 1
            temp_item = [int(a[0]), int(a[1])]
            if item_id != temp_item[0]:
                item_id = temp_item[0]
                num_all += 1
                if first == True:
                    first = False
                else:
                    self.test_list.append(temp_str)
                temp_str = str(temp_item[0]) + '\t' + str(temp_item[1])
            else:
                temp_str += ',' + str(temp_item[1])
        self.test_list.append(temp_str)
        print num_1, num_all

    # 读取次序的权重系数
    def set_weight(self, range=10):
        self.range = range
        self.order_weight = np.array([0.0] * range)
        r_path = os.path.join(self.data_dir, "次序关联.txt".decode("utf8"))
        r_stream = open(r_path, 'r')
        i_line = -1
        for line_i in r_stream:
            if i_line == -1:
                i_line += 1
                continue
            my_str = line_i.strip().split('\t')
            if abs(int(my_str[0])) <= range:
                self.order_weight[abs(int(my_str[0])) - 1] += 0.5 * (float(my_str[3]) - 0.0006)
        self.order_weight = self.order_weight / max(self.order_weight)

    # 利用全局热度 扩展到 某一个分类的热度分布
    def all_2_class(self, class_index):
        # 未记录的分类
        if class_index == -1:
            self.temp_item_array_hot = self.item_array[:, 1]
        else:
            zhi_shu = self.like_matrix[self.top_k, class_index] / sum(self.item_array[self.top_k:, 1])
            self.temp_item_array_hot = zhi_shu * self.item_array[:, 1]
            self.temp_item_array_hot[0:self.top_k] = self.like_matrix[0:self.top_k, class_index]

    # 找到某一商品后面其他商品的出现概率
    def item_2_item(self, item_id, user_str):
        # 返回折合关联次数
        if user_str[0:2] == '-1':
            result_array = np.array([0.0] * (self.item_num + 1))
        else:
            result_array = np.array([0.0] * (self.item_num + 1))
            user_list = user_str.split(',')
            for user in user_list:
                user_index = self.user_dict[int(user)]
                for i_record in xrange(self.user_array[user_index, 0], self.user_array[user_index, 1]):
                    if (i_record > self.user_array[user_index, 0]) and \
                            (self.user_item_array[i_record, 0] == self.user_item_array[i_record - 1, 0]):
                        continue  # 连续的购买相同商品
                    temp = self.user_item_array[i_record,]  # 商品id  时间差
                    # 向前看n个商品
                    i_diff = 0
                    while i_diff < self.range:
                        pre_ind = i_record - 1 - i_diff
                        if pre_ind >= self.user_array[user_index, 0]:  # 同一用户的记录范围内
                            temp_now = self.user_item_array[pre_ind, :]
                            if (temp[1] - temp_now[1]) <= self.day_diff:  # 时间范围内
                                item_index = self.item_dict.get(temp_now[0], -1)
                                if item_index != -1:
                                    result_array[item_index] += self.order_weight[i_diff]
                                else:
                                    continue
                            else:
                                break
                            i_diff += 1
                        else:
                            break
                    # 向后看n个商品
                    i_diff = 0
                    while i_diff < self.range:
                        suf_ind = i_record + 1 + i_diff
                        if suf_ind < self.user_array[user_index, 1]:  # 此处为 小于号
                            temp_now = self.user_item_array[suf_ind, :]
                            if (temp_now[1] - temp[1]) <= self.day_diff:  # 时间范围内
                                item_index = self.item_dict.get(temp_now[0], -1)
                                if item_index != -1:
                                    result_array[item_index] += self.order_weight[i_diff]
                                else:
                                    continue
                            else:
                                break
                            i_diff += 1
                        else:
                            break
        return result_array
    # 统计该商品的关联商品分布 并返回序列
    def count_items2(self, item_id, user_str):
        """

        :type item_id: 商品id 整数
        :type user_str: item_id 的购买者列表 字符串，不同用户逗号间隔
        """
        # 空的 user 列表
        # 将 result_array 直接转化为概率
        # 计算统计 该商品的关联性质
        result_array = self.item_2_item(item_id, user_str)

        temp_result_array = np.zeros((600, 2))  # 存储 计算结果
        i_temp_result = 0
        temp_array1 = np.array([self.p_match] * (self.item_num + 1))  # 随机搭配的概率 假设
        # temp_array1[0:self.top_k_da] = self.pro_da_pei  # 构造一个全长度的 搭配向量
        item_index = self.item_dict.get(item_id, 0)  # 商品存储位置编号
        class_id1 = int(self.item_class[item_index])
        if class_id1 == self.pre_class_id and class_id1 != -1:  # 和前一次相同
            temp_array1 = self.pre_class_gailv
        else:
            for item_index in xrange(0, (self.item_num + 1)):
                class_id2 = int(self.item_class[item_index])
                temp_array1[item_index] = self.my_cgailv.get_gailv2(class_id1, class_id2)
            self.pre_class_id = class_id1
            self.pre_class_gailv = temp_array1
        temp_array2 = result_array + self.temp_item_array_hot  # 构造一个全长的 发生向量(最优概率的近似)
        result_array = temp_array2  #
        array_sum = sum(result_array)  # 求和
        temp_array = temp_array1 * temp_array2 / (self.item_array[:, 1]+0.00000001)  # 相乘
        my_orders1 = np.argsort(-temp_array)  # 预排序
        item_index = self.item_dict.get(item_id, -1)
        if item_index == -1:
            class_id = -1
        else:
            class_id = self.item_class[item_index]
        pes = pro_es2.Pro_estimate()
        for i_order in xrange(0, self.top_k_da):
            temp_item_index = my_orders1[i_order]  # 商品的下标
            if self.item_class[temp_item_index] == class_id:  # 类别相同
                continue
            # if self.pro_da_pei[i_order] < self.p_match:  # 小于基线
            #     continue
            # temp_pro = pes.get_pro_r(self.temp_item_array_hot[temp_item_index]
            #                          , result_array[temp_item_index], array_sum)  # 考虑原假设后 的 发生的概率
            temp_pro = result_array[temp_item_index]/ array_sum  # 不考虑原假设
            temp_result_array[i_temp_result, :] = [self.item_array[temp_item_index, 0],
                                                   temp_pro/(self.item_array[item_index, 1]+0.000000001) * temp_array1[temp_item_index]]
            i_temp_result += 1
            if i_temp_result == 600:
                break
        temp_result_array = temp_result_array[0:i_temp_result, :]
        temp_order = np.argsort(-temp_result_array[:, 1])  # 按照概率降序排列
        result_str = str(item_id) + ' ' + str(int(temp_result_array[temp_order[0], 0]))
        for i in xrange(1, self.r_top_num):
            result_str += ',' + str(int(temp_result_array[temp_order[i], 0]))
        return result_str

    # 计算所有的商品列表
    def calculate_all2(self, file_path='fm_submissions2_tag_m.txt'):
        # 索引需要计算的 item_array
        re_item_dict = {}
        for str_i in xrange(0, len(self.test_list)):
            item_user_str = self.test_list[str_i]
            string0 = item_user_str.split('\t')
            re_item_dict[int(string0[0])] = str_i  # 指向其存储位置 方便查找
        w_stream = open(os.path.join(self.data_dir, 'fm_submissions21.txt'), 'w')
        r_stream = open(os.path.join(self.data_dir, file_path), 'r')  # 词计算的结果
        iii = 0
        t0 = time.time()
        for line_s in r_stream:
            if iii % 100 == 0 or time.time()-t0 > 100:
                t0 = time.time()
                print iii,  t0
            iii += 1
            my_str = line_s.split('\t')
            item_id = int(my_str[0])
            for x in xrange(1, self.top_k_da + 1):
                self.pro_da_pei[x - 1] = float(my_str[x])
            i_item_user_str = re_item_dict.get(item_id, -1)
            if i_item_user_str == '-1':
                # print "happy bugs: 商品没有购买历史"
                item_user_str = [item_id, '-1']
            else:
                item_user_str = self.test_list[i_item_user_str]
                item_user_str = item_user_str.split('\t')
            item_index = self.item_dict.get(item_id, 0)  # 商品存储位置编号
            class_id = self.item_class[item_index]
            class_index = self.class_dict[class_id]
            self.all_2_class(class_index)  # 获取类别 后续商品热度
            string0 = self.count_items2(item_id, item_user_str[1])  # 用户与
            w_stream.writelines(string0 + '\n')
        r_stream.close()
        w_stream.close()


if __name__ == "__main__":
    a = READ_Bought_History()
    a.set_weight()
    a.my_test()
    print time.time(), 0
    a.read_history()
    print time.time(), 1
    a.item_hot2()  # 保证排序和wenben_rlike相同，热度降序
    print time.time(), 2
    a.read_class_id()
    print time.time(), 3
    # a.class_item_hot()  # 商品顺序改变 或者 第一次计算  需要运行
    a.read_write_class_item_hot('r')  # 运行class_item_hot 时，无参数 自动记录，否则 填写 ‘r’ 为参数读取之前的结果
    print time.time(), 4
    a.calculate_all2("fm_submissions2_tag_m.txt")
    print time.time(), 5