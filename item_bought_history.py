# coding=utf-8
"""
功能：
1、有购买历史的商品的关联购买
2、无购买历史的商品的关联购买序列（冷启动）
bar_mark 为True 表示 前面的id经过第二次映射
"""
from information import known_information
import numpy as np
import gl

# 继承information.known_information 类的信息
class items(known_information):

    def __init__(self):
        known_information.__init__(self)
        self.item_hot_pro = np.array([0.0] * 10)  # 商品购买热度
        self.word_hot_pro = np.array([0.0] * 10)  # 每个词的出现概率
        self.item_relate = np.array([0.0] * 10)  # 商品购买数
        self.KNN_k = 500  # KNN的 k

    def set_information(self):
        self.map()
        self.map_word()

    def count_relate_num(self, item_id_bar, item_array, bar_mark=True):
        # 代完成
        """

        :rtype : self.item_num_history 长度的向量
        """
        a = np.array([0] * self.item_num_history)
        return a

    def item_relate_item(self, item_id, bar_mark=True):
        if not bar_mark:
            item_id = self.itemid_dict[item_id]
        temp_relate_num_a = np.array([0.0] * self.item_num_history)  # 有购买历史的商品的长度
        user_array = self.item2user(item_id, True)  # 购买过item_id 的 所有用户
        for user_id in user_array:
            item_array = self.user2item(user_id, True)
            temp_relate_num_a += self.count_relate_num(item_id, item_array, True)
        return temp_relate_num_a / sum(temp_relate_num_a)

    def item_relate_item_no_history(self, item_id, bar_mark=True):
        if not bar_mark:
            item_id = self.itemid_dict[item_id]
        # step1：  获取类似产品
        word_array = self.item2word(item_id, True)
        class_id = self.item2class(item_id, True)
        word_num = len(word_array)
        temp_array = np.zeros((word_num, self.item_num_history), bool)
        for i in xrange(0, word_num):
            temp_array[i,] = self.word2itemArray(word_array[i], True)
        temp_class_array = self.class2itemArray(class_id, True)
        # temp_array.sum(0)  # 按照列求和
        temp_array2 = temp_array.sum(0)*temp_class_array  # 只看同类别的商品
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
                        relate_item[1] *= self.word_hot_pro
                i_relate_num += 1
                if i_relate_num == 1000:
                    break
        relate_item = relate_item[:, 0:i_relate_num]
        np.random.shuffle(relate_item)  # 随机排序
        a = np.argsort(relate_item[0:self.KNN_k, 2]) # 取 前 KNN_k个商品
        relate_item = relate_item[a, ]  # 按照词差异排序后取值
        #  获取分组数量
        group_num = len(set(relate_item[:, 2]))
        # step 2 ： 按照分组 找出关联商品
        temp_relate_num = np.zeros((group_num, self.item_num_history))
        weight_group = np.array([0.0]*group_num)
        group_before = relate_item[0, 2]
        group_num_i = 0
        x_start = 0
        for x in xrange(0, len(a)):
            if group_before == relate_item[x, 2]:
                continue
            else:
                item_id_array = relate_item[x_start:x, 0]
                user_array = self.item2user(item_id_array, True)
                for user_id in user_array:
                    item_array = self.user2item(user_id, True)
                    temp_relate_num[group_num_i, :] += self.count_relate_num(item_id_array, item_array, True)
                weight_group[group_num_i] = relate_item[x_start, 1]
                x_start = x
                group_num_i += 1
                group_before = relate_item[x, 2]
        item_id_array = relate_item[x_start:, 0]
        user_array = self.item2user(item_id_array, True)
        for user_id in user_array:
            item_array = self.user2item(user_id, True)
            temp_relate_num[group_num_i, :] += self.count_relate_num(item_id_array, item_array, True)
        weight_group[group_num_i] = relate_item[x_start, 1]
        # step3： 归一化  组合结果
        weight_group = weight_group/sum(weight_group)
        for x in xrange(0, group_num):
            temp_relate_num[group_num_i, ] = temp_relate_num[group_num_i, :] / sum(temp_relate_num[group_num_i, :]) \
                                             * weight_group[x]
        return temp_relate_num.sum(0)