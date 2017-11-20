#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import os
import time
import subprocess
from core import auth
from core import logger
from conf import settings
from conf import goods
from core import accounts


access_logger = logger.logger("access")  # 获取登陆日志的logger对象

shopping_cart = {}  # 初始化购物车

all_cost = [0]  # 初始总花费金额，定义成列表是为了当在函数内改动后全局都会跟着改变

# 临时帐户数据，仅将数据保存在内存中
user_data = {
    'is_authenticated': False,
    'account_data': None
}


def login():
    """
    用户登陆的函数，并取得用户数据
    :return: True
    """""
    acc_data = auth.acc_login(user_data, access_logger)  # 登录验证，并返回用户数据
    if user_data['is_authenticated']:
        user_data['account_data'] = acc_data  # 将用户数据保存到临时账户数据中
        return True


def logout():
    """
    退出程序的函数
    :return: None
    """""
    exit("再见，谢谢!")


def interactive():
    """
    与用户交互函数
    :return:
    """""
    menu = '''
    ----------操作选项----------
        1: 登陆
        2: 注册
        3: 退出
        '''

    dict_function = {
        "1": "login()",
        "2": "auth.sign_up(user_data)",
        "3": "logout()"
    }

    exit_flag = False
    while not exit_flag:
        print(menu)
        user_choice = input("选择要操作选项的ID: ").strip()
        if user_choice in dict_function:
            exit_flag = eval(dict_function[user_choice])  # 注意如果用exec()话无法获取函数的运行结果
        else:
            print("\033[31;1m选项ID不存在，请重新输入!\033[0m")


def show_shopping_cart(user_data, cost):
    """
    显示购物车和更新用户信息的函数
    :param user_data: 账户数据
    :param cost: 购物总花费金额
    :return:
    """""
    if user_data["is_authenticated"] is True:
        account_data = user_data["account_data"]  # 获取用户信息
        money = account_data['balance']  # 获取用户当前的余额
        print("您购买的商品如下".center(50, "*"))
        print("%-25s %-20s %-20s %-20s" % ("商品", "价格", "数量", "总价"))
        for key in shopping_cart:
            product_name = key[0]  # 商品名
            product_price = int(key[1])  # 商品价格
            product_number = int(shopping_cart[key])  # 购买的数量
            print("%-25s %-20s %-20s \033[32;1m%-20s\033[0m" % (product_name, product_price, product_number, product_price * product_number))
        print("*".center(50, "*"))
        print("您购物总消费为: \033[32;1m%s\033[0m元，您当前可用余额为: \033[32;1m%s\033[0m元" % (cost, money))
        accounts.dump_account(account_data)  # 将用户数据保存到文件中


def show_shopping_history(user_name, log_type):
    """
    显示购物历史函数，如果需要显示购物历史，则显示
    :param user_name: 用户名
    :param log_type: 购物日志的logger对象
    :return:
    """""
    log_file = "%s/log/%s_%s" % (settings.BASE_DIR, user_name, settings.LOG_TYPES[log_type])  # 生成购物日志的路绝对路径
    if os.path.getsize(log_file):
        logger.show_log(user_name, log_type)
    else:
        print("没有购物历史记录，日志文件%s_%s为空" % (user_name, settings.LOG_TYPES[log_type]))


def list_one_layer():
    """
    打印商品种类的函数
    :return: None 或 用户所选择的商品种类中包含的所有商品信息的列表
    """""
    one_layer_list = []  # 记录商品种类的列表
    print("商品种类".center(50, "-"))
    for index, item in enumerate(goods.menu):  # 返回元组，第一个元素是数字，从0开始，第二个元素是商品字典中的key
        print("商品编号 \033[32;1m%d\033[0m --> %s" % (index, item))
        one_layer_list.append(item)  # 商品字典的key加到商品种类的列表中
    print("End".center(50, "-"))

    print("输入商品编号开始购物, "
          "查看购物车输入\033[1;33m[c]\033[0m，"
          "更新信息输入\033[1;33m[t]\033[0m，"
          "退出输入\033[1;33m[q|b]\033[0m")
    once_choice = input("请输入: ").strip()
    if once_choice.isdigit():
        once_choice = int(once_choice)
        if 0 <= once_choice < len(goods.menu):  # 用户输入的数字有效
            return goods.menu[one_layer_list[once_choice]]  # 返回用户所选择的商品种类中包含的所有商品信息的列表
        else:
            print("\033[31;1m输入的数字无效，请重新输入!\033[0m")
    elif once_choice in ["c", "check"]:
        show_shopping_cart(user_data, all_cost[0])
    elif once_choice == "t":
        account_data = user_data['account_data']  # 获取用户信息
        money = account_data['balance']  # 用户的余额
        money = charge_money(money)  # 充值余额后的余额
        user_data['account_data']['balance'] = money  # 将余额保存到用户数据中，并更新账户数据
    elif once_choice in ["q", "quit", "b", "back"]:
        show_shopping_cart(user_data, all_cost[0])
        time.sleep(0.1)  # 由于显示问题，添加此步解决
        exit("再见，谢谢！".center(50, "#"))
    else:
        print("\033[31;1m输入的内容无效，请按照提示输入内容!\033[0m")

    return None


def list_two_layer(two_layer_list):
    """
    显示用户所选择的商品种类中包含的所有商品信息
    :param two_layer_list: 用户所选择的商品种类中包含的所有商品信息的列表
    :return:
    """""
    print("产品列表".center(50, '-'))
    for item in enumerate(two_layer_list):  # 返回元组，第一个元素是数字，从0开始，第二个元素是元组，是商品的名称和价格
        index = item[0]  # 获取返回元组的第一个元素，为数字
        product_name = item[1][0]  # 获取第二个元素，元组中商品名称
        product_price = item[1][1]  # 获取第二个元素，元组中商品价格
        print("%s.%-20s %+15s 元" % (index, product_name, product_price))
    print("结束".center(50, '-'))


def charge_money(money):
    """
    充值余额的函数
    :param money: 当前账户中的余额
    :return: 充值后的余额
    """""
    atm_api = os.path.dirname(settings.BASE_DIR) + "/ATM/api/pay.py"

    exit_flag = False
    while not exit_flag:
        user_charge = input("您是否需要充值余额？充值输入\033[32;1m[y]\033[0m，不需要充值输入\033[32;1m[n|b]\033[0m: ").strip()
        if user_charge in ["y", "yes"]:
            print("使用ATM账户充值")
            while True:
                charge_number = input("请输入需要充值的金额: ").strip()
                if charge_number.isdigit():

                    # 电脑中装了两个python，使用python3调用的是python3.x的版本，该处如果用python2.x的版本运行会出错
                    command = "python3 " + atm_api + " " + charge_number
                    p_object = subprocess.Popen(command, shell=True)  # 创建Popen对象，调用atm接口付款
                    stdout, stderr = p_object.communicate()  # 交互
                    if p_object.returncode == 0:
                        print("\033[32;1m充值成功\033[0m")
                        money += int(charge_number)  # 充值后的余额
                        print("您充值后的余额为[\033[32;1m%s\033[0m]" % money)
                    else:
                        print("\033[31;1m充值失败，请重新充值\033[0m")
                        continue

                    exit_flag = True
                    break
                else:
                    print("您输入的金额不是数字，请重新输入")
                    continue

        elif user_charge in ["n", "no", "b", "back"]:
            exit_flag = True
        else:
            print("输入的内容有误，请重新输入")

    return money


def go_shopping(log_obj, user_data):
    """
    购物函数
    :param log_obj: 购物日志函数的logger对象
    :param user_data: 帐户数据
    :return:
    """""
    account_data = user_data['account_data']  # 用户数据
    money = account_data['balance']  # 当前用户的余额

    flag = False
    while not flag:
        two_layer_list = list_one_layer()  # 得到用户所选择的商品种类中包含的所有商品信息的列表
        if not two_layer_list:
            continue

        exit_flag = False
        while not exit_flag:
            list_two_layer(two_layer_list)  # 列出用户所选择的商品种类中包含的所有商品信息
            print("输入商品编号开始购物, "
                  "查看购物车输入\033[1;33m[c]\033[0m，"
                  "返回上层输入\033[1;33m[b]\033[0m，"
                  "退出输入\033[1;33m[q]\033[0m")

            user_choice = input("请输入: ").strip()
            if user_choice.isdigit():
                user_choice = int(user_choice)

                if 0 <= user_choice < len(two_layer_list):
                    product_number = input("请输入需要购买该产品的个数: ").strip()
                    if product_number.isdigit():
                        product_number = int(product_number)
                    else:
                        continue  # 重新选择需要够买的商品和个数
                else:
                    print("输入的商品编号无效，请重新输入")
                    continue

                product_item = two_layer_list[user_choice]  # 根据用户的选择取出对应的商品名和商品价格，是一个元组
                product_name = product_item[0]  # 商品名
                product_price = int(product_item[1])  # 商品价格

                new_added = {}  # 初始化一个字典，记录商品名、商品价格和够买的个数

                if product_price * product_number <= money:  # 商品价格乘于商品个数小于等于余额，表示买的起
                    new_added = {product_item: product_number}  # 商品名和商品价格的元组作为字典的key，够买的个数作为value
                    for key, value in new_added.items():  # 将字典变成一个大列表，元组是列表的一个元素，字典的key是小元组的第一个元素，value是小元组的二个元素
                        if key in shopping_cart:
                            shopping_cart[key] += value  # 当购买的商品在购物车字典中时，累加够买的个数
                        else:
                            shopping_cart[key] = value  # 当购买的商品不在购物车字典中时，value就是本次够买的个数

                    money -= product_price * product_number  # 扣款，更新余额
                    all_cost[0] += product_price * product_number  # 更新购物总花费

                    log_obj.info("帐号: %s  操作: %s  购买商品名: %s  购买数量: %s  总价: %s元" %
                                 (account_data['user'], "shopping",  product_name, product_number, all_cost[0]))
                    print("添加[\033[32;1m%s\033[0m] [\033[32;1m%d\033[0m]到购物车中，"
                          "当前可用余额为[\033[32;1m%s\033[0m]元" % (product_name, product_number, money))
                    time.sleep(0.1)  # 由于日志显示问题，添加此步解决

                else:  # 买不起的情况
                    print("所购买的商品总金额为[\033[31;1m%s\033[0m]元，"
                          "你的当前余额为[\033[31;1m%s\033[0m]元，"
                          "余额不足无法购买" % (product_price * product_number, money))
                    money = charge_money(money)  # 调用充值余额的函数

                user_data["account_data"]["balance"] = money  # 更新用户余额

            elif user_choice in ["c", "check"]:
                show_shopping_cart(user_data, all_cost[0])
            elif user_choice in ["b", "back"]:
                exit_flag = True
            elif user_choice in ["q", "quit"]:
                show_shopping_cart(user_data, all_cost[0])
                exit("再见，谢谢！".center(50, "#"))
            else:
                print("输入错误!")


def run():
    """
    程序运行主函数
    :return:
    """""
    print("欢迎光临购物中心".center(50, "#"))

    interactive()  # 做登录、注册、退出的操作

    account_data = user_data["account_data"]
    user_name = account_data["user"]

    log_type = "shopping"  # 定义购物的日志类型
    shopping_logger = logger.logger(log_type, user_name)  # 获取购物日志的logger对象，注意此时就已经生成了用户的购物日志文件

    print("是否需要查看购物历史记录，"
          "输入\033[1;33m[y或yes]\033[0m查看购物历史记录，"
          "\033[1;33m[其它]\033[0m则不查看")
    see_history = input("请输入: ").strip()
    if see_history in ["y", "yes"]:
        show_shopping_history(user_name, log_type)  # 调用显示购物历史函数，如果要显示购物历史则显示

    go_shopping(shopping_logger, user_data)  # 调用购物函数
