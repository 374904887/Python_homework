#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import json
from core import db_handler
from conf import settings


def load_account_info(account_id):
    """
    从文件中取出用户的数据
    :param account_id: 用户名
    :return: 返回账户余额和其它基本信息
    """""
    db_path = db_handler.db_handler(settings.DATABASE)  # db_path是保存用户数据的文件所在目录的信息
    account_file = "%s/%s.json" % (db_path, account_id)  # 目录加上文件名

    with open(account_file, "r", encoding="utf-8") as f:
        acc_data = json.load(f)  # 通过反序列化取出用户所有的信息

    return acc_data


def dump_account(account_data):
    """
    将用户数据保存到文件中
    :param account_data: 用户数据
    :return: True
    """""
    db_path = db_handler.db_handler(settings.DATABASE)  # db_path是保存用户信息的文件所在目录的信息
    account_file = "%s/%s.json" % (db_path, account_data["user"])  # 目录加上文件名

    with open(account_file, "w", encoding="utf-8") as f:
        json.dump(account_data, f)  # 通过序列化将用户所有的信息存入文件中

    return True
