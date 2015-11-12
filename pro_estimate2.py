# coding=utf-8
# 与上一版本相比 主要是将简化计算的步骤（可能情况下给出误差不太大的近似结果，而不进行概率完整的估算）
__author__ = '01053185'
import numpy as np
import math


def error_f(alpha, p):
    # 计算误差的绝对值 e^α+(1/α+p)∙(1-e^α)=0
    return abs(math.exp(alpha) + (1.0 / alpha + p) * (1 - math.exp(alpha)))


class Pro_estimate():

    def __init__(self):
        self.alpha = 0
        self.beta = 0
        self.p_pre = 0.01
        self.x_array = np.array([0.0] * 10000)
        self.pro_x_array = np.array([0.0] * 10000)
        self.step_x_array = np.array([0.0] * 10000)
        self.p_estimate = 0  # 最后估计的概率值
        self.step_i = 0
        self.solve_function(self.p_pre)
        self.set_array()
        self.dict_memory = {}

    def get_pro_r(self, pro_pre, n, m):
        if n > 100:
            return 1.0 * n / m  # 抽样m次命中大于一百次 无需优化
        if 0 == m:
            return (pro_pre)
        if (m != 0) and (abs(1.0 * n / m / pro_pre - 1) < 0.05):
            return 0.5 * n / m + 0.5 * pro_pre
        else:
            if abs(pro_pre / self.p_pre - 1) < 0.01:
                if self.dict_memory.get(str(m)+','+str(n), -1) == -1:  # 没有存储
                    self.p_estimate = self.get_pro(n, m)
                    self.dict_memory[str(m)+','+str(n)] = self.p_estimate
                else:
                    self.p_estimate = self.dict_memory[str(m)+','+str(n)]
            else:
                self.solve_function(pro_pre)
                self.set_array()
                self.dict_memory = {}  # 清空记忆
                self.p_estimate = self.get_pro(n, m)
                self.dict_memory[str(m)+','+str(n)] = self.p_estimate
        return self.p_estimate

    def solve_function(self, p):
        self.p_pre = p
        if p < 0.02:
            self.alpha = -1 / p
            self.beta = 1 - math.log(1.0 / self.alpha * (math.exp(self.alpha) - 1))
            # self.beta = 1 + math.log(self.alpha) - self.alpha
        else:
            alpha = -1000 + 10 ** -9
            if p > 0.5:
                alpha = 10 + 10 ** -9
            sign = 1.0
            step = 1.0
            error_now = error_f(alpha, self.p_pre)
            T = 0
            while (error_now > 10 ** -9):
                temp_alpha = alpha + step * sign
                temp_error = error_f(temp_alpha, self.p_pre)
                if temp_error < error_now:
                    alpha = temp_alpha
                    error_now = temp_error
                    T += 1
                    if T == 2:
                        step *= 2
                    continue
                sign *= -1  # 反向尝试
                temp_alpha = alpha + step * sign
                temp_error = error_f(temp_alpha, self.p_pre)
                if temp_error < error_now:
                    T = 0
                    alpha = temp_alpha
                    error_now = temp_error
                    continue
                step *= 0.3
            self.alpha = alpha
            self.beta = 1 - math.log(1.0 / self.alpha * (math.exp(self.alpha) - 1))

    # 修改设置数组的方式
    def set_array(self):
        min_step = 0.0002  # 区间概率
        min_size = 0.005  # 区间宽度
        start = 0.0
        self.step_i = 0
        while start < 1:
            if math.exp(self.alpha * start - 1 + self.beta) < 10 ** -12:
                step = min_size
            else:
                if self.alpha * start - 1 + self.beta > 30:
                    step = 10 ** -10
                else:
                    step = min(min_step / math.exp(self.alpha * start - 1 + self.beta), min_size)
                    step = max(10 ** -10, step)
            step_end = min(start + step, 1)
            temp_x = 0.5 * (start + step_end)
            # temp_step_x = step_end - start
            # 概率密度为：math.exp(self.alpha * temp_x - 1 + self.beta) 取其对数
            temp_pro = self.alpha * temp_x - 1 + self.beta
            self.x_array[self.step_i] = temp_x
            self.step_x_array[self.step_i] = step_end - start
            self.pro_x_array[self.step_i] = temp_pro
            start = step_end
            self.step_i += 1

    def get_pro(self, n, m):
        # 计算不同的段x概率在m次试验中,发生n次的概率  使用对数避免精度损失
        # self.pro_x_array * self.step_x_array 每种情况发生的原始分布
        now_jiashe = np.log(self.x_array[0:self.step_i]) * n \
                     + np.log(1 - self.x_array[0:self.step_i]) * (m - n) \
                     + self.pro_x_array[0:self.step_i] \
                     + np.log(self.step_x_array[0:self.step_i])  # 调整原始的经验分布
        my_max = now_jiashe.max()  # 以最大值为1 进行计算
        now_jiashe = now_jiashe - my_max
        now_jiashe = np.exp(now_jiashe) / sum(np.exp(now_jiashe))  # 返回为不同情况的 真实的概率分布
        return sum(now_jiashe * self.x_array[0:self.step_i])


if __name__ == "__main__":
    b = Pro_estimate()
    print b.get_pro_r(0.001, 2, 100)
    print b.get_pro_r(0.000001032, 0, 21432)