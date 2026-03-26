#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
lexer.py
用于词法分析

Author:Kulib
Date:2026-3-25
Version:0.2
"""
import re
from utils.logger import report_error

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"<{self.type}:'{self.value}' at {self.line}:{self.column}>"
        

class Lexer:
    def __init__(self):
        # 定义 Token 规则
        self.rules = [
            ('IF',          r'\bif\b'),     # 使用 \b 确保是独立单词
            ('ELSE',        r'\belse\b'),
            ('WHILE',       r'\bwhile\b'),
            ('INPUT',       r'\binput\b'),
            ('OUTPUT',      r'\boutput\b'),
            ('NUMBER',      r'\d+'),

            ('ID',          r'[a-zA-Z_][a-zA-Z0-9_]*'), # 匹配标识符
            ('EQ',          r'=='),         # 等于
            ('NE',          r'!='),         # 不等于
            ('GE',          r'>='),         # 大于等于
            ('LE',          r'<='),         # 小于等于
            ('GT',          r'>'),          # 大于
            ('LT',          r'<'),          # 小于
            ('ASSIGN',      r'='),          # 赋值符号
            ('ADD',         r'\+'),         # 加号
            ('SUB',         r'-'),          # 减号
            ('LPAREN',      r'\('),         # 左括号
            ('RPAREN',      r'\)'),         # 右括号
            ('LBRACE',      r'\{'),         # 左花括号
            ('RBRACE',      r'\}'),         # 右花括号
            ('NEWLINE',     r'\n'),         # 换行符
            ('SKIP',        r'[ \t]+'),     # 跳过空格和制表符
            ('COMMENT',     r'#.*'),        # 注释
            ('MISMATCH',    r'.'),          # 未知字符
        ]
        self.regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.rules)

    """
    Token化用函数, 返回token列表
    """
    def tokenize(self, code):
        tokens = []
        line_num = 1
        line_start = 0

        for mo in re.finditer(self.regex, code):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - line_start + 1

            if kind == 'NUMBER':
                value = int(value)
            elif kind == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
            elif kind == 'SKIP' or kind == 'COMMENT':   # 删除注释
                continue
            elif kind == 'INVALID_ID':
                report_error(code, f"词义错误: 无效的标识符 '{value}'", Token(kind, value, line_num, column))
                continue
            elif kind == 'MISMATCH':
                report_error(code, f"词义错误: 未知的符号", Token(kind, value, line_num, column))
                continue

            tokens.append(Token(kind, value, line_num, column))

        return tokens