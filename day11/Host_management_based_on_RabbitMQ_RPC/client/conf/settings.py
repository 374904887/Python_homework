#!/user/bin/env python
# -*- coding:utf-8 -*-
__author__ = "Zhong Lu"


import os
import logging


# 获取client目录的绝对路径
CLIENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# rabbitmq server的ip地址
ip_address = "127.0.0.1"


# 定义日志级别
log_level = logging.INFO
# 按照日志类型来设定存储日志的文件
log_types = {
    "execute_command": "execute_command.log",
    "view_command": "view_command.log"
}
