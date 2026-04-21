#!/usr/bin/env python3
"""
Measure symbolic execution slowdown with angr.
"""

import angr
import time
import sys

def symbolic_exec_time(binary_path: str, target_func: str = "check") -> float:
    """Return time (seconds) for angr to explore all paths to target_func."""
    proj = angr.Project(binary_path, auto_load_libs=False)
    state = proj.factory.entry_state()
    simgr = proj.factory.simulation_manager(state)
    
    start = time.time()
    # Run until no active states or max steps
    simgr.run(until=lambda s: len(s.active) == 0, n=1000)
    end = time.time()
    return end - start

def main():
    if len(sys.argv) < 5:
        print("Usage: python run_angr.py --baseline <bin> --homogenized <bin>")
        sys.exit(1)
    
    base_bin = sys.argv[2]
    eml_bin = sys.argv[4]
    
    t_base = symbolic_exec_time(base_bin)
    t_eml = symbolic_exec_time(eml_bin)
    
    print(f"Baseline time: {t_base:.2f}s")
    print(f"EML time:      {t_eml:.2f}s")
    print(f"Slowdown:      {t_eml/t_base:.1f}x")

if __name__ == "__main__":
    main()