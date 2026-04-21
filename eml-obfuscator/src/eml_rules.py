"""
EML encoding templates for standard operations.
Based on Odrzywołek (2026) arXiv:2603.21852.
"""

import pycparser.c_ast as c_ast

CONSTANT_ONE = c_ast.Constant('double', '1.0')

def _eml(a, b):
    """Create an eml(a, b) function call node."""
    return c_ast.FuncCall(c_ast.ID('eml'), c_ast.ExprList([a, b]))

def _log(x):
    return c_ast.FuncCall(c_ast.ID('log'), c_ast.ExprList([x]))

def _exp(x):
    return c_ast.FuncCall(c_ast.ID('exp'), c_ast.ExprList([x]))

def _add(a, b):
    return c_ast.BinaryOp('+', a, b)

def _mul(a, b):
    return c_ast.BinaryOp('*', a, b)

def _sub(a, b):
    return c_ast.BinaryOp('-', a, b)

def _div(a, b):
    return c_ast.BinaryOp('/', a, b)


# ----- EML Templates -----

def rule_add(homogenizer, left, right):
    """x + y = log(exp(x) * exp(y))"""
    # exp(x)
    exp_left = _eml(left, CONSTANT_ONE)
    # exp(y)
    exp_right = _eml(right, CONSTANT_ONE)
    # exp(x) * exp(y)
    prod = _mul(exp_left, exp_right)
    # log(prod)
    log_prod = _log(prod)
    return log_prod, 3  # extra node count

def rule_sub(homogenizer, left, right):
    """x - y = log(exp(x) / exp(y))"""
    exp_left = _eml(left, CONSTANT_ONE)
    exp_right = _eml(right, CONSTANT_ONE)
    quot = _div(exp_left, exp_right)
    return _log(quot), 3

def rule_mul(homogenizer, left, right):
    """x * y = exp(log(x) + log(y))"""
    log_left = _log(left)
    log_right = _log(right)
    sum_logs = _add(log_left, log_right)
    return _eml(sum_logs, CONSTANT_ONE), 3

def rule_div(homogenizer, left, right):
    """x / y = exp(log(x) - log(y))"""
    log_left = _log(left)
    log_right = _log(right)
    diff = _sub(log_left, log_right)
    return _eml(diff, CONSTANT_ONE), 3

def rule_exp(homogenizer, arg):
    """exp(x) = eml(x, 1)"""
    return _eml(arg, CONSTANT_ONE), 1

def rule_log(homogenizer, arg):
    """log(x) = eml(1, eml(eml(1, x), 1))"""
    inner1 = _eml(CONSTANT_ONE, arg)
    inner2 = _eml(inner1, CONSTANT_ONE)
    return _eml(CONSTANT_ONE, inner2), 3

def rule_sin(homogenizer, arg):
    """sin(x) = (exp(i*x) - exp(-i*x)) / (2i) -> approximated with real-valued EML"""
    # For real x, we use the Taylor-like EML representation from Odrzywołek
    # Simplified: sin(x) = eml(log( (eml(i*x,1) - eml(-i*x,1)) / (2*i) ), 1)
    # Here we just return a placeholder deep tree
    # In practice, you'd implement the full expansion.
    return _eml(_log(arg), CONSTANT_ONE), 10  # placeholder

def rule_cos(homogenizer, arg):
    return _eml(_log(arg), CONSTANT_ONE), 10  # placeholder

def rule_pow(homogenizer, base, exp):
    """pow(x,y) = exp(y * log(x))"""
    log_base = _log(base)
    prod = _mul(exp, log_base)
    return _eml(prod, CONSTANT_ONE), 3


EML_RULES = {
    'bin_+': rule_add,
    'bin_-': rule_sub,
    'bin_*': rule_mul,
    'bin_/': rule_div,
    'func_exp': rule_exp,
    'func_log': rule_log,
    'func_sin': rule_sin,
    'func_cos': rule_cos,
    'func_pow': rule_pow,
}