#!/usr/bin/env python3
"""
Quick example of homogenizing a polynomial expression.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.eml_compiler import homogenize_expression

def main():
    expr = "x*x + 2*x + 1"
    code, metrics = homogenize_expression(expr, "x")
    
    print("Original expression:", expr)
    print("\n--- Homogenized C Code ---")
    print(code)
    print("\n--- Metrics ---")
    print(f"OOR: {metrics['OOR']:.2f}")
    print(f"DEF: {metrics['DEF']:.2f}")
    print(f"Original nodes: {metrics['orig_nodes']}, EML nodes: {metrics['eml_nodes']}")
    print(f"Original depth: {metrics['orig_depth']}, EML depth: {metrics['eml_depth']}")

if __name__ == "__main__":
    main()