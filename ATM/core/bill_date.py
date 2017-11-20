#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import datetime
from conf import settings


def get_bill_time(year_month):
    """
    获取给出的年-月的信用卡帐单月份起止时间
    :param year_month: 年月的组合，如2017-06
    :return: 返回时间类型的账单开始日期和结束日期
    """""
    string_bill_day = "%s-%s" % (year_month, settings.BILL_DAY)  # 字符串类型的账单开始日期，包含年月日
    bill_begin_time = datetime.datetime.strptime(string_bill_day, "%Y-%m-%d")  # 将字符串类型日期转换成日期时间类型，为账单开始日期

    year = bill_begin_time.year  # 取出日期时间类型的年
    month = bill_begin_time.month  # 取出日期时间类型的月
    if month == 12:
        month = 1  # 12月的下一个月为1月
        year += 1  # 12月的下一个月为新的一年
    else:
        month += 1  # 12月以外的其它月份都只用加一

    bill_end_time = datetime.datetime(year, month, settings.BILL_DAY)  # 时间类型的账单结束日期

    return bill_begin_time, bill_end_time
