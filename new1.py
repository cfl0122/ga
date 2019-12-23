    # 最终楼层数 (先假设各户型统一) 高低配算法
    def cal_final_floor_num_plan_dict(self):
        # 楼层的阀值11或者18
        floor_num_threshold = [11, 18]
        # 最终总方案
        final_floor_num_plan_dict = {}# 最终楼层数的集合
        # 新的楼栋数集合
        new_building_nums_dict = {}
        # 各密度塔楼最高层数 
        towerHighestStoreys = {}
        # 各密度塔楼最低层数
        towerLowestStoreys = {} 
        # 遍历方案
        # self.type_height
        # 各面积段实际（最接近）楼层数
        for density, floor_num_dict in self.final_floor_limit_dict.items():
            # print(density)
            # 最终单个方案
            final_floor_num_dict = {}
            # 取最高楼层数
            max_floor = 0
            for area, floor_num in floor_num_dict.items():
                if floor_num > max_floor:
                    max_floor = floor_num
            # 判断是否需要进行高低配（新逻辑必定进行高低配）
            if max_floor <= floor_num_threshold[0]:
                # 都是底层，不用高低配(转换格式)
                floor_num_dicts = {k:[v] for k,v in floor_num_dict.items()}
                final_floor_num_dict = floor_num_dicts
                # 当前方案楼栋数即是最终楼栋数
                new_building_nums = {k:[v] for k,v in self.building_num_plans_dict[density].items()}
                building_num_couple = []
                for area, building_num in self.building_num_plans_dict[density].items():
                    building_num_couple.append([building_num, area])
                building_num_couple.sort()
                info_dict = {}
                for i in range(len(building_num_couple)):
                    # 该面积下每层户数
                    area = building_num_couple[i][1]
                    house_num = self.blend[area]
                    floor_num = floor_num_dict[area]
                    # 存为字典
                    info = {"tower_num": [building_num_couple[i][0]], "area": area, "house_num": house_num, "floor_num": [floor_num]}
                    info_dict[str(i)] = info
                # 计算面积
                total_area = self.cal_area_by_info_dict(info_dict,density)
                # 选择户型 计算消化差值
                self.cal_diff_select_house(total_area, self.theory_house_area, info_dict, density)

            elif max_floor > floor_num_threshold[1]:
                # 有19层及以上，按“楼层数限制”进行高低配
                final_floor_num_dict, new_building_nums, success = self.cal_high_and_low(max_floor, floor_num_threshold[1], self.theory_house_area, self.building_num_plans_dict[density], self.section_num_dict, density)
        
                # 有时会全部降两段
                if not success:
                    final_floor_num_dict, new_building_nums, success = self.cal_high_and_low(floor_num_threshold[1],
                                                                        floor_num_threshold[0], self.theory_house_area,
                                                                        self.building_num_plans_dict[density],
                                                                        self.section_num_dict, density)
                # 继续降层(10层为限制)
                if not success:
                    final_floor_num_dict, new_building_nums, success = self.cal_high_and_low(floor_num_threshold[0],
                                                        10, self.theory_house_area,
                                                        self.building_num_plans_dict[density],
                                                        self.section_num_dict, density)
                                                                        
            else:
                # 最高层在11~18之间，按“18层”进行高低配(楼层数限制(33),楼层阀值(18),住宅的理论面积,楼栋数的4套方案,各面积段每层的户数|)
                final_floor_num_dict, new_building_nums, success = self.cal_high_and_low(floor_num_threshold[1], floor_num_threshold[0], self.theory_house_area, self. building_num_plans_dict[density], self.section_num_dict, density)
                # 继续降层(10层为限制)
                if not success:
                    final_floor_num_dict, new_building_nums, success = self.cal_high_and_low(floor_num_threshold[0],
                                                        10, self.theory_house_area,
                                                        self.building_num_plans_dict[density],
                                                        self.section_num_dict, density)
            # 当前密度最高层数
            towerHighestStoreys[density] = max(max(final_floor_num_dict.values()))
            # 当前密度最低层数
            towerLowestStoreys[density] = min(min(final_floor_num_dict.values()))
            #找到满足要求面积的最大楼层数 ---- final_floor_num_plan_dict[density]
            final_floor_num_plan_dict[density] = final_floor_num_dict
            new_building_nums_dict[density] = new_building_nums
        self.final_floor_num_plan_dict = final_floor_num_plan_dict
        # 新楼栋数方案
        self.new_building_nums_dict = new_building_nums_dict
        self.towerHighestStoreys = towerHighestStoreys
        self.towerLowestStoreys = towerLowestStoreys 

    # 高低配计算
    # 参数：1.所有楼栋限层 2.目标面积
    def cal_high_and_low(self, max_floor_limit, min_floor_limit, target_area, building_num_dict, house_num_dict,density):
        building_num_couple = list()
        for area, building_num in building_num_dict.items():
            building_num_couple.append([building_num, area])
        building_num_couple.sort()

        # 初始化为最高层数
        info_dict = {}
        for i in range(len(building_num_couple)):
            # 该面积下每层户数
            area = building_num_couple[i][1]
            house_num = len(self.blend[area])
            # 都升到最高层数(33层/18)
            # 判断该户型是否是大户型
            # if self.select_house_height[area] == 3.15 and max_floor_limit:
            #     floor_num = max_floor_limit -1
            # else:
            if self.final_floor_limit_dict[density][area] < max_floor_limit:
                floor_num = self.final_floor_limit_dict[density][area]
            else:
                floor_num = max_floor_limit
            # 存为字典
            info = {"tower_num": [building_num_couple[i][0]], "area": area, "house_num": house_num, "floor_num": [floor_num]}
            info_dict[str(i)] = info
        # 找到满足面积要求的最大楼层数
        # 增加判断是否是11层降10层
        if min_floor_limit !=10:
            success = self.find_max_min_floor_num_dict(building_num_couple, info_dict, min_floor_limit, target_area, density)
        else:
            # 11降10特殊处理
            success = self.special_find_max_min_floor_num_dict(building_num_couple, info_dict, min_floor_limit, target_area, density)
        # 重新整理格式 {115: 25, 140: 24, 180: 18}
        result_dict = {}
        # 新的楼栋数
        new_building_nums = {}
        for building_num, info in info_dict.items():
            result_dict[info["area"]] = info["floor_num"]
            new_building_nums[info['area']] = info['tower_num']
        return result_dict,new_building_nums, success


    # 特殊
    def special_find_max_min_floor_num_dict(self, building_num_couple, info_dict, min_floor_limit, target_area, density):
        # 遍历楼栋
        for i in range(len(building_num_couple)):    
            # 取信息
            info = info_dict[str(i)]
            # 存储未降层前的楼层数
            info_floor_num_copy = info['floor_num'].copy()
            # 该面积下的楼层统一降到10层
            info['floor_num'][0] = min_floor_limit
            if min_floor_limit > 18 :
                li = 19
            elif 11<=min_floor_limit<=18:
                li = 18
            else:
                li = 11
            # 此时计算总面积
            total_area = self.cal_area_by_info_dict(info_dict,density)
            data = sum(self.select_house_type_lists[density][info['area']][li]['realArea'])/2
            if self.building_area == 0:
                determine = '-data<=(total_area - target_area)<=0'
            else:
                determine =  '-data<=(total_area - target_area)<=data'
            # 如果满足条件计算总面积差是否小于等于该楼栋层面积的一半
            if eval(determine):
                total_area = self.cal_area_by_info_dict(info_dict,density)
                self.cal_diff_select_house(total_area, target_area, info_dict, density)
                return True
            # 该面积楼层降层数量过大,开始逐栋降层
            elif (target_area - total_area) > data:
                # 直接计算该户型多少栋楼应回升到11层
                if self.building_area == 0:
                    down_house_nums = math.ceil((target_area - total_area)/(sum(self.blend[info['area']])))
                else:
                    down_house_nums = round((target_area - total_area)/(sum(self.blend[info['area']])))
                info['floor_num'] = [min_floor_limit, info_floor_num_copy[0]]
                info['tower_num'] = [info['tower_num'][0] - down_house_nums, down_house_nums]
                total_area = self.cal_area_by_info_dict(info_dict,density)
                self.cal_diff_select_house(total_area, target_area, info_dict, density)
                return True

    # 找到满足面积要求的最大楼层数
    def find_max_min_floor_num_dict(self, building_num_couple, info_dict, min_floor_limit, target_area, density):
        # 遍历楼栋
        for i in range(len(building_num_couple)):
            min_floor_limits = min_floor_limit
            # 取信息
            info = info_dict[str(i)]
            if self.select_house_height[info['area']] == 3.15:     
                # 判断当前楼层的禁用楼层段
                if min_floor_limit == 18:
                    ban_floor_list = [18, 19, 20, 21]
                else:
                    ban_floor_list = [11, 12, 13]
                min_floor_limits = min_floor_limit - 1  
            else:
                if min_floor_limit == 18:
                    ban_floor_list = [19, 20, 21, 22]
                else:
                    ban_floor_list = [12, 13, 14]
            
            # 存储未降段前的楼层数
            info_floor_num_copy = info['floor_num'].copy()
            # 该面积下的楼层统一降段
            info['floor_num'][0] = min_floor_limits 
            if min_floor_limit > 18 :
                li = 19
            elif 11<=min_floor_limit<=18:
                li = 18
            else:
                li = 11
            total_area = self.cal_area_by_info_dict(info_dict,density)
            data = sum(self.select_house_type_lists[density][info['area']][li]['realArea'])/2
            if self.building_area == 0:
                determine = '-data<=(total_area - target_area)<=0'
            else:
                determine =  '-data<=(total_area - target_area)<=data'
            # 如果满足条件计算总面积差是否小于等于该楼栋层面积的一半
            if eval(determine):
                total_area = self.cal_area_by_info_dict(info_dict,density)
                # 计算消化差值、选择户型
                self.cal_diff_select_house(total_area, target_area, info_dict, density)
                return True
            # 该面积楼层降层数量过大,开始逐栋降段 
            elif (target_area - total_area) > data:
                building_floor_list = [info_floor_num_copy for i in range(int(building_num_couple[i][0]))]
                for building_nums1 in range(len(building_floor_list)):
                    # 记录当栋的层数
                    # now_floor_num = building_floor_list[building_nums1].copy()
                    building_floor_list[building_nums1] = min_floor_limits
                    info['tower_num'] = [building_nums1+1, len(building_floor_list)-building_nums1-1]
                    info['floor_num'] = [min_floor_limits, info_floor_num_copy[0]]
                    total_area = self.cal_area_by_info_dict(info_dict,density)
                    down_period_area = total_area
                    # 如果满足条件计算总面积差是否小于等于该楼栋层面积的一半
                    if eval(determine):
                        total_area = self.cal_area_by_info_dict(info_dict,density)
                        # 计算消化差值、选择户型
                        self.cal_diff_select_house(total_area, target_area, info_dict, density)
                        return True
                    # 该栋楼降层数量过大,开始该栋降层
                    elif (total_area - target_area) < -data:
                        # 将该栋回升到最高层
                        building_floor_list[building_nums1] = info_floor_num_copy[0]
                        if building_nums1 == 0:
                            info['tower_num'] = [len(building_floor_list) - building_nums1]
                            info['floor_num'] = [building_floor_list[building_nums1]]
                        else:
                            info['tower_num'] = [building_nums1, len(building_floor_list) - building_nums1]
                            info['floor_num'] = [min_floor_limits, building_floor_list[building_nums1]]
                        total_area = self.cal_area_by_info_dict(info_dict,density)
                        area_diff = total_area - target_area
                        if area_diff < 0:
                            self.cal_diff_select_house(total_area, target_area, info_dict, density)
                            return True
                        if self.building_area == 0:
                            down_floor_nums = math.ceil(area_diff / (data*2))
                        else:
                            down_floor_nums = round(area_diff / (data*2))
                        building_floor_list[building_nums1] -= down_floor_nums
                        # 楼栋数只有一栋---------------------------
                        if len(building_floor_list) == 1:
                            if building_floor_list[building_nums1]  in ban_floor_list:
                                # 判断是否是最后一个户型
                                if i == len(building_num_couple) - 1:
                                    # 阀值层差
                                    threshold_diff = target_area - down_period_area
                                    info['tower_num'] = [len(building_floor_list)-building_nums1]
                                    info['floor_num'] = [ban_floor_list[-1] + 1]
                                    total_area = self.cal_area_by_info_dict(info_dict,density)
                                    # 禁用层邻层差
                                    ban_next_diff = target_area - total_area
                                    # 比较阀值层和禁用层的邻层
                                    if threshold_diff > ban_next_diff:
                                        total_area = self.cal_area_by_info_dict(info_dict,density)
                                        # 计算消化差值、选择户型
                                        self.cal_diff_select_house(total_area, target_area, info_dict, density)
                                        return True
                                    else:
                                        # 所有栋降段
                                        info['tower_num'] = [len(building_floor_list) + 1]
                                        info['floor_num'] = [min_floor_limits]
                                        total_area = self.cal_area_by_info_dict(info_dict,density)
                                        # 计算消化差值、选择户型
                                        self.cal_diff_select_house(total_area, target_area, info_dict, density)
                                        return True
                                else:
                                    continue
                            else:
                                info['tower_num'] = [1]
                                info['floor_num'] = [building_floor_list[building_nums1]]
                                total_area = self.cal_area_by_info_dict(info_dict,density)
                                # 计算消化差值、选择户型
                                self.cal_diff_select_house(total_area, target_area, info_dict, density)     
                                return True
                    
                        # 降段到最后一栋---------------
                        elif len(building_floor_list) != 1 and building_nums1 == len(building_floor_list) - 1:
                            if building_floor_list[building_nums1]  in ban_floor_list:
                                # 判断该户型是中间户型还是最后降段户型
                                if i < len(building_num_couple) - 1: # 中间户型
                                    flag = self.cal_digestion_floor(info,building_nums1, building_floor_list, info_floor_num_copy[0], down_floor_nums,ban_floor_list)
                                    if flag == True:
                                        total_area = self.cal_area_by_info_dict(info_dict,density)
                                        self.cal_diff_select_house(total_area, target_area, info_dict, density)
                                        return True
                                    else:
                                        continue
                
                                elif i == len(building_num_couple)-1: # 最后一个户型段(最后一栋)
                                    # 同上处理 区别：优先进行最后一栋降邻层处理，然后进行其它栋平均降层
                                    flag = self.cal_digestion_end_floor(info,building_nums1, building_floor_list, info_floor_num_copy[0], down_floor_nums,target_area,density,ban_floor_list)
                                    total_area = self.cal_area_by_info_dict(info_dict,density)
                                    self.cal_diff_select_house(total_area, target_area, info_dict, density)
                                    return True
                            else:
                                if min_floor_limits == building_floor_list[building_nums1]:
                                    info['tower_num'] = [building_nums1+1]
                                    info['floor_num'] = [min_floor_limits]
                                else:
                                    # 不在禁用层
                                    info['tower_num'] = [building_nums1, 1]
                                    info['floor_num'] = [min_floor_limits, building_floor_list[building_nums1]]
                                total_area = self.cal_area_by_info_dict(info_dict,density)
                                # 计算消化差值、选择户型
                                self.cal_diff_select_house(total_area, target_area, info_dict, density)
                                return True

                        # 中间栋数-------------------
                        # 首先判断是否在禁用层
                        else:
                            # 首先把该层恢复到最高层，然后将回升层转换成降层
                            building_floor_list[building_nums1] = building_floor_list[-1]
                            down_avg_nums = down_floor_nums / (info['tower_num'][-1])
                            decimal_floor = math.modf(down_avg_nums)[0]
                            integer_floor = math.modf(down_avg_nums)[1]
                            if decimal_floor == 0:
                                # 将降层平均分配给剩下的楼栋
                                info['floor_num'] = [min_floor_limits, info_floor_num_copy[0] - integer_floor]
                                info['tower_num'] = [building_nums1, len(building_floor_list) - building_nums1]
                                # 当前面积
                                total_area = self.cal_area_by_info_dict(info_dict,density)
                                # 计算消化差值、选择户型
                                self.cal_diff_select_house(total_area, target_area, info_dict, density)
                                return True
                            else:
                                extry_floor = round(decimal_floor * (info['tower_num'][-1])) 
                                info['floor_num'] = [min_floor_limits, building_floor_list[-1][0] - integer_floor -1, building_floor_list[-1][0] - integer_floor]
                                info['tower_num'] = [building_nums1, extry_floor, len(building_floor_list) - building_nums1 - extry_floor]
                                # 当前面积
                                total_area = self.cal_area_by_info_dict(info_dict,density)
                                # 计算消化差值、选择户型
                                self.cal_diff_select_house(total_area, target_area, info_dict, density)
                                return True


    # 逐栋-降段（降层-禁用层）进行层数消化           
    def cal_digestion_floor(self, info, building_nums1, building_floor_list, info_floor_num_copy, down_floor_nums,ban_floor_list):
        down_min_floor = 0
        if self.select_house_height[info['area']] == 3.15:
            down_min_floor = 1
        # 所有楼栋降层数（到禁用层）总和
        if building_floor_list[0] == 18 - down_min_floor:
            # 到禁用层邻层层数
            down_next_nums = 3 
            if info_floor_num_copy in ban_floor_list:
                sum_down_floors = building_nums1 * 3 - down_min_floor + info_floor_num_copy - building_floor_list[0]
            else:
                sum_down_floors = building_nums1 * 3 + (info_floor_num_copy - 23 - down_min_floor)

        elif building_floor_list[0] == 11 - down_min_floor:
            # 到禁用层邻层层数
            down_next_nums = 1
            if info_floor_num_copy in ban_floor_list:
                sum_down_floors = building_nums1 - down_min_floor + (info_floor_num_copy - 11)
            else:
                sum_down_floors = building_nums1 + 3 - down_min_floor
        # 判断前面楼栋消化了多少层（是否能够消化完）
        if building_nums1 * down_next_nums >= down_floor_nums:
            down_avg_nums = down_floor_nums / building_nums1
            decimal_floor = math.modf(down_avg_nums)[0]
            integer_floor = math.modf(down_avg_nums)[1]
            if decimal_floor == 0:
                # 将降层数平均分配给剩下的楼栋
                info['floor_num'] = [building_floor_list[0] - integer_floor, info_floor_num_copy]
                info['tower_num'] = [building_nums1, len(building_floor_list) - building_nums1]
                return True
            else:
                extry_floor = round(decimal_floor * building_nums1) 
                info['floor_num'] = [building_floor_list[0] - integer_floor -1, building_floor_list[0] - integer_floor, info_floor_num_copy]
                info['tower_num'] = [extry_floor,building_nums1- extry_floor, len(building_floor_list) - building_nums1]
                return True
        else:
            # 判断所有楼栋降到禁用层是否能够消化
            if sum_down_floors >= down_floor_nums:
                info['floor_num'] = [building_floor_list[0] - down_next_nums, info_floor_num_copy - (down_floor_nums - building_nums1 * down_next_nums)]
                info['tower_num'] = [building_nums1, len(building_floor_list) - building_nums1]
                return True
            else:
                info['floor_num'] = [building_floor_list[0], info_floor_num_copy]
                info['tower_num'] = [building_nums1, len(building_floor_list) - building_nums1]
                return False      

    # 最后一个户型(逐栋-降段（降层-禁用层）进行层数消化)
    def cal_digestion_end_floor(self, info,building_nums1, building_floor_list, info_floor_num_copy, down_floor_nums,target_area,density,ban_floor_list):
        down_min_floor = 0
        
        if self.select_house_height[info['area']] == 3.15:
            down_min_floor = 1
        # 所有楼栋降层数（到禁用层）总和
        if building_floor_list[0] == 18 - down_min_floor:
            # 降到禁用层邻层层数
            down_next_nums = 3 
            if info_floor_num_copy in ban_floor_list:
                sum_down_floors = building_nums1 * 3 + (info_floor_num_copy - building_floor_list[0]) - down_min_floor
                next_ban_floor = 18 - down_min_floor
            else:
                sum_down_floors = building_nums1 * 3 + (info_floor_num_copy - 23 - down_min_floor)
                next_ban_floor = 23 - down_min_floor
        elif building_floor_list[0] == 11 - down_min_floor:
            # 降到禁用层邻层层数
            down_next_nums = 1
            if info_floor_num_copy in ban_floor_list:
                sum_down_floors = building_nums1 + info_floor_num_copy - building_floor_list[0] - down_min_floor
                next_ban_floor = info_floor_num_copy - building_floor_list[0]
            else:
                sum_down_floors = building_nums1 + 3 - down_min_floor
                next_ban_floor = 15 - down_min_floor
        # 区别: 先全局判断是否能够消化，若能消化，则优先最后一栋进行层数消化   
        if sum_down_floors < down_floor_nums: # 不能够消化
            # 若不能够消化(全体降为该层段的阀值层邻层)，再与该栋降段  进行消化差值的比较
            info['floor_num'] = [building_floor_list[0] - down_next_nums, next_ban_floor]
            info['tower_num'] = [building_nums1, len(building_floor_list) - building_nums1]
            total_area = self.cal_area_by_info_dict(info_dict,density)
            all_area_diff_next = abs(total_area - target_area)
            info['floor_num'] = [building_floor_list[0]]
            info['tower_num'] = [len(building_floor_list)]
            all_area_diff_period = abs(total_area - target_area)
            if all_area_diff_period < all_area_diff_next:
                return True
            else:
                info['floor_num'] = [building_floor_list[0] - down_next_nums, next_ban_floor]
                info['tower_num'] = [building_nums1, len(building_floor_list) - building_nums1]
                return True
        else:
            # 能够消化,优先降最后一栋
            # 最后一栋可降层数
            down_floor_nums_last = info_floor_num_copy - next_ban_floor
            final_down_floor_nums = down_floor_nums - down_floor_nums_last
            down_avg_nums = final_down_floor_nums  / building_nums1
            decimal_floor = math.modf(down_avg_nums)[0]
            integer_floor = math.modf(down_avg_nums)[1]
            if decimal_floor == 0:
                # 将降层数平均分配给剩下的楼栋
                info['floor_num'] = [building_floor_list[0] - integer_floor, next_ban_floor]
                info['tower_num'] = [building_nums1, len(building_floor_list) - building_nums1]
                return True
            else:
                # 额外再降一层
                extry_floor = round(decimal_floor * building_nums1) 
                info['floor_num'] = [building_floor_list[0] - integer_floor -1, building_floor_list[0] - integer_floor, next_ban_floor]
                info['tower_num'] = [extry_floor,building_nums1- extry_floor, len(building_floor_list) - building_nums1]
                return True
            

    # 计算总面积                           
    def cal_area_by_info_dict(self,info_dict,density):
        # 首先选择户型-再计算面积
        total_area = 0
        # 大厅面积
        hall_area = 15
        for info in info_dict.values():
            for count in range(len(info['tower_num'])):      
                # 户型楼层段
                floors = 11
                if info['floor_num'][count] > 18:
                    floors = 19
                elif info['floor_num'][count] > 11:
                    floors = 18
                house_type = self.select_house_type_lists[density][info['area']][floors]
                if self.json_para["projectInfo"]["overHead"] == '1':
                    hall_area = 100
                    floor_nums = info['floor_num'][count] - 1
                else:
                    floor_nums = info['floor_num'][count] 
                total_area += info['tower_num'][count] * floor_nums * sum(house_type['realArea']) + hall_area * info['tower_num'][count]
                # for house_type in self.select_house_type_lists[info['area']]:
                #     key = [i for i in house_type.keys()]
                #     if key[0] == floors:
                #         # 计算真实总面积
                #         total_area += info['tower_num'][count] * info['floor_num'][count] * sum(house_type[floors]['realArea']) + hall_area * info['tower_num'][count]
                #         break

        return total_area