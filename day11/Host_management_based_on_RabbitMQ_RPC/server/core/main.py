#!/user/bin/env python
# -*- coding:utf-8 -*-
__author__ = "Zhong Lu"


import pika
import subprocess
from conf import settings


class RpcServer(object):
    """RPC服务端类"""
    def __init__(self):
        # 创建连接对象，并在构建时将连接参数对象传递到连接适配器
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.ip_address))

        # 在连接上创建一个通道
        channel = connection.channel()

        # 在通道中创建队列
        channel.queue_declare(queue=settings.receive_message_queue)

        # 声明接收消息
        channel.basic_consume(self.on_request,  # 如果收到消息，就调用on_response方法函数来处理消息
                              queue=settings.receive_message_queue  # 从哪个队列中接收消息
                              )

        # 接收消息。永远的接收下去。当没有接收到消息时就会被block
        channel.start_consuming()

    def on_request(self, ch, method, props, body):
        """
        接收到消息后触发的回调函数
        :param ch: 通道（或频道）的内存对象
        :param method: 方法。method中包含了将信息发送给谁的一些信息，例如队列、交换（exchange）
        :param props: 属性
        :param body: 接收的消息
        :return:
        """""
        self.command_bytes = body
        command_execute_result = self.execute_command()  # 调用执行系统shell命令的方法函数

        # 以给定的交换（exchange）、路由键（routing_key）和主体（body）发布到通道
        ch.basic_publish(exchange='',

                         # 将消息发送到哪个queue中
                         # props.reply_to就是获取，对端主动告诉本端的，将响应对端的结果发送到哪个队列中
                         routing_key=props.reply_to,

                         properties=pika.BasicProperties(
                             # 将对端发送给本端的UUID再发送给对端
                             # props.correlation_id就是获取，对端发送给本端的UUID
                             correlation_id=props.correlation_id
                         ),

                         body=command_execute_result  # 发送命令执行结果
                         )

        print("命令执行结果已经发送给rpc客户端")

        # 给rabbitmq server发送确认，消息被消费了
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def execute_command(self):
        """
        执行系统shell命令的方法函数
        :return:
        """""
        # 从bytes类型转换成字符串
        command = self.command_bytes.decode(encoding="utf-8")
        print("接收到rpc客户端发送的命令", command)
        # 执行命令
        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        result_stdout = result.stdout.read()  # 获取标准输出的值
        result_stderr = result.stderr.read()  # 获取标准错误输出的值

        # 标准输出有值就获取标准输出的值，标准输出没有值就获取标准错误输出
        command_result_bytes = result_stdout if result_stdout else result_stderr
        print("命令执行结果", command_result_bytes)

        # 从bytes类型转换成字符串
        command_result = command_result_bytes.decode(encoding="gbk")

        return command_result
