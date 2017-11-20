#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import os
import datetime
import json
from conf import settings
from core import db_handler
from core import accounts


def acc_auth(account, password):
    """
    账户验证函数
    :param account: 用户输入的帐号
    :param password: 用户输入的密码
    :return:
    """""
    db_path = db_handler.db_handler(settings.DATABASE)  # db_path是保存用户信息的文件所在目录的信息
    account_file = "%s/%s.json" % (db_path, account)  # 目录加上文件名
    if os.path.isfile(account_file):
        with open(account_file, "r", encoding="utf-8") as f:
            account_data = json.load(f)  # 通过反序列化取出用户所有的信息
            if account_data["password"] == password:

                #  将字符串类型的日期时间转换成日期时间类型
                exp_time_stamp = datetime.datetime.strptime(account_data['expire_date'], "%Y-%m-%d")
                status = account_data['status']
                if datetime.datetime.now() > exp_time_stamp:
                    print("帐号%s的信用卡已过期，请申请新的信用卡" % account)
                elif status == 0 or status == 8:  # 状态正常，或为管理员
                    return account_data  # account_data是用户详细信息
                else:
                    print("帐号%s状态异常" % account)
            else:
                print("帐号或密码错误")
    else:
        print("帐号%s不存在" % account)


def acc_login(user_data, log_obj):
    """
    通过交互方式，让用户输入用户名和密码。帐号和密码正确后将认证状态改为已认证。
    :param user_data: 存在内存中的临时账户数据
    :param log_obj: 访问日志函数的logger
    :return:
    """""
    exit_count = 3  # 限制用户尝试登陆的次数
    retry_count = 0  # 记录用户登陆的次数
    same_account = 0  # 记录输入相同用户的次数
    last_account = ""  # 初始化上一次输入的用户

    while user_data["is_authenticated"] is not True and retry_count < exit_count:
        account = input("帐号(六位数字)> ").strip()
        password = input("密码> ").strip()

        if account == last_account:  # 判断本次输入的用户名和上次输入的用户名是否一样
            same_account += 1

        auth = acc_auth(account, password)
        last_account = account  # 记录本次登陆的用户名

        if auth:  # 如果auth为空，代表没有通过认证
            user_data["is_authenticated"] = True
            user_data["account_id"] = account
            return auth  # auth是用户详细信息

        retry_count += 1
    else:
        if same_account == exit_count:  # 使用相同用户名登陆三次输入的密码都错误
            log_obj.error("用户%s尝试登陆次数过多" % account)
        exit("用户%s尝试登陆次数过多, 程序退出" % account)


def acc_check(account):
    """
    查看账户是否存在
    :param account: 用户名
    :return: 帐号存在返回用户信息，帐号不存在或帐号过期则返回False
    """""
    db_path = db_handler.db_handler(settings.DATABASE)  # db_path是保存用户信息的文件所在目录的信息
    account_file = "%s/%s.json" % (db_path, account)  # 目录加上文件名

    if os.path.isfile(account_file):
        with open(account_file, "r", encoding="utf-8") as f:
            account_data = json.load(f)

            #  将字符串类型的日期时间转换成日期时间类型
            exp_time_stamp = datetime.datetime.strptime(account_data['expire_date'], "%Y-%m-%d")

            if datetime.datetime.now() > exp_time_stamp:
                print("\033[31;1m帐号[%s]已过期!\033[0m" % account)
                return False
            else:
                return account_data
    else:
        return False


def sign_up():
    """
    添加账户的函数
    :return: True
    """""
    pay_day = 22

    exist_flag = True
    while exist_flag:
        account = input("\033[32;1m用户名(六位数字): \033[0m").strip()  # 输入需要注册的用户名
        password = input("\033[32;1m密码: \033[0m").strip()  # 设置注册用户名的密码

        exist_flag = acc_check(account)  # 检查输入的用户是否存在，不存在的话exist_flag值会变成False

        if exist_flag:  # 当输入的用户名存在时exist_flag的值为用户信息
            print("用户[\033[31;1m%s\033[0m]已存在，请重新输入其它用户名" % account)
            exist_flag = True
            continue
        else:
            enroll_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 将当前的日期时间类型的年月日转换成字符串类型
            after_5_years = datetime.datetime.now().year + 5  # 5年后的年份，设定5年为过期时间
            after_5_years_today = datetime.datetime.now().replace(year=after_5_years)  # 5年后的今天
            expire_day = (after_5_years_today - datetime.timedelta(days=1)).strftime('%Y-%m-%d')  # 过期时间

            account_data = {"enroll_date": enroll_date, "balance": 0, "password": password, "id": account,
                            "credit": 15000, "status": 0, "expire_date": expire_day, "pay_day": pay_day}
            accounts.dump_account(account_data)  # 将用户的信息保存到文件中

            print("用户[\033[32;1m%s\033[0m]添加成功" % account)

            return True


def modify():
    """
    修改用户信息的函数
    :return: True
    """""
    items = ["password", "credit", "status", "expire_date", "pay_day"]  # 可以修改项目的列表

    acc_data = False
    continue_flag = False
    while acc_data is False:
        account = input("\033[32;1m用户名: \033[0m").strip()
        account_data = acc_check(account)
        if account_data is False:  # 输入用户不存在
            print("用户[\033[31;1m%s\033[0m]不存在，请输入其他用户名" % account)
            continue
        else:  # 用户存在返回的是用户信息
            while continue_flag is not True:
                print("可以修改的项目有: %s" % items)
                print("""修改格式例如: {"password": "abc", "credit": 15000, "status": 0, "expire_date": "2021-01-01", "pay_day": 22}""")

                modify_items = input("\033[32;1m输入修改的选项: \033[0m").strip()
                try:
                    modify_items_dict = json.loads(modify_items)  # 使用json将字符串类型的字典转化成真正的字典
                except Exception as e:
                    print("\033[31;1m输入的内容是json不能支持的数据类型，请重新输入\033[0m")
                    continue

                error_flag = False  # 初始化错误标记
                for index in modify_items_dict:  # 取出所输入字典的key
                    if index in items:  # 所输入字典的key在可以修改项目的列表中
                        account_data[index] = modify_items_dict[index]  # 修改
                    else:
                        print("你输入的项目[\033[31;1m%s\033[0m]为不能修改的项目" % index)
                        error_flag = True  # 输入有错误
                        break

                if error_flag:  # 输入有错误，要求重新输入
                    continue

                accounts.dump_account(account_data)  # 更新到数据库
                print("\033[32;1m用户信息更新成功!\033[0m")
                continue_flag = True
                acc_data = True

    return True
