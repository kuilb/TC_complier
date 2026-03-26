#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
assembler.py
支持 Label 自动回填的扫描汇编器

Author:Kulib
Date:2026-3-26
Version:0.2
"""
from core.isa import get_opcode, pack_32bit, REGISTER_MAP
class Assembler:
    def __init__(self):
        self.label_map = {}     # 标签->PC 表

    """
    处理整个汇编列表，返回机器码列表
    """
    def assemble_program(self, asm):
        # 第一遍扫描，记录标签位置
        clean_instructions = []
        current_pc = 0
        # 预处理
        for line in asm:
            line = line.split("#")[0]
            if not line.strip(): continue

            # 处理标签
            if line.startswith("@"):
                label_name = line.rstrip(":").strip("@")
                self.label_map[label_name] = current_pc
                print(f"Label '{label_name}' at PC={current_pc}")
            else:
                clean_instructions.append(line.strip())
                current_pc += 4

        # 第二遍扫描，生成机器码
        machine_codes = []        
        for line in clean_instructions:
            code = self._assemble_single_line(line)
            if code is not None:
                machine_codes.append(code)

        return machine_codes
    
    def _assemble_single_line(self, asm_line):
        parts = asm_line.split()
        if not parts: return None

        op = get_opcode(parts[0])
        a1 = self._to_val(parts[1])
        a2 = self._to_val(parts[2])
        out = self._to_val(parts[3])

        return pack_32bit(op, a1, a2, out)
    
    """
    将汇编转换为机器码，并返回字节列表
    """
    def to_byte_list(self, machine_code):
        byte_list = []
        for i in range(3, -1, -1):
            byte = (machine_code >> (i * 8)) & 0xFF
            byte_list.append(f"0x{byte:02X}")
        return byte_list
    
    """
    将单行汇编转换为机器码
    """        
    def _to_val(self, token):
        token = str(token).upper()
        token = token.lstrip('@')
        if token in REGISTER_MAP:
            return REGISTER_MAP[token]
        
        if token in self.label_map:
            print(f"Resolving label '{token}' to address {self.label_map[token]}")
            return self.label_map[token] & 0xFFFF

        try:
            return int(token) & 0xFFFF
        except ValueError:
            return 0
