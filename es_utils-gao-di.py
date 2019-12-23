import numpy as np
import random
from collections import Counter
import math
import logging
from new import input
import operator
import time


class Gao_di:
    def __init__(self, theory_area, building_num_dict, floor_num_dict, building_type, ban_floor_dict=None,
                 cross_rate=1.0, mutation_rate=1.0, pop_size=200,flag=False):
        """
        遗传算法，两种变异方法，一种为传统遗传算法的变异方法，一种为仿照以前的高低配算法实现形式，待评估
        DNA: ['A',27],['A',18],['B',27],['B',18],['C',18]
        :param theory_area:  理论面积
        :param building_num_dict:  栋数：{'A':2,'B':3,'C':1}
        self.building_num_list_sorted: 格式：[('B', 3), ('A', 2), ('C', 1)]
        :param floor_num_dict: 层高:{A:27,B:26,C:28}
        :param ban_floor_dict: 禁用层：{A:[[18,23],[12,14],[5,7],B:[[],[]],C:[[],[]]} 根据第一个值进行排序
        获取单层面积：get_area(户型，层高)

        :param cross_rate: 交叉率
        :param mutation_rate: 变异率
        :param pop_size：物种大小

        self.mutate_pos: 从哪栋楼变异，一般从最后开始，一直往前
        self.mutation_i： 从哪栋楼变异的次数
        self.ban_step: 维度跟DNA相同，表示每栋楼有多少个禁用段
        :param flag: 实际面积是否可以小于理论面积
        """
        self.theory_area = theory_area
        self.building_num_dict = building_num_dict
        x = self.building_num_dict.items()
        self.floor_num_dict = floor_num_dict
        self.building_num_list_sorted = sorted(x, key=lambda x:(x[1],self.floor_num_dict.get(x[0])))  # 这里改为按照item的第二个字符排序，即value排序
        self.dna_init = [[k, self.floor_num_dict.get(k)]
                         for k, v in self.building_num_list_sorted for _ in range(int(v))]
        if ban_floor_dict is None:
            ban_floor_dict = self.get_ban_floor_dict(self.floor_num_dict.keys())
        self.ban_floor_dict = ban_floor_dict
        self.ban_floor_dict_sorted = {k: sorted(v, key=lambda x: x[0]) for k, v in ban_floor_dict.items()}
        self.building_type = building_type

        self.cross_rate = cross_rate
        self.mutation_rate = mutation_rate
        self.pop_size = pop_size
        self.dna_size = int(sum(self.building_num_dict.values()))

        # 每栋楼具有的层段数
        self.floor_segment_num = [len(self.ban_floor_dict[k]) + 1 for k, v in self.building_num_list_sorted for _ in
                                  range(int(v))]
        self.POP = self.init_DNA_total()
        self.mutate_pos = self.get_mutate_pos(self.floor_segment_num)
        self.mutation_i = 0
        self.flag = flag

        self.segment_dict = self.get_segment_dict()

    def get_segment_dict(self):
        res = {}
        print(self.ban_floor_dict_sorted)
        for k, v in self.ban_floor_dict_sorted.items():
            pre = 0
            tmp = []
            for x,y in v:
                tmp.append([pre,x-1])
                pre = x
            tmp.append([pre, self.floor_num_dict[k]])
            res[k] = tmp
        return res

    def loss_area(self, DNA):
        """
        :param DNA: ['A',27],['A',18],['B',27],['B',18],['C',18]
        :return: 面积损失
        """
        # print("&&&&&&&&&&&&&&&&&&&&")
        # print(self.get_area_total(DNA))
        tmp = self.theory_area - self.get_area_total(DNA)
        if tmp < 0 and self.flag:
            tmp *= 300
        elif -200 < tmp < 200:
            tmp = 0
        elif tmp < 0:
            tmp *= 10

        return float(np.square(tmp))

    def loss_building_type(self, DNA):
        """
        :param DNA: ['A',27],['A',18],['B',27],['B',18],['C',18]
        :return: 高低配损失：楼栋信息熵 乘以 层数信息熵 每种楼型不同的楼层数量越多，信息熵越大，高低配层数信息熵越小
        """
        tmp = self.dna_dict(DNA)

        total = 0
        for index, (k, v) in enumerate(DNA):
            v = int(v)
            thera = (len(set(tmp.get(k))) - 1) / self.building_num_dict.get(k)
            # print(thera)
            sub = self.get_top(k,v) - v      #本栋层数与本地理论限制层数的差值，只能大于0
            if sub < 0:
                sub = 1000
            total += abs(thera * (v - self.get_next_segment_top(k, v)) * sub)
        return total

    def loss_ban(self, DNA):
        total = 0
        for k, v in DNA:
            if self.in_ban_floor(k, v):
                total += 100000000000000
        return total

    def loss_segment(self,DNA):

        self.get_current_floor_segment()



    def loss_small_rate(self,DNA):
        total = sum(self.building_num_dict.values())
        loss = 0
        if min(self.building_num_dict.keys())/total <=0.1:
            loss = 0
        return loss


    def in_ban_floor(self, k, v):
        res = False
        for start, end in self.ban_floor_dict[k]:
            if start <= int(v) <= end:
                res = True
        return res

    def get_area_total(self, DNA):
        """
        :param DNA: ['A',27],['A',18],['B',27],['B',18],['C',18]
        :return: 获取总面积
        """
        total = 0
        for k, v in DNA:
            # print(self.get_area(k, v))
            total += self.get_area(k, v) * int(v)
        return total

    def dna_dict(self, DNA):
        """
        :param DNA: ['A',27],['A',18],['B',27],['B',18],['C',18]
        :return: {A:[27,18], B:[27,18], C:[18]}
        """
        res = {}
        for k, v in DNA:
            if k not in res:
                res[k] = []
            res[k].append(v)
        return res

    def get_top_total(self,DNA):
        return [self.get_top(k,v) for k,v in DNA]


    def get_top(self,k,v):
        seg = self.get_current_floor_segment(k,v)
        res = self.segment_dict[k][seg][1]
        return res



    def get_area(self, type=None, floor=None):
        """
        :param type: 楼型
        :param floor: 层数
        :return: 获取单层面积
        """
        # try:
        tmp = self.building_type[type]
        x = sorted(tmp.items(),key=lambda k:k[0])
        tmp_ = 0
        for k,v in x:
            floor = int(floor)
            k = int(k)
            tmp_ = k
            if floor <= k :
                floor_ = k
                break
        else:
            floor_ = tmp_

        apartmentRadio = tmp.get(float(floor_)) if tmp.get(float(floor_)) else tmp.get(int(floor_))
        # print(apartmentRadio)
        res = apartmentRadio['realArea']
        res = sum(res)
        return res
        # except:
        #     logging.warning("传入的字段格式错误，请检测字段格式,传入的字段如下：")
        #     logging.warning(str(input))
        #     logging.warning("请求参数如下：")
        #     logging.warning("type = " + str(type) + ",  floor= " + str(floor))
        #     return None

    def get_next_segment_top(self, k, v):
        """

        :param k:  楼型
        :param v:  当前层
        :return:  当前层段下一层段的最高层，当前层段的禁用层首层减去1
        """
        segment = self.get_current_floor_segment(k, v)  # 当前层段
        if segment > 0:
            res = np.array(self.ban_floor_dict_sorted[k])[segment-1][0] - 1
        else:
            res = 0
        return res

    def get_current_floor_segment(self, k, v):
        """

        :param k: 楼型
        :param v: 当前层
        :return: 当前层段  从0开始，第一个禁用层以下为0，依次增加，最后一个层段在最后一个禁用层及以上
        """
        j = 0
        for i in np.array(self.ban_floor_dict_sorted[k])[:, 0]:
            if int(v) < int(i):
                return j
            else:
                j += 1
        return j

    def get_current_floor_segment_total(self,DNA):
        return [self.get_current_floor_segment(k,v) for k, v in DNA]


    def get_fitness(self, DNA):
        """
        得到一个个体(方案)的适应度
        """
        fitness_loss = self.loss_area(DNA) + self.loss_building_type(DNA) + self.loss_ban(DNA)
        # print(self.loss_building_type(DNA))
        return fitness_loss

    def get_best(self, POP):
        fitness = [self.get_fitness(i) for i in POP]
        arg = np.argmin(fitness)
        return POP[arg].copy()

    def get_best_sort(self, POP):
        fitness = [self.get_fitness(i) for i in POP]
        # print(fitness)
        pop_sorted = np.argsort(fitness)
        res = POP[pop_sorted].copy()
        return res

    def init_DNA(self):
        """
        初始化一个个体
        """
        DNA = [[k, random.randint(self.floor_num_dict.get(k) // 2, self.floor_num_dict.get(k))]
               for k, v in self.building_num_list_sorted for _ in range(int(v))]
        return DNA

    def init_DNA_total(self):
        """
        初始化一个种群
        """
        POP = [self.dna_init for i in range(self.pop_size)]
        return np.array(POP)

    def crossover(self, POP):
        """
        交叉过程，每个个体都可能进行交叉
        会从种群中随机选择一个个体、随机选择个体中的点，把其值赋值给被选择交叉的个体
        """
        first = self.get_best_sort(POP)[:int(self.pop_size * 0.3)]
        for parent in POP:
            if random.random() < self.cross_rate:
                i_ = random.randrange(0, self.pop_size)  # 从种群中随机选择一个个体
                cross_points = np.random.randint(0, 2, self.dna_size).astype(np.bool)  # 随机选择个体中的点
                parent[cross_points] = POP[i_, cross_points]
        POP[:int(self.pop_size * 0.3)] = first
        return POP

    def mutate(self, POP):
        """
        变异过程
        """
        first = self.get_best_sort(POP)[:int(self.pop_size * 0.3)]
        for parent in POP:
            for point in range(self.dna_size):
                x, y = parent[point]

                if random.random() < self.mutation_rate:
                    y = int(float(y)) + random.randint(-5, 2)
                    if y < 0:
                        y = 0
                    if y > self.floor_num_dict[x]:
                        y = self.floor_num_dict[x]

                parent[point] = x, y
        POP[:int(self.pop_size * 0.3):] = first
        return POP

    def mutate_new(self):
        self.POP[-1] = self.get_best(self.POP)
        self.first = self.POP[-1].copy()
        # print(self.first)
        for index in range(self.pop_size - 2):
            # self.first = self.get_best(self.POP)
            self.POP[index] = self.mutate_dna(self.first.copy())
        return self.POP

    def mutate_dna(self, DNA):
        # print(self.mutate_pos,self.mutation_i,self.floor_segment_num)
        # print(int(self.dna_init[-self.mutate_pos][1]),self.mutation_i)
        print("%%%%%%%%%%%%%")
        print(int(DNA[-self.mutate_pos][1]) - self.mutation_i )
        DNA[-self.mutate_pos][1] = int(DNA[-self.mutate_pos][1]) - self.mutation_i  # 当前层段层最高层减去当前变异量
        self.mutation_i += 1
        k, v = DNA[-self.mutate_pos]
        # print(v)

        if self.in_ban_floor(k, int(v) + 1) and not self.in_ban_floor(k, int(v)):  # 如果当前层为当前层段的最高层，通过当前层+1是否为禁用层的首层，而且当前层不在禁用层判断
            # self.dna_init[-self.mutate_pos][1] = v  # 修改dna_init,将当前位置设置成当前层段的最高值，作用：计算损失熵
            self.floor_segment_num[-self.mutate_pos] -= 1  # 本栋楼具有的层段数减去1
            self.mutate_pos += 1
            self.mutation_i = 1
            self.POP[-2] = DNA
            # TODO
            self.POP[-1] = self.get_best(self.POP.copy())
            self.first = self.POP[-1].copy()
            print(self.first)

            if self.mutate_pos > self.dna_size:  # 完成一轮，进入下一轮
                self.mutate_pos = self.get_mutate_pos(self.floor_segment_num)
                self.mutation_i = 1
        return DNA

    def get_mutate_pos(self, floor_segment_num):
        return int(np.argmax(floor_segment_num.reverse())) + 1

    def get_ban_floor_dict(self, l):
        res = {}
        for k in l:
            if input[k].values()[0]['height'] == 3.15:
                res[k] = [[11,13],[18,21]]
            else:
                res[k] = [[12,14],[19,22]]
        return res




if __name__ == '__main__':
    from api_param import *
    ban_floor_dict = {}
    for k,v in ban_floor_list.items():
        tmp = []
        for i in v:
            tmp.append([i[0],i[-1]])

        ban_floor_dict[k] = tmp

    t1 = time.time()
    res = []
    loss = []
    ef = Gao_di(theory_area=total_house_area,
                   building_num_dict=item,
                   floor_num_dict=final_floor_limit_dict,
                   ban_floor_dict=ban_floor_dict,
                   building_type=building_type,pop_size=30)
    POP = ef.init_DNA_total()
    # print(POP)

    for i in range(200):
        print("########################################")
        # ef.select(POP)
        # ef.crossover(POP)
        ef.mutate_new()

        # 找到本轮循环最好的方案
        P = ef.get_best(ef.POP)
        print(ef.loss_area(P))
        print(ef.loss_ban(P))
        print(ef.loss_building_type(P))

        # 判断结果中是否已经存在这个方案，如果没有，将这个方案放进去
        flag = False
        for i in res:
            if (P == i).all():
                flag = True
        if not flag:
            res.append(P.copy())
            loss_tmp = ef.get_fitness(P)
            loss.append(loss_tmp)
            if loss_tmp == 0:
                print(loss_tmp)
                break

    # 找到结果中，最小损失的方案
    index = np.where(np.array(loss) == min(loss))[0]
    res = np.array(res)[index]
    print(res)
    loss = np.array(loss)[index]
    print(loss)
    a = [(k, v) for k, v in zip(res, loss)]
    b = res[:, :, 1].astype(np.int)



    # #buildtype_的位置转换成buildtype的位置
    # pos_new = []
    # for i in range(len(buildtype_)):
    #     tmp = []
    #     for k, v in pos.items():
    #         if v == i:
    #             tmp.append(k)
    #     pos_new.append(tmp[int(np.random.randint(0, len(tmp), 1))])
    #
    #
    #
    # #将buildtype_对应的输出结果映射成buildtype对应的输出结果
    # b_ = np.zeros((b.shape[0],len(buildtype)))
    # for i in range(b_.shape[0]):
    #     for j in range(b_.shape[1]):
    #         if j in pos_new:
    #             print(b[i].tolist())
    #             print(j)
    #             b_[i][j] = b[i][pos_new.index(j)]
    #
    #
    # index = np.random.randint(0, b.shape[0], min([b_.shape[0], 3]))
    # return b_[index]

