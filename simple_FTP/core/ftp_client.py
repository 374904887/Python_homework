#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import os
import socket
from conf import settings
from prettytable import PrettyTable
from core import logger


# 获取系统日志的logger对象
system_logger = logger.logger_function("system")


class FtpClient(object):
    """ftp客户端类"""
    def __init__(self):
        self.client = socket.socket()  # 地址簇采用IPv4，协议类型采用TCP
        self.client.connect(settings.ip_port)  # 连接服务端

        self.help_information = {
            "注册帐号": "如果没有ftp帐号，必须注册帐号后才能使用get、put、dir功能",
            "登陆帐号": "如果有ftp帐号，必须登陆帐号后才能使用get、put、dir功能",
            "get 文件名": "用于从服务端下载文件到客户端，注意get和文件名之间要有空格",
            "put 文件名": "用于从客户端上传文件到服务端，注意put和文件名之间要有空格",
            "dir": "用于查看当前用户家目录中的文件信息",
            "help": "查看FTP程序使用帮助信息",
            "退出程序": "用于结束程序运行，退出整个程序"
        }  # ftp客户端的使用帮助信息

        result = self.authentication()  # 调用验证帐号的方法函数，并获取返回值

        if result:
            self.start()  # 当验证帐号的方法函数返回值为真时，调用开始方法函数

        self.client.close()  # 关闭socket

    def authentication(self):
        """认证ftp帐号的方法函数"""
        menu_dict = {
            "1": ["注册帐号", "register"],
            "2": ["登陆帐号", "login"],
            "3": ["退出程序", "exit_program"]
        }
        menu_list = PrettyTable(["功能ID", "功能描述"])  # 设置表格的列数为两列，以及对每列数据作用的说明
        menu_list.padding_width = 2  # 列数据两边的空格数各增加1个
        menu_list.add_row(["1", menu_dict["1"][0]])  # 向表中添加一行
        menu_list.add_row(["2", menu_dict["2"][0]])
        menu_list.add_row(["3", menu_dict["3"][0]])

        while True:
            print(menu_list)

            user_choice = input("输入操作的ID:\n>>>").strip()

            if user_choice in ["1", "2"]:
                function = getattr(self, "register_login")  # 获取对象中注册和登陆方法函数的内存对象地址
                command_action = menu_dict[user_choice][1]  # 获取命令操作类型
                result = function(command_action)  # 调用注册和登陆方法函数

                if result:
                    return True

            if hasattr(self, menu_dict[user_choice][1]):  # 判断对象中是否有用户输入的字符串类型成员
                function = getattr(self, menu_dict[user_choice][1])  # 获取对象中成员的内存对象地址
                function()
            else:
                print("\033[1;31m输入的编号有误请重试\033[0m")

    def register_login(self, command_action):
        """
        注册和登陆ftp帐号的方法函数
        :param command_action: 命令操作类型
        :return:
        """""
        while True:  # 不断开连接的情况下，客户端能和服务端通信多次
            username = input("ftp用户名:\n>>>").strip()
            password = input("ftp密码:\n>>>").strip()

            if len(username) == 0 or len(password) == 0:
                print("\033[1;31m输入的帐号或密码为空，请重新输入\033[0m")
                continue
            else:
                command = "%s %s %s" % (command_action, username, password)  # 拼接字符串，当作一条注册用户的命令
                self.client.send(command.encode(encoding="utf-8"))  # 将命令转化成二进制后发送给服务端
                print("客户端发往服务端的命令", command)

                # 接收服务端响应的数据，并把数据转换成字符串
                server_response = self.client.recv(4096).decode(encoding="utf-8")
                print("客户端接收到服务端响应数据", server_response)

                if server_response == "fail":
                    print("\033[1;31m用户[%s][%s]失败\033[0m" % (username, command_action))
                elif server_response == "success":
                    self.current_user = username  # 将当前用户封装到对象中

                    system_logger.info("用户 %s %s 成功" % (username, command_action))  # 保存到日志文件中

                    print("\033[1;32m用户[%s][%s]成功\033[0m" % (username, command_action))

                    return True

    def start(self):
        """
        开始方法函数
        1: 使客户端能和服务端通信多次
        2: 根据命令的操作类型，分别调用对应的方法函数
        :return:
        """""
        while True:  # 不断开连接的情况下，客户端能和服务端通信多次
            user_input = input("[%s]请输入命令，或输入q退出程序:\n>>>" % self.current_user).strip()

            if len(user_input) == 0:  # 不能发送空内容
                print("\033[1;31m输入的命令为空误，请重新输入\033[0m")
                continue

            command_list = user_input.split()  # 把输入的命令以空格为分隔符转换成列表

            if command_list[0] in ["q", "quit"]:
                print("\033[1;31m退出程序\033[0m")
                break
            elif hasattr(self, command_list[0]):  # 判断对象中是否有用户输入的字符串类型成员
                function = getattr(self, command_list[0])  # 获取对象成员的内存对象地址
                function(command_list)  # 调用
            else:
                print("\033[1;31m输入的命令有误，请重新输入\033[0m")

    def get(self, command_list):
        """
        客户端从服务端下载文件的方法函数
        1: 客户端往服务端发送下载文件的命令
        2: 客户端接收服务端响应的下载文件总大小
        3: 客户端根据累计接收到的数据大小和文件总大小做对比，然后做数据的接收
        :param command_list: 用户输入的命令，已经转换成列表
        :return:
        """""
        command = " ".join(command_list)  # 将列表转换成字符串，转换后列表元素以空格分隔开
        self.client.send(command.encode(encoding="utf-8"))  # 将命令转化成二进制后发送给服务端

        # 接收服务端响应的数据，并把数据转换成字符串
        server_response = self.client.recv(4096).decode(encoding="utf-8")
        print("服务端响应的数据为:", server_response)
        if server_response == "fail":
            print("服务端上不存在需要下载的文件\033[1;31m[%s]\033[0m" % command_list[1])
        else:
            # 服务端接收到客户端的命令后，会返回下载文件的大小，该处将大小的值转成整型
            file_total_size = int(server_response)
            print("客户端下载的文件总大小为\033[1;32m[%s]\033[0m字节" % file_total_size)

            cumulative_receive_size = 0  # 累计接收的数据大小
            file_name = command_list[1]  # 文件名

            with open(file_name, "wb") as f:  # 以二进制写的方式打开文件
                while cumulative_receive_size < file_total_size:  # 当累计接收数据小于文件总大小，则循环接收
                    data = self.client.recv(4096)  # 接收服务端发送的数据
                    f.write(data)  # 将本次接收的数据写入文件中
                    cumulative_receive_size += len(data)  # 记录累计接收数据的大小

            # 保存到日志文件中
            system_logger.info("用户 %s 从服务端下载文件 %s，总大小为 %s 字节"
                               % (self.current_user, command_list[1], file_total_size))

            print("文件\033[1;32m[%s]\033[0m接收成功" % file_name)

    def put(self, command_list):
        """
        客户端上传文件到服务端的方法函数
        1: 判断上传文件是否存在
        2: 获取上传文件的文件名部分
        3: 将上传文件的命令发送到服务端
        4: 打开文件，发送文件
        :param command_list: 用户输入的命令，已经转换成列表
        :return:
        """""
        file_name = command_list[1]
        if os.path.isfile(file_name):  # 上传文件存在
            file_total_size = os.path.getsize(file_name)  # 获取上传文件的总大小
            print("客户端发送的文件总大小为\033[1;32m[%s]\033[0m字节" % file_total_size)

            # 可以以相对路径和绝对路径方式表示文件名
            # 当输入的文件名带有路径时，以当前操作系统路径分隔符为分割符转换成字典，取字典最后一个元素，即文件名
            file_name_new = file_name.split(os.sep)[-1]

            # 拼接命令，格式为：命令操作类型 文件名 文件总大小
            command = "%s %s %s" % (command_list[0], file_name_new, file_total_size)
            self.client.send(command.encode(encoding="utf-8"))  # 将命令转化成二进制后发送给服务端

            send_size = 4096  # 每次发送数据大小
            cumulative_send_size = 0  # 累计发送的数据量大小

            with open(file_name, "rb") as f:  # 以二进制读的方式打开文件
                while file_total_size > cumulative_send_size:  # 文件总大小大于累计发送的数据量代表还没有发送完

                    # 剩余数据量大于4K时，发送数据量为4K，小于4K时，发送的数据量是剩余数据量大小
                    if file_total_size - cumulative_send_size > send_size:
                        data = f.read(send_size)
                    else:
                        send_size = file_total_size - cumulative_send_size
                        data = f.read(send_size)

                    self.client.send(data)
                    cumulative_send_size += send_size  # 记录累计发送的数据量

            # 保存到日志文件中
            system_logger.info("用户 %s 往服务端上传文件 %s ，总大小为 %s 字节"
                               % (self.current_user, file_name_new, file_total_size))

            print("文件\033[1;32m[%s]\033[0m发送成功" % file_name)

        else:
            print("客户端发送的文件\033[1;31m[%s]\033[0m不存在" % file_name)

    def dir(self, command_list):
        """
        查看用户家目录中文件信息的方法函数
        1: 向服务端发送命令
        2: 接收服务端响应的命令执行结果大小
        3: 接收服务端发送的命令执行结果
        4: 打印命令执行结果
        :param command_list: 用户输入的命令，已经转换成列表
        :return:
        """""
        command = command_list[0]

        self.client.send(command.encode(encoding="utf-8"))  # 将命令转化成二进制后发送给服务端

        # 接收服务端响应的数据，并把数据转换成字符串
        server_response = self.client.recv(4096).decode(encoding="utf-8")
        if server_response == "fail":
            print("命令\033[1;31m[%s]\033[0m运行出错" % command)
        else:
            # 服务端接收到客户端的命令后，会返回命令运行结果的大小，该处将大小的值转成整型
            data_total_size = int(server_response)
            print("%s 命令运行结果大小为\033[1;32m[%s]\033[0m字节" % (command, data_total_size))

            cumulative_receive_size = 0  # 累计接收的数据大小
            receive_data = b""  # 接收数据内容

            while cumulative_receive_size < data_total_size:  # 当累计接收数据小于总大小，则循环接收
                data = self.client.recv(4096)  # 接收服务端发送的数据
                receive_data += data  # 存下接收的所有数据
                cumulative_receive_size += len(data)  # 记录累计接收数据的大小
            else:

                # 显示命令运行结果。注意，windows默认字符编码是gbk
                print(receive_data.decode(encoding="gbk"))

                # 保存到日志文件中
                system_logger.info("用户 %s 执行命令 %s 查看家目录中文件信息，命令执行结果总大小为 %s 字节"
                                   % (self.current_user, command, data_total_size))

    def help(self, command_list):
        """
        查看FTP程序使用帮助信息的方法函数
        :param command_list: 用户输入的命令，已经转换成列表
        :return:
        """""
        for key, value in self.help_information.items():
            print("%-10s : %-20s" % (key, value))

    def exit_program(self):
        """退出程序的方法函数"""
        self.client.close()  # 关闭socket
        exit("退出程序")
