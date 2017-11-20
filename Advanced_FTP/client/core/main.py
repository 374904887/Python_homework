#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import socket
import hashlib
import json
import os
import time
import re
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
        """认证ftp帐号的方法函数"""
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
                    self.username = username  # 将用户名封装到对象中

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
        self.current_directory = self.delimiter  # 当前所处目录的路径，默认为用户家目录，用一个路径分隔符表示

        while True:  # 使客户端能和服务端多次通信

            shell_prompt = self.edit_shell_prompt()  # 合成shell提示符的方法函数

            user_input = input(shell_prompt).strip()

            if len(user_input) == 0:  # 不能发送空内容
                continue

            command_list = user_input.split()  # 把输入的命令以空格为分隔符转换成列表

            if command_list[0] in ["q", "quit", "exit"]:
                print("\033[1;31m退出程序\033[0m")
                break
            elif hasattr(self, "_%s" % command_list[0]):  # 判断对象中是否有用户输入的字符串类型成员
                function = getattr(self, "_%s" % command_list[0])  # 获取对象成员的内存对象地址
                function(command_list)  # 调用
            else:
                print("\033[1;31m输入的命令有误，请重新输入\033[0m")
                self._help()

    def _get(self, command_list):
        """
        客户端从服务端下载文件的方法函数
        1: 客户端往服务端发送下载文件的命令，文件如果带有路径分隔符，分隔符的数量必须是两个
        2: 客户端接收服务端响应的下载文件总大小
        3: 判断客户端上是否存在需要下载的文件
        4: 存在，且文件大小大于零、小于完整文件总大小，则调用恢复上次下载的方法函数
        5: 不存在，或文件大小等于零、等于完整文件总大小，则正常下载文件
        :param command_list: 用户输入的命令，已经转换成列表
        :return:
        """""
        result = self.analysis_command(command_list)  # 调用解析输入命令的方法函数

        if not result:  # 输入的下载文件命令不完整
            return

        # 输入的下载文件信息不是以路径分隔符开头的，就将家目录到当前所处目录的路径加到前面
        if not result["file_path"].startswith(self.delimiter):
            result["file_path"] = self.current_directory + result["file_path"]

        self.send_message(result)  # 调用往服务端发送消息的方法函数，发送下载文件命令

        server_response = self.receive_message()  # 调用接收服务端消息的方法函数
        if server_response.get("status_code") == 108:  # 接收服务端发送的文件大小

            file_total_size = server_response["file_total_size"]  # 获取服务端上下载文件的总大小

            # 获取文件名
            filename = command_list[1].split(self.delimiter)[-1]
            # 生成客户端上保存下载文件的file目录绝对路径
            file_path = "%s%s%s" % (settings.file_path, self.delimiter, filename)

            # 把display_progress方法函数变成生成器
            progress = self.display_progress(file_total_size)

            m = hashlib.md5()  # 生成md5对象

            # 客户端上存在需要下载的文件，并且文件容量大于零、小于服务端上的文件容量
            if os.path.isfile(file_path) and 0 < os.path.getsize(file_path) < file_total_size:
                print("上次下载\033[1;31m%s\033[0m任务未完成，恢复任务继续下载" % command_list[1])

                incomplete_file_size = os.path.getsize(file_path)  # 获取需要继续下载的文件大小

                # 调用恢复未完成下载任务的方法函数
                client_md5_value = self.recovery_download(file_path, incomplete_file_size, file_total_size, progress, m)

            else:

                self.send_message(109)  # 调用往服务端发送消息的方法函数，客户端准备接收文件

                received_size = 0  # 累计接收到数据的总大小

                # 执行生成器，执行到yield语句处返回，并保存状态
                progress.__next__()

                with open(file_path, "wb") as f:
                    while received_size < file_total_size:  # 累计接收到的内容大小小于文件总大小就一直接收

                        # 剩余的内容大小大于1024，代表需要接收的次数不止一次
                        if file_total_size - received_size > 8096:
                            size = 8096
                        else:  # 剩余的内容大小小于1024，代表一次就可以接收完剩余数据
                            size = file_total_size - received_size

                        data = self.client.recv(size)
                        f.write(data)
                        received_size += len(data)  # 将每次接收到数据的大小累加起来

                        # 唤醒yield，将累计接收到数据的总大小传给yield
                        # 唤醒后会从上次返回的yield语句处继续执行
                        progress.send(received_size)

                        m.update(data)  # 将接收到的所有内容添加到md5中，注意hashlib模块只能处理bytes类型的内容
                    else:
                        print("")  # 这里如果不做换行的操作，接下来显示的内容会和进度条在同一行

                        print("客户端文件接收完成，客户端接收到的文件大小为", received_size)

                        client_md5_value = m.hexdigest()  # 按照16进制格式显示
                        print("客户端计算的文件md5值为", client_md5_value)

            # 这里两个recv是连在一起的，代表服务端是两个send连在一起，这样就有可能出现粘包情况
            # 上面在最后一次接收文件时，将接收大小设置为文件剩余内容的大小，这样可以解决粘包的问题
            server_response = self.receive_message()  # 调用接收服务端消息的方法函数，接收服务端发送的文件md5值
            if server_response["md5"] == client_md5_value:
                print("\033[1;32m文件[%s]一致性校验成功\033[0m" % filename)
            else:
                print("\033[1;31m文件[%s]一致性校验失败\033[0m" % filename)

        else:  # 服务端不存在需要下载的文件
            print("\033[1;31m状态码：%s，信息：%s\033[0m"
                  % (server_response["status_code"], server_response["status_message"]))

    def recovery_download(self, file_path, incomplete_file_size, file_total_size, progress, m):
        """
        恢复未完成下载任务的方法函数
        :param file_path: 不完整文件在客户端上的绝对路径
        :param incomplete_file_size: 不完整文件的大小
        :param file_total_size: 完整文件的大小
        :param progress: 打印进度条的生成器内存地址
        :param m: md5对象
        :return: 文件内容的md5值
        """""
        # 拼接恢复未完成的下载任务字典，并且将目前已完成的大小传递给服务端
        data = {
            "status_code": 112,
            "status_message": STATUS_CODE[112],
            "incomplete_file_size": incomplete_file_size
        }

        self.send_message(data)  # 调用往服务端发送消息的方法函数，通知客户端恢复未完成的下载任务

        received_size = incomplete_file_size  # 累计接收到数据的总大小

        # 执行生成器，执行到yield语句处返回，并保存状态
        progress.__next__()

        with open(file_path, "ab") as f:  # 用二进制追加模式打开
            while received_size < file_total_size:  # 累计接收到的内容大小小于文件总大小就一直接收

                # 剩余的内容大小大于1024，代表需要接收的次数不止一次
                if file_total_size - received_size > 8096:
                    size = 8096
                else:  # 剩余的内容大小小于1024，代表一次就可以接收完剩余数据
                    size = file_total_size - received_size

                data = self.client.recv(size)
                f.write(data)
                received_size += len(data)  # 将每次接收到数据的长度累加起来

                # 唤醒yield，将累计接收到数据的总大小传给yield
                # 唤醒后会从上次返回的yield语句处继续执行
                progress.send(received_size)

            else:
                print("")  # 这里如果不做换行的操作，接下来显示的内容会和进度条在同一行

                print("客户端文件接收完成，客户端接收到的文件大小为", received_size)

        with open(file_path, "rb") as f:
            for line in f:
                m.update(line)  # 将文件所有内容添加到md5中，注意hashlib模块只能处理bytes类型的内容

        client_md5_value = m.hexdigest()  # 按照16进制格式显示
        print("客户端计算的文件md5值为", client_md5_value)

        return client_md5_value

    def _put(self, command_list):
        """
        客户端上传文件到服务端的方法函数
        1: 判断上传文件是否存在
        2: 获取上传文件的大小
        3: 将上传文件的命令发送到服务端
        4: 向服务端发送文件内容
        5: 文件发送完成后做MD5值验证
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
            # 将当前在服务端所处的目录路径也加到操作字典中
            result["current_directory"] = self.current_directory

            self.send_message(result)  # 调用往服务端发送消息的方法函数，发送上传文件操作字典

            server_response = self.receive_message()  # 调用接收服务端消息的方法函数

            if server_response["status_code"] == 111:  # 服务端准备接收文件
                send_size = 0  # 累计发送数据的总大小

                m = hashlib.md5()  # 生成md5对象

                # 把display_progress方法函数变成生成器
                progress = self.display_progress(file_total_size)
                # 执行生成器，执行到yield语句处返回，并保存状态
                progress.__next__()

                with open(file_path, "rb") as f:
                    for line in f:
                        self.client.send(line)  # 按照每次只发送一整行内容的方式向客户端发送
                        send_size += len(line)  # 将每次发送数据的大小累加起来

                        # 唤醒yield，将累计发送数据的总大小传给yield
                        # 唤醒后会从上次返回的yield语句处继续执行
                        progress.send(send_size)

                        m.update(line)  # 将文件每一行的内容添加到md5中，注意hashlib模块只能处理bytes类型的内容

                print("")  # 这里如果不做换行的操作，接下来显示的内容会和进度条在同一行

                client_md5_value = m.hexdigest()  # 按照16进制格式显示
                print("客户端计算的文件md5值为", client_md5_value)

                server_response = self.receive_message()  # 调用接收服务端消息的方法函数，接收服务端发送的文件md5值
                if server_response["md5"] == client_md5_value:
                    self.send_message(114)  # 调用往服务端发送消息的方法函数，发送MD5值验证成功消息
                    print("\033[1;32m[%s]文件一致性校验成功\033[0m" % filename)

                    # 调用接收服务端消息的方法函数，接收服务端发送用户当前可用空间大小
                    server_response = self.receive_message()
                    print("当前用户可用空间大小为\033[1;32m %s \033[0m字节" % server_response["quota"])
                else:
                    print("\033[1;31m[%s]文件一致性校验失败\033[0m" % filename)

            if server_response["status_code"] == 110:  # 用户在服务端上可用空间不足，无法上传该文件
                print("\033[1;31m[%s]\033[0m" % server_response["status_message"])

        else:
            print("\033[1;31m需要上传的文件[%s]客户端上不存在\033[0m" % filename)

    def _cd(self, command_list):
        """
        切换目录的方法函数
        :param command_list: 用户输入的命令，已经转换成列表
        :return:
        """""
        result = self.analysis_command(command_list)  # 调用解析输入命令的方法函数

        if not result:
            return

        if result["file_path"] == "..%s" % self.delimiter:  # 返回到上级目录
            if self.current_directory == self.delimiter:  # 当前处于家目录顶层，不能访问家目录以外的目录
                print("\033[1;31m当前已处于根目录最顶层\033[0m")
                return

            else:  # 当前不处于家目录顶级时，返回到上级目录

                # 将当前所处目录的路径，按照路径分隔符转换成列表
                directory_list = self.current_directory.split(self.delimiter)

                # 去掉列表最后两个元素，倒数第一个元素是空，倒数第二个元素是当前所处的目录
                directory_list_new = directory_list[:-2]
                # 因为路径分隔符的原因，列表第一个元素为空
                del directory_list_new[0]

                if len(directory_list_new) >= 1:  # 返回到上级目录后，所处目录不是家目录顶级
                    # 将列表中的元素转换成字符串，每个元素直接插入路径分隔符，并在字符串开头加上路径分隔符
                    result["file_path"] = self.delimiter + self.delimiter.join(directory_list_new)
                else:
                    self.current_directory = self.delimiter
                    return

        # 输入的内容只有一个路径分隔符，代表返回到家目录顶层
        elif result["file_path"] == self.delimiter:
            self.current_directory = self.delimiter
            return

        # 输入内容开头是大小写字母、数字、下划线、汉字，只能切换到下级目录
        elif re.match("\w", result["file_path"]):
            result["file_path"] = self.current_directory + result["file_path"]

        # 输入内容开头是路径分隔符加大小写字母、数字、下划线、汉字，切换到下级目录或其它目录
        elif re.match("\\\\\w", result["file_path"]):
            # 如果输入的路径是以路径分隔符开头的，这里直接pass，必须要有这个判断，不然会匹配下面的else语句
            pass

        else:
            print("\033[1;31m输入目录名错误\033[0m")
            return

        # 如果拼接好的路径不是以路径分割符结尾，需要在结尾处加上路径分隔符，不然下次拼接出来的路径是错误的
        if not result["file_path"].endswith(self.delimiter):
            result["file_path"] = result["file_path"] + self.delimiter

        self.send_message(result)  # 调用往服务端发送消息的方法函数，发送切换目录的操作字典

        server_response = self.receive_message()  # 调用接收服务端消息的方法函数
        if server_response["status_code"] == 116:  # 服务端上存在要切换的目录

            # 路径信息后面一定要加上路径分隔符，不然下次拼接出来的路径是错的
            self.current_directory = result["file_path"]

        if server_response["status_code"] == 117:  # 服务端上不存在要切换的目录
            print("\033[1;31m不存在该目录\033[0m")

    def _mkdir(self, command_list):
        """
        创建目录的方法函数
        :param command_list: 用户输入的命令，已经转换成列表
        :return:
        """""
        result = self.analysis_command(command_list)  # 调用解析输入命令的方法函数

        if not result:
            return

        # 输入的目录信息最后有可能带上路径分隔符，所以这里将信息后面都加上路径分隔符
        if not result["file_path"].endswith(self.delimiter):
            result["file_path"] = result["file_path"] + self.delimiter  # 在最后加上路径分隔符

        # 输入的目录信息不是以路径分隔符开头的，代表在当前目录下创建目录
        if not result["file_path"].startswith(self.delimiter):
            result["file_path"] = self.current_directory + result["file_path"]

        directory_list = result["file_path"].split(self.delimiter)

        # 需要创建的目录名中包含有非字母、非数字、非下划线、非汉字的特殊字符
        if re.search("\W", directory_list[-2]): # 列表倒数第二个元素是需要创建的目录
            print("\033[1;31m输入的目录名中含有非法特殊字符\033[0m")
            return

        # 因为最后一个字符是路径分隔符的原因，列表最后一个元素是空的。将倒数两个元素删掉
        check_directory_list = directory_list[:-2]
        del check_directory_list[0]  # 因为路径是以路径分隔符开头，第一个元素是空的，这里要删除掉
        check_directory = self.delimiter.join(check_directory_list)  # 列表转换成字符串
        result["check_directory"] = self.delimiter + check_directory

        self.send_message(result)  # 调用往服务端发送消息的方法函数，发送创建目录和检测目录的操作字典

        server_response = self.receive_message()  # 调用接收服务端消息的方法函数
        if server_response["status_code"] == 118:  # 目录创建成功
            print("\033[1;32m[%s]\033[0m" % server_response["status_message"])
        elif server_response["status_code"] == 119:  # 目录创建失败，输入的目录中某一级不存在
            print("\033[1;31m[%s]\033[0m" % server_response["status_message"])
        elif server_response["status_code"] == 210:  # 需要创建的目录已存在
            print("\033[1;31m[%s]\033[0m" % server_response["status_message"])

    def _dir(self, command_list):
        """
        显示目录中的文件和子目录的方法函数
        :param command_list: 用户输入的命令，已经转换成列表
        :return:
        """""
        if len(command_list) == 1:
            path = self.current_directory
        elif len(command_list) == 2:  # dir后面还输入了路径信息
            path = command_list[1]

            if not path.startswith(self.delimiter):  # 输入的路径信息是不以路径分隔符开头的
                path = self.current_directory + path  # 将当前所处目录和输入的目录拼接起来
        else:
            print("\033[1;31m输入的命令格式错误\033[0m")

        data_header = {
            "action": command_list[0],
            "file_path": path,
        }

        self.send_message(data_header)  # 调用往服务端发送消息的方法函数，发送查看目录的操作字典

        server_response = self.receive_message()  # 调用接收服务端消息的方法函数
        if server_response["status_code"] == 211:  # 服务端发送了命令执行结果的大小
            result_total_size = server_response["result_total_size"]  # 获取命令执行结果总大小
            received_size = 0  # 累计接收到数据的总大小
            received_data = b""  # 装载接收数据内容

            self.send_message(213)  # 调用往服务端发送消息的方法函数，发送客户端准备好接收命令执行结果消息

            while received_size < result_total_size:
                data = self.client.recv(8096)
                received_data += data  # 保存每次接收的数据
                received_size += len(data)  # 将每次接收到的数据大小累加起来
            else:
                print("客户端接收到的命令执行结果大小为", received_size)
                print("命令执行结果是")

                # 显示命令运行结果。注意，windows默认字符编码是gbk
                print(received_data.decode(encoding="gbk"))

        elif server_response["status_code"] == 212:  # 需要查看的目录不存在
            print("\033[1;31m[%s]\033[0m" % server_response["status_message"])

    def _pwd(self, *args):
        """
        显示完整的当前所在目录的路径信息
        :param args: 扩展参数
        :return:
        """""
        print(self.current_directory)

    def _exit(self, *args):
        """
        退出程序的方法函数
        :param args: 扩展参数
        :return:
        """""
        self.client.close()  # 关闭socket
        exit("退出程序")

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

        -- 从ftp server下载文件
            命令示例：
                get \d1\d2\shell.wmv：下载ftp server上d2目录中的shell.wmv文件
                get shell.wmv：下载在ftp server上当前所处目录中的shell.wmv文件

        -- 上传文件到ftp server上
            命令示例：
                put shell.wmv：将shell.wmv文件上传到在ftp server上当前所处的ftp server目录中

        -- 在ftp server上用户家目录中切换目录
            命令示例：
                cd \：切换到家目录最顶层
                cd d1：切换到在ftp server上当前所处的目录下的d1目录中
                cd \d1\d2：切换到\d1\d2目录中

        -- 在ftp server上用户家目录中创建目录
            命令示例：
                mkdir d1：在ftp server上当前所处的目录下创建d1目录
                mkdir \d1\d2：在ftp server上创建\d1\d2目录

        -- 查看在ftp server上目录中的文件和子目录信息
            命令示例：
                dir：查看在ftp server上，当前所处目录中的文件和子目录信息
                dir \：查看ftp server上，家目录最顶层下的文件和子目录信息
                dir d1：查看ftp server上，当前所处的目录下的d1目录中的文件和子目录信息
                dir \d1\d2\：查看ftp server上，\d1\d2目录中的文件和子目录信息

        -- 查看当前在ftp server上所处的目录路径
            命令示例：
                pwd

        -- 结束程序运行，退出整个程序
            命令示例：
                eixt

        -- 查看FTP程序使用帮助信息
            命令示例：
                help
        """
        print(help_information)

    def analysis_command(self, command_list):
        """
        解析输入命令的方法函数，将输入的命令拼接成字典
        :param command_list: 用户输入的命令，已经转换成列表
        :return:
        """""
        print("命令列表为", command_list)

        if len(command_list) < 2:
            print("\033[1;31m输入的命令不完整，只有命令类型，请重新输入\033[0m")
            return

        data_header = {
            "action": command_list[0],
            "file_path": command_list[1]
        }

        return data_header

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
        data_string = self.client.recv(8096).decode(encoding="utf-8")

        # 从字符串转换为字典类型
        data = json.loads(data_string)
        print("接收到服务端的消息是", data)

        return data

    def display_progress(self, file_total_size):
        """
        传输数据时显示进度条的方法函数
        :param file_total_size: 文件总大小
        :return:
        """""
        success_size = 0  # 已经成功接收或发送的数据总大小
        time_consuming = 0  # 接收或发送文件历时，单位是秒
        speed = 0  # 网速，单位是KB/s
        start_time = time.time()  # 开始接收或发送文件时的时间戳

        # 已经成功接收或发送的数据大小 小于等于 总文件大小时，就要打印进度条
        # 一定要等于，不然百分之百就打印不出来
        # 等于后，外部函数调用生成器的次数就小于了生成器总共可调用的次数，就不用捕获StopIteration错误
        while success_size <= file_total_size:

            # 当前已经成功接收或发送的数据总大小所占总文件大小的百分比例，是一个整数
            percentage = int(success_size / file_total_size * 100)

            # \r表示回车，但是没有\n的话，就不会到下一行，而是将光标移到了本行最前面，然后继续输出\r后面的字符
            # \r后面的字符就是进度条，由于已经将进度条长度固定，所以每次新打印的进度条都会完全覆盖之前的进度条
            print(end="\r")

            # 进度条内容长度已经固定，输出进度条后不换行，实时刷新内存
            # 各字段代表的意思：完成百分比 进度条 网速 耗时
            print("{:>3}% [{:<100}] {:>8}KB/s {:>6}s".format(percentage, ">" * percentage, speed, time_consuming),
                  end="", flush=True)

            success_size = yield  # 通过yield接收已经成功接收或发送的数据总大小

            stop_time = time.time()  # 本次yield接收到数据时的时间戳

            # 接收或发送文件历时，四舍五入保留小数点后两位
            time_consuming = round(stop_time - start_time, 2)

            # 第一次给yield传值的时候，开始时间戳和结束时间戳是一样的，而除数不能为零
            if time_consuming != 0:

                # 已经成功接收或发送的数据总大小除于1024后单位就是KB，再除于接收或发送文件历时后单位就是KB/s
                # 获得的值四舍五入保留小数点后两位
                speed = round(success_size / 1024 / time_consuming, 2)

    def edit_shell_prompt(self):
        """
        合成shell提示符的方法函数
        :return: shell提示符
        """""
        if self.current_directory == self.delimiter:
            directory = "~"
        else:
            directory = self.current_directory.split(self.delimiter)[-2]  # 获取当前所处目录的目录名

        # 拼接shell提示符
        shell_prompt = "\033[1;36m[%s@%s %s]$\033[0m " % (self.username, settings.ip_port[0], directory)

        return shell_prompt
