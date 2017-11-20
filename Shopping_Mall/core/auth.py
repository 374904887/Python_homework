#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import os
import json
import datetime
from core import db_handler
from conf import settings
from core import accounts


def acc_auth(account, password):
    """
    账户验证函数
    :param account: 用户输入的帐号
    :param password: 用户输入的密码
    :return: 用户详细数据
    """""
    db_path = db_handler.db_handler(settings.DATABASE)  # db_path是保存用户信息的文件所在目录的信息
    account_file = "%s/%s.json" % (db_path, account)  # 目录加上文件名
    if os.path.isfile(account_file):
        with open(account_file, "r", encoding="utf-8") as f:
            account_data = json.load(f)  # 通过反序列化取出用户所有的信息
            if account_data["password"] == password:
                return account_data
            else:
                print("密码错误")
    else:
        print("帐号%s不存在" % account)


def acc_login(user_data, log_obj):
    """
    帐号登陆函数
    :param user_data: 存在内存中的临时账户数据
    :param log_obj: 访问日志函数的logger对象
    :return: 用户详细数据
    """""
    exit_count = 3  # 限制用户尝试登陆的次数
    retry_count = 0  # 记录用户登陆的次数
    same_account = 0  # 记录输入相同用户的次数
    last_account = ""  # 初始化上一次输入的用户

    while user_data["is_authenticated"] is not True and retry_count < exit_count:
        account = input("帐号> ").strip()
        password = input("密码> ").strip()

        if account == last_account:  # 判断本次输入的用户名和上次输入的用户名是否一样
            same_account += 1

        auth = acc_auth(account, password)
        if auth:  # 如果auth为空，代表没有通过认证
            user_data["is_authenticated"] = True
            user_data["account_id"] = account
            money = auth["balance"]  # 记录用户余额
            old_money = money  # 旧余额
            return auth  # auth是用户详细数据

        last_account = account  # 记录本次登陆的用户名
        retry_count += 1
    else:
        if same_account == exit_count:  # 使用相同用户名登陆三次输入的密码都错误
            log_obj.error("用户%s尝试登陆次数过多" % account)
        exit("用户%s尝试登陆次数过多, 程序退出" % account)


def acc_check(account):
    """
    查看账户是否存在
    :param account: 用户名
    :return: 帐号存在返回用户信息，帐号不存在返回False
    """""
    db_path = db_handler.db_handler(settings.DATABASE)  # db_path是保存用户信息的文件所在目录的信息
    account_file = "%s/%s.json" % (db_path, account)  # 目录加上文件名

    if os.path.isfile(account_file):
        with open(account_file, "r", encoding="utf-8") as f:
            account_data = json.load(f)

            return account_data


def sign_up(user_data):
    """
    用户注册的函数
    :param user_data: 存在内存中的临时账户数据
    :return: True
    """""
    exit_flag = True
    while exit_flag is True:
        user = input("\033[32;1m用户名: \033[0m").strip()
        password = input("\033[32;1m密码: \033[0m").strip()

        exit_flag = acc_check(user)
        if exit_flag:
            print("帐号[\033[31;1m%s\033[0m]存在，请输入其它帐号" % user)
            exit_flag = True
            continue

        else:
            today = datetime.datetime.now().strftime('%Y-%m-%d')  # 将当前的日期时间类型时间转换成字符串类型
            account_data = {"enroll_date": today, "balance": 0, "password": password, "user": user, "status": 0}

            accounts.dump_account(account_data)  # 将用户数据保存到文件中
            print("帐号注册成功!")

            user_data['is_authenticated'] = True
            user_data['user'] = user
            user_data['account_data'] = account_data

            return True
