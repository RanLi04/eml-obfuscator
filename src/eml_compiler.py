#!/usr/bin/env python3
"""
EML Homogenization Compiler
Transforms C expressions into pure EML trees with domain clamping.
"""

import ast
from typing import Dict, Tuple
import pycparser
from pycparser import c_ast, c_generator

from .eml_rules import EML_RULES
from .ast_metrics import compute_metrics


class EMLHomogenizer:
    def __init__(self, variable: str = "x", randomize: bool = False, max_depth: int = 10):
        self.variable = variable
        self.randomize = randomize
        self.max_depth = max_depth
        self.temp_counter = 0
        self.current_depth = 0
        
    def homogenize(self, c_expr_str: str) -> Tuple[str, Dict]:
        dummy_code = f"double dummy({self.variable}) {{ return {c_expr_str}; }}"
        parser = pycparser.CParser()
        ast_tree = parser.parse(dummy_code, filename='<inline>')
        func_def = ast_tree.ext[0]
        return_expr = func_def.body.block_items[0].expr
        
        eml_expr, _ = self._transform_expr(return_expr)
        
        generator = c_generator.CGenerator()
        eml_tree_code = generator.visit(eml_expr)
        
        full_code = self._wrap_function(eml_tree_code)
        
        orig_metrics = compute_metrics(c_expr_str, is_eml=False)
        eml_metrics = compute_metrics(full_code, is_eml=True)
        
        metrics = {
            'OOR': eml_metrics['node_count'] / orig_metrics['node_count'] if orig_metrics['node_count'] > 0 else 1.0,
            'DEF': eml_metrics['depth'] / orig_metrics['depth'] if orig_metrics['depth'] > 0 else 1.0,
            'orig_nodes': orig_metrics['node_count'],
            'eml_nodes': eml_metrics['node_count'],
            'orig_depth': orig_metrics['depth'],
            'eml_depth': eml_metrics['depth']
        }
        
        return full_code, metrics
    
    def _transform_expr(self, node) -> Tuple[c_ast.Node, int]:
        # 防止无限递归（若达到最大深度则停止展开）
        self.current_depth += 1
        if self.current_depth > self.max_depth:
            self.current_depth -= 1
            return self._wrap_identity(node), 1
            
        if isinstance(node, c_ast.BinaryOp):
            left, left_cnt = self._transform_expr(node.left)
            right, right_cnt = self._transform_expr(node.right)
            template_func = EML_RULES.get(f"bin_{node.op}")
            if template_func:
                new_node, extra_cnt = template_func(self, left, right)
                self.current_depth -= 1
                return new_node, left_cnt + right_cnt + extra_cnt
            self.current_depth -= 1
            return self._wrap_identity(node), left_cnt + right_cnt + 1
                
        elif isinstance(node, c_ast.UnaryOp):
            expr, expr_cnt = self._transform_expr(node.expr)
            template_func = EML_RULES.get(f"unary_{node.op}")
            if template_func:
                new_node, extra_cnt = template_func(self, expr)
                self.current_depth -= 1
                return new_node, expr_cnt + extra_cnt
            self.current_depth -= 1
            return self._wrap_identity(node), expr_cnt + 1
                
        elif isinstance(node, c_ast.FuncCall):
            func_name = node.name.name
            args = [self._transform_expr(arg)[0] for arg in node.args.exprs]
            template_func = EML_RULES.get(f"func_{func_name}")
            if template_func:
                new_node, extra_cnt = template_func(self, *args)
                total_cnt = sum(self._transform_expr(arg)[1] for arg in node.args.exprs)
                self.current_depth -= 1
                return new_node, total_cnt + extra_cnt
            self.current_depth -= 1
            return self._wrap_identity(node), 1
                
        elif isinstance(node, c_ast.Constant):
            self.current_depth -= 1
            return self._make_constant_node(node.value), 1
            
        elif isinstance(node, c_ast.ID):
            self.current_depth -= 1
            return node, 0
            
        self.current_depth -= 1
        return node, 0
        
    def _make_constant_node(self, value: str) -> c_ast.Constant:
        return c_ast.Constant('double', value)
        
    def _wrap_identity(self, node: c_ast.Node) -> c_ast.FuncCall:
        log_call = c_ast.FuncCall(c_ast.ID('log'), c_ast.ExprList([node]))
        one = c_ast.Constant('double', '1.0')
        return c_ast.FuncCall(c_ast.ID('eml'), c_ast.ExprList([log_call, one]))
        
    def _wrap_function(self, expr_code: str) -> str:
        # 域钳位保护
        eml_def = """
#include <math.h>

static inline double eml(double x, double y) {
    return exp(x) - log(fmax(y, 1e-8));
}
"""
        return f"{eml_def}\ndouble homogenized_{self.variable}(double {self.variable}) {{\n    return {expr_code};\n}}\n"

def homogenize_expression(expr_str: str, variable: str = "x") -> Tuple[str, Dict]:
    return EMLHomogenizer(variable=variable).homogenize(expr_str)
