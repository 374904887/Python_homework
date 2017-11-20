#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import logging
from conf import settings


def logger(log_type, *args, **kwargs):
    """
    创建logger，并定义logger的函数
    :param log_type: 日志的类型
    :param args: 用户名
    :param kwargs: 用户名
    :return:
    """""
    logger = logging.getLogger(log_type)  # 创建logger
    logger.setLevel(settings.LOG_LEVEL)  # 定义全局日志级别

    # 创建屏幕handler，并定义日志级别
    ch = logging.StreamHandler()
    ch.setLevel(settings.LOG_LEVEL)

    # 定义文件handler保存日志的文件名
    if args:
        log_file = "%s/log/%s_%s" % (settings.BASE_DIR, args[0], settings.LOG_TYPES[log_type])
    elif kwargs:
        log_file = "%s/log/%s_%s" % (settings.BASE_DIR, kwargs["user_name"], settings.LOG_TYPES[log_type])
    else:
        log_file = "%s/log/%s" % (settings.BASE_DIR, settings.LOG_TYPES[log_type])

    # 创建文件handler，并定义日志级别
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(settings.LOG_LEVEL)

    # 定义日志格式，屏幕handler和文件handler采用一样的格式
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s")

    # 将定义的日志格式与屏幕handler和文件handler关联起来
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # 将屏幕handler和文件handler添加到logger中
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger


def show_log(account, log_type):
    """
    显示日志内容
    :param account: 是用户名
    :param log_type: 日志类型
    :return:
    """""
    log_file = "%s/log/%s_%s" % (settings.BASE_DIR, account, settings.LOG_TYPES[log_type])  # 生成日志的绝对路径

    print("用户\033[32;1m%s\033[0m购物历史记录: " % account)

    with open(log_file, "r", encoding="utf-8") as f:
        print("-".center(50, "-"))
        for line in f:
            print(line.strip())
        print("-".center(50, "-"))
