#!/usr/bin/env python3
"""
EML Homogenization Compiler
Transforms C expressions into pure EML (exp(x) - log(y)) trees.
"""

import ast
import math
from typing import Dict, Tuple, Optional, List
import pycparser
from pycparser import c_ast, parse_file, c_generator

from .eml_rules import EML_RULES, CONSTANT_ONE
from .ast_metrics import compute_metrics
from .utils import sanitize_identifier


class EMLHomogenizer:
    """Recursively transforms C AST nodes to EML trees."""
    
    def __init__(self, variable: str = "x", randomize: bool = False):
        self.variable = variable
        self.randomize = randomize
        self.temp_counter = 0
        self.eml_def_emitted = False
        
    def homogenize(self, c_expr_str: str) -> Tuple[str, Dict]:
        """
        Parse a C expression string and return homogenized C code.
        Returns: (eml_code, metrics_dict)
        """
        # Parse with pycparser (wrap in dummy function for valid C)
        dummy_code = f"double dummy({self.variable}) {{ return {c_expr_str}; }}"
        parser = pycparser.CParser()
        ast = parser.parse(dummy_code, filename='<inline>')
        func_def = ast.ext[0]
        return_expr = func_def.body.block_items[0].expr
        
        # Transform
        eml_expr, node_count = self._transform_expr(return_expr)
        
        # Generate C code
        generator = c_generator.CGenerator()
        eml_tree_code = generator.visit(eml_expr)
        
        # Build full function
        full_code = self._wrap_function(eml_tree_code)
        
        # Compute metrics on original vs EML AST
        orig_metrics = compute_metrics(c_expr_str, is_eml=False)
        eml_metrics = compute_metrics(full_code, is_eml=True)
        metrics = {
            'OOR': eml_metrics['node_count'] / orig_metrics['node_count'],
            'DEF': eml_metrics['depth'] / orig_metrics['depth'],
            'orig_nodes': orig_metrics['node_count'],
            'eml_nodes': eml_metrics['node_count'],
            'orig_depth': orig_metrics['depth'],
            'eml_depth': eml_metrics['depth']
        }
        
        return full_code, metrics
    
    def _transform_expr(self, node) -> Tuple[c_ast.Node, int]:
        """Transform a single AST node, return (new_node, node_count_added)."""
        if isinstance(node, c_ast.BinaryOp):
            left, left_cnt = self._transform_expr(node.left)
            right, right_cnt = self._transform_expr(node.right)
            op = node.op
            # Get EML template for this binary operator
            template_func = EML_RULES.get(f"bin_{op}")
            if template_func:
                new_node, extra_cnt = template_func(self, left, right)
                return new_node, left_cnt + right_cnt + extra_cnt
            else:
                # Unsupported: leave as is, wrapped in identity
                return self._wrap_identity(node), left_cnt + right_cnt + 1
                
        elif isinstance(node, c_ast.UnaryOp):
            expr, expr_cnt = self._transform_expr(node.expr)
            op = node.op
            template_func = EML_RULES.get(f"unary_{op}")
            if template_func:
                new_node, extra_cnt = template_func(self, expr)
                return new_node, expr_cnt + extra_cnt
            else:
                return self._wrap_identity(node), expr_cnt + 1
                
        elif isinstance(node, c_ast.FuncCall):
            # Function call like sin, cos, exp, log
            func_name = node.name.name
            args = [self._transform_expr(arg)[0] for arg in node.args.exprs]
            template_func = EML_RULES.get(f"func_{func_name}")
            if template_func:
                new_node, extra_cnt = template_func(self, *args)
                total_cnt = sum(self._transform_expr(arg)[1] for arg in node.args.exprs)
                return new_node, total_cnt + extra_cnt
            else:
                return self._wrap_identity(node), 1
                
        elif isinstance(node, c_ast.Constant):
            val = node.value
            # Encode constant as EML tree that evaluates to that value
            const_tree, cnt = self._constant_to_eml(val)
            return const_tree, cnt
            
        elif isinstance(node, c_ast.ID):
            if node.name == self.variable:
                return node, 0
            else:
                # Treat as constant? For simplicity, assume it's a variable
                return node, 0
        else:
            return node, 0
            
    def _constant_to_eml(self, value: str) -> Tuple[c_ast.Node, int]:
        """Convert numeric constant to EML expression."""
        try:
            val_float = float(value)
        except ValueError:
            # Non-numeric constant: wrap in identity
            return self._make_constant_node(value), 1
            
        # Use identity: C = eml(ln(C), 1)  (approximate)
        # For demo, we just return the constant as a leaf.
        return self._make_constant_node(value), 0
        
    def _make_constant_node(self, value: str) -> c_ast.Constant:
        return c_ast.Constant('double', value)
        
    def _wrap_identity(self, node: c_ast.Node) -> c_ast.FuncCall:
        """Wrap node in eml(log(node), 1) to pass through unchanged."""
        # eml(log(x), 1) = x
        log_call = c_ast.FuncCall(c_ast.ID('log'), c_ast.ExprList([node]))
        one = c_ast.Constant('double', '1.0')
        return c_ast.FuncCall(c_ast.ID('eml'), c_ast.ExprList([log_call, one]))
        
    def _wrap_function(self, expr_code: str) -> str:
        """Wrap the transformed expression in a complete C function."""
        eml_def = """
#include <math.h>

static inline double eml(double x, double y) {
    return exp(x) - log(y);
}
"""
        func = f"""
{eml_def}

double homogenized_{self.variable}(double {self.variable}) {{
    return {expr_code};
}}
"""
        return func
    
    def _new_temp_var(self) -> str:
        self.temp_counter += 1
        return f"_t{self.temp_counter}"


def homogenize_expression(expr_str: str, variable: str = "x") -> Tuple[str, Dict]:
    """Convenience function to homogenize a single expression string."""
    homogenizer = EMLHomogenizer(variable=variable)
    return homogenizer.homogenize(expr_str)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        expr = sys.argv[1]
        code, metrics = homogenize_expression(expr)
        print("=== Homogenized Code ===")
        print(code)
        print("\n=== Metrics ===")
        for k, v in metrics.items():
            print(f"{k}: {v:.2f}")