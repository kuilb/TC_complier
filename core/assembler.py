#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
assembler.py
用于将汇编代码生成机器码

Author:Kulib
Date:2026-3-25
Version:0.1
"""
from core.isa import get_opcode, pack_32bit, REGISTER_MAP
class Assembler:
    """
    合成指令的机器码
    """
    def assemble(self, asm_line):
        # 预处理
        asm_line = asm_line.split("#")[0]
        if not asm_line.strip(): return None

        parts = asm_line.split()
        if not parts: return None

        op = get_opcode(parts[0])
        a1 = self._to_val(parts[1])
        a2 = self._to_val(parts[2])
        out = self._to_val(parts[3])

        machine_code = pack_32bit(op, a1, a2, out)
        return machine_code
    
    def to_byte_list(self, machine_code):
        byte_list = []
        for i in range(3, -1, -1):
            byte = (machine_code >> (i * 8)) & 0xFF
            byte_list.append(f"0x{byte:02X}")
        return byte_list
            
    def _to_val(self, token):
        token = str(token).upper()
        if token in REGISTER_MAP:
            return REGISTER_MAP[token]
        try:
            return int(token) & 0xFFFF
        except ValueError:
            return 0
