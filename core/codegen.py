#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
codegen.py
用于将输入的token生成汇编语言代码

Author:Kulib
Date:2026-3-25
Version:0.1
"""
import re

from hardware.memory import StaticMemory
from hardware.registers import RegisterPool

class CodeGenerator:
    def __init__(self, mem=None, reg_pool=None):
        self.mem = mem
        self.reg = reg_pool
        self.instructions = []
    
    """
    根据 Parser 提供的语义节点生成指令
    """
    def generate(self, node):
        if not node: return

        self.reg.free_all()  # 每次生成前重置寄存器状态
        if node["type"] == "ASSIGN":
            self._gen_assign(node)
        elif node["type"] == "BINARY_OP":
            self._gen_binary_op(node)
        #elif node["type"] == "CONTROL":
            #self._gen_control(node)
        else:
            raise NotImplementedError(f"不支持的节点类型: {node['type']}")
        
    """
    获取寄存器
    """
    def _get_reg(self, token):
        # 获取寄存器
        if token.startswith("REG"):
            return token
        
        # 是变量则从内存获取地址并加载到寄存器
        r = self.reg.alloc()
        addr = self.mem.get_addr(token)
        self.emit("READ", addr, r, 0, f"{r} = {token} from RAM addr {addr}")
        return r
    
    """
    a+b
    """
    def _gen_assign(self, node):
        target = node["target"]
        val = node["value"]
        
        # 申请寄存器存放右值
        res_reg = self.reg.alloc()

        # 立即数
        if val.isdigit():
            self.emit("IMM", val, 0, res_reg, f"{res_reg} = {val}")
        # 寄存器
        elif self._is_reg(val):
            self.emit("MOV", val, 0, res_reg, f"{res_reg} = {val}")
        # RAM地址
        else:
            addr = self.mem.get_addr(val)
            self.emit("READ", addr, 0, res_reg, f"{res_reg} = {val} from RAM addr {addr}")

        # 将结果写回目标变量
        self._store_result(target, res_reg)

    """
    a=b+c
    """
    def _gen_binary_op(self, node):
        target = node["target"]
        left = node["left"]
        right = node["right"]
        base_op = node["op_type"]  # e.g. "ADD", "SUB"

        # 左操作数寄存器
        reg_l = self._load_to_temp_reg(left)

        # 结果寄存器
        reg_res = self.reg.alloc()

        # 右操作数立即数
        if right.isdigit():
            self.emit(f"{base_op}+IMM2", reg_l, right, reg_res, f"{reg_res} = {reg_l} {base_op} {right}")
        else:
            reg_r = self._load_to_temp_reg(right)
            self.emit(base_op, reg_l, reg_r, reg_res, f"{reg_res} = {reg_l} {base_op} {reg_r}")

        self._store_result(target, reg_res)

    
    # --- 辅助函数 ---
    def _is_reg(self, token):
        return token.startswith("REG")
    
    def _load_to_temp_reg(self, token):
        if self._is_reg(token):
            return token
        
        r = self.reg.alloc()
        addr = self.mem.get_addr(token)
        self.emit("READ", addr, 0, r, f"{r} = {token} from RAM addr {addr}")
        return r
    
    def _store_result(self, target, res_reg):
        if self._is_reg(target):
            self.emit("MOV", res_reg, 0, target, f"{target} = {res_reg}")
        else:
            addr = self.mem.get_addr(target)
            self.emit("WRITE", addr, res_reg, 0, f"write {target} in RAM addr {addr}")

    def emit(self, opcode, arg1, arg2, target, comment=""):
        if str(arg1).isdigit() and opcode in ["READ", "WRITE"]:
            opcode += "+IMM1"

        line = f"{opcode:<10} {arg1:<5} {arg2:<5} {target:<10}"
        if comment:
            line += f" # {comment}"
        self.instructions.append(line)
