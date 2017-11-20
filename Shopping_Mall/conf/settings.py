#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import os
import logging


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 指定存储用户数据的文件类型
DATABASE = {
    'engine': 'file_storage',
    'name': 'accounts',
    'path': "%s/db" % BASE_DIR
}


LOG_LEVEL = logging.INFO  # 定义日志级别

# 按照购物和访问来命名两个不同的日志文件
LOG_TYPES = {
    'shopping': 'shopping.log',
    'access': 'access.log',
}
