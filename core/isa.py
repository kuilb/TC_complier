#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
isa.py
用于定义指令集架构 (ISA)

Author:Kulib
Date:2026-3-25
Version:0.1
"""
# 基础指令定义 (6-bit 核心码)
BASE_OPCODES = {
    # 运算与 I/O (0b00)
    "ADD":    0b000000,
    "SUB":    0b000001,
    "AND":    0b000010,
    "OR":     0b000011,
    "NOT":    0b000100,
    "XOR":    0b000101,
    "MOV":    0b000110,
    "I/O":    0b000111,

    # RAM 操作
    "READ":   0b001000,
    "WRITE":  0b001001,

    # 栈操作 (0b01)
    "PUSH":   0b010000,
    "POP":    0b010001,
    "RST":    0b011001,

    # 条件跳转 (0b10)
    "IF_E":   0b100000,
    "IF_L":   0b100010,
    "IF_LOE": 0b100011,
    "IF_G":   0b100100,
    "IF_GOE": 0b100101,

    # 无条件跳转 (特殊编码)
    "JMP":    0b100110,
    "CALL":   0b111110,
    "IMM":    0b000110, # 对应 0b11000110
}

# 立即数标志位 (最高 2 位)
IMM_FLAGS = {
    "NONE": 0b00000000,
    "IMM1": 0b10000000,
    "IMM2": 0b01000000,
    "BOTH": 0b11000000,
}

# 寄存器编号映射
REGISTER_MAP = {
    "REG0":   0,
    "REG1":   1,
    "REG2":   2,
    "REG3":   3,
    "REG4":   4,
    "REG5":   5,
    "INPUT":  6,
    "OUTPUT": 7,
}

"""
输入: "READ+IMM1" 或 "ADD+IMM2"
输出: 融合后的 8-bit Opcode (int)
"""
def get_opcode(asm_opcode):
    base_name = asm_opcode.split("+")[0]

    if base_name == "IMM":
        return 0b11000110  # IMM 指令的特殊编码
    
    code = BASE_OPCODES.get(base_name, 0)

    if "+IMM1" in asm_opcode:
        code |= IMM_FLAGS["IMM1"]
    if "+IMM2" in asm_opcode:
        code |= IMM_FLAGS["IMM2"]

    # 处理 JMP/CALL 的特殊前缀
    if base_name == "JMP": code |= 0b10000000
    if base_name == "CALL": code |= 0b10000000

    return code & 0xFF

"""
按照 32 位（4字节）拼接指令
"""
def pack_32bit(op, a1, a2, out):
    
    # 确保每个部分都是 8 位
    return ((op & 0xFF) << 24) | \
           ((a1 & 0xFF) << 16) | \
           ((a2 & 0xFF) << 8)  | \
           (out & 0xFF)