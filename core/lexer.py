#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
lexer.py
用于词法分析

Author:Kulib
Date:2026-3-25
Version:0.1
"""
import re

class Lexer:
    def __init__(self):
        self.token_pattern = re.compile(r'\w+|[=+\-/]')

    """
    Token化用函数, 返回token列表
    """
    def tokenize(self, line):
        # 去除注释
        code_part = line.split('#')[0]

        # 去空格
        clean_code = code_part.strip()

        if not clean_code: return

        # 提取token
        tokens = self.token_pattern.findall(clean_code)

        return tokens