# 禁用层
ban_floor_list = {'YJ140n-6':[[19, 20, 21, 22], [12, 13, 14]],
				  'YJ180n-4b':[[19, 20, 21, 22], [12, 13, 14]],
				  'YJY140&105n-1':[[19, 20, 21, 22], [12, 13, 14]]}

# 各户型层高
house_height = {'YJ140n-6': 2.95, 'YJ140n-9': 2.95, 'YJ180n-4b': 3.15, 'YJ180n-5': 3.15, 'YJY140&105n-1': 2.95}

# 住宅理论总面积
total_house_area = 110728.04

# 各户型栋数
item = {'YJ140n-6': 5.0, 'YJ180n-4b': 5.0, 'YJY140&105n-1': 5.0}

# 各户型理论最高层数
final_floor_limit_dict = {'YJ140n-6': 27, 'YJ180n-4b': 25, 'YJY140&105n-1': 27}

# 户型选择:
building_type = {
	'YJ140n-6': {
		19.0: {
			'geometricInfo': {
				'length': 30.200000548391472,
				'width': 13.650002275537872
			},
			'houseType': '四房两厅两卫',
			'flatStatus': 'BZT-CPT001-001-004-001',
			'floors': 19.0,
			'floorNumbers': [1.0, 1.0],
			'name': 'YJ140n-6(T2-18X)（占坑）-19',
			'theoreticalArea': [140.0, 140.0],
			'houseCount': 2.0,
			'realArea': [143.61, 143.42],
			'rightWall': 0,
			'height': 2.95,
			'leftWall': 0
		},
		18.0: {
			'geometricInfo': {
				'length': 30.200000548391472,
				'width': 13.650002275537872
			},
			'houseType': '四房两厅两卫',
			'flatStatus': 'BZT-CPT001-001-004-001',
			'floors': 18.0,
			'floorNumbers': [1.0, 1.0],
			'name': 'YJ140n-6(T2-18X)',
			'theoreticalArea': [140.0, 140.0],
			'houseCount': 2.0,
			'realArea': [143.61, 143.42],
			'rightWall': 0,
			'height': 2.95,
			'leftWall': 0
		},
		11.0: {
			'geometricInfo': {
				'length': 29.800000003527202,
				'width': 14.700000059396416
			},
			'houseType': '四房两厅两卫',
			'flatStatus': 'BZT-CPT001-001-004-001',
			'floors': 11.0,
			'floorNumbers': [1.0, 1.0],
			'name': 'YJ140n-6(T2-11X)',
			'theoreticalArea': [140.0, 140.0],
			'houseCount': 2.0,
			'realArea': [140.62, 140.62],
			'rightWall': 0,
			'height': 2.95,
			'leftWall': 0
		}
	},
	'YJ180n-4b': {
		18.0: {
			'geometricInfo': {
				'length': 35.39979146535006,
				'width': 14.250041367158701
			},
			'houseType': '四房两厅三卫',
			'windowsillHeight': '0.9',
			'flatStatus': 'BZT-CPT001-001-004-001',
			'floors': 18.0,
			'floorNumbers': [1.0, 1.0, 0.0, 0.0],
			'name': 'YJ180n-4b(T2-17X)',
			'theoreticalArea': [180.0, 180.0],
			'houseCount': 2.0,
			'realArea': [187.06, 188.1],
			'height': 3.15
		},
		19: {
			'geometricInfo': {
				'length': 35.39979146535006,
				'width': 14.250041367158701
			},
			'houseType': '四房两厅三卫 ',
			'windowsillHeight ': '0.9 ',
			'name': 'YJ180n-4b(T2-17X)(代替26层段)',
			'theoreticalArea': [180.0, 180.0],
			'houseCount': 2.0,
			'realArea': [191.06, 192.1],
			'height': 3.15,
			'type_floor': 19,
			'real_house_name': 'YJ180n-4b(T2-17X)',
			'ghost': 2
		}, 
		11: {
		'geometricInfo': {
			'length': 35.39979146535006,
			'width': 14.250041367158701
		},
		'houseType': '四房两厅三卫',
		'windowsillHeight': '0.9',
		'flatStatus': 'BZT-CPT001-001-004-001',
		'floors': 18.0,
		'floorNumbers': [1.0, 1.0, 0.0, 0.0],
		'name': 'YJ180n-4b(T2-17X)(代替11层段)',
		'theoreticalArea': [180.0, 180.0],
		'houseCount': 2.0,
		'realArea': [183.06, 184.1],
		'height': 3.15,
		'real_house_name': 'YJ180n-4b(T2-17X)',
		'type_floor': 11,
		'ghost': 2
		}
	}, 
	'YJY140&105n-1': {
		19.0: {
			'geometricInfo': {
				'length': 37.87481237383872,
				'width': 26.434569777345587
			},
		'houseType': '四房两厅两卫|三房两厅两卫',
		'windowsillHeight': '0.9',
		'flatStatus': 'BZT-CPT001-001-004-011',
		'floors': 19.0,
		'floorNumbers': [1.0, 1.0, 2.0],
		'name': 'YJY140&105n-1(T4-33X)',
		'theoreticalArea': [140.0, 140.0, 105.0, 105.0],
		'houseCount': 4.0,
		'realArea': [128.0, 141.97, 105.32, 105.32],
		'height': 2.95
	},
		18: {
		'geometricInfo': {
			'length': 37.87481237383872,
			'width': 26.434569777345587
		},
		'houseType': '四房两厅两卫|三房两厅两卫',
		'windowsillHeight': '0.9',
		'flatStatus': 'BZT-CPT001-001-004-011',
		'floors': 19.0,
		'floorNumbers': [1.0, 1.0, 2.0],
		'name': 'YJY140&105n-1(T4-33X)(代替18层段)',
		'theoreticalArea': [140.0, 140.0, 105.0,
			105.0
		],
		'houseCount': 4.0,
		'realArea': [126.0, 139.97, 103.32, 103.32],
		'height': 2.95,
		'type_floor': 18,
		'real_house_name': 'YJY140&105n-1(T4-33X)',
		'ghost': 3
	},
		11: {
		'geometricInfo': {
			'length': 37.87481237383872,
			'width': 26.434569777345587
		},
		'houseType': '四房两厅两卫|三房两厅两卫 ', 
		'windowsillHeight ': '0.9 ',
		'flatStatus': 'BZT-CPT001-001-004-011',
		'floors': 19.0, 
		'floorNumbers': [1.0, 1.0, 2.0], 
		'name': 'YJY140&105n-1(T4-33X)(代替11 层段)', 
		'theoreticalArea ': [140.0, 140.0, 105.0, 105.0],
		'houseCount ': 4.0,
		'realArea': [124.25, 138.22, 101.57, 101.57],
		'height ': 2.95, 
		'type_floor': 11, 'real_house_name': 'YJY140&105n-1(T4-33X)', 'ghost': 3
		}
	}, 
	'YJ140n-9': {
		18.0: {
		'geometricInfo': {
			'length': 29.499999992229277,
			'width': 13.349993149405236
		},
		'houseType': '四房两厅两卫',
		'windowsillHeight': '0.9',
		'flatStatus': 'BZT-CPT001-001-004-001',
		'floors': 18.0,
		'floorNumbers': [1.0, 1.0],
		'name': 'YJ140n-9(T2-18X)',
		'theoreticalArea': [140.0, 140.0],
		'houseCount': 2.0,
		'realArea': [141.19, 142.92],
		'height': 2.95
	},
		19: {
			'geometricInfo': {
				'length': 29.499999992229277,
				'width': 13.349993149405236
			},
		'houseType': '四房两厅两卫',
		'windowsillHeight': '0.9',
		'flatStatus': 'BZT-CPT001-001-004-001',
		'floors': 18.0,
		'floorNumbers': [1.0, 1.0],
		'name': 'YJ140n-9(T2-18X)(代替26层段)',
		'theoreticalArea': [140.0, 140.0],
		'houseCount': 2.0,
		'realArea': [145.19, 146.92],
		'height': 2.95,
		'type_floor': 19,
		'real_house_name': 'YJ140n-9(T2-18X)',
		'ghost': 2
	},
		11: {
			'geometricInfo': {
				'length': 29.499999992229277,
				'width': 13.349993149405236
			},
		'houseType': '四房两厅两卫',
		'windowsillHeight': '0.9',
		'flatStatus': 'BZT-CPT001-001-004-001',
		'floors': 18.0,
		'floorNumbers': [1.0, 1.0],
		'name': 'YJ140n-9(T2-18X)(代替11层段)',
		'theoreticalArea ': [140.0, 140.0],
		'houseCount ': 2.0,
		'realArea ': [137.19, 138.92], 
		'height ': 2.95,
		'real_house_name ': 'YJ140n - 9(T2 - 18 X)', 
		'type_floor ': 11, 
		'ghost ': 2}},
		
	'YJ180n - 5 ': {
		19.0: {
		'geometricInfo ': {'length ': 34.09917167686194, 'width ': 17.099999999263787}, 
		'houseType ': '四房两加一厅三卫 ',
		'windowsillHeight ': '0.9 ', 
		'floors': 19.0,
		'name ': 'YJ180n - 5(T2 - 31 X)',
		'theoreticalArea ': [180.0, 180.0], 
		'houseCount ': 2.0, 
		'realArea ': [192.29, 192.29], 
		'height ': 3.15}, 
		
		18.0: {
		'geometricInfo ': {'length ': 34.699171930719785, 'width ': 14.550000465950916}, 
		'houseType ': '四房两 + 1 厅三卫 ',
		'floors': 18.0,
		'name': 'YJ180n-5(T2-17X)', 
		'theoreticalArea': [180.0, 180.0], 
		'houseCount': 2.0, 
		'realArea': [184.03, 184.03],
		'height': 3.15
	}, 
	11: {
		'geometricInfo': {
			'length': 34.699171930719785,
			'width': 14.550000465950916
		},
		'houseType': '四房两+1厅三卫',
		'windowsillHeight': '0.9',
		'floors': 18.0,
		'floorNumbers': [2.0, 0.0],
		'name': 'YJ180n-5(T2-17X)(代替11层段)',
		'theoreticalArea': [180.0, 180.0],
		'houseCount': 2.0,
		'realArea': [180.03, 180.03],
		'height': 3.15,
		'type_floor': 11,
		'real_house_name': 'YJ180n-5(T2-17X)',
		'ghost': 2
	}
	}
	}