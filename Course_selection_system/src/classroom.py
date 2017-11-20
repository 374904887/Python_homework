#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


class ClassRoom(object):
    """班级类"""
    def __init__(self, class_name, datetime, course_obj):
        """
        :param class_name: 班级名
        :param datetime: 开班日期
        :param course_obj: 课程对象
        """""
        self.class_name = class_name
        self.datetime = datetime  # 开班时间
        self.course_obj = course_obj  # 将课程对象封装到班级对象中
        self.class_student = {}  # 班级也包含多个学生对象。学生名为key，学生对象为value来建立对应关系
