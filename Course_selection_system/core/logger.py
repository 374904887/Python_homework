#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import logging
from conf import settings


def logger_function(log_type):
    """
    创建logger，并定义logger的函数
    :param log_type: 日志的类型
    :return:
    """""
    logger = logging.getLogger(log_type)  # 创建logger
    logger.setLevel(settings.log_level)  # 定义全局日志级别

    # # 创建屏幕handler，并定义日志级别
    # ch = logging.StreamHandler()
    # ch.setLevel(settings.log_level)

    # 创建文件handler，并定义日志级别
    log_file = "%s/log/%s" % (settings.CSS_DIR, settings.log_types[log_type])  # 指定保存日志的文件
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(settings.log_level)

    # 定义日志格式，屏幕handler和文件handler采用一样的格式
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s")

    # 将定义的日志格式与屏幕handler和文件handler关联起来
    # ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # 将屏幕handler和文件handler添加到logger中
    # logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
