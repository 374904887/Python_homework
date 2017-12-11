#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import os
import logging


# 获取主机管理程序目录的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# 存放主机信息文件的目录绝对路径
host_path = os.path.join(BASE_DIR, "db", "host")


# 存放下载文件、上传文件的目录绝对路径
file_path = os.path.join(BASE_DIR, "file")


# 定义日志级别
log_level = logging.INFO
# 按照日志类型来设定存储日志的文件
log_types = {
    "command": "command.log",
    "download": "download.log",
    "upload": "upload.log"
}
