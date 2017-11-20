#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import os
import sys


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 获取ATM目录的绝对路径
sys.path.append(base_dir)  # 将ATM目录的绝对路径加到环境变量中


from core import main


if len(sys.argv) <= 1:
    exit("未检测到参数，脚本后面至少需要跟一个参数，程序结束!")

amount = int(sys.argv[1])  # 脚本后跟的第一个参数，即需要付款的金额
if amount > 0:
    result = main.pay(amount)  # 调用付款的函数结账
    if result:
        exit(0)  # result为真时，脚本退出的返回值为零
    else:
        exit(1)  # result为假时，脚本退出的返回值为非零
else:
    print("无效的付款金额，应该为一个大于零的正数")
    exit(2)
