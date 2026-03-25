#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
memory.py
用于内存管理

Author:Kulib
Date:2026-3-25
Version:0.1
"""

class StaticMemory:
    def __init__(self, ram_size = 256):
        self.table = {}
        self.pointer = 0
        self.ram_size = ram_size

    # 重置内存字典
    def reset(self):
        self.table = {}
        self.pointer = 0

    # 获取输入名称的RAM物理地址，如果没有则创建一个
    def get_addr(self, name):
        if name not in self.table:
            if(self.pointer >= self.ram_size):
                raise MemoryError(f"编译错误: RAM 已满，无法为变量 '{name}' 分配空间。")
            
            self.table[name] = self.pointer
            self.pointer += 1
        
        return self.table[name]
