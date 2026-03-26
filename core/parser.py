#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
lexer.py
用于语法分析

Author:Kulib
Date:2026-3-25
Version:0.2
"""
from core.lexer import Token
from utils.logger import report_error
class Parser:
    def __init__(self, tokens, sorce_code):
        self.tokens = tokens
        self.source_code = sorce_code
        self.pos = 0

    # 获取当前单个 token
    def current_token(self):
        if self.pos >= len(self.tokens):
            return Token("EOF", "None", -1, -1)
        return self.tokens[self.pos]
    
    # 处理当前 token 并前进到下一个 token
    def prosess(self, target_type):
        token = self.current_token()
        if token.type == target_type:
            self.pos += 1
            return token
        else:
            report_error(self.source_code, f"语法错误: 期望 {target_type}，但得到 {token.type}", token)

    # 读取基础值
    def parse_term(self):
        token = self.current_token()
        if token.type == "LPAREN":
            self.prosess("LPAREN")  # 读掉 '('
            node = self.parse_expr()  # 读表达式
            self.prosess("RPAREN")  # 读掉 ')'
            return node
        
        if token.type == "NUMBER":
            return {
                "type": "NUMBER",
                "value": self.prosess("NUMBER").value,
                'token': token
            }
        
        elif token.type == "ID":
            return {
                "type": "ID",
                "value": self.prosess("ID").value,
                'token': token
            }
        else:
            report_error(self.source_code, f"语法错误: 期望 数字/ID/'(', 但得到 {token.type}", token)


    def parse_program(self):
        program_body = []
        while self.current_token().type != "EOF":
            stmt = self.parse_statement()
            if stmt:
                program_body.append(stmt)

            # 如果当前是换行，跳过它进入下一轮
            if self.current_token().type == 'NEWLINE':
                self.prosess('NEWLINE')

        return {"type": "PROGRAM", "body": program_body}

    """
    语句分发器
    输入: Token(ID, 'A', 1, 1), 
    输出: "type": "BINARY_OP"
    """
    def parse_statement(self):
        # 先跳过空行
        while self.current_token().type == 'NEWLINE':
            self.prosess('NEWLINE')

        token = self.current_token()

        # print(f"DEBUG: 正在解析语句，Token类型: {token.type}, 内容: {token.value}")

        # 赋值
        if token.type == 'IF':
            return self._parse_if()

        elif token.type == "ID":
            return self._parse_assignment()
        
        elif token.type == "INPUT":
            return self._parse_input()

        elif token.type == "OUTPUT":
            return self._parse_output()

        elif token.type == "WHILE":
            return self.parse_while()

        elif token.type in ['RBRACE', 'EOF']:
            return None

        else:
            report_error(self.source_code, f"语法错误: 无法识别的语句开头: {token.type}", token)

    """
    解析表达式，支持加减运算
    """
    def parse_expr(self):
        node = self.parse_term()  # 读右值

        operators = ['ADD', 'SUB', 'EQ', 'NE', 'GT', 'LT', 'GE', 'LE']

        while self.current_token().type in operators:
            op_token = self.current_token()
            self.prosess(op_token.type)  # 读掉运算符

            # 读右值
            right_node = self.parse_term()

            # 构建二元操作节点
            node = {
                "type": "BINARY_OP",
                "op": op_token.type,
                "left": node,
                "right": right_node,
                "token": op_token
            }

        return node
    

    def _parse_assignment(self):
        # 读左值
        left = self.prosess("ID")
        self.prosess("ASSIGN")  # 读掉 '='

        # 读右值
        right = self.parse_expr()
        return {
            "type": "ASSIGN",
            "target": left,
            "value": right
        }
    
    def _parse_input(self):
        self.prosess("INPUT")  # 读掉 input
        self.prosess("LPAREN")  # 读掉 '('

        # 读输入变量
        node = self.parse_term()

        self.prosess("RPAREN")  # 读掉 ')'

        return {
            "type": "IO_IN",
            "value": node
        }
        

    def _parse_output(self):
        self.prosess("OUTPUT")  # 读掉 output
        self.prosess("LPAREN")  # 读掉 '('

        # 读输出内容
        node = self.parse_expr()

        self.prosess("RPAREN")  # 读掉 ')'

        return {
            "type": "IO_OUT",
            "value": node
        }
    
    """
    解析 if (cond) { body } else { body }
    """
    def _parse_if(self):
        if_token = self.current_token()  # 用于报错定位
        self.prosess("IF")  # 读掉 if
        self.prosess("LPAREN")  # 读掉 '('

        # 读条件表达式
        condition_node = self.parse_expr()
        if condition_node["type"] != "BINARY_OP" or condition_node["op"] not in ["EQ", "NE", "GT", "LT", "GE", "LE"]:
            report_error(self.source_code, f"语法错误: if 条件必须是比较表达式", condition_node['token'])

        self.prosess("RPAREN")  # 读掉 ')'
        

        # 读 if 块
        if_body = self.parse_block()

        # 读 else 块
        else_body = []
        if self.current_token().type == "ELSE":
            self.prosess("ELSE")  # 读掉 else
            else_body = self.parse_block()

        return {
            "type": "IF_STMT",
            "condition": condition_node,
            "if_body": if_body,
            "else_body": else_body,
            "token": if_token
        }
    
    def parse_while(self):
        while_token = self.current_token()  # 用于报错定位
        self.prosess("WHILE")  # 读掉 while
        self.prosess("LPAREN")  # 读掉 '('

        # 读条件表达式
        condition = self.parse_expr()
        if condition["type"] != "BINARY_OP" or condition["op"] not in ["EQ", "NE", "GT", "LT", "GE", "LE"]:
            report_error(self.source_code, f"语法错误: while 条件必须是比较表达式", condition['token'])

        self.prosess("RPAREN")  # 读掉 ')'

        body = self.parse_block()
        return {
            "type": "WHILE_STMT",
            "condition": condition,
            "body": body,
            "token": while_token
        }

    def parse_block(self):
        self.prosess("LBRACE")  # 读掉 '{'
        body = []

        while self.current_token().type != "RBRACE" and self.current_token().type != "EOF":
            if self.current_token().type == 'NEWLINE':
                self.prosess('NEWLINE')
                continue

            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)

        self.prosess("RBRACE")  # 读掉 '}'
        # print(f"DEBUG: 解析块完成，包含 {len(body)} 条语句")
        return body


