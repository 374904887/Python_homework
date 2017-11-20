#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


class Course(object):
    """课程类"""
    def __init__(self, course_name, course_price, course_time):
        """
        :param course_name: 课程名
        :param course_price: 课程价格
        :param course_time: 课程周期
        """""
        self.course_name = course_name
        self.course_price = course_price
        self.course_time = course_time
