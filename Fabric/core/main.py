#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import configparser
import paramiko
import threading
import os
from prettytable import PrettyTable
from conf import settings
from core import logger


# 获取执行shell命令日志的logger对象
command_logger = logger.logger_function("command")
# 获取下载文件日志的logger对象
download_logger = logger.logger_function("download")
# 获取上传文件日志的logger对象
upload_logger = logger.logger_function("upload")


class Fabric(object):
    """主机管理程序类"""
    def __init__(self):
        menu_dict = {
            "1": ["主机组1", "group1"],
            "2": ["主机组2", "group2"],
            "3": ["退出程序", "_exit"]
        }
        menu_list = PrettyTable(["功能ID", "功能描述"])  # 设置表格的列数为两列，以及对每列数据作用的说明
        menu_list.padding_width = 2  # 列数据两边的空格数各增加1个
        menu_list.add_row(["1", menu_dict["1"][0]])  # 向表中添加一行
        menu_list.add_row(["2", menu_dict["2"][0]])
        menu_list.add_row(["3", menu_dict["3"][0]])
        while True:
            print(menu_list)
            user_choice = input("选择ID:\n>>>").strip()

            # 当输入的数字不存在或不是数字时，去字典中取值会报KeyError的错
            try:
                if user_choice in ["1", "2"]:
                    self.config = configparser.ConfigParser()  # 生成ConfigParser对象，并封装进对象中

                    # 生成机器组文件的绝对路径
                    group_path = os.path.join(settings.host_path, menu_dict[user_choice][1])
                    self.config.read(group_path)

                    self.ip_address_list = self.config.sections()  # 将主机ip地址列表封装进对象中
                    print("主机ip地址：")
                    for ip_address in self.ip_address_list:
                        print("\t", ip_address)

                    self.interactive_two_layer()  # 调用交互第二层方法函数

                elif hasattr(self, menu_dict[user_choice][1]):  # 判断对象中是否有用户输入的字符串类型成员
                    function = getattr(self, menu_dict[user_choice][1])  # 获取对象中成员的内存对象地址
                    function()
            except KeyError as e:
                print("\033[1;31m输入的内容 [%s] 有误请重试\033[0m" % e)

    def interactive_two_layer(self):
        """
        交互第二层方法函数
        :return:
        """""
        operation_dict = {
            "1": ["执行shell命令", "interactive_shell_command"],
            "2": ["下载文件", "interactive_get"],
            "3": ["上传文件", "interactive_put"],
            "4": ["返回上一层", "break"],
            "5": ["退出程序", "_exit"]
        }
        operation_list = PrettyTable(["功能ID", "功能描述"])  # 设置表格的列数为两列，以及对每列数据作用的说明
        operation_list.padding_width = 2  # 列数据两边的空格数各增加1个
        operation_list.add_row(["1", operation_dict["1"][0]])  # 向表中添加一行
        operation_list.add_row(["2", operation_dict["2"][0]])
        operation_list.add_row(["3", operation_dict["3"][0]])
        operation_list.add_row(["4", operation_dict["4"][0]])
        operation_list.add_row(["5", operation_dict["5"][0]])
        while True:
            print(operation_list)
            choice = input("选择ID:\n>>>").strip()

            # 当输入的数字不存在或不是数字时，去字典中取值会报KeyError的错
            try:
                if choice == "4":
                    break
                elif hasattr(self, operation_dict[choice][1]):
                    func = getattr(self, operation_dict[choice][1])
                    func()
            except KeyError as e:
                print("\033[1;31m输入的内容 [%s] 有误请重试\033[0m" % e)

    def interactive_shell_command(self):
        """
        用户输入shell命令的方法函数
        :return:
        """""
        while True:
            command = input("输入需要执行的shell命令，或输入b返回到上一层\n>>>").strip()
            if command in ["b", "back"]:
                break
            elif len(command) == 0:
                print("输入的命令为空，请重新输入")
                continue

            self.data_header = {
                "function": self._shell_command,
                "command": command
            }

            self.open_thread()  # 调用开启线程的方法函数

    def interactive_get(self):
        """
        下载文件交互的方法函数
        :return:
        """""
        while True:
            source_file = input("输入需要下载的文件，或输入b返回到上一层\n>>>").strip()
            if source_file in ["b", "back"]:
                break
            elif len(source_file) == 0:
                print("下载文件为空请重新输入")
                continue
            # 输入的下载文件信息中有可能带有路径信息，这里截取出文件名
            filename = source_file.split("/")[-1]

            download_file = input("下载文件保存在本机上的文件名，输入为空代表不更改文件名\n>>>").strip()
            # 下载文件的文件名为空代表与源文件名相同
            download_file = download_file if download_file else filename
            # 生成目标文件保存在本机上的绝对路径
            destination_file = os.path.join(settings.file_path, download_file)

            self.data_header = {
                "function": self._get_put,
                "action": "get",
                "source_file": source_file,
                "destination_file": destination_file
            }

            self.open_thread()  # 调用开启线程的方法函数

    def interactive_put(self):
        """
        上传文件交互的方法函数
        :return:
        """""
        while True:
            upload_file = input("输入要上传的文件，或输入b返回到上一层\n>>>").strip()
            if upload_file in ["b", "back"]:
                break
            elif len(upload_file) == 0:
                print("输入的上传文件为空，请重新输入")
                continue

            # 生成上传文件在本机上的绝对路径
            source_file = os.path.join(settings.file_path, upload_file)
            if not os.path.isfile(source_file):
                print("输入的上传文件不存在，请重新输入")
                continue

            destination_file = input("上传的文件保存到远程主机上的文件名，输入为空代表不更改文件名\n>>>").strip()
            # 目标文件名为空代表与源文件名相同
            destination_file = destination_file if destination_file else upload_file

            self.data_header = {
                "function": self._get_put,
                "action": "put",
                "source_file": source_file,
                "destination_file": destination_file
            }

            self.open_thread()  # 调用开启线程的方法函数

    def _get_put(self, ip_address):
        """
        连接服务器上传文件或下载文件的方法函数
        :param ip_address: 服务器的ip地址
        :return:
        """""
        self.semaphore.acquire()  # 信号量加锁
        port = int(self.config[ip_address]["port"])  # 获取主机的ssh端口号
        username = self.config[ip_address]["username"]  # 获取主机的用户名
        password = self.config[ip_address]["password"]  # 获取主机的密码

        transport = paramiko.Transport((ip_address, port))  # 创建transport对象
        transport.connect(username=username, password=password)  # 指定用户名和密码
        sftp = paramiko.SFTPClient.from_transport(transport)  # 创建sftp对象
        if self.data_header["action"] == "put":
            sftp.put(self.data_header["source_file"], self.data_header["destination_file"])
            print("文件已上传到%s上" % ip_address)
            # 将操作记录保存到日志文件中
            upload_logger.info("将文件%s上传到主机%s上" % (self.data_header["source_file"], ip_address))
        elif self.data_header["action"] == "get":
            file_path_new = self.data_header["destination_file"] + "_" + ip_address  # 防止文件被覆盖
            sftp.get(self.data_header["source_file"], file_path_new)
            print("从%s下载文件已完成" % ip_address)
            # 将操作记录保存到日志文件中
            download_logger.info("从主机%s下载到本地的文件为%s" % (ip_address, file_path_new))

        transport.close()
        self.semaphore.release()  # 信号量释放锁

    def _shell_command(self, ip_address):
        """
        连接服务器执行shell命令的方法函数
        :param ip_address: 服务器的ip地址
        :return:
        """""
        self.semaphore.acquire()  # 信号量加锁
        ssh = paramiko.SSHClient()  # 创建ssh对象
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 第一次连接服务器时自动保存服务器ssh的RSA公钥

        port = int(self.config[ip_address]["port"])  # 获取主机的ssh端口号
        username = self.config[ip_address]["username"]  # 获取主机的用户名
        password = self.config[ip_address]["password"]  # 获取主机的密码
        ssh.connect(hostname=ip_address, port=port, username=username, password=password)  # 连接服务器

        stdin, stdout, stderr = ssh.exec_command(self.data_header["command"])  # 执行命令
        stdout = stdout.read()  # 读取标准输出
        stderr = stderr.read()  # 读取标准错误输出
        result = stdout if stdout else stderr  # 命令执行成功就显示标准输出，命令执行失败就显示标准错误输出
        result = result.decode(encoding="utf-8")  # 获取的结果是二进制，需要转成字符串类型

        ip_address_new = "\033[1;32m%s\033[0m" % ip_address
        print(ip_address_new.rjust(30, "-"))
        print(result)

        ssh.close()  # 关闭连接
        self.semaphore.release()  # 信号量释放锁

        # 将操作记录保存到日志文件中
        command_logger.info("对主机%s执行了%s命令" % (ip_address, self.data_header["command"]))

    def _exit(self):
        """
        退出程序的方法函数
        :return:
        """""
        exit("退出程序")

    def open_thread(self):
        """
        开启线程的方法函数
        :return:
        """""
        thread_obj_list = []  # 承放线程对象的列表
        # 生成信号量实例，并设置最多允许2个线程可以同时修改数据
        self.semaphore = threading.BoundedSemaphore(2)

        for ip_address in self.ip_address_list:
            t = threading.Thread(target=self.data_header["function"], args=(ip_address,))  # 生成线程实例
            t.setDaemon(True)  # 将线程设置成守护线程
            t.start()  # 开启线程
            thread_obj_list.append(t)  # 将线程实例加到列表中

        for obj in thread_obj_list:
            obj.join()  # 等待线程执行完毕
