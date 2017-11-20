#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


class Student(object):
    """学生类"""
    def __init__(self, student_name, student_age, student_sex):
        """
        :param student_name: 学生姓名
        :param student_age: 学生年龄
        :param student_sex: 学生性别
        """""
        self.student_name = student_name
        self.student_age = student_age
        self.student_sex = student_sex
        self.student_course = []  # 保存学生购买课程的列表
        self.total_amount = 0  # 学生购买课程花费的总金额
        self.student_score = {}  # 保存学生分数的字典

    def modify_score(self, class_name, course_name, new_score):
        """
        修改学生成绩的方法函数
        :param class_name: 学生参加的班级
        :param course_name: 学生班级班级上的课程名
        :param new_score: 学生新的成绩分数
        :return:
        """""
        self.student_score[class_name] = [course_name, new_score]  # 班级名为key，value为一个列表，列表由课程名和分数组成

    def pay(self, course_name, course_price):
        """
        购买课程的方法函数
        :param course_name: 要购买的课程
        :param course_price: 课程价格
        :return:
        """""
        course_price = int(course_price)
        self.total_amount += course_price

        # 购买课程的列表元素为元组
        course_info = (course_name, course_price)
        self.student_course.append(course_info)

