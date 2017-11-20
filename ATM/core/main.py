#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import time
import datetime
import os
from core import auth
from core import logger
from core import accounts
from core import transaction
from core import db_handler
from conf import settings


# 获取交易日志的logger对象
trans_logger = logger.logger_function("transaction")

# 获取登陆日志的logger对象
access_logger = logger.logger_function("access")

# 临时的账户数据，数据只存在内存中
user_data = {
    "account_id": None,  # 用户名
    "is_authenticated": False,  # 是否认证
    "account_data": None  # 用户详细信息，如密码、信用额度、余额、状态等信息
}


def display_account_info(account_data):
    """
    打印用户的信息
    :param account_data: 是用户信息
    :return: None
    """""
    ignore_display = "password"

    for key in account_data:
        if key in ignore_display:
            continue
        else:
            print("{:<20}:\033[32;1m{:<20}\033[0m".format(key, account_data[key]))


def account_info(acc_data):
    """
    从账户数据中取出用户的信息，并调用打印用户信息的函数
    :param acc_data: 是账户数据
    :return: True
    """""
    account_data = acc_data["account_data"]  # 从账户数据中取出用户的信息
    display_account_info(account_data)

    return True


def repay(acc_data):
    """
    打印当前余额，并提供还款功能的函数
    :param acc_data: 是账户数据
    :return: None
    """""
    account_data = accounts.load_current_balance(acc_data["account_id"])  # account_data是最新的用户信息

    current_balance = """ --------- 余额信息 --------
        信用度 :    %s
        余额 :    %s""" % (account_data["credit"], account_data["balance"])
    print(current_balance)  # 打印出用户的信用和余额信息

    back_flag = False
    while not back_flag:
        repay_amount = input("\033[33;1m输入还款的金额，或输入[b]返回到上一层> \033[0m").strip()  # 用户输入还款的金额
        if len(repay_amount) > 0 and repay_amount.isdigit():

            # account_data_new为交易后最新的用户详细信息
            account_data_new = transaction.make_transaction(trans_logger, account_data, 'repay', repay_amount)
            time.sleep(1)  # 处理显示问题

            if account_data_new:
                print('''\033[32m交易后的余额为: %s\033[0m''' % (account_data_new['balance']))

        elif repay_amount == "b":
            back_flag = True
        else:
            print('''[\033[31;1m%s\033[0m]不是有效的金额，只能为正整数! ''' % repay_amount)


def withdraw(acc_data):
    """
    打印当前余额，并提供取款功能的函数
    :param acc_data: 是账户数据
    :return:
    """""
    account_data = accounts.load_current_balance(acc_data["account_id"])  # account_data是最新的用户信息

    current_balance = ''' --------- 余额信息 --------
        信用度 :    %s
        余额 :    %s''' % (account_data['credit'], account_data['balance'])
    print(current_balance)  # 打印出用户的信用和余额信息

    back_flag = False
    while not back_flag:
        withdraw_amount = input("\033[33;1m输入取款金额，或输入[b]返回到上一层> \033[0m").strip()  # 用户输入取款的金额
        if len(withdraw_amount) > 0 and withdraw_amount.isdigit():

            # account_data_new为交易后最新的用户详细信息
            account_data_new = transaction.make_transaction(trans_logger, account_data, 'withdraw', withdraw_amount)
            time.sleep(1)  # 处理显示问题

            if account_data_new:
                print('''\033[32m交易后的余额为: %s\033[0m''' % (account_data_new['balance']))

        elif withdraw_amount == "b":
            back_flag = True
        else:
            print('[\033[31;1m%s\033[0m]不是有效的金额，只能为正整数! ' % withdraw_amount)


def transfer(acc_data):
    """
    打印当前余额，并提供转账功能的函数
    :param acc_data: 是账户数据
    :return:
    """""
    account_data = accounts.load_current_balance(acc_data["account_id"])  # account_data是最新的用户信息

    current_balance = ''' --------- 余额信息 --------
        信用度 :    %s
        余额 :    %s''' % (account_data['credit'], account_data['balance'])
    print(current_balance)  # 打印出用户的信用和余额信息

    back_flag = False
    while not back_flag:
        receiver = input("\033[33;1m输入收款人，或输入[b]返回到上一层> \033[0m").strip()  # 用户输入收款人
        if receiver == account_data["id"]:
            print("\033[31;1m收款人不能是自己!\033[0m")
            continue
        elif receiver == "b":
            back_flag = True
        else:
            receiver_account_data = auth.acc_check(receiver)  # 判断收款人帐号是否存在和过期
            status = receiver_account_data["status"]

            if status == 0:  # 收款人为普通帐户，且状态正常，才能转帐
                transfer_amount = input("\033[33;1m输入转账金额，或输入[b]返回到上一层> \033[0m").strip()
                if len(transfer_amount) > 0 and transfer_amount.isdigit:

                    # account_data_new为交易后最新的用户详细信息
                    account_data_new = transaction.make_transaction(trans_logger, account_data, 'transfer', transfer_amount)

                    # 更新收款人的信息
                    transaction.make_transaction(trans_logger, receiver_account_data, 'receive', transfer_amount)

                    if account_data_new:
                        print('''\033[32m交易后的余额为: %s\033[0m''' % (account_data_new['balance']))

                elif transfer_amount == "b":
                    back_flag = True
                else:
                    print('[\033[31;1m%s\033[0m]不是有效的金额，只能为正整数! ' % transfer_amount)


def save(acc_data):
    """
    打印当前余额，并提供存款功能的函数
    :param acc_data: 是账户数据
    :return:
    """""
    account_data = accounts.load_current_balance(acc_data["account_id"])  # account_data是最新的用户信息

    current_balance = ''' --------- 余额信息 --------
        信用度 :    %s
        余额 :    %s''' % (account_data['credit'], account_data['balance'])
    print(current_balance)  # 打印出用户的信用和余额信息

    back_flag = False
    while not back_flag:
        save_amount = input("\033[33;1m输入存款金额，或输入[b]返回到上一层> \033[0m").strip()  # 用户输入存款的金额
        if len(save_amount) > 0 and save_amount.isdigit():

            # account_data_new为交易后最新的用户详细信息
            account_data_new = transaction.make_transaction(trans_logger, account_data, 'save', save_amount)
            time.sleep(1)  # 处理显示问题

            if account_data_new:
                print('''\033[32m交易后的余额为: %s\033[0m''' % (account_data_new['balance']))

        elif save_amount == "b":
            back_flag = True
        else:
            print('[\033[31;1m%s\033[0m]不是有效的金额，只能为正整数! ' % save_amount)


def pay_check(acc_data):
    """
    提供查询账单功能的函数
    :param acc_data: 是账户数据
    :return:
    """""
    bill_date = input("请输入要查询的日期，例如[\033[32;1m2017-6\033[0m]> ").strip()  # 用户输入需要查询哪个月的账单

    log_path = db_handler.db_handler(settings.LOG_DATABASE)  # log_path是保存用户交易日志所在目录的信息
    bill_log = "%s/%s.bills" % (log_path, acc_data['account_id'])  # 目录加上文件名

    if not os.path.isfile(bill_log):
        print("账户[\033[32;1m%s\033[0m]没有账单记录" % acc_data["account_id"])
        return

    print("账户[\033[32;1m%s\033[0m]的账单记录: " % acc_data["account_id"])
    print("-".center(50, "-"))
    with open(bill_log, "r", encoding="utf-8") as f:
        for bill in f:
            b_date = bill.split(" ")[1]  # 保存在帐单中的年-月
            print(b_date)
            if bill_date == b_date:
                print("\033[33;1m%s\033[0m" % bill.strip())

    log_type = "transaction"
    print("账户[\033[32;1m%s\033[0m]历史记录: " % acc_data["account_id"])
    logger.show_log(acc_data['account_id'], log_type, bill_date)


def logout(acc_data):
    """
    退出程序函数
    :param acc_data: 用户详细信息
    :return:
    """""
    exit("程序退出")


def interactive(acc_data):
    """
    与用户交互的函数，并根据用户的输入调取相应的功能函数
    :param acc_data: 用户登陆成功后，做过修改的账户数据
    :return:
    """""
    menu_options = """
    ------ 老男孩银行 ------
    1. 账户信息
    2. 还款
    3. 取款
    4. 转账
    5. 存款
    6. 账单查询
    7. 退出程序
    """

    function_dict = {
        "1": account_info,
        "2": repay,
        "3": withdraw,
        "4": transfer,
        "5": save,
        "6": pay_check,
        "7": logout,
    }

    while True:
        print(menu_options)
        user_choice = input("请输入交易类型编号> ").strip()
        if user_choice in function_dict:
            function_dict[user_choice](acc_data)
        else:
            print("输入的交易类型不存在，请重新输入")


def get_bill(account_id):
    """
    设定每月1日是账单的生成日，生成上个月的帐单
    :param account_id: 用户id
    :return:
    """""
    time_now = datetime.datetime.now()  # 获取当前时间
    year_month = "%s-%s" % (time_now.year, time_now.month - 1)  # 帐单年月
    account_data = accounts.load_current_balance(account_id)  # 获取用户信息
    balance = account_data["balance"]  # 可用余额
    credit = account_data["credit"]  # 信用额度

    if time_now.day != settings.BILL_DAY:
        print("\033[31;1m今天不是账单生成日，每月的%s日是账单生成日\033[0m" % settings.BILL_DAY)
        # return  # 为了调试程序，暂时先注释掉

    if balance >= credit:
        repay_amount = 0
        print("账户[\033[32;1m%s\033[0m]不需要还款" % account_id)
    else:
        repay_amount = credit - balance
        print("账户[\033[32;1m%s\033[0m]需要还款[\033[33;1m%s\033[0m]元" % (account_id, repay_amount))

    log_path = db_handler.db_handler(settings.LOG_DATABASE)  # 生成存放用户账单的路径
    bill_log = "%s/%s.bills" % (log_path, account_id)  # 生成存放用户账单的文件名

    with open(bill_log, "a+", encoding="utf-8") as f:  # 将数据存入账单中
        f.write("账单日期: %s  用户名: %s  本月需要还款: %d元\n" % (year_month, account_id, repay_amount))


def get_all_bill():
    """
    生成全部可用用户的帐单
    :return: True或None
    """""
    db_path = db_handler.db_handler(settings.DATABASE)
    for root, dirs, files in os.walk(db_path):  # 获取到db下accounts目录的绝对路径，accounts目录中的子目录和文件
        for file in files:
            if os.path.splitext(file)[1] == ".json":  # 以.json结尾的文件
                account_id = os.path.splitext(file)[0]  # 得到用户名
                account_data = auth.acc_check(account_id)  # 获取最新的用户信息
                status = account_data["status"]  # 获取用户的状态

                print("账单".center(50, "-"))
                if status != 8:  # 除了管理员，其它帐户都应该出帐单，即使帐户禁用了
                    display_account_info(account_data)  # 显示用户的信息
                    get_bill(account_id)  # 获取帐单
                print("结束".center(50, "-"))

    return True


def check_admin(function):
    """
    验证是否是管理员的函数
    :param function: 函数manage_function的内存地址
    :return:
    """""
    def wrapper(*args, **kwargs):
        if user_data["account_data"].get("status") == 8:
            result = function(*args, **kwargs)
            return result
        else:
            print('\033[31;1m权限不够\033[0m')

    return wrapper


@check_admin
def manage_function(acc_data):
    """
    管理员独有的功能函数
    :param acc_data: 用户登陆成功后，做过修改的账户数据
    :return:
    """""
    menu_options = """
    ------ 管理员功能菜单 ------
    1. 添加账户
    2. 查询用户信息
    3. 用户信息修改（冻结帐户、用户信用卡额度等）
    4. 生成全部用户帐单
    5. 退出程序
    """

    function_dict = {
        "1": "auth.sign_up()",
        "2": "account_info(acc_data)",
        "3": "auth.modify()",
        "4": "get_all_bill()",
        "5": "logout(acc_data)"
    }

    tag = True
    while tag:
        print(menu_options)
        choice = input("输入功能编号> ").strip()
        if choice in function_dict:
            tag = eval(function_dict[choice])  # 注意如果用exec()话无法获取函数的运行结果
        else:
            print("\033[31;1m输入的功能编号不存在!\033[0m")


def get_user_data():
    """
    当用户登陆成功后，则将用户各项信息填入user_data中
    :return: 用户登陆成功返回user_data，用户登陆失败返回None
    """""
    account_data = auth.acc_login(user_data, access_logger)  # acc_login函数返回的是用户详细信息
    if user_data["is_authenticated"]:
        user_data["account_data"] = account_data  # 将user_data字典account_data对应的value改成用户详细信息
        return user_data  # user_data是修改后的账户数据
    else:
        return None


def run():
    """
    当程序执行后，该函数会立即被执行
    :return:
    """""
    user_data = get_user_data()  # 调用get_user_data函数做用户登陆验证，user_data是用户登陆成功后做过修改的账户数据

    user_name = user_data["account_id"]
    if user_name == "admin":  # 管理员
        print("ATM管理员".center(50, "#"))
        manage_function(user_data)
    else:  # 普通用户
        print("欢迎来到ATM".center(50, "#"))
        interactive(user_data)


def pay(amount):
    """
    购物付款的函数
    :param amount: 购物需要付款的金额
    :return: True 或 False
    """""
    user_data = get_user_data()  # 调用get_user_data函数做用户登陆验证，user_data是用户登陆成功后做过修改的账户数据
    account_data = user_data["account_data"]  # 取出用户数据

    new_account_data = transaction.make_transaction(trans_logger, account_data, 'pay', amount)  # 调用交易处理函数做扣款操作
    if new_account_data:  # 交易处理函数扣款成功
        print("\033[33;1m扣款完成后，您的信用卡余额为: %s 元\033[0m" % new_account_data["balance"])
        return True
    else:
        return False

