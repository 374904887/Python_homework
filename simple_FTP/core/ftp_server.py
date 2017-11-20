#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import socket
import os
import json
import subprocess
from conf import settings


class FtpServer(object):
    """ftp服务端类"""
    def __init__(self):
        self.server = socket.socket()  # 地址簇采用IPv4，协议类型采用TCP
        self.server.bind(settings.ip_port)  # 绑定ip地址和端口号
        self.server.listen(5)  # 开始监听传入的连接，并设置最多只能挂起5个连接
        self.start()  # 调用开始方法函数

        self.server.close()  # 关闭socket

    def start(self):
        """
        开始方法函数
        1: 使服务端能接收多个连接
        2: 使服务端能和每个连接互相通信多次
        3: 根据命令类型，调用对应的方法函数
        :return:
        """""
        while True:  # 能接收多个连接

            # 接收连接，并将客户端连接上服务端后生成的连接对象赋值给conn，将客户端ip地址和使用端口号的元组赋值给address
            self.conn, self.address = self.server.accept()
            print("接入一个新的连接\033[1;32m%s\033[0m" % self.conn)

            while True:  # 在不断开连接的情况下，能和该连接通信多次
                data = self.conn.recv(4096)  # 接收客户端发送的数据，并设定最多只能接收大小为4K的数据

                if not data:  # 和客户端断开连接后，服务端会一直循环接收空内容，避免出现这种情况
                    print("\033[1;31m和客户端断开连接\033[0m")
                    break

                # 把接收的数据从bytes类型转换成str类型，并以空格为分隔符转换成列表
                command_list = data.decode(encoding="utf-8").split()

                command_action = command_list[0]  # 获取操作类型
                if hasattr(self, command_action):  # 判断对象中是否有用户输入的字符串类型成员
                    function = getattr(self, command_action)  # 获取对象成员的内存对象地址

                    function(command_list)  # 调用方法函数

                else:
                    self.conn.send(b"fail")  # 向客户端失败的消息
                    print("\033[1;31m命令的操作类型有误\033[0m")

    def register(self, command_list):
        """
        注册ftp帐号的方法函数
        :param command_list: 客户端发送到服务端的命令，已经转换成列表
        :return:
        """""
        print("客户端发送的命令为:", command_list)

        username = command_list[1]  # 获取用户名
        password = command_list[2]  # 获取用户密码

        delimiter = os.sep  # 获取当前操作系统路径的分隔符

        username_file = username + ".json"  # 保存用户数据文件的文件名

        # 生成保存用户数据文件的绝对路径，根据当前操作系统生成对应的路径分隔符，否则运行dir命令时会报错
        user_file = "%s%s%s" % (settings.user_database_path, delimiter, username_file)

        if os.path.isfile(user_file):
            self.conn.send(b"fail")  # 向客户端发送失败的消息
            print("用户\033[1;31m[%s]\033[0m已存在，请重新输入" % username)

        else:  # 输入的用户不存在

            # 生成用户家目录绝对路径，根据当前操作系统生成对应的路径分隔符，否则运行dir命令时会报错
            home_path = "%s%s%s%s" % (settings.user_home_path, delimiter, username, delimiter)

            os.mkdir(home_path)  # 创建用户家目录

            user_data = {"id": username, "password": password, "home_path": home_path}  # 生成用户数据字典

            with open(user_file, "w", encoding="utf-8") as f:
                json.dump(user_data, f)  # 通过序列化将用户数据字典保存到文件中

            self.user_data = user_data  # 将用户数据封装到对象中

            self.conn.send(b"success")  # 注册成功后向客户端发送消息

            print("用户\033[1;32m[%s]\033[0m创建成功" % username)

    def login(self, command_list):
        """
        登陆ftp帐号的方法函数
        :param command_list: 客户端发送到服务端的命令，已经转换成列表
        :return:
        """""
        print("客户端发送的命令为:", command_list)

        username = command_list[1]  # 获取用户名
        password = command_list[2]  # 获取用户密码

        user_file = "%s/%s.json" % (settings.user_database_path, username)  # 生成保存用户数据文件的绝对路径

        if os.path.isfile(user_file):  # 输入的用户存在

            with open(user_file, "r", encoding="utf-8") as f:
                user_data = json.load(f)  # 通过反序列化从文件中取出用户数据，并转换成字典

            self.user_data = user_data  # 将用户数据封装到对象中

            if password == user_data["password"]:  # 验证密码是否正确
                self.conn.send(b"success")  # 注册成功后向客户端发送消息
                print("用户\033[1;32m[%s]\033[0m登陆成功" % self.user_data["id"])

            else:
                self.conn.send(b"fail")  # 向客户端发送失败的消息
                print("\033[1;31m密码错误，请重新输入\033[0m")

        else:
            self.conn.send(b"fail")  # 向客户端发送失败的消息
            print("用户\033[1;31m[%s]\033[0m不存在，请重新输入" % username)

    def get(self, command_list):
        """
        客户端从服务端下载文件的方法函数
        1: 服务端接收客户端发送下载文件的命令
        2: 服务端向客户端发送下载文件的总大小
        3: 服务端每次读取定量数据发送到客户端
        :param command_list: 客户端发送到服务端的命令，已经转换成列表
        :return:
        """""
        print("客户端发送的命令为:", command_list)

        user_home = self.user_data["home_path"]  # 获取当前用户的家目录
        file_path = user_home + command_list[1]  # 拼接下载文件的绝对路径

        if os.path.isfile(file_path):  # 下载的文件存在
            file_total_size = os.path.getsize(file_path)  # 获取客户端需要下载的文件总大小
            print("服务端发送的文件总大小为\033[1;32m[%s]\033[0m字节" % file_total_size)

            self.conn.send(str(file_total_size).encode(encoding="utf-8"))  # 向客户端发送所下载的文件总大小

            send_size = 4096  # 每次发送数据大小
            cumulative_send_size = 0  # 累计发送的数据量大小
            with open(file_path, "rb") as f:  # 以二进制读的方式打开文件
                while file_total_size > cumulative_send_size:  # 文件总大小大于累计发送的数据量代表还没有发送完

                    # 剩余数据量大于4K时，发送数据量为4K，小于4K时，发送的数据量是剩余数据量大小
                    if file_total_size - cumulative_send_size > send_size:
                        data = f.read(send_size)
                    else:
                        send_size = file_total_size - cumulative_send_size
                        data = f.read(send_size)

                    self.conn.send(data)
                    cumulative_send_size += send_size  # 记录累计发送的数据量

            print("文件\033[1;32m[%s]\033[0m发送成功" % command_list[1])

        else:
            self.conn.send(b"fail")  # 向客户端发送失败的消息
            print("客户端需要下载的文件\033[1;31m[%s]\033[0m不存在" % command_list[1])

    def put(self, command_list):
        """
        服务端接收客户端上传文件的方法函数
        1: 根据客户端发送的上传文件命令获取文件总大小
        2: 拼接保存客户端上传文件的绝对路径
        3: 打开文件，接收文件
        :param command_list: 客户端发送到服务端的命令，已经转换成列表
        :return:
        """""
        print("客户端发送的命令为:", command_list)

        file_total_size = int(command_list[2])  # 获取客户端上传文件的总大小
        print("客户端发送的文件总大小为\033[1;32m[%s]\033[0m字节" % file_total_size)

        user_home = self.user_data["home_path"]  # 获取当前用户的家目录
        file_path = user_home + command_list[1]  # 拼接保存客户端上传文件的绝对路径

        cumulative_receive_size = 0  # 累计接收的数据大小

        with open(file_path, "wb") as f:  # 以二进制写的方式打开文件
            while cumulative_receive_size < file_total_size:  # 当累计接收数据的小于文件总大小，则循环接收
                data = self.conn.recv(4096)  # 接收客户端发送的数据
                f.write(data)  # 将本次接收的数据写入文件中
                cumulative_receive_size += len(data)  # 记录累计接收数据的大小

        print("文件\033[1;32m[%s]\033[0m接收成功" % command_list[1])

    def dir(self, command_list):
        """
        查看用户家目录中文件信息的方法函数
        1: 获取客户端发送的命令
        2: 执行命令，并取到执行结果
        3: 将命令执行结果大小发送给客户端
        4: 将命令执行结果发送给客户端
        :param command_list: 客户端发送到服务端的命令，已经转换成列表
        :return:
        """""
        print("客户端发送的命令为:", command_list)

        action = command_list[0]

        user_home = self.user_data["home_path"]  # 获取当前用户的家目录
        command = r"%s %s" % (action, user_home)
        print("命令为", command)

        # 执行命令，并获取命令执行结果。注意，通过subprocess获取的命令执行结果默认都是以二进制方式显示
        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result_new = result.stdout.read()  # 取出命令结果
        data_total_size = len(result_new)  # 获取命令执行结果大小
        print("%s 命令运行结果总大小为\033[1;32m[%s]\033[0m字节" % (action, data_total_size))

        if data_total_size == 0:
            self.conn.send(b"fail")  # 从标准输出中读取到的数据为零时，向客户端发送失败的消息
        else:
            self.conn.send(str(data_total_size).encode(encoding="utf-8"))  # 向客户端发送所下载的文件总大小
            self.conn.sendall(result_new)  # 使用sendall将命令运行结果全部发送出去

            print("\033[1;32m[%s]\033[0m命令运行的结果已全部发送" % action)
