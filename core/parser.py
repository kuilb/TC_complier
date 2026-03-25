#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
lexer.py
用于语法分析

Author:Kulib
Date:2026-3-25
Version:0.1
"""

class Parser:
    def __init__(self):
        pass

    """
    输入: ['A', '=', 'B', '+', '10']
    输出: {'type': 'BINARY_OP', 'target': 'A', 'left': 'B', 'op': '+', 'right': '10'}
    """
    def parse(self, tokens):
        if not tokens: return

        if "=" in tokens:
            return self._parse_assignment(tokens)
        
        if tokens[0].startswith("if") or tokens[0].startswith("goto"):
            return self._parse_control_flow(tokens)
        
        return {"type": "UNKNOWN", "tokens": tokens}
    
    def _parse_assignment(self, tokens):
        target = tokens[0]
        # token[1] = "="
        
        if len(tokens) == 3:
            return {
                "type": "ASSIGN",
                "target": target,
                "value": tokens[2]
            }
        
        if len(tokens) == 5:
            # 映射汇编指令
            operator = tokens[3]
            op_map = {
                "+": "ADD",
                "-": "SUB",
                "&": "AND",
                "|": "OR",
                "^": "XOR",
            }

            return{
                "type": "BINARY_OP",
                "op_type": op_map.get(operator, "UNKNOWN"),
                "target": target,
                "left": tokens[2],
                "right": tokens[4]
            }
        return None
    
    def _parse_control_flow(self, tokens):
        return {
            "type": "CONTROL",
            "opcode": tokens[0],
            "arg1": tokens[1],
            "arg2": tokens[2],
            "target": tokens[3]
        }
