"""
Compute AST metrics: node count, depth, operator types.
Uses full recursive traversal without artificial weighting.
"""

import ast
from typing import Dict, Set

class ASTFullCounter(ast.NodeVisitor):
    """Counts every AST node exactly once, with accurate depth."""
    def __init__(self):
        self.node_count = 0
        self.max_depth = 0
        self._current_depth = 0
        self.op_types = set()

    def generic_visit(self, node):
        self.node_count += 1
        self._current_depth += 1
        
        if self._current_depth > self.max_depth:
            self.max_depth = self._current_depth
        
        # Record operator types
        if isinstance(node, ast.BinOp):
            self.op_types.add(type(node.op).__name__)
        elif isinstance(node, ast.UnaryOp):
            self.op_types.add(type(node.op).__name__)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                self.op_types.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                self.op_types.add(node.func.attr)
                
        super().generic_visit(node)
        self._current_depth -= 1

def compute_metrics(code_str: str, is_eml: bool = False) -> Dict:
    # Extract expression
    if 'return' in code_str:
        start = code_str.find('return') + 6
        end = code_str.find(';', start)
        if end == -1:
            end = len(code_str)
        expr_str = code_str[start:end].strip()
    else:
        expr_str = code_str.strip()
    
    try:
        tree = ast.parse(expr_str, mode='eval')
    except SyntaxError:
        return {'node_count': len(expr_str), 'depth': 1, 'op_types': set(), 'op_type_count': 1}
    
    counter = ASTFullCounter()
    counter.visit(tree)
    
    # After homogenization, all operators collapse to 'eml'
    op_types = {'eml'} if is_eml else counter.op_types
    
    return {
        'node_count': counter.node_count,
        'depth': counter.max_depth,
        'op_types': op_types,
        'op_type_count': len(op_types)
    }
