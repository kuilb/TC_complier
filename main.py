#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main.py
程序入口

Author:Kulib
Date:2026-3-26
Version:0.2
"""
import os
import sys
import argparse
import json
from core.lexer import Lexer
from core.lexer import Token
from core.parser import Parser
from core.codegen import CodeGenerator
from core.assembler import Assembler
from hardware.memory import StaticMemory
from hardware.registers import RegisterPool
from utils.logger import Color

# 仅在 Windows 上启用颜色支持
if sys.platform == "win32":
    os.system('color')

def token_encoder(obj):
    # 如果是 Token 对象，返回它的字典形式或特定的值
    if hasattr(obj, '__dict__'):
        return obj.__dict__ 
    # 或者如果你只想在 JSON 里看到它的字面值：
    # if isinstance(obj, Token): return obj.value
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def run_compiler(input_path, output_path, save_intermediate=False):
    # 基础文件名（去掉扩展名）
    base_name = os.path.splitext(input_path)[0]

    # 初始化组件
    mem = StaticMemory()
    regs = RegisterPool()   
    assembler = Assembler()

    print(f"TC编译器 0.2 by Kulib")

    # 读取源码
    print(f"[{Color.BLUE}*{Color.END}] 正在读取源文件: {Color.BLUE}{input_path}{Color.END}")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            source_code = f.read()  # 获取完整的源码流
    except FileNotFoundError:
        print(f"{Color.RED}[!] 错误: 文件 '{input_path}' 未找到{Color.END}")
        return

    

    # 预处理和词法分析
    print(f"[{Color.BLUE}*{Color.END}] 预处理和词法分析...")
    lexer = Lexer()
    tokens = lexer.tokenize(source_code)
    if save_intermediate:
        # 保存 .tokens
        print(f"[{Color.BLUE}*{Color.END}] 保存词法分析结果到: {Color.BLUE}{base_name}.tokens{Color.END}")
        with open(f"{base_name}.tokens", 'w') as f:
            for t in tokens:
                # 显式提取你想记录的信息，记得转成字符串
                f.write(f"Type: {t.type:<10} Value: {t.value:<10} Line: {t.line:<3} Col: {t.column}\n")

    # 语法分析
    print(f"[{Color.BLUE}*{Color.END}] 语法分析...")
    parser = Parser(tokens, source_code)
    ast = parser.parse_program()
    if save_intermediate:
        # 保存 .ast (JSON格式)
        print(f"[{Color.BLUE}*{Color.END}] 保存语法分析结果到: {Color.BLUE}{base_name}.ast{Color.END}")
        with open(f"{base_name}.ast", 'w') as f:
            json.dump(ast, f, indent=4, default=token_encoder)

    # 汇编阶段
    print(f"[{Color.BLUE}*{Color.END}] 生成汇编代码...")
    codegen = CodeGenerator(mem, regs)
    codegen.generate(ast, source_code)

    # 保存 .asm
    final_output = output_path if output_path else f"{base_name}.asm"
    with open(final_output, 'w', encoding='utf-8') as f:
        for instr in codegen.instructions:
            f.write(f"{instr}\n")

    print(f"[{Color.GREEN}OK{Color.END}] 汇编文件: {final_output}")
    print(f"[{Color.BLUE}*{Color.END}] 生成机器码...")
    machine_codes = assembler.assemble_program(codegen.instructions)

    all_bytes = []
    for m_code in machine_codes:
        all_bytes.extend(assembler.to_byte_list(m_code))

    # 保存 .hex
    base_name = os.path.splitext(input_path)[0]
    hex_file = f"{base_name}.hex"
    
    with open(hex_file, 'w', encoding='utf-8') as f:
        for i in range(0, len(all_bytes), 4):
            # 取出 4 个字节
            chunk = all_bytes[i : i + 4]
            # 用空格连接并换行
            f.write(" ".join(chunk) + "\n")

    print(f"[{Color.GREEN}OK{Color.END}] 机器码文件: {hex_file} (总字节数: {len(all_bytes)})")

    print(f"{Color.GREEN}编译成功{Color.END}")

if __name__ == "__main__":
    # 配置命令行参数
    arg_parser = argparse.ArgumentParser(description="TinyCode 0.2 Compiler (64-bit Target)")
    
    # 必填参数：输入文件
    arg_parser.add_argument("input", help="Path to the .tc source file")
    
    # 可选参数：自定义输出路径
    arg_parser.add_argument("-o", "--output", help="Custom path for the output .asm file")
    
    # 可选参数：是否生成中间文件 (-v 模式)
    arg_parser.add_argument("-v", "--verbose", action="store_true", help="Generate .tokens and .ast intermediate files")

    args = arg_parser.parse_args()

    # 执行编译
    run_compiler(args.input, args.output, args.verbose)