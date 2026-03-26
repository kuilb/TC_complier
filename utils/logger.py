#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
logger.py
用于日志和报错显示

Author:Kulib
Date:2026-3-25
Version:0.2
"""
import sys
class CompileError(Exception):
    """自定义编译器异常"""
    pass

class Color:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m' # 加粗
    UNDERLINE = '\033[4m' # 下划线
    END = '\033[0m'  # 以这个结尾

"""
source_code: 原始读取的 .tc 字符串
message: 错误信息
token: 触发错误的 Token 对象
"""
def report_error(source_code, message, token):
    line_content = source_code.splitlines()[token.line - 1]  # 获取错误行的内容
   
    # 彩色输出
    header = f"{Color.RED}{Color.BOLD}[!] 编译错误: {Color.END}{message}"
    location = f"{Color.BOLD}位置: 第 {token.line} 行, 第 {token.column} 列{Color.END}"
    
    # 将错误那一行加粗
    source_display = f"  {Color.BLUE}> {Color.BOLD}{line_content}{Color.END}"
    
    # 红色箭头指向
    pointer = " " * (token.column + 3) + f"{Color.RED}{Color.BOLD}^{Color.END}"

    print(f"\n{header}")
    print(f"{location}")
    print(f"{source_display}")
    print(f"{pointer}\n")

    sys.exit(1)