#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import os
import logging


ATM_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# 指定存储用户数据的工具类型
DATABASE = {
    "engine": "file_storage",  # 还可以支持mysql
    "name": "accounts",
    "path": "%s/db" % ATM_DIR
}


log_level = logging.INFO  # 定义日志级别

# 按照交易和访问来命名两个不同的日志文件
log_types = {
    "transaction": "transactions.log",
    "access": "access.log"
}

# 指定存储用户交易日志的工具类型
LOG_DATABASE = {
    'engine': 'file_storage',  # 还可以支持mysql
    'name': 'accounts',
    'path': "%s/log" % ATM_DIR
}


# 定义每种交易类型是加钱还是扣钱，并且指定利息
TRANSACTION_TYPE = {
    'repay': {'action': 'plus', 'interest': 0},  # 还款
    'receive': {'action': 'plus', 'interest': 0},   # 接收
    'withdraw': {'action': 'minus', 'interest': 0.05},  # 提款
    'transfer': {'action': 'minus', 'interest': 0.05},  # 转出
    'pay': {'action': 'minus', 'interest': 0},  # 支付
    'save': {'action': 'plus', 'interest': 0},  # 存钱

}


BILL_DAY = 1  # 定义每个月1号生成帐单，生成从上个月1号到上个月最后一天之间的账单
