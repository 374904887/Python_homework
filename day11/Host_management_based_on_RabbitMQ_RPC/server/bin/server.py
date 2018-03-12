#!/user/bin/env python
# -*- coding:utf-8 -*-
__author__ = "Zhong Lu"


import os
import sys


# 获取server目录的绝对路径
CLIENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将server目录的绝对路径加到环境变量中
sys.path.insert(0, CLIENT_DIR)

from core import main


if __name__ == "__main__":
    main.RpcServer()
