#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import os
import logging


# 获取FTP目录的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ip和端口信息
ip_port = ("127.0.0.1", 6666)


# 用户帐号文件所在目录的绝对路径
user_database_path = os.path.join(BASE_DIR, "db", "accounts")


# 用户家目录的绝对路径
user_home_path = os.path.join(BASE_DIR, "home")


# 按照日志类型来设定存储日志的文件
log_types = {'system': 'system.log'}
# 定义日志级别
log_level = logging.INFO
