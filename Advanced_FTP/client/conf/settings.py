#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import os


# 获取client目录的绝对路径
CLIENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ip和端口信息
ip_port = ("127.0.0.1", 55555)


# 下载的文件和上传的文件存放的路径
file_path = os.path.join(CLIENT_DIR, "file")
