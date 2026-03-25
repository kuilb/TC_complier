#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main.py
程序入口

Author:Kulib
Date:2026-3-25
Version:0.1
"""
import os
import argparse
import json
from core.lexer import Lexer
from core.parser import Parser
from core.codegen import CodeGenerator
from core.assembler import Assembler
from hardware.memory import StaticMemory
from hardware.registers import RegisterPool

def run_compiler(input_path, output_path, save_intermediate=False):
    # 基础文件名（去掉扩展名）
    base_name = os.path.splitext(input_path)[0]

    # 初始化组件
    mem = StaticMemory()
    regs = RegisterPool()   
    lexer = Lexer()
    parser = Parser()
    codegen = CodeGenerator(mem, regs)
    assembler = Assembler()

    print(f"[*] 编译开始: {input_path}")

    # 读取源码
    print(f"[*] 读取源文件: {input_path}")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: 文件 '{input_path}' 未找到.")
        return

    all_tokens = []
    all_ast = []

    print(f"[*] 已找到 {len(lines)} 行代码，开始编译...")
    # 编译循环
    for line in lines:
        if not line.strip(): continue  # 跳过空行
        tokens = lexer.tokenize(line)
        if tokens:
            all_tokens.append(tokens)

            node = parser.parse(tokens)
            if node:
                all_ast.append(node)
                codegen.generate(node)

    # 汇编阶段
    print(f"[*] 生成汇编代码...")
    machine_hex_list = []
    all_bytes = []
    for asm in codegen.instructions:
        m_code = assembler.assemble(asm)
        if m_code is not None:
            # 格式化为 16位 16进制字符串 (64-bit)
            all_bytes.extend(assembler.to_byte_list(m_code))

    # 保存 .asm
    final_output = output_path if output_path else f"{base_name}.asm"
    with open(final_output, 'w', encoding='utf-8') as f:
        for instr in codegen.instructions:
            f.write(f"{instr}\n")

    # 保存 .hex
    base_name = os.path.splitext(input_path)[0]
    hex_file = f"{base_name}.hex"
    
    with open(hex_file, 'w', encoding='utf-8') as f:
        for i in range(0, len(all_bytes), 6):
            # 取出 6 个字节
            chunk = all_bytes[i : i + 6]
            # 用空格连接并换行
            f.write(" ".join(chunk) + "\n")

    print(f"[OK] 汇编文件: {final_output}")
    print(f"[OK] 机器码文件: {hex_file} (总字节数: {len(all_bytes)})")

    print(f"[*] 编译成功")

    # --- 可选：保存中间过程文件 ---
    if save_intermediate:
        # 保存 .tokens
        with open(f"{base_name}.tokens", 'w') as f:
            for t in all_tokens: f.write(f"{' '.join(t)}\n")
        
        # 保存 .ast (JSON格式)
        with open(f"{base_name}.ast", 'w') as f:
            json.dump(all_ast, f, indent=4)
        
        print(f"[*] Intermediate files saved: {base_name}.tokens, {base_name}.ast")


if __name__ == "__main__":
    # 配置命令行参数
    arg_parser = argparse.ArgumentParser(description="TinyCode 0.1 Compiler (64-bit Target)")
    
    # 必填参数：输入文件
    arg_parser.add_argument("input", help="Path to the .tc source file")
    
    # 可选参数：自定义输出路径
    arg_parser.add_argument("-o", "--output", help="Custom path for the output .asm file")
    
    # 可选参数：是否生成中间文件 (-v 模式)
    arg_parser.add_argument("-v", "--verbose", action="store_true", help="Generate .tokens and .ast intermediate files")

    args = arg_parser.parse_args()

    # 执行编译
    run_compiler(args.input, args.output, args.verbose)