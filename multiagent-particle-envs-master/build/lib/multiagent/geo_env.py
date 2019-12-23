from geopandas.geoseries import GeoSeries
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from multiagent.standard.standard_frame import standard_frame
from multiagent.standard.cal_space import CalSpace
# from standard.distance.pre_cal_space import PreCalSpace
import numpy as np
import math
import logging


class Geo_env:
    def __init__(self, red_line_raw=None, red_line=None, coord_len=8, buildinginf=None, rule_name="佛山"):

        self.rule_name = rule_name

        self.red_line_raw = red_line_raw
        if self.red_line_raw is None:
            self.red_line_raw = self.get_red_line_raw()
        self.red_line = red_line
        if self.red_line is None:
            self.red_line = self.red_line_geo(self.red_line_raw)  #.rotate(-self.get_thera(self.red_line_raw))
        self.red_line_minx, self.red_line_miny, self.red_line_maxx, self.red_line_maxy = \
            self.red_line.bounds.values[0]
        self.coord_len = coord_len
        self.buildinginf = buildinginf
        if self.buildinginf is None:
            self.buildinginf = self.get_buildinginf(self.coord_len)
        else:
            self.coord_len = len(buildinginf)

        self.coord = self.init_coord()
        self.house_type = self.get_house_type()
        self.house_type_len = len(self.house_type)
        self.house_type_key = self.house_type_dict()
        print("^^^^^^^^^^^^^^^^^^")
        print(self.house_type_key)


        # print(self.coord_len)
        # print(self.buildinginf)
        # print(len(self.buildinginf))
        self.parallel_matrix = self.gene_rel_parallel(self.house_type)
        print(self.parallel_matrix)
        self.vertical_matrix = self.gene_rel_vertical(self.house_type)
        print(self.vertical_matrix)

    # 户型外墙转换成geo对象
    def house_wall_geo(self, house_wall_raw):
        house_wall = GeoSeries(Polygon(np.reshape(house_wall_raw, (-1, 2))))
        return house_wall

    # 将所有建筑物转换成geo对象
    def house_wall_geo_total(self, DNA):
        res = []
        for i in range(self.coord_len):
            res.append(self.house_wall_geo(self.buildinginf[i]["walls"]).translate(xoff=DNA[i][0], yoff=DNA[i][1]))
        return res

    # 将外墙坐标点迁移至某点
    def house_wall_raw_translate(self, house_wall_raw, p):
        return np.reshape(np.reshape(house_wall_raw, (-1, 2)) + p, (-1,))

    # 红线生成几何图形
    def red_line_geo(self, red_line_raw):
        red_line = GeoSeries(Polygon([(i[0], i[1]) for i in red_line_raw]))
        return red_line

    # 两栋楼的最小距离
    def distance_geopandas(self, house_wall_raw1, house_wall_raw2):
        house_wall1 = self.house_wall_geo(house_wall_raw1)
        house_wall2 = self.house_wall_geo(house_wall_raw2)
        return house_wall1.distance(house_wall2)

    # 建筑物是否在红线内
    def in_area(self, p, house_wall_raw):
        """
        args:
            p: 房屋坐标，numpy类型，shape为(2, )

        returns:
            房屋在红线内返回1，否则返回0
        """
        house_wall = self.house_wall_geo(house_wall_raw)

        h1 = house_wall.translate(xoff=p[0], yoff=p[1])  # 将房屋移动到p点处
        aa = h1.within(self.red_line)  # 判断移动后的房屋是否在红线内
        return 1 if bool(aa[0]) else 0

    # 所有建筑物是否在红线内，布尔矩阵
    def in_area_total(self, DNA):
        res = []
        for i in range(self.coord_len):
            house_wall_raw = self.buildinginf[i]["walls"]
            p = DNA[i]
            res.append(self.in_area(p, house_wall_raw))
        return res

    # 建筑物位置随机初始化
    def init_coord(self):
        logging.info("建筑物位置随机初始化")
        """
        初始化一个个体
        """
        # print(self.coord_len)
        DNA = []
        i = 0
        while True:
            # 将点初始化在红线的中心位置附近
            x = float(self.red_line.centroid.x[0]) + float(np.random.normal(loc=0, scale=self.red_line_maxx/30))
            y = float(self.red_line.centroid.y[0]) + float(np.random.normal(loc=0, scale=self.red_line_maxy/30))
            # print(self.red_line_raw)
            # self.red_line.plot()
            # plt.show()
            # print(x,y)
            if not self.in_area([x, y], self.buildinginf[i]["walls"]):
                continue
            DNA.append([x, y])
            i += 1
            # print(i)
            if len(DNA) == self.coord_len:
                break
        return np.array(DNA)

    # def house_total(self, DNA):
    #     self.DNA = self.house_wall_geo_total(DNA)
    #     houses = [self.DNA.translate(xoff=i[0], yoff=i[1]) for i in DNA]
    #     return houses

    # 绘制最终结果图
    def house_plot(self, DNA):
        plt.close()
        ax = self.red_line.plot(edgecolor='red', color='white', figsize=(6, 6))
        houses = self.house_wall_geo_total(DNA)
        for i in houses:
            ax = i.plot(ax=ax, facecolor='white', edgecolor=np.random.rand(3, ))
        # plt.pause(0.1)

    # 生成平行关系间距规则矩阵，初始化执行一次
    def gene_rel_parallel(self, house_type):
        logging.info("生成平行关系间距规则矩阵，初始化执行一次")
        res = np.zeros((self.house_type_len, self.house_type_len))
        for i in range(self.house_type_len):
            for j in range(self.house_type_len):
                i_tmp = house_type[i].copy()
                j_tmp = house_type[j].copy()
                i_tmp, j_tmp = self.fake_inf(i_tmp, j_tmp, mode='parallel')
                res[i, j] = standard_frame(i_tmp, j_tmp, self.rule_name)
                logging.info(res[i,j])
                if int(res[i, j]) == 0:
                    logging.debug(i_tmp)
                    logging.debug(j_tmp)
        logging.debug("parallel_rel = " + str(res))
        return res

    # 生成山墙相对关系间距规则矩阵，初始化执行一次
    def gene_rel_vertical(self, house_type):
        logging.info("生成山墙相对关系间距规则矩阵，初始化执行一次")
        res = np.zeros((self.house_type_len, self.house_type_len))
        for i in range(self.house_type_len):
            for j in range(self.house_type_len):
                i_tmp = house_type[i].copy()
                j_tmp = house_type[j].copy()
                i_tmp, j_tmp = self.fake_inf(i_tmp, j_tmp, mode='gable-opposite')
                res[i, j] = standard_frame(i_tmp, j_tmp, self.rule_name)
        return res

    # 获得所有需要排楼的户型类型
    def get_house_type(self):
        logging.info("获得所有需要排楼的户型类型")
        house_type = []
        for i in self.buildinginf:
            for j in house_type:
                if i["name"] == j["name"]:
                    break
            else:
                house_type.append(i)
        return house_type

    # 户型名称在所有户型类型中的排位  户型名称：排位
    def house_type_dict(self):
        logging.info("户型名称在所有户型类型中的排位  户型名称：排位")
        a = {}
        for i in range(self.house_type_len):
            a[self.house_type[i]["name"]] = i
        logging.info(a)
        return a

    # 根据两栋建筑物之间的关系，填充虚拟坐标，为生成间距关系矩阵做准备
    def fake_inf(self, b_inf1, b_inf2, mode):
        logging.info("fake_inf.... 根据两栋建筑物之间的关系，填充虚拟坐标，为生成间距关系矩阵做准备")
        # 构造平行关系
        if mode == 'parallel':
            # 将建筑一放到南边
            b_inf1["coordinate"] = [50, 50]
            # 将建筑二放到北边
            b_inf2["coordinate"] = [50, 120]
        # 构造山墙相对关系
        if mode == 'gable-opposite':
            # 将建筑一放到东边
            b_inf1["coordinate"] = [100, 50]
            # 将建筑二放到西边
            b_inf2["coordinate"] = [250, 50]
        return b_inf1, b_inf2

    # 根据规则匹配得到的建筑物之间的间距要求矩阵
    def requset_distance(self, DNA):
        logging.debug("根据规则匹配得到的建筑物之间的间距要求矩阵")

        self.DNA = self.house_wall_geo_total(DNA)

        request = np.zeros((self.coord_len, self.coord_len))
        for i in range(self.coord_len):
            for j in range(i + 1, self.coord_len):

                min_xi, min_yi, max_xi, max_yi = self.DNA[i].bounds.values[0]
                min_xj, min_yj, max_xj, max_yj = self.DNA[j].bounds.values[0]

                if max_xi < min_xj or min_xi > max_xj:
                    # 山墙相对
                    i_tmp = self.house_type_key.get(self.buildinginf[i]["name"])
                    j_tmp = self.house_type_key.get(self.buildinginf[j]["name"])
                    request[i][j] = self.vertical_matrix[i_tmp, j_tmp]
                    request[j][i] = self.vertical_matrix[i_tmp, j_tmp]

                else:
                    # 平行关系
                    if max_yi < max_yj:
                        # i 在南边
                        i_tmp = self.house_type_key.get(self.buildinginf[i]["name"])
                        j_tmp = self.house_type_key.get(self.buildinginf[j]["name"])
                        request[i][j] = self.parallel_matrix[i_tmp, j_tmp]
                        request[j][i] = self.parallel_matrix[i_tmp, j_tmp]
                    else:
                        # i 在北边
                        i_tmp = self.house_type_key.get(self.buildinginf[i]["name"])
                        j_tmp = self.house_type_key.get(self.buildinginf[j]["name"])
                        request[i][j] = self.parallel_matrix[j_tmp, i_tmp]
                        request[j][i] = self.parallel_matrix[j_tmp, i_tmp]
        return request

    # 根据规则匹配得到的建筑物之间的间距要求矩阵
    def requset_distance2(self, DNA):

        logging.info("根据规则匹配得到的建筑物之间的间距要求矩阵")
        self.DNA = self.house_wall_geo_total(DNA)
        request = np.ones((self.coord_len, self.coord_len))
        for i in range(self.coord_len):
            for j in range(i + 1, self.coord_len):
                min_xi, min_yi, max_xi, max_yi = self.DNA[i].bounds.values[0]
                min_xj, min_yj, max_xj, max_yj = self.DNA[j].bounds.values[0]

                if max_xi < min_xj or min_xi > max_xj:
                    # 山墙相对
                    i_tmp = self.house_type_key.get(self.buildinginf[i]["name"])
                    j_tmp = self.house_type_key.get(self.buildinginf[j]["name"])
                    request[i][j] = self.vertical_matrix[i_tmp, j_tmp]

                else:
                    # 平行关系
                    if max_yi < max_yj:
                        # i 在南边
                        i_tmp = self.house_type_key.get(self.buildinginf[i]["name"])
                        j_tmp = self.house_type_key.get(self.buildinginf[j]["name"])
                        request[i][j] = self.parallel_matrix[i_tmp, j_tmp]

                    else:
                        # i 在北边
                        i_tmp = self.house_type_key.get(self.buildinginf[i]["name"])
                        j_tmp = self.house_type_key.get(self.buildinginf[j]["name"])
                        request[i][j] = self.parallel_matrix[j_tmp, i_tmp]

        logging.debug("间距要求是request=" + str(request))
        return request

    # 获取所有建筑物之间的距离矩阵
    def get_distance(self, DNA):
        logging.info("获取所有建筑物之间的距离矩阵")
        res = np.zeros((self.coord_len, self.coord_len))
        wall_ = [self.house_wall_raw_translate(self.buildinginf[i]["walls"], DNA[i]) for i in range(self.coord_len)]
        # print(wall_[0].tolist())
        # print(wall_[4].tolist())
        d = CalSpace(wall_[0], wall_[4], [0, 0], 0)

        for i in range(self.coord_len):
            # print(wall_[i])
            for j in range(i + 1, self.coord_len):

                temp = CalSpace(wall_[i], wall_[j], [0, 0], 0).min_dist

                # 返回布尔值，说明两建筑物无遮挡部分，用geopandas计算间距
                if isinstance(temp, bool):
                    temp = self.distance_geopandas(wall_[i], wall_[j])
                res[i, j] = temp
        logging.debug("distance = " + str(res))
        return res

    # 根据规则要求和建筑物之间的距离，获得适应度
    def get_fitness(self, DNA):
        logging.info("根据规则要求和建筑物之间的距离，获得适应度")
        request = self.requset_distance2(DNA)
        # print(request)
        distance = self.get_distance(DNA)
        res = np.clip(distance / request, 0, 1).sum()
        logging.debug("fitness = " + str(res))
        return res

    def get_fitness_matrix(self, DNA):
        logging.debug("根据规则要求和建筑物之间的距离，获得适应度的矩阵")
        request = self.requset_distance2(DNA)
        distance = self.get_distance(DNA)
        res = np.clip(distance / request, 0, 1)
        logging.debug("fitness_matrix = " + str(res))
        return res

    def get_fitness_matrix_double(self, DNA):
        res = self.get_fitness_matrix(DNA)
        res = res + res.T
        return res

    def get_buildinginf(self, coord_len):
        logging.info("未传入buildinginf信息，自动用默认值生成")
        inf = {
            "width": 35.9,
            "storey_height": 3.15,
            "walls": [17.449998287924245, -4.5249812712366975, 10.149998270702781, -4.5249812712366975,
                      10.149998270702781, -5.724981273365074, 3.1000181398849236, -5.724999648368794,
                      3.1000181400449947, -6.721362400801922, 0.8998864867135126, -6.721947946592195,
                      0.9001086181742721, -7.575012896296016, -2.2000013073848095, -7.5750060655680045,
                      -2.2000086489642854, -6.325006134759974, -4.499998197505192, -6.325006078320257, -4.4999981975634,
                      -5.7249948031397935, -10.650001706362673, -5.724914081314068, -10.65000170595522,
                      -4.524981273730418, -17.950001716711995, -4.524981226044474, -17.950001716912084,
                      5.77500519034902, 17.449998284453613, 5.775005190659954],
            "depth": 15.15,
            "layers": 18,
            "name": "YJ190n-2c(T2-17X)",
            "type": ["洋房", "住宅"],
            "area": "新区",
            "main_direction": 0,
            "gable_left": 0,
            "gable_right": 0
        }
        res = [inf for _ in range(coord_len)]
        return res

    def get_red_line_raw(self):
        logging.info("未传入red_ling_raw信息，自动用默认值生成")
        red_line_raw = [
            [
                292.97193114942945,
                69.23694509438042
            ],
            [
                270.49752129460126,
                64.43763069434544
            ],
            [
                85.57415698677241,
                0.0
            ],
            [
                71.23599136412386,
                4.609250296054995
            ],
            [
                0.0,
                157.14511236155744
            ],
            [
                9.5823888094001,
                178.8952189407151
            ],
            [
                229.81717318064543,
                252.98487683037922
            ],
            [
                245.05314478185616,
                245.4413738346188
            ],
            [
                300.8504164056261,
                82.75487187589272
            ],
            [
                292.97193114942945,
                69.23694509438042
            ]
        ]
        return red_line_raw

    def get_thera(self, red_line_raw):
        res = []
        for i in range(len(red_line_raw) - 1):
            tmp = math.pow(red_line_raw[i][0] - red_line_raw[i + 1][0], 2) + math.pow(
                red_line_raw[i][1] - red_line_raw[i + 1][1], 2)
            res.append(tmp)
        i = np.argmax(res)
        res = math.atan((red_line_raw[i][1] - red_line_raw[i + 1][1]) / (red_line_raw[i][0] - red_line_raw[i + 1][0]))
        return res * 180 / math.pi


if __name__ == '__main__':
    env = Geo_env(coord_len=12)
    ge = [[140.62748047, 52.94330564],
          [247.39694662, 143.79723604],
          [236.80482807, 195.51671906],
          [191.83433571, 223.35857811],
          [180.9226784, 144.93057402],
          [78.60116964, 55.5498785],
          [96.24964197, 173.0037561],
          [29.37610475, 154.57972094],
          [97.3946903, 115.65797914],
          [266.52925639, 83.97333117],
          [146.36648225, 203.86591255],
          [194.93076059, 66.06552163]]

    env.house_plot(ge)

    a = env.red_line.boundary.values[0]
    print(np.array(a).reshape((-1,)).tolist())

    print(env.get_fitness(ge))

    print(env.red_line_maxx)

    # ax = env.red_line.plot(edgecolor='red', color='white')
    # print(env.get_thera(env.red_line_raw))
    # env.red_line.rotate(-env.get_thera(env.red_line_raw)).plot(ax=ax,edgecolor='green', color='white',alpha=0.5 )
    # plt.show()
