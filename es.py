from es_utils import ES_FUNC
import time
import numpy as np
import math

# 各类参数
cross_rate = 1.  # 交叉率
mutation_rate = 1.  # 变异率
pop_size = 50  # 种群大小

house_dict = {90: 40, 115: 30, 140: 30}
house_dict = {'105': 40.0, '140': 30.0, '180': 30.0}

buildtype = [[115, 115, 90], [90, 90, 115], [140, 90, 115]]
buildtype = [[105.0, 105.0], [180.0, 180.0], [140.0, 140.0], [140.0, 140.0], [140.0, 140.0], [180.0, 180.0],
             [180.0, 180.0], [140.0, 140.0], [140.0, 140.0], [140.0, 140.0], [180.0, 180.0], [140.0, 140.0],
             [140.0, 140.0]]
totol_building = 40


# 应可能有多个结果，返回类型为二维numpy矩阵，矩阵每一行对应一个结果
def main(house_dict, totol_building, buildtype):
    house_type = []
    house_rate = []
    for i, j in house_dict.items():
        house_type.append(i)
        house_rate.append(j / 100.0)

    # buildtype_ 新的无重复混拼类型的buildtype
    buildtype_ = []
    j = 0
    pos = {}
    for i in range(len(buildtype)):
        tmp = sorted(buildtype[i])
        if tmp not in buildtype_:
            buildtype_.append(tmp)
            pos[i] = j
            j += 1
        else:
            j_ = buildtype_.index(tmp)
            pos[i] = j_

    building_type = {i: j for i, j in enumerate(buildtype_)}
    totol_building = math.ceil(totol_building)

    t1 = time.time()
    res = []
    loss = []
    ef = ES_FUNC(house_type, house_rate, totol_building, building_type,
                 cross_rate, mutation_rate, pop_size)

    POP = ef.init_DNA_total()

    for i in range(100 * len(building_type)):
        # ef.select(POP)
        ef.crossover(POP)
        ef.mutate(POP)

        # 找到本轮循环最好的方案
        P = ef.get_best(POP)[0]

        # 判断结果中是否已经存在这个方案，如果没有，将这个方案放进去
        flag = False
        for i in res:
            if (P == i).all():
                flag = True
        if not flag:
            res.append(P.copy())
            loss.append(ef.get_fitness(P))

    # 找到结果中，最小损失的方案
    index = np.where(np.array(loss) == min(loss))[0]
    res = np.array(res)[index]
    loss = np.array(loss)[index]
    print(loss)
    a = [(k, v) for k, v in zip(res, loss)]
    b = res[:, :, 1].astype(np.int)



    #buildtype_的位置转换成buildtype的位置
    pos_new = []
    for i in range(len(buildtype_)):
        tmp = []
        for k, v in pos.items():
            if v == i:
                tmp.append(k)
        pos_new.append(tmp[int(np.random.randint(0, len(tmp), 1))])



    #将buildtype_对应的输出结果映射成buildtype对应的输出结果
    b_ = np.zeros((b.shape[0],len(buildtype)))
    for i in range(b_.shape[0]):
        for j in range(b_.shape[1]):
            if j in pos_new:
                print(b[i].tolist())
                print(j)
                b_[i][j] = b[i][pos_new.index(j)]


    index = np.random.randint(0, b.shape[0], min([b_.shape[0], 3]))
    return b_[index]


if __name__ == '__main__':
    t1 = time.time()
    main(house_dict, totol_building, buildtype)
    print(time.time() - t1)
