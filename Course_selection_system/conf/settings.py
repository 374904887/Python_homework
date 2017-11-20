#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import os
import logging


CSS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 获取Course_selection_system目录的绝对路径


# 指定存储学校对象的存储路径
# school_database_path = CSS_DIR + r"\db\school"
school_database_path = os.path.join(CSS_DIR, "db", "school")


# 定义时间格式
datetime_format = "%Y-%m-%d"


log_types = {'system': 'system.log'}  # 按照日志类型来设定存储日志的文件

log_level = logging.INFO  # 定义日志级别
