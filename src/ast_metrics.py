"""
Compute AST metrics: node count, depth, operator types.
"""

import ast
from typing import Dict, Set

def compute_metrics(code_str: str, is_eml: bool = False) -> Dict:
    """
    Parse C-like code string and return metrics.
    Uses Python's ast for simplicity (assuming expression similarity).
    For accurate C metrics, we would use pycparser, but this is a proxy.
    """
    # Clean code to extract just the expression
    if 'return' in code_str:
        # Extract return expression
        start = code_str.find('return') + 6
        end = code_str.find(';', start)
        expr_str = code_str[start:end].strip()
    else:
        expr_str = code_str.strip()
    
    # Parse as Python expression (good enough for node count/depth trend)
    try:
        tree = ast.parse(expr_str, mode='eval')
    except SyntaxError:
        # Fallback: count manually
        return {'node_count': len(expr_str), 'depth': expr_str.count('('), 'op_types': set()}
    
    nodes = list(ast.walk(tree))
    node_count = len(nodes)
    
    def get_depth(node):
        if not hasattr(node, '_fields'):
            return 1
        children = list(ast.iter_child_nodes(node))
        if not children:
            return 1
        return 1 + max(get_depth(c) for c in children)
    
    depth = get_depth(tree.body)
    
    # Count distinct operator types
    op_types = set()
    for node in nodes:
        if isinstance(node, ast.BinOp):
            op_types.add(type(node.op).__name__)
        elif isinstance(node, ast.UnaryOp):
            op_types.add(type(node.op).__name__)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                op_types.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                op_types.add(node.func.attr)
    
    return {
        'node_count': node_count,
        'depth': depth,
        'op_types': op_types,
        'op_type_count': len(op_types)
    }