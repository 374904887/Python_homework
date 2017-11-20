#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 获取Course_selection_system目录的绝对路径

sys.path.append(BASE_DIR)  # 将Course_selection_system目录的绝对路径加到环境变量中

from core import main

if __name__ == "__main__":
    main.Run.interactive()
