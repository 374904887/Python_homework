#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import os
import shelve
import time
from prettytable import PrettyTable
from core import logger
from conf import settings
from src.school import School


# 获取系统日志的logger对象
system_logger = logger.logger_function("system")


class BaseClass(object):
    """基础类"""
    def exit_program(self):
        """退出程序的方法函数"""
        self.school_file.close()  # 关闭文件
        exit("退出程序")


class StudentView(BaseClass):
    """学生视图类"""
    def __init__(self):
        if os.path.exists(settings.school_database_path + ".dat"):  # 因为都关联了学校，所以只需将学校对象保存到文件中就行了
            self.school_file = shelve.open(settings.school_database_path)
            self.student_manager()  # 调用学生管理员方法

            self.school_file.close()  # 关闭文件
        else:
            print("\033[1;31m学生不存在，请先创建出学校\033[0m")
            exit("程序退出")

    def student_manager(self):
        """学生管理员方法函数"""
        exit_flag = True
        while exit_flag:
            for school_name in self.school_file:  # 打印已创建的学校的学校名
                print("学校名称: \033[1;32m%s\033[0m" % school_name)

            choice_school = input("请选择学校，或输入b返回到选择视图界面:\n>>>").strip()
            if choice_school in self.school_file:  # 输入的学校存在
                print("欢迎来到老男孩\033[1;32m[%s]\033[0m校区" % choice_school)
                self.choice_school = choice_school  # 将输入的学校封装到当前实例中
                self.school_obj = self.school_file[choice_school]  # 将输入的学校的对象封装到当前实例中

                menu_dict = {
                    "1": ["学员注册", self.register],
                    "2": ["查看课程信息", self.show_course],
                    "3": ["查看学生信息", self.show_student],
                    "4": ["报名参加培训", self.sign_up_for_training],
                    "5": ["退出程序", self.exit_program]
                }
                menu_list = PrettyTable(["功能ID", "功能描述"])  # 设置表格的列数为两列，以及对每列数据作用的说明
                menu_list.padding_width = 2  # 列数据两边的空格数各增加1个
                menu_list.add_row(["1", menu_dict["1"][0]])  # 向表中添加一行
                menu_list.add_row(["2", menu_dict["2"][0]])
                menu_list.add_row(["3", menu_dict["3"][0]])
                menu_list.add_row(["4", menu_dict["4"][0]])
                menu_list.add_row(["5", menu_dict["5"][0]])
                menu_list.add_row(["6", "返回到选择视图页面"])
                while exit_flag:
                    print(menu_list)
                    user_choice = input("输入你想要的操作:\n>>>").strip()

                    if not user_choice.isdigit() or len(user_choice) == 0:
                        print("输入的编号有误请重试")
                    elif user_choice == "6":
                        exit_flag = False
                    else:
                        menu_dict[user_choice][1]()
            elif choice_school in ["b", "back"]:
                break
            else:
                print("输入的学校\033[1;31m[%s]\033[0m不存在，请重新输入" % choice_school)

    def register(self):
        """学员注册的方法函数"""
        student_name = input("输入学生的姓名:\n>>>").strip()
        student_age = input("输入学生的年龄:\n>>>").strip()
        student_sex = input("输入学生的性别:\n>>>").strip()

        if student_name not in self.school_obj.school_student:
            self.school_obj.create_student(student_name, student_age, student_sex)

            self.school_file.update({self.choice_school: self.school_obj})  # key必须是字符串。学校名为key，学校对象为value，保存到文件中

            system_logger.info("%s校区注册了一位新学生%s" % (self.choice_school, student_name))  # 保存到日志文件中

            print("学生\033[1;32m[%s]\033[0m\n注册成功" % student_name)
        else:
            print("学生\033[1;31m[%s]\033[0m已存在")

    def show_course(self):
        """显示课程信息的方法函数"""
        print("##########\033[1;32m[%s]\033[0m校区所有课程详细信息##########" % self.choice_school)
        self.school_obj.show_course()

    def show_student(self):
        """查看学生信息方法函数"""
        student_name = input("输入想要查看的学生姓名:\n>>>").strip()
        if student_name in self.school_obj.school_student:
            self.school_obj.show_student_info(student_name)
        else:
            print("没有\033[1;31m[%s]\033[0m这位学生" % student_name)

    def sign_up_for_training(self):
        """报名参加培训的方法函数
        1: 输入信息
        2: 判断输入的信息，校区中必须有输入的学生，校区必须开设了输入的班级，班级必须是教输入的课程
        3: 学生关联班级
        """
        print("##########\033[1;32m[%s]\033[0m校区开设的班级课程信息##########" % self.choice_school)
        self.school_obj.show_classroom()

        student_name = input("输入学生的姓名:\n>>>").strip()
        choice_course = input("输入学生\033[1;32m[%s]\033[0m想要报名的课程名称:\n>>>" % student_name).strip()
        if student_name in self.school_obj.school_student:
            student_obj = self.school_obj.school_student[student_name]  # 获取学生对象

            choice_class = input("输入学生\033[1;32m[%s]\033[0m想要参加的班级名称:\n>>>" % student_name).strip()
            if choice_class in self.school_obj.school_classroom:  # 学校开设了该班级
                class_obj = self.school_obj.school_classroom[choice_class]  # 获取输入班级的班级对象

                if choice_course == class_obj.course_obj.course_name:
                    course_obj = self.school_obj.school_course[choice_course]  # 获取课程对象
                    print("你要参加\033[1;32m[%s]\033[0m校区"
                          "\033[1;32m[%s]\033[0m班级的"
                          "\033[1;32m[%s]\033[0m课程，"
                          "课程价格: \033[1;32m%s\033[0m元"
                          % (self.choice_school, choice_class, choice_course, course_obj.course_price))
                    user_choice = input("确定输入\033[1;32m[y]\033[0m，\033[1;32m[其他输入代表否]\033[0m:\n>>>").strip()
                    if user_choice in ["y", "yes", "Y", "YES"]:
                        student_obj.pay(course_obj.course_name, course_obj.course_price)  # 调用学生类中购买课程的方法函数
                        class_obj.class_student[student_name] = student_obj  # 学生关联班级

                        self.school_file.update({self.choice_school: self.school_obj})

                        print("成功购买\033[1;32m[%s]\033[0m课程" % choice_course)

                        system_logger.info("%s校区的学生%s报名参加%s班级的%s课程" % (self.choice_school, student_name,
                                                                       choice_class, choice_course))  # 保存到日志文件中
                    else:
                        print("\033[1;请进行其他操作\033[0m")
                else:
                    print("选择的\033[1;31m[%s]\033[0m班级并不是教\033[1;31m[%s]\033[0m课程的" % (choice_class, choice_course))
            else:
                print("\033[1;31m[%s]\033[0m校区未开设\033[1;31m[%s]\033[0m班级" % (self.choice_school, choice_class))
        else:
            print("\033[1;31m[%s]\033[0m校区中没有\033[1;31m[%s]\033[0m学生" % (self.choice_school, student_name))


class TeacherView(BaseClass):
    """讲师视图类"""
    def __init__(self):
        if os.path.exists(settings.school_database_path + ".dat"):  # 因为都关联了学校，所以只需将学校对象保存到文件中就行了
            self.school_file = shelve.open(settings.school_database_path)
            self.teacher_manager()  # 调用老师管理员方法

            self.school_file.close()  # 关闭文件
        else:
            print("\033[1;31m讲师不存在，请先创建出学校\033[0m")
            exit("程序退出")

    def teacher_manager(self):
        """老师管理员方法函数"""
        exit_flag = True
        while exit_flag:
            for school_name in self.school_file:  # 打印已创建的学校的学校名
                print("学校名称: \033[1;32m%s\033[0m" % school_name)

            choice_school = input("请选择校区，或输入b返回到选择视图界面:\n>>>").strip()
            if choice_school in self.school_file:  # 输入的学校存在
                print("欢迎来到老男孩\033[1;32m[%s]\033[0m校区" % choice_school)
                self.choice_school = choice_school  # 将输入的学校名封装到当前实例中
                self.school_obj = self.school_file[choice_school]  # 将输入的学校的对象封装到当前实例中

                while exit_flag:
                    for teacher_name in self.school_obj.school_teacher:  # 打印出学校已招聘的讲师
                        print("讲师姓名: \033[1;32m%s\033[0m" % teacher_name)

                    choice_teacher = input("输入讲师姓名，或输入b返回到选择学校界面:\n>>>").strip()
                    if choice_teacher in self.school_obj.school_teacher:  # 该校区中有输入的讲师这个人
                        print("欢迎讲师: \033[1;32m%s\033[0m回来" % choice_teacher)
                        self.choice_teacher = choice_teacher  # 将输入的讲师名封装到当前实例中
                        self.teacher_obj = self.school_obj.school_teacher[choice_teacher]  # 将输入的讲师的对象封装到当前实例中

                        menu_dict = {
                            "1": ["选择班级上课", self.attend_class],
                            "2": ["查看班级学生", self.show_class_student],
                            "3": ["修改学生成绩", self.revise_grades],
                            "4": ["退出程序", self.exit_program]
                        }
                        menu_list = PrettyTable(["功能ID", "功能描述"])  # 设置表格的列数为两列，以及对每列数据作用的说明
                        menu_list.padding_width = 2  # 列数据两边的空格数各增加1个
                        menu_list.add_row(["1", menu_dict["1"][0]])  # 向表中添加一行
                        menu_list.add_row(["2", menu_dict["2"][0]])
                        menu_list.add_row(["3", menu_dict["3"][0]])
                        menu_list.add_row(["4", menu_dict["4"][0]])
                        menu_list.add_row(["5", "返回到选择老师界面"])
                        menu_list.add_row(["6", "返回到选择视图页面"])
                        while exit_flag:
                            print(menu_list)
                            user_choice = input("输入你想要的操作:\n>>>").strip()

                            if not user_choice.isdigit() or len(user_choice) == 0:
                                print("输入的编号有误请重试")
                            elif user_choice == "5":
                                break
                            elif user_choice == "6":
                                exit_flag = False
                            else:
                                menu_dict[user_choice][1]()
                    elif choice_teacher in ["b", "back"]:
                        break
                    else:
                        print("输入的讲师\033[1;31m[%s]\033[0m不存在，请重新输入" % choice_teacher)
            elif choice_school in ["b", "back"]:
                break
            else:
                print("输入的学校\033[1;31m[%s]\033[0m不存在，请重新输入" % choice_school)

    def attend_class(self):
        """选择班级上课的方法函数"""
        print("-----讲师\033[1;32m[%s]\033[0m代理的班级信息-----" % self.choice_teacher)
        self.school_obj.show_teacher_student_info(self.choice_teacher)

        class_name = input("请输入需要上课的班级:\n>>>").strip()
        if class_name in self.teacher_obj.teacher_classroom:  # 输入的班级是讲师代课的班级
            print("讲师\033[1;32m[%s]\033[0m在\033[1;32m[%s]\033[0m班级开始上课" % (self.choice_teacher, class_name))
            time.sleep(2)
            print("讲师\033[1;32m[%s]\033[0m在\033[1;32m[%s]\033[0m班级讲课完毕" % (self.choice_teacher, class_name))
        else:
            print("讲师\033[1;31m[%s]\033[0m是不代课\033[1;31m[%s]\033[0m班级的" % (self.choice_teacher, class_name))

    def show_class_student(self):
        """查看班级学生的方法函数"""
        self.school_obj.show_teacher_student_info(self.choice_teacher)

    def revise_grades(self):
        """修改学生成绩的方法函数"""
        self.school_obj.show_teacher_student_info(self.choice_teacher)
        class_name = input("请输入讲师授课的班级:\n>>>").strip()
        student_name = input("请输入想要修改哪位学生的成绩:\n>>>").strip()
        new_score = input("请输入该学生的新成绩:\n>>>").strip()

        # 调用学校类中修改学生成绩的方法函数
        self.school_obj.modify_student_score(self.choice_teacher, class_name, student_name, new_score)

        self.school_file.update({self.choice_school: self.school_obj})  # key必须是字符串。学校名为key，学校对象为value，保存到文件中

        system_logger.info("%s校区的%s老师将%s班级的学生%s分数修改为%s" % (self.choice_school, self.choice_teacher,
                                                           class_name, student_name, new_score))  # 保存到日志文件中


class AdminView(BaseClass):
    """管理员视图类"""
    def __init__(self):
        if os.path.exists(settings.school_database_path + ".dat"):  # 保存学校对象的文件存在
            self.school_file = shelve.open(settings.school_database_path)  # 打开文件后，将shelve对象封装到当前实例中
        else:  # 保存学校对象的文件不存在
            self.init_school()  # 调用创建学校的方法函数，并生成保存学校对象的文件

        self.school_manager()  # 调用学校管理员方法

        self.school_file.close()  # 关闭文件

    def init_school(self):
        """调用创建学校的方法函数，并生成保存学校对象的文件"""
        self.school_file = shelve.open(settings.school_database_path)  # 创建保存学校对象的文件
        self.school_file["北京"] = School("北京总校", "昌平沙河")  # 生成北京校区对象，并以北京为key，北京校区对象为value，保存到shelve对象中
        self.school_file["上海"] = School("上海分校", "陆家嘴")  # 生成上海校区对象，并以上海为key，上海校区对象为value，保存到shelve对象中

        print("成功创建了\033[1;32m[北京总校]\033[0m和\033[1;32m[上海分校]\033[0m两个校区")

        system_logger.info("成功创建了北京总校和上海分校两个校区")  # 保存到日志文件中

    def school_manager(self):
        """学校管理员方法函数"""
        exit_flag = True
        while exit_flag:
            print("-----老男孩学校信息-----")
            for school_name in self.school_file:  # 打印已创建的学校的学校名
                print("学校名称: \033[1;32m%s\033[0m" % school_name)

            choice_school = input("请输入要管理的学校名称，或输入b返回到选择视图界面:\n>>>").strip()
            if choice_school in self.school_file:  # 输入的学校存在
                self.choice_school = choice_school  # 将输入的学校名封装到当前实例中
                self.school_obj = self.school_file[choice_school]  # 将输入的学校的对象封装到当前实例中

                menu_dict = {
                    "1": ["添加课程", self.add_course],
                    "2": ["添加班级", self.add_classroom],
                    "3": ["添加讲师", self.add_teacher],
                    "4": ["为讲师分配班级", self.assign_class],
                    "5": ["查看课程", self.show_course],
                    "6": ["查看班级", self.show_classroom],
                    "7": ["查看讲师", self.show_teacher],
                    "8": ["退出程序", self.exit_program]
                }
                menu_list = PrettyTable(["功能ID", "功能描述"])  # 设置表格的列数为两列，以及对每列数据作用的说明
                menu_list.padding_width = 2  # 列数据两边的空格数各增加1个
                menu_list.add_row(["1", menu_dict["1"][0]])  # 向表中添加一行
                menu_list.add_row(["2", menu_dict["2"][0]])
                menu_list.add_row(["3", menu_dict["3"][0]])
                menu_list.add_row(["4", menu_dict["4"][0]])
                menu_list.add_row(["5", menu_dict["5"][0]])
                menu_list.add_row(["6", menu_dict["6"][0]])
                menu_list.add_row(["7", menu_dict["7"][0]])
                menu_list.add_row(["8", menu_dict["8"][0]])
                menu_list.add_row(["9", "返回到选择视图页面"])
                while exit_flag:
                    print("欢迎来到老男孩%s校区" % choice_school)
                    print(menu_list)
                    user_choice = input("输入你想要的操作:\n>>>").strip()

                    if not user_choice.isdigit() or len(user_choice) == 0:
                        print("输入的编号有误请重试")
                    elif user_choice == "9":
                        exit_flag = False
                    else:
                        menu_dict[user_choice][1]()

            elif choice_school in ["b", "back"]:
                break
            else:
                print("输入的学校\033[1;31m[%s]\033[0m不存在，请重新输入" % choice_school)

    def add_course(self):
        """
        添加课程的方法函数
        1: 输入信息
        2: 判断输入的课程是否存在，有就提示，没有课程就调用school类的create_course方法创建课程
        """
        course_name = input("请输入课程名称:\n>>>").strip()
        course_price = input("请输入课程价格:\n>>>").strip()
        course_time = input("请输入课程周期:\n>>>").strip()
        if course_name in self.school_obj.school_course:
            print("课程\033[1;31m[%s]\033[0m已存在，无需创建" % course_name)
        else:
            self.school_obj.create_course(course_name, course_price, course_time)  # 调用school类中的create_course方法创建课程

            self.school_file.update({self.choice_school: self.school_obj})  # key必须是字符串。学校名为key，学校对象为value，保存到文件中

            print("课程\033[1;32m[%s]\033[0m\n添加成功" % course_name)
            system_logger.info("管理员给%s校区添加了%s课程" % (self.choice_school, course_name))  # 保存到日志文件中

    def show_course(self):
        """
        查看课程信息的方法函数
        1: 调用school类中的show_course方法显示课程信息
        """
        self.school_obj.show_course()  # 调用school类中的show_course方法显示课程信息

    def add_classroom(self):
        """
        添加班级的方法函数
        1: 输入信息
        2: 判断输入的班级是否存在，班级不存在且课程存在的情况下，才可以创建新的班级
        3: 否则打印提示信息
        """
        class_name = input("请输入班级名称:\n>>>").strip()
        if class_name not in self.school_obj.school_classroom:  # 输入的班级名不存在

            class_course = input("请输入\033[1;32m[%s]\033[0m班级开设的课程名称:\n>>>" % class_name).strip()
            if class_course in self.school_obj.school_course:  # 输入的课程名存在
                course_obj = self.school_obj.school_course[class_course]  # 获取输入的课程的课程对象
                datetime = time.strftime(settings.datetime_format)  # 开班时间，当前的年月日

                self.school_obj.create_classroom(class_name, datetime, course_obj)  # 调用school类中的create_classroom方法创建班级

                self.school_file.update({self.choice_school: self.school_obj})  # key必须是字符串。学校名为key，学校对象为value，保存到文件中

                print("班级\033[1;32m[%s]\033[0m创建成功" % class_name)

                system_logger.info("管理员给%s校区添加了%s班级" % (self.choice_school, class_name))  # 保存到日志文件中
            else:
                print("课程\033[1;31m[%s]\033[0m不存在，必须在创建该课程后，才能创建班级" % class_course)

        else:
            print("班级\033[1;31m[%s]\033[0m已存在" % class_name)

    def show_classroom(self):
        """
        显示班级信息的方法函数
        1: 调用school类中的show_classroom方法显示班级信息
        """
        self.school_obj.show_classroom()

    def add_teacher(self):
        """
        添加讲师的方法函数
        1: 输入信息
        2: 创建讲师
        """
        teacher_name = input("请输入讲师的姓名:\n>>>").strip()
        teacher_age = input("请输入讲师的年龄:\n>>>").strip()
        teacher_sex = input("请输入讲师的性别:\n>>>").strip()
        teacher_salary = input("请输入讲师的薪水:\n>>>").strip()

        entry_time = time.strftime(settings.datetime_format)
        if teacher_name not in self.school_obj.school_teacher:  # 讲师不存在
            self.school_obj.create_teacher(teacher_name, teacher_age, teacher_sex,
                                           teacher_salary, entry_time)  # 调用school类中的create_teacher方法创建讲师

            self.school_file.update({self.choice_school: self.school_obj})  # key必须是字符串。学校名为key，学校对象为value，保存到文件中

            print("讲师\033[1;32m[%s]\033[0m招聘成功" % teacher_name)

            system_logger.info("%s校区招聘了%s老师" % (self.choice_school, teacher_name))  # 保存到日志文件中

        else:
            print("讲师\033[1;31m[%s]\033[0m已存在" % teacher_name)

    def assign_class(self):
        """为讲师分配班级的方法函数"""
        teacher_name = input("请输入讲师的姓名:\n>>>").strip()
        if teacher_name in self.school_obj.school_teacher:  # 有该讲师
            teacher_obj = self.school_obj.school_teacher[teacher_name]  # 获取讲师对象

            while True:
                self.school_obj.show_classroom()  # 调用school类中显示班级信息的方法函数

                teacher_class = input("请输入要给\033[1;32m[%s]\033[0m讲师分配的班级，或输入b返回到上一层:\n>>>" % teacher_name).strip()
                if teacher_class in self.school_obj.school_classroom:  # 输入的班级存在

                    if teacher_class not in teacher_obj.teacher_classroom:  # 并且该班级没有分配给该讲师
                        self.school_obj.assign_class(teacher_name, teacher_class)  # 调用学校类中为讲师分配班级的方法函数

                        self.school_file.update({self.choice_school: self.school_obj})

                        print("给\033[1;32m[%s]\033[0m讲师分配了\033[1;32m[%s]\033[0m班级" % (teacher_name, teacher_class))

                        system_logger.info("给%s讲师分配了%s班级" % (teacher_name, teacher_class))  # 保存到日志文件中

                    else:
                        print("班级\033[1;31m[%s]\033[0m已经分配给\033[1;31m[%s]\033[0m讲师了" % (teacher_class, teacher_name))

                elif teacher_class in ["b", "back"]:
                    break
                else:
                    print("班级\033[1;31m[%s]\033[0m不存在，要先创建该班级" % teacher_class)
        else:
            print("讲师\033[1;31m[%s]\033[0m不存在，请先招聘该讲师" % teacher_name)

    def show_teacher(self):
        """显示讲师信息的方法函数
        1: 调用school类中的show_teacher方法显示讲师信息
        """
        self.school_obj.show_teacher()


class Run(object):
    """程序交互类"""
    @staticmethod
    def interactive():
        """与用户交互的方法函数"""
        operation = {
            "1": ["学员视图", StudentView],
            "2": ["讲师视图", TeacherView],
            "3": ["管理员视图", AdminView],
        }

        operation_list = PrettyTable(["功能ID", "功能描述"])  # 设置表格的列数为两列，以及对每列数据作用的说明
        operation_list.padding_width = 2  # 列数据两边的空格数各增加1个
        operation_list.add_row(["1", operation["1"][0]])  # 向表中添加一行
        operation_list.add_row(["2", operation["2"][0]])
        operation_list.add_row(["3", operation["3"][0]])
        operation_list.add_row(["4", "退出程序"])

        flag = True
        while flag:
            print(operation_list)
            action_operation = input("输入你想要的操作:\n>>>").strip()
            if not action_operation.isdigit() or len(action_operation) == 0:
                print("输入的编号有误请重试")
            elif action_operation == "4":
                flag = False
            else:
                operation[action_operation][1]()
