#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


from src.classroom import ClassRoom
from src.course import Course
from src.student import Student
from src.teacher import Teacher


class School(object):
    """学校类"""
    def __init__(self, school_name, school_address):
        """
        :param school_name: 学校的名字
        :param school_address: 学校的地址
        """""
        self.school_name = school_name
        self.school_address = school_address
        self.school_course = {}  # 学校的课程，课程名为key，课程对象为value来建立对应关系
        self.school_classroom = {}  # 学校的班级，班级名为key，班级对象为value来建立对应关系
        self.school_teacher = {}  # 学校的讲师，讲师名为key，讲师对象为value来建立对应关系
        self.school_student = {}  # 学校的学生，学生名为key，学生对象为value来建立对应关系

    def create_course(self, course_name, course_price, course_time):
        """
        创建课程并关联学校的方法函数
        :param course_name: 课程名
        :param course_price: 课程价格
        :param course_time: 课程周期
        :return:
        """""
        course_obj = Course(course_name, course_price, course_time)  # 实例化课程类
        self.school_course[course_name] = course_obj  # 课程关联学校，课程名为key，课程对象为value来建立对应关系

    def show_course(self):
        """显示课程信息的方法函数"""
        for course in self.school_course:
            course_obj = self.school_course[course]  # 获取到课程对象
            print("-----课程\033[1;32m[%s]\033[0m信息-----\n"
                  "\t名称: \033[1;32m%s\033[0m\n"
                  "\t价格: \033[1;32m%s\033[0m 元\n"
                  "\t周期: \033[1;32m%s\033[0m"
                  % (course_obj.course_name, course_obj.course_name, course_obj.course_price, course_obj.course_time))

    def create_classroom(self, class_name, datetime, course_obj):
        """
        创建班级，将学生关联班级，将课程关联班级，最后将班级关联学校的方法函数
        :param class_name: 班级名
        :param datetime: 开班时间
        :param course_obj: 课程对象
        :return:
        """""
        class_obj = ClassRoom(class_name, datetime, course_obj)
        self.school_classroom[class_name] = class_obj  # 班级关联学校

    def show_classroom(self):
        """显示班级信息的方法函数"""
        for classroom in self.school_classroom:
            class_obj = self.school_classroom[classroom]
            print("-----班级\033[1;32m[%s]\033[0m信息-----\n"
                  "\t名称: \033[1;32m%s\033[0m\n"
                  "\t开班日期: \033[1;32m%s\033[0m\n"
                  "\t课程: \033[1;32m%s\033[0m"
                  % (class_obj.class_name, class_obj.class_name,
                     class_obj.datetime, class_obj.course_obj.course_name))

    def create_teacher(self, teacher_name, teacher_age, teacher_sex, teacher_salary, entry_time):
        """
        创建讲师的方法函数
        :param teacher_name: 讲师姓名
        :param teacher_age: 讲师年龄
        :param teacher_sex: 讲师性别
        :param teacher_salary: 讲师的薪水
        :param entry_time: 讲师的入职时间
        :return:
        """""
        teacher_obj = Teacher(teacher_name, teacher_age, teacher_sex, teacher_salary, entry_time)
        self.school_teacher[teacher_name] = teacher_obj  # 讲师关联学校

    def assign_class(self, teacher_name, teacher_class):
        """
        为讲师分配班级的方法函数
        :param teacher_name: 讲师名
        :param teacher_class: 给讲师分配的班级名
        :return:
        """""
        class_obj = self.school_classroom[teacher_class]  # 获取班级对象
        teacher_obj = self.school_teacher[teacher_name]  # 获取讲师对象
        teacher_obj.add_teacher_classroom(teacher_class, class_obj)  # 将讲师所教的班级和讲师对应起来

    def show_teacher(self):
        """显示讲师信息的方法函数"""
        for teacher in self.school_teacher:
            teacher_obj = self.school_teacher[teacher]
            print("-----讲师\033[1;32m[%s]\033[0m信息-----\n"
                  "\t姓名: \033[1;32m%s\033[0m\n"
                  "\t年龄: \033[1;32m%s\033[0m\n"
                  "\t性别: \033[1;32m%s\033[0m\n"
                  "\t薪水: \033[1;32m%s\033[0m 元\n"
                  "\t入职时间: \033[1;32m%s\033[0m"
                  % (teacher_obj.teacher_name, teacher_obj.teacher_name,  teacher_obj.teacher_age,
                     teacher_obj.teacher_sex, teacher_obj.teacher_salary, teacher_obj.entry_time))
            for classroom in teacher_obj.teacher_classroom:  # 讲师教授多个班级时，查看教授的所有班级名称
                print("讲师教授班级: \033[1;32m%s\033[0m" % classroom)

    def create_student(self, student_name, student_age, student_sex):
        """
        创建学生对象的方法函数，并将学生关联学校
        :param student_name: 学生姓名
        :param student_age: 学生年龄
        :param student_sex: 学生性别
        :return:
        """""
        student_obj = Student(student_name, student_age, student_sex)  # 实例化学生类得到学生对象
        self.school_student[student_name] = student_obj  # 学生关联学校

    def show_student_info(self, student_name):
        """
        显示学生信息的方法函数
        :param student_name: 学生姓名
        :return:
        """""
        student_obj = self.school_student[student_name]  # 获取学生对象
        print("-----学生\033[1;32m[%s]\033[0m基本信息-----\n"
              "姓名: \033[1;32m%s\033[0m\n"
              "年龄: \033[1;32m%s\033[0m\n"
              "性别: \033[1;32m%s\033[0m"
              % (student_name, student_name, student_obj.student_age, student_obj.student_sex))

        print("-----学生\033[1;32m[%s]\033[0m分数信息-----" % student_name)
        for class_name in student_obj.student_score:
            print("班级:\033[1;32m%-20s\033[0m"
                  "课程:\033[1;32m%-20s\033[0m"
                  "分数:\033[1;32m%-15s\033[0m"
                  % (class_name, student_obj.student_score[class_name][0], student_obj.student_score[class_name][1]))

        print("-----学生\033[1;32m[%s]\033[0m购买课程信息-----" % student_name)
        for course_name, course_price in student_obj.student_course:
            print("课程:\033[1;32m%-20s\033[0m"
                  "价格:\033[1;32m%+15s\033[0m元" % (course_name, course_price))
        print("总金额: \033[1;32m%s\033[0m 元" % student_obj.total_amount)

    def show_teacher_student_info(self, teacher_name):
        """
        显示班级、该班级所上的课程及上该课程的学生的信息方法函数
        :param teacher_name: 讲师姓名
        :return:
        """""
        teacher_obj = self.school_teacher[teacher_name]  # 通过学校对象获取出讲师对象
        for class_name in teacher_obj.teacher_classroom:  # 通过讲师对象获取讲师所教授的班级名
            class_obj = self.school_classroom[class_name]  # 通过学校对象获取班级对象。注意所有班级都要关联学校，这里可以直接通过学校对象获取班级对象
            student_list = []
            for student in class_obj.class_student:  # 通过班级对象获取该班级所有学生的姓名
                student_list.append(student)  # 将学生的姓名追加到列表中
            print("班级: \033[1;32m%s\033[0m\n"
                  "课程: \033[1;32m%s\033[0m\n"
                  "学生: \033[1;32m%s\033[0m"
                  % (class_obj.class_name, class_obj.course_obj.course_name, student_list))

    def modify_student_score(self, teacher_name, class_name, student_name, new_score):
        """
        1: 输入信息
        2.1: 因为一个学生可以同时报多个班，而讲师修改的是学生在某个班级的成绩
        2.2: 判断老师是否对所输入的班级授课，是则再判断输入的班级中是否包含输入的学员，如果包含则就修改学生在该班级中的成绩
        3: 保存数据
        :param teacher_name: 讲师姓名
        :param class_name: 班级名
        :param student_name: 学生姓名
        :param new_score: 学生新的成绩
        :return:
        """""
        teacher_obj = self.school_teacher[teacher_name]
        if class_name in teacher_obj.teacher_classroom:  # 讲师是在该班级教课

            class_obj = self.school_classroom[class_name]  # 通过学校对象获取班级对象
            course_obj = class_obj.course_obj  # 通过班级对象获取课程对象
            if student_name in class_obj.class_student:  # 学生是在该班级里上课

                student_obj = self.school_student[student_name]  # 通过学校对象获取学生对象
                student_obj.modify_score(class_name, course_obj.course_name, new_score)  # 调用学生类中修改学生成绩的方法函数

                print("学生\033[1;32m[%s]\033[0m的成绩修改成功" % student_name)

            else:
                print("班级\033[1;31m[%s]\033[0m中没有学生\033[1;31m[%s]\033[0m这个人" % (class_name, student_name))
        else:
            print("讲师\033[1;31m[%s]\033[0m是不代课\033[1;31m[%s]\033[0m班级的" % (teacher_name, class_name))
