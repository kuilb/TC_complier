#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
codegen.py
用于将输入的token生成汇编语言代码

Author:Kulib
Date:2026-3-26
Version:0.2
"""
import re

from core.lexer import Token
from utils.logger import report_error, Color
from hardware.memory import StaticMemory
from hardware.registers import RegisterPool

class CodeGenerator:
    def __init__(self, mem=None, reg_pool=None):
        self.mem = mem
        self.reg = reg_pool
        self.instructions = []
        self.label_count = 0  # 用于生成唯一标签
    
    """
    根据 Parser 提供的语义节点生成指令
    """
    def generate(self, node, source_code=None):
        if not node: return
        if node["type"] == "PROGRAM":
            for stmt in node["body"]:
                self.generate(stmt, source_code)

        elif node["type"] == "ASSIGN":
            reg_src = self.gen_expr(node["value"])
            addr = self.mem.get_addr(node["target"])
            self.emit("WRITE", addr, reg_src, 0, f"[addr {addr}] = {node['target'].value}")
            self.reg.free(reg_src)  # 用完就释放寄存器

        elif node["type"] == "ARRAY_ASSIGN":
            self.gen_array_assignment(node, source_code)

        elif node["type"] == "IO_IN":
            reg_dst = self.reg.alloc(node, source_code)
            self.emit("MOV", "INPUT", 0, reg_dst, f"[{reg_dst}] = INPUT")
            self.reg.free(reg_dst)  # 用完就释放寄存器

        elif node["type"] == "IO_OUT":
            reg_src = self.gen_expr(node["value"])
            self.emit("MOV", reg_src, 0, "OUTPUT", f"output = [{reg_src}]")
            self.reg.free(reg_src)  # 用完就释放寄存器 

        elif node["type"] == "IF_STMT":
            self.gen_if_statement(node, source_code)

        elif node["type"] == "WHILE_STMT":
            self.gen_while_statement(node, source_code)

        else:
            report_error(source_code, f"不支持的节点类型: {node['type']}", node['token'])

    """
    递归处理表达式节点，返回寄存器
    """ 
    def gen_expr(self, node, source_code=None):
        if node["type"] == "NUMBER":
            reg = self.reg.alloc(node, source_code)
            self.emit("IMM", node["value"], 0, reg, f"[{reg}] = {node['value']}")
            return reg
        
        elif node["type"] == "ID":
            reg = self.reg.alloc(node, source_code)
            addr = self.mem.get_addr(node["value"])
            self.emit("READ", addr, 0, reg, f"[{reg}] = {node['value']} [addr {addr}]")
            return reg
        
        elif node["type"] == "BINARY_OP":
            left_reg = self.gen_expr(node["left"], source_code)
            right_reg = self.gen_expr(node["right"], source_code)
            res_reg = left_reg  # 结果寄存器可以复用左操作数的寄存器
            self.emit(node["op"], left_reg, right_reg, res_reg, f"[{res_reg}] = [{left_reg}] {node['op']} [{right_reg}]")
            self.reg.free(right_reg)  # 右操作数寄存器用完就释放
            return res_reg

    def emit(self, opcode, arg1, arg2, target, comment=""):
        if str(arg1).isdigit() and opcode in ["READ", "WRITE"]:
            opcode += "+IMM1"

        line = f"{opcode:<10} {arg1:<5} {arg2:<5} {target:<10}"
        if comment:
            line += f" # {comment}"
        self.instructions.append(line)

    def emit_comment(self, comment):
        line = f"# {comment}"
        self.instructions.append(line)

    def emit_set_label(self, label):
        line = f"{label}:"
        self.instructions.append(line)

    def _new_label(self):
        self.label_count += 1
        return f"@L{self.label_count}"
    
    def get_inverse_op(self, op):
        inverse_ops = {
            "EQ": "IF_NE",
            "NE": "IF_E",
            "GT": "IF_LOE",
            "LT": "IF_GOE",
            "GE": "IF_L",
            "LE": "IF_G"
        }
        return inverse_ops.get(op, None)
    
    def gen_array_assignment(self, node, source_code=None):
        pass

    """
    生成 if 语句的代码
    """
    def gen_if_statement(self, node, source_code=None):
        # 计算左侧和右侧表达式
        left_reg = self.gen_expr(node['condition']['left'], source_code)
        right_reg = self.gen_expr(node['condition']['right'], source_code)

        l_else = self._new_label()
        l_end = self._new_label()

        # 条件跳转指令 此处填充 0
        jump_op = self.get_inverse_op(node['condition']['op'])
        self.emit(jump_op, left_reg, right_reg, l_else, f"if {left_reg} {node['condition']['op']} {right_reg} jump to {l_else}")

        # 生成 if 块的代码
        self.emit_comment("--- IF BODY ---")
        for stmt in node['if_body']:
            self.generate(stmt, source_code)
        
        self.emit("JMP", 0, 0, l_end, f"jump to {l_end}")

        self.emit_comment("--- END OF IF BODY ---")

        # 生成 else 块的代码
        if(node['else_body']):
            self.emit_comment(f"--- ELSE BODY ({l_else}) ---")
            self.emit_set_label(l_else)
            for stmt in node['else_body']:
                self.generate(stmt, source_code)

        self.reg.free(left_reg)
        self.reg.free(right_reg)

        self.emit_set_label(l_end)
        self.emit_comment(f"--- END BODY ({l_end}) ---")

        """
        生成 while 语句的代码
        """
    def gen_while_statement(self, node, source_code=None):
        # 创建循环开始和结束标签
        start_label = self._new_label()
        end_label = self._new_label()

        # 循环开始标签
        self.emit_set_label(start_label)

        # 计算条件表达式
        cond = node['condition']
        left_reg = self.gen_expr(cond['left'], source_code)
        right_reg = self.gen_expr(cond['right'], source_code)

        # 获取反转的跳转操作
        jump_op = self.get_inverse_op(cond['op'])
        self.emit(jump_op, left_reg, right_reg, end_label, f"while {left_reg} {cond['op']} {right_reg} jump to {end_label}")

        # 生成循环体代码
        self.emit_comment("--- WHILE BODY ---")
        for stmt in node['body']:
            self.generate(stmt, source_code)

        #跳转回循环开始
        self.emit("JMP", 0, 0, start_label, f"jump to {start_label}")

        self.emit_set_label(end_label)
        self.emit_comment(f"--- END OF WHILE BODY ({end_label}) ---")

        self.reg.free(left_reg)
        self.reg.free(right_reg)

