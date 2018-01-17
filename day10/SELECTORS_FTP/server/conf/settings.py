#!/user/bin/env python
# -*- coding:utf-8 -*-
__author__ = "Zhong Lu"


import os
import logging


# 获取server目录的绝对路径
SERVER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ip和端口信息
ip_port = ("0.0.0.0", 55555)


# 用户帐号文件所在目录的绝对路径
user_database_path = os.path.join(SERVER_DIR, "db", "accounts")


# 存放用户家目录的home目录的绝对路径
home_path = os.path.join(SERVER_DIR, "home")


# 定义日志级别
log_level = logging.INFO
# 按照日志类型来设定存储日志的文件
log_types = {
    "register_login": "register_login_accounts.log",
    "command": "shell_command.log",
    "download": "download_file.log",
    "upload": "upload_file.log"
}
