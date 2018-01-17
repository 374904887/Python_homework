#!/user/bin/env python
# -*- coding:utf-8 -*-
__author__ = "Zhong Lu"


import socket
import selectors
import json
import os
import subprocess
import queue
from conf import settings
from core import logger


# 获取注册或登陆帐号日志的logger对象
login_logger = logger.logger_function("register_login")
# 获取执行shell命令日志的logger对象
command_logger = logger.logger_function("command")
# 获取下载文件日志的logger对象
download_logger = logger.logger_function("download")
# 获取上传文件日志的logger对象
upload_logger = logger.logger_function("upload")


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


class FtpServer(object):
    """ftp服务端类"""
    def __init__(self):
        # DefaultSelector类自动根据当前系统平台选择最有效的IO多路复用机制，linux就会选择epoll、windows选择select
        # 同时也生成一个对象
        self.sel = selectors.DefaultSelector()

        # 声明socket类型，同时生成socket连接对象
        # family默认是AF_INET，type默认是SOCK_STREAM，可以不用再写了
        server = socket.socket()

        # 绑定ip地址和端口号
        server.bind(settings.ip_port)

        # 监听连接。并设置连接通信后最多可以挂起1000个连接
        server.listen(1000)

        # 把socket server设置成非阻塞模式，会导致accept()和recv()都不阻塞。accept()和recv()一旦没有数据就会报错
        # 代码一定要写在accept()和recv()之前
        server.setblocking(False)

        # 注册文件对象。SelectorKey类，一般用这个类的实例来描述一个已经注册的文件对象的状态
        # fileobj可以是文件描述符，也可以是一个拥有fileno()方法的对象。这里是socket server对象
        # EVENT_READ表示可读的。它的值其实是1
        # 绑定的data是accept函数。只要来了新连接就调用accept函数
        self.sel.register(server, selectors.EVENT_READ, self.accept)  # fileobj就相当select.select(rlist, wlist, xlist)里的rlist列表中的对象

        self.connect_dict = {}  # 初始化一个字典，用来存放连接信息

        while True:
            # 开始监听
            # 返回的是一个(key, events)的元组，key是SelectorKey类的实例，events是event Mask（EVENT_READ或EVENT_WRITE，或者二者的组合）
            # 默认是阻塞状态，当监听的文件描述符（socket连接）就绪了，代表来新连接了或者客户端发来数据了
            events = self.sel.select()  # key就相当select.select(rlist, wlist, xlist)返回的readable列表（与rlist列表对应）中的对象

            for key, mask in events:
                # key是SelectorKey类的实例，data表示注册文件对象时绑定的data（函数）
                # 当来了新连接的情况下，注册文件对象时绑定的data是accept函数，这里就相当于callback = accept
                # 当新连接发来数据的情况下，注册文件对象时绑定的data是read函数，这里就相当于callback = read
                callback = key.data

                # 调用accept函数或read函数，并且传递了一个参数
                # fileobj表示注册文件对象时传递的文件描述符或fileno()方法的对象，这里fileobj是socket server对象
                callback(key.fileobj)

    def accept(self, socket_obj):
        """
        接收新连接的方法函数
        :param socket_obj: 是key.fileobj。注册文件对象时，注册的文件描述符或注册的fileno()方法的对象。这里fileobj是socket server对象
        :return:
        """""
        conn, address = socket_obj.accept()  # 接收新的连接
        print('接收的新连接', conn, '来自于', address)

        conn.setblocking(False)  # 将接收的新连接也设置成非阻塞模式

        # 再注册文件对象
        # fileobj是新连接对象
        # EVENT_READ表示可读的。它的值其实是1
        # 绑定的data是read函数。当新连接活动了（客户端发来数据了）就调用read函数
        self.sel.register(conn, selectors.EVENT_READ, self.read)  # fileobj就相当select.select(rlist, wlist, xlist)里的rlist列表中的对象

        self.connect_dict[conn] = {
            "login_status": False,        # 用户是否登陆
            "user_home_path": None,       # 用户家目录
            "perform_command": None,      # 连接当前执行的命令
            "transmission_data": False,   # 连接当前是否处于传输剩余数据阶段
            "file_name": None,            # 当前上传、下载的文件绝对路径
            "file_size": 0,               # 当前上传、下载的文件总大小
            "receive_size": 0,            # 当前已接收到文件内容的大小
            "send_size": 0,               # 当前已发送文件内容的大小
            "data": queue.Queue(),        # 存放数据的队列，为线程队列
        }

    def read(self, conn):
        """
        接收新连接发送的数据的方法函数
        :param conn: 客户端连接上服务端后，在服务端上为其生成的连接对象
        :return:
        """""
        self.conn = conn  # 将连接对象封装到实例中

        try:
            if self.connect_dict[self.conn]["login_status"]:  # 用户已登录
                if self.connect_dict[self.conn]["transmission_data"]:  # 当前处于传输剩余数据阶段
                    # 获取对象成员的内存对象地址
                    function = getattr(self, "_%s" % self.connect_dict[self.conn]["perform_command"])
                    # 调用对象成员
                    function()
                else:
                    self.analysis()  # 调用解析用户操作的方法函数
            else:
                self.analysis()  # 调用解析用户操作的方法函数

        # ConnectionResetError：与客户端的连接断开的错误
        # json.decoder.JSONDecodeError：当有多个连接同时连接server执行命令的时候，其中一个连接运行exit命令退出后，server端会出现该错误
        except (ConnectionResetError, json.decoder.JSONDecodeError):
            print('关闭连接', self.conn)
            self.sel.unregister(self.conn)  # 注销一个已经注册过的文件对象，这里注销的是与客户端的连接
            self.conn.close()  # 关闭与客户端的连接
            del self.connect_dict[self.conn]  # 从连接信息字典中删除连接的信息
            del self.conn  # 从对象中删除客户端的连接对象

    def analysis(self):
        """
        解析用户操作的方法函数
        :return:
        """""
        # 如果客户端发送的数据大于8192字节的话，由于本次未将全部数据接收完，下次select或epoll循环时，
        # 该连接的文件描述符还会就绪（该连接有数据），这样下次就可以接收剩余的数据了
        data = self.conn.recv(8192)

        # 接收客户端消息，并将消息转换成字符串
        data_string = data.decode(encoding="utf-8")

        # 从字符串转换为字典类型
        data = json.loads(data_string)
        print("接收到客户端的消息是", data)

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

    def _register(self, data):
        """
        注册ftp帐号的方法函数
        :param data: 客户端发送到服务端的操作字典
        :return:
        """""
        username = data["username"]  # 获取用户输入的用户名
        password = data["password"]  # 获取用户输入的密码

        delimiter = os.sep  # 获取当前操作系统路径的分隔符

        # 生成存储用户数据文件的文件名
        user_file = username + ".json"
        # 生成保存账户数据文件的绝对路径。根据当前操作系统生成对应的路径分隔符，否则运行dir命令时会报错
        user_file_path = "%s%s%s" % (settings.user_database_path, delimiter, user_file)

        if os.path.isfile(user_file_path):
            self.send_message(103)  # 调用往客户端发送消息的方法函数
            print("用户\033[1;31m[%s]\033[0m已存在，请重新输入" % username)

        else:  # 输入的用户不存在

            # 生成用户家目录的相对路径。根据当前操作系统生成对应的路径分隔符，否则运行dir命令时会报错
            user_path = "%s%s" % (delimiter, username)

            # 将home目录和用户家目录拼接起来，并封装到对象中
            user_home_path = settings.home_path + user_path

            os.mkdir(user_home_path)  # 创建用户家目录

            # 生成账户数据字典
            account_data = {
                "id": username,
                "password": password,
            }

            self.dump_account(account_data, user_file_path)  # 调用将账户数据保存到文件中的方法函数

            self.send_message(102)  # 调用往客户端发送消息的方法函数，发送注册成功消息

            self.connect_dict[self.conn]["login_status"] = True  # 修改用户登陆状态
            self.connect_dict[self.conn]["user_home_path"] = user_home_path  # 将拼接起来的路径存到连接信息字典中

            login_logger.info("用户 %s 注册成功" % username)  # 保存到日志文件中

            print("用户\033[1;32m[%s]\033[0m创建成功" % username)

    def _login(self, data):
        """
        登陆ftp帐号的方法函数
        :param data: 客户端发送到服务端的操作字典
        :return:
        """""
        username = data["username"]  # 获取用户输入的用户名
        password = data["password"]  # 获取用户输入的密码

        delimiter = os.sep  # 获取当前操作系统路径的分隔符

        # 生成存储用户数据文件的文件名
        user_file = username + ".json"
        # 生成保存账户数据文件的绝对路径。根据当前操作系统生成对应的路径分隔符，否则运行dir命令时会报错
        user_file_path = "%s%s%s" % (settings.user_database_path, delimiter, user_file)

        if os.path.isfile(user_file_path):  # 输入的用户存在

            account_data = self.load_account(user_file_path)  # 调用从文件中取出账户数据的方法函数

            if password == account_data["password"]:  # 验证密码是否正确

                # 生成用户家目录的相对路径。根据当前操作系统生成对应的路径分隔符，否则运行dir命令时会报错
                user_path = "%s%s" % (delimiter, username)
                # 将home目录和用户家目录拼接起来
                user_home_path = settings.home_path + user_path

                self.send_message(104)  # 调用往客户端发送消息的方法函数，发送用户登陆成功消息

                self.connect_dict[self.conn]["login_status"] = True  # 修改用户登陆状态
                self.connect_dict[self.conn]["user_home_path"] = user_home_path  # 将拼接起来的路径存到连接信息字典中

                login_logger.info("用户 %s 登陆成功" % username)  # 保存到日志文件中

            else:
                self.send_message(105)  # 调用往客户端发送消息的方法函数，发送密码错误消息

        else:
            self.send_message(106)  # 调用往客户端发送消息的方法函数，发送用户不存在消息

    def _dir(self, *args):
        """
        显示目录中的文件和子目录的方法函数
        :param args: 扩充参数，有可能是客户端发送到服务端的操作字典
        :return:
        """""
        if not self.connect_dict[self.conn]["perform_command"]:  # 客户端申请执行新的命令
            data = args[0]

            command = "%s %s" % (data["action"], self.connect_dict[self.conn]["user_home_path"])  # 拼接命令

            # 执行命令，并获取命令执行结果。注意，通过subprocess获取的命令执行结果默认都是以二进制方式显示
            result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result_bytes = result.stdout.read()  # 取出命令结果，是bytes类型

            # 将命令结果放入队列中
            self.connect_dict[self.conn]["data"].put(result_bytes)

            result_total_size = len(result_bytes)  # 获取命令执行结果大小

            # 调用往客户端发送消息的方法函数，发送命令执行结果的大小
            self.send_message(111, data_dict={"result_total_size": result_total_size})

            self.connect_dict[self.conn]["perform_command"] = "dir"  # 修改连接信息字典中执行命令（key）的value
            self.connect_dict[self.conn]["transmission_data"] = True  # 修改连接信息字典中是否处于传输剩余数据阶段（key）的value
        else:
            # 接收客户端的消息，并转换数据类型
            client_response = json.loads(self.conn.recv(8192).decode(encoding="utf-8"))
            if client_response["status_code"] == 112:
                self.conn.send(self.connect_dict[self.conn]["data"].get())

            command_logger.info("执行dir命令查看 %s 目录" % self.connect_dict[self.conn]["user_home_path"])  # 保存到日志文件中

            self.end_command()  # 命令执行完成后，调用修改连接信息字典的方法函数

    def _get(self, *args):
        """
        客户端从服务端下载文件的方法函数
        :param args: 扩展参数，有可能是客户端发送到服务端的操作字典
        :return:
        """""
        if not self.connect_dict[self.conn]["perform_command"]:  # 客户端申请执行新的命令
            data = args[0]

            # 拼接下载文件在服务端上的绝对路径
            file_path = self.connect_dict[self.conn]["user_home_path"] + os.sep + data["file_path"]

            if os.path.isfile(file_path):  # 下载的文件存在
                file_total_size = os.path.getsize(file_path)  # 获取客户端需要下载的文件总大小
                print("客户端需要下载的文件总大小为\033[1;32m[%s]\033[0m字节" % file_total_size)

                # 调用往客户端发送消息的方法函数，发送文件大小
                self.send_message(108, data_dict={"file_total_size": file_total_size})

                self.connect_dict[self.conn]["perform_command"] = "get"  # 修改连接信息字典
                self.connect_dict[self.conn]["transmission_data"] = True
                self.connect_dict[self.conn]["file_name"] = file_path
                self.connect_dict[self.conn]["file_size"] = file_total_size
            else:
                self.send_message(107)  # 调用往客户端发送消息的方法函数，发送需要下载的文件不存在消息
        else:
            client_response = json.loads(self.conn.recv(8192).decode(encoding="utf-8"))  # 接收客户端的消息，并转换数据类型
            if client_response["status_code"] == 109:

                if self.connect_dict[self.conn]["file_size"] - self.connect_dict[self.conn]["send_size"] > 8192:
                    size = 8192
                else:
                    size = self.connect_dict[self.conn]["file_size"] - self.connect_dict[self.conn]["send_size"]

                with open(self.connect_dict[self.conn]["file_name"], "rb") as f:
                    # 从文件头向文件尾偏移文件指针，移到上次发送文件停止时文件指针所处的位置
                    f.seek(self.connect_dict[self.conn]["send_size"], 0)
                    data = f.read(size)
                    self.conn.send(data)

                    self.connect_dict[self.conn]["send_size"] += len(data)

                # 文件内容传输完毕后，修改连接信息字典
                if self.connect_dict[self.conn]["send_size"] >= self.connect_dict[self.conn]["file_size"]:
                    print("\033[1;32m文件[%s]已传输完成\033[0m" % self.connect_dict[self.conn]["file_name"].split(os.sep)[-1])

                    download_logger.info("下载了 %s 文件" % self.connect_dict[self.conn]["file_name"])  # 保存到日志文件中

                    self.end_command()  # 命令执行完成后，调用修改连接信息字典的方法函数

    def _put(self, *args):
        """
        客户端往服务端上传文件的方法函数
        :param args: 扩展参数，有可能是客户端发送到服务端的操作字典
        :return:
        """""
        if not self.connect_dict[self.conn]["perform_command"]:  # 客户端申请执行新的命令
            data = args[0]

            file_total_size = data["file_total_size"]  # 获取客户端要上传的文件总大小

            # 拼接上传的文件保存到服务端的绝对路径
            file_path = self.connect_dict[self.conn]["user_home_path"] + os.sep + data["file_path"]

            self.send_message(110)  # 调用往客户端发送消息的方法函数，服务端准备好接收文件

            self.connect_dict[self.conn]["perform_command"] = "put"  # 修改连接信息字典
            self.connect_dict[self.conn]["transmission_data"] = True
            self.connect_dict[self.conn]["file_name"] = file_path
            self.connect_dict[self.conn]["file_size"] = file_total_size
        else:
            with open(self.connect_dict[self.conn]["file_name"], "ab") as f:
                file_data = self.conn.recv(8192)
                f.write(file_data)
                self.connect_dict[self.conn]["receive_size"] += len(file_data)  # 将每次接收到数据的大小累加起来

            if self.connect_dict[self.conn]["receive_size"] >= self.connect_dict[self.conn]["file_size"]:  # 文件内容接收完毕
                print("\033[1;32m文件[%s]已上传完成\033[0m" % self.connect_dict[self.conn]["file_name"].split(os.sep)[-1])

                upload_logger.info("上传了 %s 文件" % self.connect_dict[self.conn]["file_name"])  # 保存到日志文件中

                self.end_command()  # 命令执行完成后，调用修改连接信息字典的方法函数

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

        self.conn.send(response_string.encode(encoding="utf-8"))
        print("发往客户端的消息是", response)  # 注意这里打印的信息要是转换二进制前的数据

    def load_account(self, user_file_path):
        """
        从文件中取出账户数据的方法函数
        :param user_file_path: 保存账户数据文件的绝对路径
        :return:
        """""
        with open(user_file_path, "r", encoding="utf-8") as f:
            account_data = json.load(f)  # 通过反序列化从文件中取出账户数据，并转换成字典

        return account_data

    def dump_account(self, account_data, user_file_path):
        """
        将账户数据保存到文件中的方法函数
        :param account_data: 账户数据
        :param user_file_path: 保存账户数据文件的绝对路径
        :return:
        """""
        with open(user_file_path, "w", encoding="utf-8") as f:
            json.dump(account_data, f)  # 通过序列化将账户数据字典保存到文件中

        print("\033[1;32m账户数据保存成功\033[0m")

        return True

    def end_command(self):
        """命令执行完毕，修改连接信息字典的方法函数"""
        self.connect_dict[self.conn]["perform_command"] = None
        self.connect_dict[self.conn]["transmission_data"] = False
        self.connect_dict[self.conn]["file_name"] = None
        self.connect_dict[self.conn]["file_size"] = 0
        self.connect_dict[self.conn]["receive_size"] = 0
        self.connect_dict[self.conn]["send_size"] = 0
