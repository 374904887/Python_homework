#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


class Teacher(object):
    """讲师类"""
    def __init__(self, teacher_name, teacher_age, teacher_sex, teacher_salary, entry_time):
        """
        :param teacher_name: 教师姓名
        :param teacher_age: 教师年龄
        :param teacher_sex: 教师性别
        :param teacher_salary: 教师工资
        :param entry_time: 讲师入职时间
        """""
        self.teacher_name = teacher_name
        self.teacher_age = teacher_age
        self.teacher_sex = teacher_sex
        self.teacher_salary = teacher_salary
        self.entry_time = entry_time
        self.teacher_classroom = {}  # 讲师所教授的班级

    def add_teacher_classroom(self, class_name, class_obj):
        """
        讲师和班级绑定的方法函数
        :param class_name: 班级名
        :param class_obj: 班级对象
        :return:
        """""
        self.teacher_classroom[class_name] = class_obj
