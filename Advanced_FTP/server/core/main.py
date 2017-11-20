#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import socketserver
import json
import os
import hashlib
import subprocess
from conf import settings
from core import logger


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
    110: "该用户在服务端上可用空间不足，无法上传该文件到服务端",
    111: "服务端准备好接收文件",
    112: "恢复上次下载该文件的任务，并且发送目前已完成的大小",
    113: "发送MD5值，开始做MD5验证",
    114: "MD5值相同，校验成功",
    115: "发送用户当前可用空间大小",
    116: "当前所处目录中存在该目录，并发送存在的目录路径信息",
    117: "当前所处目录中不存在该目录",
    118: "目录创建成功",
    119: "目录创建失败，输入的目录中某一级不存在",
    210: "需要创建的目录已存在",
    211: "服务端发送了命令执行结果的大小，并准备发送数据",
    212: "需要查看的目录不存在",
    213: "客户端准备好接收命令执行结果",
}


# 获取系统日志的logger对象
system_logger = logger.logger_function("system")


class MyFtpServer(socketserver.BaseRequestHandler):
    """自己创建的ftp请求处理类"""
    def handle(self):
        """处理跟客户端交互的方法函数"""
        while True:  # 使服务端能和连接多次通信

            # 当和客户端的连接断开后，服务端不会出现一直接收空数据从而进入死循环状态，会抛出ConnectionResetError错误
            try:
                data = self.receive_message()  # 调用接收客户端消息的方法函数，接收操作字典

                print("客户端的ip地址是 {}".format(self.client_address[0]))

                if data.get("action") is not None:  # 操作字典中存在操作类型
                    if hasattr(self, "_%s" % data.get("action")):  # 处理该命令类型的方法函数存在
                        function = getattr(self, "_%s" % data.get("action"))  # 获取对象成员的内存对象地址
                        function(data)  # 调用对象成员

                    else:
                        print("\033[1;31m无效的命令操作类型\033[0m")
                        self.send_message(101)  # 调用往客户端发送消息的方法函数

                else:
                    print("\033[1;31m客户端发送的是一个无效的字典格式\033[0m")
                    self.send_message(100)  # 调用往客户端发送消息的方法函数

            except ConnectionResetError as e:
                print("错误信息为\033[1;31m %s \033[0m" % e)
                break  # 断开和客户端的连接

    def _register(self, data):
        """
        注册ftp帐号的方法函数
        1: 将用户名、保存账户数据文件的绝对路径、用户家目录的绝对路径都封装到对象中
        :param data: 客户端发送到服务端的操作字典
        :return:
        """""
        self.username = data["username"]  # 获取用户输入的用户名，并且封装到对象中
        password = data["password"]  # 获取用户输入的密码

        delimiter = os.sep  # 获取当前操作系统路径的分隔符，并且封装到对象中

        # 生成存储用户数据文件的文件名
        user_file = self.username + ".json"
        # 生成保存账户数据文件的绝对路径，并封装到对象中。根据当前操作系统生成对应的路径分隔符，否则运行dir命令时会报错
        self.user_file_path = "%s%s%s" % (settings.user_database_path, delimiter, user_file)

        if os.path.isfile(self.user_file_path):
            self.send_message(103)  # 调用往客户端发送消息的方法函数
            print("用户\033[1;31m[%s]\033[0m已存在，请重新输入" % self.username)

        else:  # 输入的用户不存在

            # 生成用户家目录的相对路径。根据当前操作系统生成对应的路径分隔符，否则运行dir命令时会报错
            user_path = "%s%s" % (delimiter, self.username)

            # 将home目录和用户家目录拼接起来，并封装到对象中
            self.user_home_path = settings.home_path + user_path

            os.mkdir(self.user_home_path)  # 创建用户家目录

            # 生成账户数据字典。磁盘配额默认大小为200M，单位转换成字节
            account_data = {
                "id": self.username,
                "password": password,
                "quota": 209715200
            }

            self.dump_account(account_data)  # 调用将账户数据保存到文件中的方法函数

            self.send_message(102)  # 调用往客户端发送消息的方法函数，发送注册成功消息

            system_logger.info("用户%s注册成功" % self.username)  # 保存到日志文件中

            print("用户\033[1;32m[%s]\033[0m创建成功" % self.username)

    def _login(self, data):
        """
        登陆ftp帐号的方法函数
        1: 将用户名、保存账户数据文件的绝对路径、用户家目录的绝对路径都封装到对象中
        :param data: 客户端发送到服务端的操作字典
        :return:
        """""
        self.username = data["username"]  # 获取用户输入的用户名
        password = data["password"]  # 获取用户输入的密码

        delimiter = os.sep  # 获取当前操作系统路径的分隔符

        # 生成存储用户数据文件的文件名
        user_file = self.username + ".json"
        # 生成保存账户数据文件的绝对路径，并封装到对象中。根据当前操作系统生成对应的路径分隔符，否则运行dir命令时会报错
        self.user_file_path = "%s%s%s" % (settings.user_database_path, delimiter, user_file)

        if os.path.isfile(self.user_file_path):  # 输入的用户存在

            account_data = self.load_account()  # 调用从文件中取出账户数据的方法函数

            if password == account_data["password"]:  # 验证密码是否正确

                # 生成用户家目录的相对路径。根据当前操作系统生成对应的路径分隔符，否则运行dir命令时会报错
                user_path = "%s%s" % (delimiter, self.username)
                # 将home目录和用户家目录拼接起来，并封装到对象中
                self.user_home_path = settings.home_path + user_path

                self.send_message(104)  # 调用往客户端发送消息的方法函数，发送用户登陆成功消息

                system_logger.info("用户%s登陆成功" % self.username)  # 保存到日志文件中

            else:
                self.send_message(105)  # 调用往客户端发送消息的方法函数，发送密码错误消息

        else:
            self.send_message(106)  # 调用往客户端发送消息的方法函数，发送用户不存在消息

    def _get(self, data):
        """
        客户端从服务端下载文件的方法函数
        :param data: 客户端发送到服务端的操作字典
        :return:
        """""
        # 拼接下载文件在服务端上的绝对路径
        file_path = self.user_home_path + data["file_path"]

        if os.path.isfile(file_path):  # 下载的文件存在
            file_total_size = os.path.getsize(file_path)  # 获取客户端需要下载的文件总大小
            print("客户端需要下载的文件总大小为\033[1;32m[%s]\033[0m字节" % file_total_size)

            # 调用往客户端发送消息的方法函数，发送文件大小
            self.send_message(108, data_dict={"file_total_size": file_total_size})

            # 调用接收客户端消息的方法函数，接收客户端准备好接收文件的消息
            # 一发一收解决粘包问题
            client_response = self.receive_message()

            m = hashlib.md5()  # 生成md5对象

            if client_response["status_code"] == 112:
                print("恢复客户端下载%s文件任务" % data["file_path"])

                send_size = client_response["incomplete_file_size"]  # 获取上次已发送的数据总大小

                with open(file_path, "rb") as f:
                    f.seek(send_size, 0)  # 从文件头向文件尾偏移文件指针，移到上次程序断开时文件指针所处的位置

                    for line in f:
                        self.request.send(line)  # 按照每次只发送一整行内容的方式向客户端发送

                with open(file_path, "rb") as f:
                    for line in f:
                        m.update(line)  # 将文件每一行的内容添加到md5中，注意hashlib模块只能处理bytes类型的内容

            if client_response["status_code"] == 109:

                with open(file_path, "rb") as f:
                    for line in f:
                        self.request.send(line)  # 按照每次只发送一整行内容的方式向客户端发送
                        m.update(line)  # 将文件每一行的内容添加到md5中，注意hashlib模块只能处理bytes类型的内容

            md5_value = m.hexdigest()  # 按照16进制格式显示
            print("服务端计算的文件md5值为", md5_value)

            self.send_message(113, data_dict={"md5": md5_value})  # 调用往客户端发送消息的方法函数，发送文件md5值

            system_logger.info("用户%s下载文件%s" % (self.username, data["file_path"]))  # 保存到日志文件中

        else:
            self.send_message(107)  # 调用往客户端发送消息的方法函数，发送需要下载的文件不存在消息

    def _put(self, data):
        """
        客户端往服务端上传文件的方法函数
        :param data: 客户端发送到服务端的操作字典
        :return:
        """""
        file_total_size = data["file_total_size"]  # 获取客户端要上传的文件总大小

        account_data = self.load_account()  # 取出账户数据

        if account_data["quota"] > file_total_size:  # 可用容量大于文件总大小

            # 拼接上传的文件保存到服务端的绝对路径
            file_path = self.user_home_path + data["current_directory"] + data["file_path"]

            m = hashlib.md5()  # 生成md5对象

            self.send_message(111)  # 调用往客户端发送消息的方法函数，发送可用空间不足消息

            received_size = 0  # 累计接收到数据的总大小

            with open(file_path, "wb") as f:
                while received_size < file_total_size:  # 累计接收到的内容大小小于文件总大小就一直接收
                    file_data = self.request.recv(8096)
                    f.write(file_data)
                    received_size += len(file_data)  # 将每次接收到数据的大小累加起来
                    m.update(file_data)

            print("服务端文件接收完成，接收到的文件大小为", received_size)

            md5_value = m.hexdigest()  # 按照16进制格式显示
            print("服务端计算的文件md5值为", md5_value)

            self.send_message(113, data_dict={"md5": md5_value})  # 调用往客户端发送消息的方法函数，发送文件md5值

            client_response = self.receive_message()  # 调用接收客户端消息的方法函数，接收MD5验证是否成功的消息
            if client_response["status_code"] == 114:
                new_quota = account_data["quota"] - file_total_size  # 计算出新的可用空间大小
                account_data["quota"] = new_quota  # 修改到账户数据字典中去

                self.dump_account(account_data)  # 将账户数据保存到文件中

                # 调用往客户端发送消息的方法函数，发送用户当前可用空间大小
                self.send_message(115, data_dict={"quota": new_quota})

                # 保存到日志文件中
                system_logger.info("用户%s上传文件%s到目录%s下，剩余磁盘配额为%s字节"
                                   % (self.username,
                                      data["file_path"],
                                      data["current_directory"],
                                      new_quota))

            else:
                print("\033[1;31m[%s]文件一致性校验失败\033[0m" % data["file_path"])

        else:

            self.send_message(110)  # 调用往客户端发送消息的方法函数，发送可用空间不足消息

    def _cd(self, data):
        """
        切换目录的方法函数
        :param data: 客户端发送到服务端的操作字典
        :return:
        """""
        # 获取用户要切换的目录
        directory = data["file_path"]

        # 在要切换的目录前面加上家目录的绝对路径
        change_directory = self.user_home_path + directory

        if os.path.isdir(change_directory):
            # 调用往客户端发送消息的方法函数，发送服务端上存在要切换的目录
            self.send_message(116)
        else:
            # 调用往客户端发送消息的方法函数，发送服务端上不存在要切换的目录
            self.send_message(117)

    def _mkdir(self, data):
        """
        创建目录的方法函数
        :param data: 客户端发送到服务端的操作字典
        :return:
        """""
        # 在需要检查的目录前面加上家目录的绝对路径
        check_directory = self.user_home_path + data["check_directory"]
        # 在需要创建的目录前面加上家目录的绝对路径
        create_directory = self.user_home_path + data["file_path"]

        if os.path.isdir(check_directory):
            if os.path.isdir(create_directory):
                # 调用往客户端发送消息的方法函数，发送需要创建的目录已存在消息
                self.send_message(210)
            else:
                os.mkdir(create_directory)

                # 调用往客户端发送消息的方法函数，发送目录创建成功消息
                self.send_message(118)

                # 保存到日志文件中
                system_logger.info("用户%s成功创建目录%s" % (self.username, data["file_path"]))
        else:
            # 调用往客户端发送消息的方法函数，发送输入的目录中某一级不存在消息
            self.send_message(119)

    def _dir(self, data):
        """
        显示目录中的文件和子目录的方法函数
        :param data: 客户端发送到服务端的操作字典
        :return:
        """""
        # 在需要查看的目录前面加上家目录的绝对路径
        create_directory = self.user_home_path + data["file_path"]

        if os.path.isdir(create_directory):
            command = "%s %s" % (data["action"], create_directory)  # 拼接命令

            # 执行命令，并获取命令执行结果。注意，通过subprocess获取的命令执行结果默认都是以二进制方式显示
            result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result_bytes = result.stdout.read()  # 取出命令结果，是bytes类型
            result_total_size = len(result_bytes)  # 获取命令执行结果大小

            # 调用往客户端发送消息的方法函数，发送命令执行结果的大小
            self.send_message(211, data_dict={"result_total_size": result_total_size})

            # 调用接收客户端消息的方法函数
            client_response = self.receive_message()
            if client_response["status_code"] == 213:
                self.request.send(result_bytes)
        else:
            # 调用往客户端发送消息的方法函数，发送需要查看的目录不存在消息
            self.send_message(212)

    def send_message(self, status_code, data_dict=None):
        """
        往客户端发送消息的方法函数
        1: 发给客户端的消息格式和字典的格式一样
        :param status_code: 是一个状态码
        :param data_dict: 是一个字典
        :return:
        """""
        # 将状态码和状态码所表示的意思拼成一个字典
        response = {"status_code": status_code, "status_message": STATUS_CODE[status_code]}

        # 当data_dict不为空时，将其合并到response字典中
        if data_dict:
            response.update(data_dict)

        response_string = json.dumps(response)  # 将字典转换成字符串

        self.request.send(response_string.encode(encoding="utf-8"))
        print("发往客户端的消息是", response)  # 注意这里打印的信息要是转换二进制前的数据

    def receive_message(self):
        """
        接收客户端消息的方法函数
        :return:
        """""
        # 接收客户端消息，并将消息转换成字符串
        data_string = self.request.recv(8096).decode(encoding="utf-8")

        # 从字符串转换为字典类型
        data = json.loads(data_string)
        print("接收到客户端的消息是", data)

        return data

    def load_account(self):
        """从文件中取出账户数据的方法函数"""
        with open(self.user_file_path, "r", encoding="utf-8") as f:
            account_data = json.load(f)  # 通过反序列化从文件中取出账户数据，并转换成字典

        return account_data

    def dump_account(self, account_data):
        """
        将账户数据保存到文件中的方法函数
        :param account_data: 账户数据
        :return: True
        """""
        with open(self.user_file_path, "w", encoding="utf-8") as f:
            json.dump(account_data, f)  # 通过序列化将账户数据字典保存到文件中

        print("\033[1;32m账户数据保存成功\033[0m")

        return True


class FtpServer(object):
    """ftp服务端类"""
    def __init__(self):
        print("服务端开始运行")

        # 实例化服务类，并且将ip地址、端口号和自定义的请求处理类传递进去
        server = socketserver.ThreadingTCPServer((settings.HOST, settings.PORT), MyFtpServer)

        server.serve_forever()  # 能处理多个连接，并且不会退出
