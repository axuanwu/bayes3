# coding=utf-8
"""
功能：
1、有购买历史的商品的关联购买
2、无购买历史的商品的关联购买序列（冷启动）
bar_mark 为True 表示 前面的id经过第二次映射
注意事项：
1、该算法所搭配出来的商品全部限定在有购买历史的商品中
"""
import time
import pickle
from information import known_information
from class_opinion import class_gailv
import numpy as np
import gl

# 继承information.known_information 类的信息
class items(known_information):

    def __init__(self):
        known_information.__init__(self)
        self.item_hot_pro = np.array([0.0] * 10)  # 商品购买热度
        self.word_hot_pro = np.array([0.0] * 10)  # 每个词的出现概率
        self.class_id_bar = np.array([0.0] * 10)
        self.item_relate = np.array([0.0] * 10)  # 关联商品购买数
        self.KNN_k = 50  # KNN的 k
        self.weight_array = np.array([0]*10)
        self.my_range = 10
        self.class_information = class_gailv()
        self.class_opinion = np.array([0.0] * 10)  # 类别的打分意见

    # 读取次序的权重系数
    def set_weight(self, my_range=10):
        self.my_range = my_range
        self.order_weight = np.array([0.0] * my_range)
        r_stream = open(gl.weight_path, 'r')
        i_line = -1
        for line_i in r_stream:
            if i_line == -1:
                i_line += 1
                continue
            my_str = line_i.strip().split('\t')
            if abs(int(my_str[0])) < my_range:
                self.order_weight[abs(int(my_str[0]))] += 0.5 * (float(my_str[3]) - 0.0006)
        self.order_weight = self.order_weight / max(self.order_weight)

    def set_information(self):
        # 购买历史
        self.map()
        # 商品词汇
        self.map_word()
        self.map_class()
        # 类别关联意见
        self.class_information.read_txt()
        self.class_information.set_dict_class(self.classid_dict)
        self.class_information.my_tongji2()
        # 设置 商品的热度
        self.item_hot_pro = 1.0 * self.item_array[0:self.item_num_history, 1]/sum(self.item_array[0:self.item_num_history, 1])
        # 设置 词热度
        self.word_hot_pro = 1.0 * self.word_array[:, 2]/sum(self.word_array[:, 2])
        # 所有有历史商品的映射类别
        self.class_id_bar = self.item_array[0: self.item_num_history, 2]
        for x in xrange(0, self.item_num_history):
            self.class_id_bar[x] = self.classid_dict[self.class_id_bar[x]]
        self.set_weight()

    def count_relate_num(self, item_id_bar, user_item_array, bar_mark=True):
        # 计算 商品的关联商品热度
        """

        :rtype : self.item_num_history 长度的向量
        """
        weight = 'order'
        m = user_item_array.shape[0]
#        user_item_array[:, 1] = np.arange(0,m)  # 转化为次序
        try:
            b = len(item_id_bar)
        except:
            item_id_bar = [item_id_bar]
        temp_dict = {}
        for x in item_id_bar:
            temp_dict[x] = True
        if weight == 'order':
            #  使用次序计算权重
            in_before = False
            i_record = 0
            for x in xrange(0, m):
                if temp_dict.get(user_item_array[x, 0], False):
                    if not in_before:
                        in_before = True
                    else:
                        continue
                user_item_array[i_record, ] = [user_item_array[x, 0], i_record]
                i_record += 1
            user_item_array = user_item_array[0:i_record, ]
            m = i_record
        day_before = -1
        array_time_zero = np.array([0] * m)
        i_array_time_zero = 0
        m0 = m
        for x in xrange(0, m0):
            if temp_dict.get(user_item_array[x, 0], False):
                if user_item_array[x, 1] != day_before:
                    array_time_zero[i_array_time_zero] = user_item_array[x, 1]
                    day_before = user_item_array[x, 1]
                    i_array_time_zero += 1
                user_item_array[x, 1] = -1
                m -= 1
        array_time_zero = array_time_zero[0:i_array_time_zero]
        temp_array = np.zeros((m, 2))  # 第一列是 item_id, 第二列为距离
        i_temp_array = 0
        for x in xrange(0, m0):
            if user_item_array[x, 1] != -1:
                temp_array[i_temp_array, 0] = user_item_array[x, 0]
                temp_array[i_temp_array, 1] = min(np.abs(user_item_array[x, 1]-array_time_zero)) # 同一个商品只取距离最小的距离
                i_temp_array += 1
        a = np.array([0.0]*self.item_num_history)
        for x in xrange(0, m):
            if temp_array[x, 1] < self.my_range:
                weight = self.weight_array[temp_array[x, 1]]
                a[temp_array[x, 0] - gl.itemIDStart] = max(a[temp_array[x, 0] - gl.itemIDStart],weight)
        return a

    def item_relate_item(self, item_id, bar_mark=True):
        if not bar_mark:
            item_id = self.itemid_dict[item_id]
        temp_relate_num_a = np.array([0.0] * self.item_num_history)  # 有购买历史的商品的长度
        user_array = self.item2user(item_id, True)  # 购买过item_id 的 所有用户
        for user_id in user_array:
            item_array = self.user2item(user_id, True)
            temp_relate_num_a += self.count_relate_num(item_id, item_array, True)
        self.item_relate = (temp_relate_num_a + self.item_hot_pro)/(sum(temp_relate_num_a)+1)

    def item_relate_item_no_history(self, item_id, bar_mark=True):
        if not bar_mark:
            item_id = self.itemid_dict[item_id]
        # step1：  获取类似产品
        print 1,time.time()
        word_array = self.item2word(item_id, True)
        class_id = self.item2class(item_id, True)  # 原来的classid
        word_num = len(word_array)
        temp_array = np.zeros((word_num, self.item_num_history), bool)
        for i in xrange(0, word_num):
            temp_array[i,] = self.word2itemArray(word_array[i], True)
        temp_class_array = self.class2itemArray(class_id, False)
        # temp_array.sum(0)  # 按照列求和
        temp_array2 = temp_array.sum(0)*temp_class_array  # 只看同类别的商品
        if sum(temp_array2)==0:
            temp_array2 = temp_array.sum(0)
        temp_max = temp_array2.max()
        relate_item = np.ones((2000, 3))  # 第一列 item_id' 第二列 相似度 第三列 组别编码
        i_relate_num = 0
        mark_array = np.exp2(np.arange(0, word_num))
        for i in xrange(0, self.item_num_history):
            if temp_array2[i] == temp_max:
                relate_item[i_relate_num, 0] = i + gl.itemIDStart
                relate_item[i_relate_num, 2] = int(sum(mark_array*temp_array[:, i]))  # 公共部分相同的商品，该值相同
                for i_word in xrange(0, word_num):
                    if not temp_array[i_word, i]:
                        # 两个商品在这个词上存在差异
                        relate_item[i_relate_num, 1] *= self.word_hot_pro[word_array[i_word]]
                i_relate_num += 1
                if i_relate_num == 1000:
                    break
        relate_item = relate_item[0:i_relate_num, :]
        b = np.argmax(relate_item[:, 1])
        relate_item = relate_item[relate_item[:,2]==relate_item[b,2], ]
        np.random.shuffle(relate_item)  # 随机排序
        a = np.argsort(relate_item[0:self.KNN_k, 2])  # 取 前 KNN_k个商品
        relate_item = relate_item[a, ]  # 按照词差异排序后取值
        #  获取分组数量
        group_num = len(set(relate_item[:, 2]))
        # step 2 ： 按照分组 找出关联商品
        print 2,time.time()
        temp_relate_num = np.zeros((group_num, self.item_num_history))
        weight_group = np.array([0.0]*group_num)
        group_before = relate_item[0, 2]
        group_num_i = 0
        x_start = 0
        for x in xrange(0, len(a)):
            if group_before == relate_item[x, 2]:
                continue
            else:
                item_id_array = np.array([1]*(x - x_start), int)
                item_id_array[:] = relate_item[x_start:x, 0]
                user_array = self.item2user(item_id_array, True)
                for user_id in user_array[:, 0]:
                    item_array = self.user2item(user_id, True)
                    temp_relate_num[group_num_i, :] += self.count_relate_num(item_id_array, item_array, True)
                weight_group[group_num_i] = relate_item[x_start, 1]
                x_start = x
                group_num_i += 1
                group_before = relate_item[x, 2]
        item_id_array = relate_item[x_start:, 0]
        user_array = self.item2user(item_id_array, True)
        for user_id in user_array[:, 0]:
            item_array = self.user2item(user_id, True)
            temp_relate_num[group_num_i, :] += self.count_relate_num(item_id_array, item_array, True)
        weight_group[group_num_i] = relate_item[x_start, 1]
        # step3： 归一化  组合结果
        weight_group = weight_group/sum(weight_group)
        for x in xrange(0, group_num):
            temp_relate_num[group_num_i, ] = (temp_relate_num[group_num_i, :] + self.item_hot_pro) / (sum(temp_relate_num[group_num_i, :])+1) \
                                             * weight_group[x]
        self.item_relate = temp_relate_num.sum(0)

    # 搭配推荐模块
    def dafen(self):
        r_stream = open(gl.testFile, 'r')
        classid_before = -1
        w_stream = open(gl.resultFile, 'w')
        w_stream.close()
        for line in r_stream:
            print line.strip(), time.time()
            my_str1 = line.strip().split('\t')
            item_id = int(my_str1[-1])
            item_id_bar = self.itemid_dict[item_id]
            if (item_id_bar-gl.itemIDStart) < self.item_num_history:
                # 有购物历史
                self.item_relate_item(item_id_bar, True)
            else:
                # 无购买历史
                self.item_relate_item_no_history(item_id_bar, True)
            # 获取 class的意见
            if classid_before == self.class_id_bar[item_id_bar-gl.itemIDStart]:
                pass
            else:
                classid_before = self.class_id_bar[item_id_bar-gl.itemIDStart]
                self.class_opinion = self.class_information.get_gailv_array(classid_before,
                                                                            self.class_id_bar, True)
            # 两者意见相乘
            self.item_relate *= self.class_opinion
            a = self.item_relate
            w_stream = open(gl.resultFile, 'a')
            w_stream.write(str(item_id) + ' ' + str(self.item_inverse(gl.itemIDStart + a[0])))
            for x in xrange(1, 200):
                w_stream.write(','+str(self.item_inverse(gl.itemIDStart + a[0])))
            w_stream.write('\n')
            w_stream.close()

if __name__ == "__main__":
    t1 = time.time()
    if False:
        a = items()
        a.set_information()
        a.save_history()
        f = open(gl.pickle_file, 'wb')
        pick = pickle.Pickler(f)
        pick.dump(a)
        f.close()
        del a
        del pick
    f = open(gl.pickle_file, 'rb')
    pick = pickle.Unpickler(f)
    a = pick.load()
    f.close()
    del pick
    a.load_history()
    print 1,time.time()
    b = a.user2item(12058626, False)
    print a.itemid_dict[32567] in b[:, 0]  # 12068626 买的商品中是否有 32567
    b = a.item2user(32567, False)
    print a.userid_dict[12058626] in b[:, 0]  # 买了 32567的用户中是否有  用户 12068626
    b = a.word2item(123950, False)  #
    print a.itemid_dict[32567] in b[:, 0]  # 词123950的商品中 是否有 32567
    print time.time()-t1
    a.dafen()
