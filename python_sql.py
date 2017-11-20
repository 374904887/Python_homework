#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import os


# 第二部分：sql解析
def sql_parse(sql):
    """
    1:sql解析总控制函数，会调用insert_parse、delete_parse、update_parse、select_parse四个函数；
    :param sql: 用户输入的sql命令语句，数据类型为字符串
    :return: 返回字典格式的sql解析结果
    """""
    parse_function = {
        "insert": insert_parse,
        "delete": delete_parse,
        "update": update_parse,
        "select": select_parse,
    }

    sql_list = sql.split(" ")
    operation = sql_list[0]
    res = ""

    if operation in parse_function:
        res = parse_function[operation](sql_list)

    return res


def insert_parse(sql_list):
    """
    1:sql解析分支: insert
    2:sql命令语句: insert into db1.emp values zhong,25,11111111111,IT,2017-01-01
    :param sql_list: sql按照空格分割的列表
    :return: 返回字典格式的sql解析结果
    """""
    sql_dict = {
        "function": insert,  # 函数名
        "insert": [],  # insert选项，留出扩展
        "into": [],  # 表名
        "values": [],  # 值
    }

    return handle_parse(sql_list, sql_dict)


def delete_parse(sql_list):
    """
    1:sql解析分支: delete
    2:sql命令语句: delete from db1.emp where id=26
    :param sql_list: sql按照空格分割的列表
    :return: 返回字典格式的sql解析结果
    """""
    sql_dict = {
        "function": delete,  # 函数名
        "delete": [],  # delete选项，留出扩展
        "from": [],  # 表名
        "where": []  # filter条件
    }

    return handle_parse(sql_list, sql_dict)


def update_parse(sql_list):
    """
    1:sql解析分支: update
    2:sql命令语句: update db1.emp set age='20' where name='zhong'
    :param sql_list: sql按照空格分割的列表
    :return: 返回字典格式的sql解析结果
    """""
    sql_dict = {
        "function": update,  # 函数名
        "update": [],  # update选项，留出扩展
        "set": [],  # 修改的值
        "where": []  # filter条件
    }

    return handle_parse(sql_list, sql_dict)


def select_parse(sql_list):
    """
    1:sql解析分支：select
    2:sql命令语句: select * from db1.emp where not id = 1 and name = 'alex' or name = '李' limit 3
    3:sql命令语句: select * from db1.emp where id > 1 and id < 4
    4:sql命令语句: select * from db1.emp where not id > 20 or name like 李
    5:sql命令语句: select name,age from db1.emp where age > 22
    :param sql_list: sql命令语句按照空格分割的列表
    :return: 返回字典格式的sql解析结果
    """""
    sql_dict = {
        "function": select,  # 函数名
        "select": [],  # 查询字段
        "from": [],  # 表
        "where": [],  # filter条件
        "limit": [],  # limit条件
    }

    return handle_parse(sql_list, sql_dict)


def handle_parse(sql_list, sql_dict):
    """
    1:执行sql解析操作，将sql_list中的内容填到sql_dict里，并返回sql_dict
    :param sql_list: sql按照空格分割的列表
    :param sql_dict: 将sql_list中的内容填到sql_dict里
    :return: 返回的是sql_dict字典
    """""
    append_tag = False
    for item in sql_list:
        if append_tag and item in sql_dict:
            append_tag = False

        if not append_tag and item in sql_dict:
            append_tag = True
            sql_dict_key = item
            continue

        if append_tag:
            sql_dict[sql_dict_key].append(item)

    if sql_dict.get("where"):
        sql_dict["where"] = where_parse_one(sql_dict.get("where"))

    return sql_dict


def where_parse_one(where_list_old):
    """
    1:where_list_old是sql_dict字典中，where对应的value，是一个列表
    2:将where_list_old列表中逻辑运算符中间的内容放进子列表中
    :param where_list_old: 格式为['not', 'id', '=', '1', 'and', 'name', '=', "'alex'", 'or', 'name', '=', "'李'"]
    :return: 返回的列表格式为['not', ['id', '=', '1'], 'and', ['name', '=', "'alex'"], 'or', ['name', '=', "'李'"]]
    """""
    where_list_new = []
    logical_operator = ["and", "or", "not"]  # 逻辑运算符
    character = ""
    for item in where_list_old:
        if len(item.strip()) == 0:
            continue

        if item in logical_operator:
            if len(character.strip()) != 0:
                character = where_parse_two(character)
                where_list_new.append(character)
                where_list_new.append(item)
                character = ""
            else:
                where_list_new.append(item)
        else:
            character += item
    else:
        character = where_parse_two(character)
        where_list_new.append(character)

    return where_list_new


def where_parse_two(string_expression):
    """
    :param string_expression: 比较运算符两边没有空格的字符串，例如name='alex'
    :return: 将string_expression以比较运算符为分隔符分成三部分，分别加到列表中，例如['name', '=', "'alex'"]
    """""
    comparison_operator = ["<", ">", "="]  # 比较运算符
    result = []
    character = ""
    operator = ""
    tag = False

    for item in string_expression:
        if item in comparison_operator:
            tag = True
            if len(character.strip()) != 0:
                result.append(character)
                character = ""
            operator += item

        if not tag:
            character += item

        if tag and item not in comparison_operator:
            tag = False
            result.append(operator)
            operator = ""
            character += item
    else:
        result.append(character)

    if len(result) == 1:
        result = result[0].split("like")
        result.insert(1, "like")
    return result


# 第三部分：sql执行
def sql_action(sql_dict):
    """
    1:从字典sql_dict中提取命令，分发给具体的命令执行函数去执行
    :param sql_dict: 用户输入的sql命令语句，通过解析函数后生成的字典
    :return:
    """""
    return sql_dict.get("function")(sql_dict)


def insert(sql_dict):
    """
    1: sql命令语句: insert into db1.emp values zhong,25,11111111111,IT,2017-01-01
    :param sql_dict: 用户输入的sql命令语句，通过insert_parse函数解析后生成的字典
    :return:
    """""
    db, table = sql_dict.get("into")[0].split(".")

    with open("%s/%s" % (db, table), "ab+") as f:
        offset = -150
        while True:
            f.seek(offset, 2)
            line = f.readlines()
            if len(line) > 1:
                last = line[-1]
                break
            offset *= 2

        last = last.decode(encoding="utf-8")

        last_id = int(last.split(",")[0])
        new_id = last_id + 1

        record_list = sql_dict.get("values")[0].split(",")
        record_list.insert(0, str(new_id))

        record_str = ",".join(record_list) + "\n"

        f.write(record_str.encode(encoding="utf-8"))

        f.flush()

    return [["insert successful"]]


def delete(sql_dict):
    """
    1: sql命令语句: delete from db1.emp where id=26
    :param sql_dict: 用户输入的sql命令语句，通过delete_parse函数解析后生成的字典
    :return:
    """""
    db, table = sql_dict.get("from")[0].split(".")
    bak_file = table + "_bak"

    with open("%s/%s" % (db, table), "r", encoding="utf-8") as read_file, \
            open("%s/%s" % (db, bak_file), "w", encoding="utf-8") as write_file:
        delete_count = 0
        for line in read_file:
            title = "id,name,age,phone,dept,enroll_date"
            dic = dict(zip(title.split(","), line.split(",")))

            filter_res = logic_action(dic, sql_dict.get("where"))

            if not filter_res:
                write_file.write(line)
            else:
                print("删除内容为: ", line)
                delete_count += 1

        write_file.flush()

    os.remove("%s/%s" % (db, table))
    os.rename("%s/%s" % (db, bak_file), "%s/%s" % (db, table))

    return [[delete_count], ["delete successful"]]


def update(sql_dict):
    """
    1: sql命令语句: update db1.emp set age='20' where name='zhong'
    :param sql_dict: 用户输入的sql命令语句，通过update_parse函数解析后生成的字典
    :return:
    """""
    db, table = sql_dict.get("update")[0].split(".")

    set_old = sql_dict.get("set")[0].split(",")
    set_new = []
    for item_outside in set_old:
        set_new.append(item_outside.split("="))

    bak_file = table + "_bak"
    with open("%s/%s" % (db, table), "r", encoding="utf-8") as read_file, \
            open("%s/%s" % (db, bak_file), "w", encoding="utf-8") as write_file:
        update_count = 0
        for line in read_file:
            title = "id,name,age,phone,dept,enroll_date"
            dic = dict(zip(title.split(","), line.split(",")))

            filter_res = logic_action(dic, sql_dict.get("where"))

            if filter_res:
                for item_inside in set_new:
                    key = item_inside[0]
                    values = item_inside[-1].strip("'")
                    dic[key] = values

                line_list = []
                for field in title.split(","):
                    line_list.append(dic[field])

                line = ",".join(line_list)

                print("更改的内容为: ", line)
                update_count += 1

            write_file.write(line)

        write_file.flush()

    os.remove("%s/%s" % (db, table))
    os.rename("%s/%s" % (db, bak_file), "%s/%s" % (db, table))

    return [[update_count], ["update successful"]]


def select(sql_dict):
    """
    1:sql执行分支：select
    2:sql命令语句: select * from db1.emp where not id = 1 and name = 'alex' or name = '李' limit 3
    3:sql命令语句: select * from db1.emp where id > 1 and id < 4
    4:sql命令语句: select * from db1.emp where not id > 20 or name like 李
    5:sql命令语句: select id,name from db1.emp where id > 1 and id < 4
    :param sql_dict: 用户输入的sql命令语句，通过select_parse函数解析后生成的字典
    :return:例如[['id', 'name', 'age', 'phone', 'dept', 'enroll_data'], [['24', 'alex', '18', '13120378203', '运维', '2013-3-1\n']]]
    """""
    db, table = sql_dict.get("from")[0].split(".")

    f = open("%s/%s" % (db, table), "r", encoding="utf-8")

    filter_res = where_action(f, sql_dict.get("where"))
    f.close()

    limit_res = limit_action(filter_res, sql_dict.get("limit"))

    search_res = search_action(limit_res, sql_dict.get("select"))

    return search_res


def where_action(f, where_list):
    """
    :param f: 保存数据的文件句柄
    :param where_list: 格式例如[["name", ""like, "李"], "or", ["id", "<=", "4"]]
    :return: 例如[['24', 'alex', '18', '13120378203', '运维', '2013-3-1\n']]
    """""
    res = []
    title = "id,name,age,phone,dept,enroll_data"
    if len(where_list) != 0:
        for line in f:
            dic = dict(zip(title.split(","), line.split(",")))

            logic_res = logic_action(dic, where_list)
            if logic_res:
                res.append(line.split(","))

    else:
        res = f.readlines()

    return res


def logic_action(dic, where_list):
    """
    :param dic: 将"id,name,age,phone,dept,enroll_data"和文件的每一行内容对应起来
    :param where_list: 格式例如[["name", ""like, "李"], "or", ["id", "<=", "4"]]
    :return: True或False
    """""
    res = []
    for exp in where_list:
        if type(exp) is list:
            exp_k, opt, exp_v = exp

            if exp[1] == "=":
                opt = "%s=" % exp[1]

            if dic[exp_k].isdigit():
                dic_v = int(dic[exp_k])
                exp_v = int(exp_v)
            else:
                dic_v = "'%s'" % dic[exp_k]

            if opt != "like":
                exp = str(eval("%s%s%s" % (dic_v, opt, exp_v)))
            else:
                if exp_v in dic_v:
                    exp = "True"
                else:
                    exp = "False"

        res.append(exp)

    res = eval(" ".join(res))

    return res


def limit_action(filter_res, limit_list):
    """
    :param filter_res: 没有limit限制情况下，所有符合条件的内容，每一行为filter_res列表的一个元素
    :param limit_list: 列表的元素就是一个数字
    :return: 例如[['24', 'alex', '18', '13120378203', '运维', '2013-3-1\n']]
    """""
    res = []
    if len(limit_list) != 0:
        index = int(limit_list[0])
        res = filter_res[0:index]
    else:
        res = filter_res

    return res


def search_action(limit_res, select_list):
    """
    :param limit_res: 经过limit数量限制后，符合条件的内容，每行内容为列表的一个元素
    :param select_list: 列表的元素是用户输入的sql命令语句中select后面跟的内容，有可能是*，还有可能是id,name,age等，该列表就只有一个元素
    :return: 例如['id', 'name', 'age', 'phone', 'dept', 'enroll_data'] [['24', 'alex', '18', '13120378203', '运维', '2013-3-1\n']]
    """""
    res = []
    fileds_list = []
    title = "id,name,age,phone,dept,enroll_data"

    if select_list[0] == "*":
        fileds_list = title.split(",")
        res = limit_res
    else:
        for record in limit_res:
            dic = dict(zip(title.split(","), record))
            record_list = []
            fileds_list = select_list[0].split(",")
            for item in fileds_list:
                record_list.append(dic[item].strip())
            res.append(record_list)

    return [fileds_list, res]


# 第一部分：程序主逻辑
if __name__ == "__main__":
    while True:
        sql = input("sql> ").strip()

        if sql in ["exit", "q"]:
            break
        elif len(sql) == 0:
            continue
        else:
            continue

        sql_dict = sql_parse(sql)

        if len(sql_dict) == 0:
            continue

        result = sql_action(sql_dict)
        for record in result[-1]:
            print(record)
