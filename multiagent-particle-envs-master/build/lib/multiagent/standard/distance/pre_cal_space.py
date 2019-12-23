# -*- coding: utf-8 -*-
# from cal_space import CalSpace  # 精确，但时间增加十倍
import numpy as np
import math
from standard.distance.cal_space import CalSpace  # 粗略，快


class PreCalSpace:
    def pre_cal_space(self, wall1, wall2, angle, center, sign):
        # wall1, wall2 为楼栋轮廓坐标点的一维list，angle为旋转角度，center为旋转中心，sign表示检测消防最短间距或是普通的方位间距
        origin = [0, 0, 0, -1]  # 角度基准向量为正南
        if sign == "最短":
            wall1_ = np.reshape(wall1, (-1, 2))
            wall2_ = np.reshape(wall2, (-1, 2))
            center1 = [np.mean(wall1_[:, 0]), np.mean(wall1_[:, 1])]  # 求楼栋几何中心点坐标
            center2 = [np.mean(wall2_[:, 0]), np.mean(wall2_[:, 1])]
            included_angle = self.angle(origin, center1 + center2)
            res = CalSpace(wall1, wall2, center, included_angle).min_dist
        else:
            res = CalSpace(wall1, wall2, center, angle).min_dist
            

            if isinstance(res,bool) and res == False:
                sign = "最短"
                res_ = self.pre_cal_space(wall1, wall2, angle, center, sign)
                return res_
        return res
        # try:
        #     res2 = res[0]
        # except:
        #     res2 = False
        # return res2

    def angle(self, v1, v2):
        dx1 = v1[2] - v1[0]
        dy1 = v1[3] - v1[1]
        dx2 = v2[2] - v2[0]
        dy2 = v2[3] - v2[1]
        angle1 = math.atan2(dy1, dx1)
        angle1 = int(angle1 * 180 / math.pi)
        # print(angle1)
        angle2 = math.atan2(dy2, dx2)
        angle2 = int(angle2 * 180 / math.pi)
        # print(angle2)
        if angle1 * angle2 >= 0:
            included_angle = abs(angle1 - angle2)
        else:
            included_angle = abs(angle1) + abs(angle2)
            if included_angle > 180:
                included_angle = 360 - included_angle
        return included_angle
        

if __name__ == "__main__":
    # t0 = time.time()
    wall1 = [40.10123394792424, 157.7228450787633, 32.80123393070278, 157.7228450787633, 32.80123393070278, 156.52284507663492, 25.751253799884925, 156.5228267016312, 25.751253800044996, 155.52646394919807, 23.551122146713514, 155.5258784034078, 23.551344278174273, 154.67281345370398, 20.45123435261519, 154.672820284432, 20.451227011035716, 155.92282021524002, 18.15123746249481, 155.92282027167974, 18.1512374624366, 156.5228315468602, 12.001233953637328, 156.52291226868593, 12.001233954044782, 157.72284507626958, 4.701233943288006, 157.72284512395552, 4.701233943087917, 168.02283154034902, 40.10123394445361, 168.02283154065995]
    wall2 = [200.41605826792426, 53.8520668387633, 193.1160582507028, 53.8520668387633, 193.1160582507028, 52.65206683663492, 186.06607811988493, 52.6520484616312, 186.066078120045, 51.655685709198075, 183.86594646671352, 51.6551001634078, 183.86616859817428, 50.80203521370398, 180.7660586726152, 50.80204204443199, 180.76605133103573, 52.05204197524002, 178.46606178249482, 52.05204203167974, 178.4660617824366, 52.6520533068602, 172.31605827363734, 52.65213402868593, 172.3160582740448, 53.85206683626958, 165.01605826328802, 53.85206688395552, 165.01605826308793, 64.15205330034902, 200.41605826445362, 64.15205330065996]
   # 旋转楼栋令要求的遮挡射线沿着南北方向
    center = [0, 0]  # 取某楼栋的中心点
    angle = 0
    sign = "平行"
    res = PreCalSpace().pre_cal_space(wall1, wall1, angle, center, sign)
    print(res)
    # t1 = time.time()
    # print("计算一次时间：", t1 - t0)

