#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import os
import sys


# 获取主机管理程序目录的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将主机管理程序目录的绝对路径加到环境变量中
sys.path.insert(0, BASE_DIR)

from core import main


if __name__ == "__main__":
    main.Fabric()
