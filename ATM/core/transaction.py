#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


from conf import settings
from core import accounts


def make_transaction(log_obj, account_data, tran_type, amount, **kwargs):
    """
    所有交易处理余额用的函数
    :param log_obj: 交易日志函数的logger
    :param account_data: 用户数据
    :param tran_type: 交易类型
    :param amount: 交易的金额
    :param kwargs: 用于日志
    :return: 返回更新后的用户信息或空
    """""
    amount = float(amount)

    if tran_type in settings.TRANSACTION_TYPE:
        interest = amount * settings.TRANSACTION_TYPE[tran_type]["interest"]  # 计算出当前交易的利息
        old_balance = account_data["balance"]  # 取出用户当前的余额

        if settings.TRANSACTION_TYPE[tran_type]['action'] == 'plus':  # 加钱则当前余额加上交易金额再加上利息
            new_balance = old_balance + amount + interest
        elif settings.TRANSACTION_TYPE[tran_type]['action'] == 'minus':  # 扣钱则当前余额减去交易金额再减去利息
            new_balance = old_balance - amount - interest

            if new_balance < 0:  # 透支的情况
                print("你的信用为: [\033[31;1m%s\033[0m], "
                      "当前交易还需金额为: [%s], "
                      "你当前的余额为: [\033[32;1m%s\033[0m]"
                      % (account_data['credit'], (amount + interest), old_balance))
                return

        account_data['balance'] = new_balance  # 将用户交易后的余额存到account_data字典中
        accounts.dump_account(account_data)  # 将account_data字典序列化到文件中

        log_obj.info("account:%s   action:%s    amount:%s   interest:%s"
                     % (account_data['id'], tran_type, amount, interest))  # 将本次交易记录到交易日志文件中

        return account_data

    else:
        print("\033[31;1m交易类型[%s]不存在!\033[0m" % tran_type)
