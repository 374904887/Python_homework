#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import logging
import datetime
from conf import settings
from core import bill_date


def logger_function(log_type):
    """
    创建logger，并定义logger的函数
    :param log_type: 日志的类型
    :return:
    """""
    logger = logging.getLogger(log_type)  # 创建logger
    logger.setLevel(settings.log_level)  # 定义全局日志级别

    # 创建屏幕handler，并定义日志级别
    ch = logging.StreamHandler()
    ch.setLevel(settings.log_level)

    # 创建文件handler，并定义日志级别
    log_file = "%s/log/%s" % (settings.ATM_DIR, settings.log_types[log_type])  # 指定保存日志的文件
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(settings.log_level)

    # 定义日志格式，屏幕handler和文件handler采用一样的格式
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s")

    # 将定义的日志格式与屏幕handler和文件handler关联起来
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # 将屏幕handler和文件handler添加到logger中
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger


def show_log(account, log_type, year_month):
    """
    显示日志内容
    :param account: 是用户名
    :param log_type: 日志类型
    :param year_month: 年月的组合，如2017-06
    :return:
    """""
    begin_time, end_time = bill_date.get_bill_time(year_month)  # 计算出时间类型的账单开始日期和结束日期

    log_file = "%s/log/%s" % (settings.ATM_DIR, settings.log_types[log_type])  # 生成原始交易日志的绝对路径

    with open(log_file, "r", encoding="utf-8") as f:
        print("-".center(50, "-"))
        for line in f:
            # 将原始交易日志中的字符串类型时间转换成日期时间类型
            log_time = datetime.datetime.strptime(line.split(",")[0], "%Y-%m-%d %H:%M:%S")
            user_name = line.split()[11].split(":")[1]  # 获取原始交易日志中的用户名

            # 因为每个月1号生成帐单，账单是从上个月1号到上个月最后一天之间
            if account == user_name and begin_time <= log_time < end_time:
                print(line.strip())
        print("-".center(50, "-"))
