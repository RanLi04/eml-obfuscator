#!/usr/bin/env python3
"""
Evaluate signature elimination using YARA.
Compiles baseline and homogenized binaries, runs YARA rules.
"""

import os
import subprocess
import sys
import yara

def compile_c(source_file: str, output_bin: str, defines: list = None) -> None:
    """Compile C source to binary with gcc."""
    cmd = ["gcc", "-O0", "-o", output_bin, source_file, "-lm"]
    if defines:
        for d in defines:
            cmd.insert(1, f"-D{d}")
    subprocess.run(cmd, check=True)

def load_yara_rules(rules_dir: str) -> dict:
    """Load all .yar files from directory."""
    rules = {}
    for fname in os.listdir(rules_dir):
        if fname.endswith('.yar'):
            path = os.path.join(rules_dir, fname)
            rules[fname] = yara.compile(filepath=path)
    return rules

def scan_binary(binary_path: str, rules: dict) -> dict:
    """Return dict of rule_name -> match_count."""
    matches = {}
    for name, rule in rules.items():
        m = rule.match(binary_path)
        matches[name] = len(m) > 0
    return matches

def main():
    if len(sys.argv) < 3:
        print("Usage: python run_yara.py --baseline <src> --homogenized <src>")
        sys.exit(1)
    
    baseline_src = sys.argv[2]
    homogenized_src = sys.argv[4]
    
    # Compile
    compile_c(baseline_src, "baseline.bin")
    compile_c(homogenized_src, "homogenized.bin")
    
    # Load rules
    rules_dir = os.path.join(os.path.dirname(__file__), "yara_rules")
    rules = load_yara_rules(rules_dir)
    
    # Scan
    base_matches = scan_binary("baseline.bin", rules)
    eml_matches = scan_binary("homogenized.bin", rules)
    
    print("Rule\t\t\tBaseline\tHomogenized")
    for rule_name in rules:
        b = "✓" if base_matches[rule_name] else "✗"
        e = "✓" if eml_matches[rule_name] else "✗"
        print(f"{rule_name}\t{b}\t\t{e}")

if __name__ == "__main__":
    main()