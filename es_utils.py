import numpy as np
import random
from collections import Counter


class ES_FUNC:
    def __init__(self, house_type, house_rate, totol_building, building_type,
                 cross_rate, mutation_rate, pop_size=100):
        """
        house_type: 户型
        house_rate: 户型比例
        totol_building：总户型腿数
        building_type：混拼类型
        cross_rate: 交叉率
        mutation_rate：变异率
        pop_size：一个种群中包含多少个个体
        """
        self.house_type = house_type
        self.house_rate = house_rate
        self.totol_building = totol_building
        self.building_type = building_type
        self.thera = self.get_thera(house_rate) * 10

        self.cross_rate = cross_rate
        self.mutation_rate = mutation_rate
        self.dna_size = len(self.building_type.keys())
        self.pop_size = pop_size

    def merge(self, DNA):
        merge_house = []
        for k, v in DNA:
            for key in self.building_type.get(k):
                for i in range(int(float(v))):
                    merge_house.append(key)
        self.counter = Counter(merge_house)

    #总腿数误差
    def loss_counter(self):
        dict_counter = self.counter
        sum_ = sum(dict_counter.values())
        tmp = sum_ - self.totol_building
        if tmp > 1 or tmp < 0:
            tmp = 100 * abs(tmp)
        return np.square(tmp)

    #每个户型数量与每个户型的目标值差值
    def loss_sub(self):
        houses_ = [i * self.totol_building for i in self.house_rate]
        counters = self.counter
        a = {int(k):int(v) for k,v in zip(self.house_type, houses_)}
        res = np.array([v - counters.get(k, 0) for k, v in a.items()])
        return res

    # num 所有楼型中，该方案使用了多少个楼型,使用的楼型超过 min([len(self.house_type), 4])时，给该方案一个损失
    def loss_num(self, DNA):
        num = 0
        loss = 0
        for k, v in DNA:
            if v == 0:
                num += 1
        if len(self.counter) > min([len(self.house_type), 4]):
            loss = (num - min([len(self.house_type), 4]))
        return loss

    #户型误差
    def loss_sqr(self):
        sub_ = self.loss_sub()
        return np.sum(np.square(sub_) * self.thera)

    def loss_abs(self):
        sub_ = self.loss_sub()
        return np.square(sub_.sum())

    def get_thera(self, g):
        h = np.array(g)
        i = np.argsort(g)
        j = h[list(i)]
        lst = [-1 for _ in range(len(g))]
        for o in range(len(g)):
            lst[i[::-1][o]] = j[o]
        return np.array(lst)

    def get_fitness(self, DNA):
        """
        得到一个个体(方案)的适应度
        max([fitness_loss,10])防止fitness_loss为0
        0.2 为楼型个数损失占总损失的权重
        """
        self.merge(DNA)
        fitness_loss = self.loss_counter() + self.loss_sqr()
        res = fitness_loss + max([fitness_loss,10]) * 0.2 * self.loss_num(DNA)
        # print(res)
        return res

    def get_fitness_loss_total(self, POP):
        """
        POP: 为种群
        """
        fitness_loss = [self.get_fitness(i) for i in POP]
        return fitness_loss

    def get_best(self, POP):
        fitness = [self.get_fitness(i) for i in POP]
        pop_sorted = np.argsort(fitness)
        return POP[pop_sorted]

    def init_DNA(self):
        """
        初始化一个个体
        """
        DNA = [[k, random.randint(0, 5)] for k in self.building_type.keys()]

        return DNA

    def init_DNA_total(self):
        """
        初始化一个种群
        """
        POP = [self.init_DNA() for i in range(self.pop_size)]
        return np.array(POP)

    def crossover(self, POP):
        """
        交叉过程，每个个体都可能进行交叉
        会从种群中随机选择一个个体、随机选择个体中的点，把其值赋值给被选择交叉的个体
        """
        first = self.get_best(POP)[:int(self.pop_size * 0.3)]
        for parent in POP:
            if random.random() < self.cross_rate:
                i_ = random.randrange(0, self.pop_size)  # 从种群中随机选择一个个体
                cross_points = np.random.randint(0, 2, self.dna_size).astype(np.bool)  # 随机选择个体中的点
                parent[cross_points] = POP[i_, cross_points]
        POP[self.pop_size - int(self.pop_size * 0.3):] = first
        return POP

    def mutate(self, POP):
        """
        变异过程
        """
        first = self.get_best(POP)[:int(self.pop_size * 0.3)]
        for parent in POP:
            for point in range(self.dna_size):
                x, y = parent[point]

                if random.random() < self.mutation_rate:
                    y = int(float(y)) + random.randint(-2, 3)
                    if y < 0:
                        y = 0

                parent[point] = x, y
        POP[self.pop_size - int(self.pop_size * 0.3):] = first
        return POP
