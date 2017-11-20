#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import os
import logging


# 获取server目录的绝对路径
SERVER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ip地址和端口号
HOST = "0.0.0.0"
PORT = 55555


# 用户帐号文件所在目录的绝对路径
user_database_path = os.path.join(SERVER_DIR, "db", "accounts")


# 存放用户家目录的home目录的绝对路径
home_path = os.path.join(SERVER_DIR, "home")


# 按照日志类型来设定存储日志的文件
log_types = {'system': 'system.log'}
# 定义日志级别
log_level = logging.INFO
