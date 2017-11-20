#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import os
import sys


# 获取FTP目录的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将FTP目录的绝对路径加到环境变量中
sys.path.append(BASE_DIR)

from core import ftp_server

fs = ftp_server.FtpServer()
