# import smartutils.data.cnnum as cnnum_mod


# def test_cnnum_basic():
#     # 基本数字转换
#     assert cnnum_mod.cn2num("一百二十三") == 123
#     assert isinstance(cnnum_mod.num2cn(123), str)
#     assert cnnum_mod.cn2num("一千零一") == 1001
#     assert cnnum_mod.num2cn(1001) == "一千零零一"
#     assert cnnum_mod.cn2num("零点五") == 0.5
#     assert cnnum_mod.num2cn(0.5).startswith("零点")


# def test_cnnum_capital():
#     # 大写数字
#     assert cnnum_mod.cn2num("壹佰贰拾叁") == 123
#     assert cnnum_mod.cn2num("贰仟零壹") == 2001
#     assert cnnum_mod.cn2num("叁点壹肆") == 3.14


# def test_cnnum_special_units():
#     # 特殊单位
#     assert cnnum_mod.cn2num("一万两千") == 12000
#     assert cnnum_mod.cn2num("一亿零一万") == 100010000
#     # assert cnnum_mod.cn2num("一兆零一亿") == 1000000000100


# def test_cnnum_decimals():
#     # 小数处理
#     assert cnnum_mod.cn2num("零点零一") == 0.01
#     assert cnnum_mod.cn2num("一点二三四五") == 1.2345
#     assert cnnum_mod.cn2num("零点零零零一") == 0.0001


# def test_cnnum_edge_cases():
#     # 边界情况
#     assert cnnum_mod.cn2num("零") == 0
#     assert cnnum_mod.cn2num("一") == 1
#     assert cnnum_mod.cn2num("十") == 10
#     assert cnnum_mod.cn2num("十一") == 11
#     assert cnnum_mod.cn2num("二十") == 20
#     # 特殊写法
#     assert cnnum_mod.cn2num("两百") == 200  # "两"等价于"二"
#     assert cnnum_mod.cn2num("廿一") == 21  # "廿"等价于"二十"
#     # 错误输入
#     try:
#         cnnum_mod.cn2num("不是数字")
#     except ValueError:
#         pass
#     try:
#         cnnum_mod.cn2num("")
#     except ValueError:
#         pass
