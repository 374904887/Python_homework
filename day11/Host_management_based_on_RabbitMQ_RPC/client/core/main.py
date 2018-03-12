#!/user/bin/env python
# -*- coding:utf-8 -*-
__author__ = "Zhong Lu"


import pika
import gevent
import uuid
from gevent import monkey
from conf import settings
from core import logger


# 默认情况下，把程序直接交给gevent处理，gevent是不知道程序做了IO操作，所以就要给程序打补丁，让gevent能识别出IO操作
# 在程序开头声明下面的代码，作用是把当前程序的所有IO操作都做上标记
monkey.patch_all()


# 获取执行系统shell命令日志的logger对象
execute_command_logger = logger.logger_function("execute_command")
# 获取查看命令执行结果日志的logger对象
view_command_logger = logger.logger_function("view_command")


command_result_dict = {}  # 承放命令结果的字典


class RpcClient(object):
    """RPC客户端类"""
    def call(self, ip_address, command):
        """
        向rabbitmq server队列中发送数据的方法函数
        :param ip_address: 需要执行命令的主机ip地址
        :param command: 需要执行的命令
        :return:
        """""
        # 生成一个随机queue，并生成queue对象
        # 因为是广播所以就不指定queue的名字，不指定的话，rabbit会随机分配一个名字。这里也可以自己命令queue的名字
        # exclusive是排他的、唯一的，exclusive=True会在使用此queue的消费者断开后，自动将queue删除
        queue_obj = self.channel.queue_declare(exclusive=True)
        # 获取queue的名字
        self.callback_queue = queue_obj.method.queue
        print("随机生成的队列名为", self.callback_queue)

        self.corr_id = str(uuid.uuid4())  # 通过随机数来生成UUID，并转换成字符串

        # 以给定的交换（exchange）、路由键（routing_key）和主体（body）发布到通道
        self.channel.basic_publish(exchange='',
                                   routing_key=ip_address,  # 将消息发送到哪个queue中
                                   properties=pika.BasicProperties(

                                       # 本端主动告诉对端，将响应本端的结果发送到哪个队列中
                                       reply_to=self.callback_queue,

                                       # 将在本端生成的UUID发送给对端
                                       correlation_id=self.corr_id,
                                   ),

                                   body=command  # 将命令发送出去
                                   )

        print("命令%s已发送到rabbitmq server队列中了" % command)
        print("命令%s需要在%s机器上执行" % (command, ip_address))

        self.get_response()

        # 将单个主机执行命令后的结果放到承放命令结果的字典中
        command_result_dict[self.random_key][ip_address] = self.response

    def get_response(self):
        """
        从rabbitmq server队列中接收消息的方法函数
        :return:
        """""
        self.response = None  # self.response是承放接收到的消息内容，默认值设置为None

        # 声明接收消息
        self.channel.basic_consume(self.on_response,  # 如果收到消息，就调用self.on_response方法函数来处理消息
                                   queue=self.callback_queue  # 从哪个队列中接收消息
                                   )

        # 如果self.response的值为None就要一直接收消息
        while self.response is None:
            # 接收消息。不管有没有接收到消息，都不会被block。相当于非阻塞版的start_consuming()
            self.connection.process_data_events()

    def on_response(self, ch, method, props, body):
        """
        接收到消息后触发的回调函数
        :param ch: 通道（或频道）的内存对象
        :param method: 方法。method中包含了将信息发送给谁的一些信息，例如队列、交换（exchange）
        :param props: 属性
        :param body: 接收的消息
        :return:
        """""
        # 如果本端生成的UUID和对端发送给本端的UUID相同，就代表接收到的消息是正确的
        # 本端可以连续给对端发送多条消息，为了保证接收到的结果和发送的消息正确对应上，添加了UUID确认机制
        # props.correlation_id就是获取，对端发送给本端的UUID
        if self.corr_id == props.correlation_id:
            self.response = body  # 将接收到的消息内容赋值给self.response

        ch.basic_ack(delivery_tag=method.delivery_tag)  # 给rabbitmq server发送确认消息


class Client(RpcClient):
    """客户端类，继承了RpcClient类"""
    def __init__(self):
        # 创建连接对象，并在构建时将连接参数对象传递到连接适配器
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.ip_address))

        # 在连接上创建一个通道
        self.channel = self.connection.channel()

        self.interactive()

    def interactive(self):
        """
        和用户交互的方法函数
        :return:
        """""
        self._help()

        while True:

            input_command = input("输入命令\n>>>").strip()

            if len(input_command) == 0:  # 用户输入的命令为空
                continue

            action = input_command.split()[0]  # 获取用户操作类型，run、check_task、help、exit

            if hasattr(self, "_%s" % action):
                function = getattr(self, "_%s" % action)
                function(input_command)
            else:
                print("\033[1;31m输入的内容有误，请重新输入\033[0m")
                self._help()

    def _run(self, input_command):
        """
        解析用户输入的命令，并调用远程机器执行命令的方法函数
        :param input_command: 用户输入的命令
        :return:
        """""
        if input_command.count("--hosts") != 1:
            print("\033[1;31m输入的命令有误，缺少'--hosts'选项，请重新输入\033[0m")
            return False
        elif len(input_command.split("\"")) < 4:
            print("\033[1;31m输入的命令有误，'run'或'--hosts'后面的参数没有用双引号引起来，请重新输入\033[0m")
            return False

        command = input_command.split("\"")[1].strip()  # 获取shell命令，类型为字符串
        host_list = input_command.split("\"")[3].strip().split()  # 获取需要执行shell命令的主机，类型为列表

        if len(command) < 1 or len(host_list) < 1:
            print("\033[1;31m输入的命令有误，'run'或'--hosts'后面缺少参数，请重新输入\033[0m")
            return False

        while True:
            # 通过随机数来生成UUID，并转换成字符串
            # 生成的UUID用来做承放命令结果字典的key
            random_key = str(uuid.uuid4())

            if random_key not in command_result_dict:  # 生成的UUID不在承放命令结果字典中
                self.random_key = random_key  # 将生成的UUID封装到对象中
                # 在承放命令结果字典中再初始化一个字典，UUID为key（每一条命令对应唯一一个UUID），初始化的字典为value
                command_result_dict[self.random_key] = {}
                break

        gevent_list = []  # 承放所要开启协程的列表
        for ip_address in host_list:
            # 启动协程，并将所有要启动的协程放入列表中
            gevent_list.append(gevent.spawn(self.call, ip_address, command))

        gevent.joinall(gevent_list)  # 等待所有协程执行完成

        print("命令 \033[1;32m%s\033[0m \n"
              "task id \033[1;32m%s\033[0m" % (command, self.random_key))

        # 保存到日志文件中
        execute_command_logger.info("对主机%s执行了%s命令，生成的id是%s" % (host_list, command, self.random_key))

        return True

    def _check_task(self, input_command):
        """
        解析用户输入的命令，并查看命令执行结果的方法函数
        :param input_command: 用户输入的命令
        :return:
        """""
        command_list = input_command.split()
        if len(command_list) < 2:
            print("\033[1;31m输入的命令有误，缺少id，请重新输入\033[0m")
            return False

        command_id = command_list[1]
        if command_id not in command_result_dict:
            print("\033[1;31m输入的id不存在，请重新输入\033[0m")
            return False

        result_dict = command_result_dict[command_id]
        for items in result_dict:
            print("-----\033[1;32m%s\033[0m\n"
                  "%s" % (items, result_dict[items].decode(encoding="utf-8")))

        # 保存到日志文件中
        view_command_logger.info("用户查看了id为%s所对应的命令结果" % command_id)

        del command_result_dict[command_id]  # 将指定的key从字典中删除

    def _help(self, *args):
        """
        使用帮助的方法函数
        :param args: 扩展参数
        :return:
        """""
        help_info = r"""

        程序使用帮助信息：

        -- 在远程机器上执行系统shell命令
            命令格式：run "shell_command" --hosts "ip_address ..."
            注意，shell_command和ip_address必须要用双引号引起来
            命令示例：
                run "ipconfig" --hosts "192.168.0.23"：在192.168.0.23机器上执行ipconfig命令
                run "ipconfig" --hosts "192.168.0.23 192.168.157.128"：在192.168.0.23和192.168.157.128两台机器上分别执行ipconfig命令

        -- 查看系统shell命令执行结果
            查看id对应的命令在远程机器上执行的结果
            命令格式：check_task id
            命令示例：
                check_task 26106e37-8f0f-478d-b7b0-c0e598b72719

        -- 结束程序运行，退出整个程序
            命令示例：
                exit

        -- 查看程序使用帮助信息
            命令示例：
                help
        """
        print(help_info)

    def _exit(self, *args):
        """
        退出程序的方法函数
        :param args: 扩展参数
        :return:
        """""
        self.connection.close()  # 关闭连接
        exit("程序退出")
