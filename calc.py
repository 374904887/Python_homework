#!/user/bin/env python
# -*- coding:utf-8 -*-
# Author:Zhong Lu


import re


def compute_add_sub(expression):
    """
    :param expression: 只有加减的计算式
    :return: 计算加减后的值
    """""

    while True:
        if re.search("\-\-", expression):  # 将两个相连减号替换成加号
            expression = re.sub("\-\-", "+", expression)
        elif re.search("\+\-", expression):  # 将相连的加号和减号替换成减号
            expression = re.sub("\+\-", "-", expression)
        else:
            break

    if not re.search("[\-]?\d+\.*\d*[\+\-]\d+\.*\d*", expression):  # 如果为一个数字，则结束函数，并返回该数字
        return expression

    # 取出从左往右第一个加法或减法计算式，被加数和被减数为正负数的情况也能处理，例如-2+3、2+3、-4-2、4-2
    add_sub_formula = re.search("[\-]?\d+\.*\d*[\+\-]\d+\.*\d*", expression).group()

    if len(re.split("\+", add_sub_formula)) > 1:  # 从左往右第一个计算式是加法
        number1, number2 = re.split("\+", add_sub_formula)
        value = float(number1) + float(number2)  # 转换成浮点数后相乘
    else:  # 从左往右第一个计算式是减法
        number1, number2 = re.split("\-", add_sub_formula)
        value = float(number1) - float(number2)  # 转换成浮点数后相除

    expression = re.sub("[\-]?\d+\.*\d*[\+\-]\d+\.*\d*", str(value), expression, count=1)  # 将所算的计算式替换成计算后的结果

    return compute_add_sub(expression)  # 递归的目的是为了表达式中所有乘法或除法计算式


def compute_mul_div(expression):
    """
    :param expression: 只有加减乘除的计算式
    :return: 只有加减的计算式
    """""
    if not re.search("\d+\.*\d*[\*\/][\-]?\d+\.*\d*", expression):  # 当表达式中没有乘除计算式，直接调用加减函数
        return expression

    # 取出从左往右第一个乘法或除法计算式。乘数和除数为正负数的情况也能处理，例如2*3、2*-3、4/2、4/-2
    mul_div_formula = re.search("\d+\.*\d*[\*\/][\-]?\d+\.*\d*", expression).group()

    if len(re.split("\*", mul_div_formula)) > 1:  # 从左往右第一个计算式是乘法
        number1, number2 = re.split("\*", mul_div_formula)
        value = float(number1) * float(number2)  # 转换成浮点数后相乘
    else:  # 从左往右第一个计算式是乘法
        number1, number2 = re.split("\/", mul_div_formula)
        value = float(number1) / float(number2)  # 转换成浮点数后相除

    # 以第一个从左往右第一个乘法或除法计算式为分隔符分割成两个列表。被乘数和被除数为正负数的情况下，要保证最终结果的正负数不变
    before, after = re.split("\d+\.*\d*[\*\/][\-]?\d+\.*\d*", expression, maxsplit=1)
    expression = "%s%s%s" % (before, value, after)  # 将计算后的结果加到计算式中

    expression = re.sub("\s*", "", expression)  # 去掉计算式中的空格

    return compute_mul_div(expression)  # 递归的目的是为了表达式中所有乘法或除法计算式


def compute(expression):
    """
    :param expression: 小括号中的计算式，或去除小括号后的整个计算式
    :return: 小括号中计算式的结果，或整个计算式最终的结果
    """""

    result_mul_div = compute_mul_div(expression)

    result_add_sub = compute_add_sub(result_mul_div)

    return result_add_sub


def exec_bracket(formula):
    """
    :param formula: 带有小括号的计算式
    :return: 小括号中计算式的结果，或整个计算式最终的结果
    """""

    if not re.search("\([^()]+\)", formula):  # 当表达式中没有小括号后，直接调用计算函数
        result = compute(formula)
        return result

    # 匹配小括号中不包含小括号的字符，即从左往右匹配字符串中第一个最里层的小括号及小括号中的算式，如(-40/5)
    bracket_formula = re.search("\([^()]+\)", formula).group()
    bracket_formula_new = re.search("[^()]+", bracket_formula).group()  # 将匹配出的内容两边的小括号去掉，如-40/5
    bracket_answer = compute(bracket_formula_new)  # 算出小括号中的值

    formula_new = re.sub("\([^()]+\)", bracket_answer, formula, count=1)  # 将小括号替换成小括号中计算出的结果

    return exec_bracket(formula_new)  # 递归是为了去除表达式中所有的小括号


if __name__ == "__main__":  # 使用__name__的目的，只有执行calc.py时，以下代码才执行，如果其他人导入该模块，以下代码不执行

    while True:
        # 输入的计算式为：1 - 2 * ( (60-30 +(-40/5) * (9-2*5/3 + 7 /3*99/4*2998 +10 * 568/14 )) - (-4*3)/ (16-3*2) )
        formula = input("Formula> ").strip()

        if len(formula) == 0:
            print("未输入内容，请重新输入")
        elif formula in ["exit", "q"]:
            exit("程序退出")
        else:
            break

    formula = re.sub("\s*", "", formula)  # 去掉输入计算式中的空格

    answer = exec_bracket(formula)
    print("答案: %s" % answer)
