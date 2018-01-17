#!/user/bin/env python
# -*- coding:utf-8 -*-
__author__ = "Zhong Lu"


import socket
import hashlib
import json
import os
from conf import settings
from prettytable import PrettyTable


# 状态码及所代表的意义
STATUS_CODE = {
    100: "无效的字典格式, 正确格式例如: {'action': 'get', 'filename': 'test.py', 'size': 344}",
    101: "无效的命令操作类型",
    102: "用户注册成功",
    103: "用户注册失败，该用户已存在",
    104: "用户登陆成功",
    105: "用户登陆失败，密码错误",
    106: "用户登陆失败，该用户不存在",
    107: "服务端上不存在需要下载的文件",
    108: "服务端发送了文件大小，并且准备开始发送文件",
    109: "客户端准备好接收文件",
    110: "服务端准备好接收文件",
    111: "服务端发送了命令执行结果的大小，并准备发送数据",
    112: "客户端准备好接收命令执行结果",
}


class FtpClient(object):
    """ftp客户端类"""
    def __init__(self):
        self.client = socket.socket()  # 生成socket实例，地址簇采用IPv4，协议类型采用TCP
        self.client.connect(settings.ip_port)  # 连接服务端

        result = self.authentication()  # 调用验证帐号的方法函数，并获取返回值

        if result:  # 当验证帐号的方法函数返回值为真时，调用开始方法函数
            self.start()

        self.client.close()  # 关闭socket

    def authentication(self):
        """交互ftp认证类型的方法函数"""
        menu_dict = {
            "1": ["注册帐号", "register"],
            "2": ["登陆帐号", "login"],
            "3": ["FTP使用帮助", "_help"],
            "4": ["退出程序", "_exit"]
        }
        menu_list = PrettyTable(["功能ID", "功能描述"])  # 设置表格的列数为两列，以及对每列数据作用的说明
        menu_list.padding_width = 2  # 列数据两边的空格数各增加1个
        menu_list.add_row(["1", menu_dict["1"][0]])  # 向表中添加一行
        menu_list.add_row(["2", menu_dict["2"][0]])
        menu_list.add_row(["3", menu_dict["3"][0]])
        menu_list.add_row(["4", menu_dict["4"][0]])

        while True:
            print(menu_list)

            user_choice = input("输入操作的ID:\n>>>").strip()

            # 当输入的数字不存在或不是数字时，去字典中取值会报KeyError的错
            try:
                if user_choice in ["1", "2"]:
                    function = getattr(self, "_register_login")  # 获取对象中注册和登陆方法函数的内存对象地址
                    command_action = menu_dict[user_choice][1]  # 获取命令操作类型
                    result = function(command_action)  # 调用注册和登陆方法函数

                    if result:
                        return True

                if hasattr(self, menu_dict[user_choice][1]):  # 判断对象中是否有用户输入的字符串类型成员
                    function = getattr(self, menu_dict[user_choice][1])  # 获取对象中成员的内存对象地址
                    function()

            except KeyError as e:
                print("\033[1;31m输入的内容 [%s] 有误请重试\033[0m" % e)

    def _register_login(self, command_action):
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
                m = hashlib.sha256(b"aBcD")  # 生成对象，并添加自定义key
                m.update(password.encode(encoding="utf-8"))  # 将用户输入的明文密码加密
                password_sha256 = m.hexdigest()  # 将加密后的密码以十六进制方式显示

                # 生成一个操作字典，发给客户端做注册或登陆的操作
                data = {
                    "action": command_action,
                    "username": username,
                    "password": password_sha256
                }

                self.send_message(data)  # 调用往服务端发送消息的方法函数，发送生成的字典

                server_response = self.receive_message()  # 调用接收服务端消息的方法函数

                if server_response.get('status_code') in [102, 104]:  # 登陆或注册成功

                    print("\033[1;32m[%s][%s]\033[0m" % (username, server_response["status_message"]))
                    return True

                else:  # 登陆或注册失败
                    print("\033[1;31m[%s][%s]\033[0m" % (username, server_response["status_message"]))

    def start(self):
        """
        开始方法函数
        1: 使客户端能和服务端通信多次
        2: 根据命令的操作类型，分别调用对应的方法函数
        :return:
        """""
        self.delimiter = os.sep  # 获取当前系统路径分隔符，并封装到对象中

        while True:  # 使客户端能和服务端多次通信

            user_input = input("输入操作命令\n>>>").strip()

            if len(user_input) == 0:  # 不能发送空内容
                continue

            command_list = user_input.split()  # 把输入的命令以空格为分隔符转换成列表

            if command_list[0] in ["q", "quit"]:
                print("\033[1;31m退出程序\033[0m")
                break
            elif hasattr(self, "_%s" % command_list[0]):  # 判断对象中是否有用户输入的字符串类型成员
                function = getattr(self, "_%s" % command_list[0])  # 获取对象成员的内存对象地址
                function(command_list)  # 调用
            else:
                print("\033[1;31m输入的命令有误，请重新输入\033[0m")
                self._help()

    def _dir(self, command_list):
        """
        显示目录中的文件和子目录的方法函数
        :param command_list: 用户输入的命令，已经转换成列表
        :return:
        """""
        data_header = {
            "action": command_list[0]
        }

        self.send_message(data_header)  # 调用往服务端发送消息的方法函数，发送查看目录的操作字典

        server_response = self.receive_message()  # 调用接收服务端消息的方法函数
        if server_response["status_code"] == 111:  # 服务端发送了命令执行结果的大小
            result_total_size = server_response["result_total_size"]  # 获取命令执行结果总大小
            received_size = 0  # 累计接收到数据的总大小
            received_data = b""  # 装载接收数据内容

            self.send_message(112)  # 调用往服务端发送消息的方法函数，发送客户端准备好接收命令执行结果消息

            while received_size < result_total_size:  # 结果总大小 大于 累计接收数据的大小 就一直接收
                data = self.client.recv(8192)
                received_data += data  # 保存每次接收的数据
                received_size += len(data)  # 将每次接收到的数据大小累加起来
            else:
                print("客户端接收到的命令执行结果大小为", received_size)
                print("命令执行结果是")

                # 显示命令运行结果。注意，windows默认字符编码是gbk
                print(received_data.decode(encoding="gbk"))

        elif server_response["status_code"] == 212:  # 需要查看的目录不存在
            print("\033[1;31m[%s]\033[0m" % server_response["status_message"])

    def _get(self, command_list):
        """
        客户端从服务端下载文件的方法函数
        :param command_list: 用户输入的命令，已经转换成列表
        :return:
        """""
        result = self.analysis_command(command_list)  # 调用解析输入命令的方法函数

        if not result:  # 输入的下载文件命令不完整
            return

        self.send_message(result)  # 调用往服务端发送消息的方法函数，发送下载文件命令

        server_response = self.receive_message()  # 调用接收服务端消息的方法函数
        if server_response.get("status_code") == 108:  # 接收服务端发送的文件大小

            file_total_size = server_response["file_total_size"]  # 获取服务端上下载文件的总大小

            # 获取文件名
            filename = command_list[1]
            # 生成客户端上保存下载文件的file目录绝对路径
            file_path = "%s%s%s" % (settings.file_path, self.delimiter, filename)

            received_size = 0  # 累计接收到数据的总大小

            with open(file_path, "wb") as f:
                while received_size < file_total_size:  # 累计接收到的内容大小小于文件总大小就一直接收

                    # 调用往服务端发送消息的方法函数，客户端准备接收文件。
                    # 每次循环都要触发一次，不能在交互一次的情况下就让服务端把文件数据全都发过来，因为服务端是单线程实现的大并发，这样搞会卡住其它连接
                    self.send_message(109)

                    # 剩余的内容大小大于8192，代表需要接收的次数不止一次
                    if file_total_size - received_size > 8192:
                        size = 8192
                    else:  # 剩余的内容大小小于8192，代表一次就可以接收完剩余数据
                        size = file_total_size - received_size

                    data = self.client.recv(size)
                    f.write(data)
                    received_size += len(data)  # 将每次接收到数据的大小累加起来

            print("客户端文件接收完成，客户端接收到的文件大小为 \033[1;32m%s\033[0m 字节" % received_size)

        else:  # 服务端不存在需要下载的文件
            print("\033[1;31m状态码：%s，信息：%s\033[0m"
                  % (server_response["status_code"], server_response["status_message"]))

    def _put(self, command_list):
        """
        客户端上传文件到服务端的方法函数
        1: 判断上传文件是否存在
        2: 获取上传文件的大小
        3: 将上传文件的命令发送到服务端
        4: 向服务端发送文件内容
        :param command_list: 用户输入的命令，已经转换成列表
        :return:
        """""
        result = self.analysis_command(command_list)  # 调用解析输入命令的方法函数

        if not result:
            return

        filename = result["file_path"]  # 获取上传文件的文件名

        # 生成保存在file目录中的文件的绝对路径
        file_path = "%s%s%s" % (settings.file_path, self.delimiter, filename)

        if os.path.isfile(file_path):  # 文件存在

            # 获取上传文件的总大小
            file_total_size = os.path.getsize(file_path)

            # 往操作字典中加入一个文件大小的键值对
            result["file_total_size"] = file_total_size

            self.send_message(result)  # 调用往服务端发送消息的方法函数，发送上传文件操作字典

            server_response = self.receive_message()  # 调用接收服务端消息的方法函数

            if server_response["status_code"] == 110:  # 服务端准备接收文件

                with open(file_path, "rb") as f:
                    for line in f:
                        self.client.send(line)  # 按照每次只发送一整行内容的方式向客户端发送

            print("\033[1;32m文件[%s]上传成功\033[0m" % filename)

        else:
            print("\033[1;31m需要上传的文件[%s]客户端上不存在\033[0m" % filename)

    def _help(self, *args):
        """
        查看FTP程序使用帮助的方法函数
        :param args: 扩展参数
        :return:
        """""
        help_information = r"""
        -- 注册帐号
            如果没有ftp帐号，必须要注册帐号后才能使用其他功能

        -- 登陆帐号
            如果有ftp帐号，必须要登陆帐号后才能使用其他功能

        -- 查看ftp server上家目录中的文件信息
            命令示例：
                dir：查看ftp server上家目录中的文件信息

        -- 从ftp server下载文件
            命令示例：
                get Try.mp3：下载ftp server上的家目录中的Try.mp3文件

        -- 上传文件到ftp server上
            命令示例：
                put Try.mp3：将ftp client的 SELECTORS_FTP/file/FTPTry.mp3 文件上传到ftp server上的家目录中

        -- 结束程序运行，退出整个程序
            命令示例：
                eixt

        -- 查看FTP程序使用帮助信息
            命令示例：
                help
        """
        print(help_information)

    def _exit(self, *args):
        """
        退出程序的方法函数
        :param args: 扩展参数
        :return:
        """""
        self.client.close()  # 关闭socket
        exit("退出程序")

    def send_message(self, data):
        """
        往服务端发送消息的方法函数
        1: 发给服务端的消息格式和字典的格式一样
        :param data: 是一个字典或是一个状态码
        :return:
        """""
        if type(data) is int:
            # 将状态码和状态码所表示的意思拼成一个字典
            data = {"status_code": data, "status_message": STATUS_CODE[data]}

        data_string = json.dumps(data)  # 将字典转换成字符串

        self.client.send(data_string.encode(encoding="utf-8"))
        print("发往服务端的消息是", data)  # 注意这里打印的信息要是转换二进制前的数据

    def receive_message(self):
        """
        接收服务端消息的方法函数
        :return:
        """""
        # 接收服务端发送的数据，并转换成字符串
        data_string = self.client.recv(8192).decode(encoding="utf-8")

        # 从字符串转换为字典类型
        data = json.loads(data_string)
        print("接收到服务端的消息是", data)

        return data

    def analysis_command(self, command_list):
        """
        解析输入命令的方法函数，将输入的命令拼接成字典
        :param command_list: 用户输入的命令，已经转换成列表
        :return:
        """""
        print("命令列表为", command_list)

        if len(command_list) < 2:
            print("\033[1;31m输入的命令不完整，只有命令类型，缺少文件名信息，请重新输入\033[0m")
            return

        data_header = {
            "action": command_list[0],
            "file_path": command_list[1]
        }

        return data_header
