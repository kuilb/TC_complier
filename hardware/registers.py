#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
registers.py
用于寄存器管理

Author:Kulib
Date:2026-3-25
Version:0.1
"""
from utils.logger import report_error, Color
class RegisterPool:
    def __init__(self):
        self.regs = ["REG0", "REG1", "REG2", "REG3", "REG4", "REG5"]
        self.used = {reg: False for reg in self.regs}

    """
    分配一个空闲寄存器。
    node: 触发分配的 AST 节点（可选），用于精准报错
    source_code: 源码字符串（可选）
    """
    def alloc(self, node=None, source_code=None):
        avaliable = [r for r in self.regs if not self.used[r]]

        if not avaliable:
            # 如果有位置信息，抛出带颜色的智能错误
            if node and source_code:
                report_error(source_code, "寄存器不足: 没有可用的寄存器！", node['token'])
            else:
                report_error("", "寄存器不足: 没有可用的寄存器！", None)
        
        reg = avaliable[0]
        self.used[reg] = True

        return reg
        
    """
    释放寄存器
    """
    def free(self, reg_name):
        if reg_name in self.used:
            self.used[reg_name] = False
        
    """
    重置寄存器状态
    """
    def free_all(self):
        for r in self.used:
            self.used[r] = False

    def __repr__(self):
        return f"RegisterPool(used={self.used})"