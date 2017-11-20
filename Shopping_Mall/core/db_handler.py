#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


def file_db_handle(conn_params):
    """
    解析存储用户数据的文件路径信息的函数
    :param conn_params: 是一个字典，字典内容是存储用户数据的文件或数据库详细信息
    :return:
    """""
    db_path = "%s/%s" % (conn_params["path"], conn_params["name"])  # db_path是保存用户数据的文件所在目录的信息
    return db_path


def db_handler(conn_params):
    """
    判断存储用户数据的是文件，还是数据库
    :param conn_params: 是一个字典，字典内容是存储用户数据的文件或数据库详细信息
    :return:
    """""
    if conn_params["engine"] == "file_storage":
        return file_db_handle(conn_params)
    elif conn_params["engine"] == "mysql":
        pass  # 扩展接口
