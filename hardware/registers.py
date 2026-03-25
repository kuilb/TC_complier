#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
registers.py
用于寄存器管理

Author:Kulib
Date:2026-3-25
Version:0.1
"""

class RegisterPool:
    def __init__(self):
        self.regs = ["REG0", "REG1", "REG2", "REG3", "REG4", "REG5"]
        self.used = {reg: False for reg in self.regs}

    """
    获取空闲寄存器
    """
    def alloc(self, count=1):
        avaliable = [r for r in self.regs if not self.used[r]]

        if len(avaliable) < count:
            raise RuntimeError("编译错误: 寄存器不足，无法分配更多寄存器。")
        
        allocated = avaliable[:count]
        for r in allocated:
            self.used[r] = True

        if count == 1:
            return allocated[0]
        else:
            return tuple(allocated)
        
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