#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import os


def file_handle(file_name, backend_domain_name, record_list=None, type="fetch"):
    """
    统一的处理文件接口
    """
    file_name_new = file_name + "_new"
    file_name_bak = file_name + "_bak"

    if type == "fetch":
        record_list = []
        with open(file_name, "r", encoding="utf-8") as f_fetch:
            tag = False

            for line in f_fetch:
                if backend_domain_name == line.strip():
                    tag = True
                    continue

                if tag and line.startswith("backend"):
                    break

                if tag and len(line.strip()) != 0:
                    record_list.append(line.strip())

        for information in record_list:
            print(information)

        return record_list

    elif type == "append":
        with open(file_name, "r", encoding="utf-8") as read_file, \
                open(file_name_new, "w", encoding="utf-8") as write_file:

            for read_line in read_file:
                write_file.write(read_line)

            for new_line in record_list:
                if new_line.startswith("backend"):
                    write_file.write(new_line + "\n")
                else:
                    write_file.write("%s%s\n" % (" "*8, new_line))

        os.rename(file_name, file_name_bak)
        os.rename(file_name_new, file_name)
        os.remove(file_name_bak)

    elif type == "change":
        with open(file_name, "r", encoding="utf-8") as read_file, \
                open(file_name_new, "w", encoding="utf-8") as write_file:

            tag = False
            has_write = False

            for read_line in read_file:

                if backend_domain_name == read_line.strip():
                    tag = True
                    continue

                if tag and read_line.startswith("backend"):
                    tag = False

                if not tag:
                    write_file.write(read_line)
                else:
                    if not has_write:
                        for new_line in record_list:
                            if new_line.startswith("backend"):
                                write_file.write(new_line + "\n")
                            else:
                                write_file.write("%s%s\n" % (" " * 8, new_line))

                        has_write = True

        os.rename(file_name, file_name_bak)
        os.rename(file_name_new, file_name)
        os.remove(file_name_bak)


def fetch(data):
    """根据用户输入的backend，查询backend下的server信息"""
    backend_domain_name = "backend %s" % data
    return file_handle("haproxy.conf", backend_domain_name)


def add(data):
    """
    1: 根据用户的输入，增加backend信息或backend下的server信息
    2: 输入的data参数格式为：{"backend": "www.baidu.com", "record": {"server": "1.1.1.1", "weight": 60, "maxconn": 100}}
    """
    backend = data["backend"]
    record_list = fetch(backend)

    backend_domain_name = "backend %s" % backend
    server_information = "server %s %s weight %s maxconn %s" % (data["record"]["server"],\
                                                                data["record"]["server"],\
                                                                data["record"]["weight"],\
                                                                data["record"]["maxconn"])

    if not record_list:
        record_list.append(backend_domain_name)
        record_list.append(server_information)

        file_handle("haproxy.conf", backend_domain_name, record_list, type="append")

    else:

        record_list.insert(0, backend_domain_name)

        if server_information not in record_list:
            record_list.append(server_information)
        else:
            print("servier信息已存在")
            return

        file_handle("haproxy.conf", backend_domain_name, record_list, type="change")


def remove(data):
    """
    1: 根据用户的输入，删除backend下的server信息
    2: 输入的data参数格式为：{"backend": "www.baidu.com", "record": {"server": "1.1.1.1", "weight": 60, "maxconn": 100}}
    """
    backend = data["backend"]
    record_list = fetch(backend)

    backend_domain_name = "backend %s" % backend
    server_information = "server %s %s weight %s maxconn %s" % (data["record"]["server"],\
                                                                data["record"]["server"],\
                                                                data["record"]["weight"],\
                                                                data["record"]["maxconn"])

    if not record_list or server_information not in record_list:
        print("\033[31m无此内容\033[0m")
        return

    else:

        record_list.insert(0, backend_domain_name)
        record_list.remove(server_information)

        file_handle("haproxy.conf", backend_domain_name, record_list, type="change")


def change(data):
    """
    1: 根据用户的输入，更改backend下的server信息
    2: 输入的data参数格式为：[{"backend": "www.baidu.com", "record": {"server": "1.1.1.1", "weight": 60, "maxconn": 100}}, {"backend": "www.baidu.com", "record": {"server": "2.2.2.2", "weight": 80, "maxconn": 200}}]
    3: 列表的第一个元素是被修改的内容，第二个元素是修改后的内容
    """
    backend = data[0]["backend"]
    record_list = fetch(backend)

    backend_domain_name = "backend %s" % backend
    old_server_information = "server %s %s weight %s maxconn %s" % (data[0]["record"]["server"],\
                                                                    data[0]["record"]["server"],\
                                                                    data[0]["record"]["weight"],\
                                                                    data[0]["record"]["maxconn"])
    new_server_information = "server %s %s weight %s maxconn %s" % (data[1]["record"]["server"],\
                                                                    data[1]["record"]["server"],\
                                                                    data[1]["record"]["weight"],\
                                                                    data[1]["record"]["maxconn"])

    if not record_list or old_server_information not in record_list:
        print("\033[31m无此内容\033[0m")
        return

    else:

        record_list.insert(0, backend_domain_name)
        record_list[record_list.index(old_server_information)] = new_server_information

        file_handle("haproxy.conf", backend_domain_name, record_list, type="change")


if __name__ == "__main__":

    function_options = """
    1: 查询
    2: 添加
    3: 删除
    4: 修改
    5: 退出
    """

    function_dict = {
        1: fetch,
        2: add,
        3: remove,
        4: change,
        5: exit,
    }

    while True:
        print(function_options)

        choice = input("编号>>: ").strip()
        if choice.isdigit():
            choice = int(choice)
            if choice not in function_dict:
                print("输入的编号不在规定范围内，请重新输入")
                continue
            elif choice == 5:
                exit("退出程序")
        else:
            print("输入内容错误，请重新输入")
            continue

        data = input("数据>>: ").strip()

        if choice in [2, 3, 4]:
            data = eval(data)

        function_dict[choice](data)
