#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
memory.py
用于内存管理

Author:Kulib
Date:2026-3-25
Version:0.1
"""
from utils.logger import report_error, Color
class StaticMemory:
    def __init__(self, ram_size = 256):
        self.table = {}
        self.pointer = 0
        self.ram_size = ram_size

    # 重置内存字典
    def reset(self):
        self.table = {}
        self.pointer = 0

    def allocate_temp(self):
        temp_name = f"__temp{self.pointer}"
        if self.pointer >= self.ram_size:
            report_error("", "编译错误: RAM 已满，无法分配临时变量！", None)
        return self.get_addr(temp_name)
    
    def reset_temps(self):
        # 删除所有以 __temp 开头的变量
        temp_vars = [name for name in self.table if name.startswith("__temp")]
        for name in temp_vars:
            del self.table[name]

    # 获取输入名称的RAM物理地址，如果没有则创建一个
    def get_addr(self, name):
        if hasattr(name, "value"):
            name = name.value

        if name not in self.table:
            if(self.pointer >= self.ram_size):
                report_error("", "编译错误: RAM 已满，无法分配变量！", None)
            
            self.table[name] = self.pointer
            self.pointer += 1
        
        return self.table[name]
