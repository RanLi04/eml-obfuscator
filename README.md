[# EML Obfuscator: Operator Homogenization Prototype

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository contains the prototype implementation of **Operator Homogenization** using the Exp-Minus-Log (EML) operator. The tool transforms C expressions into pure EML trees, eliminating operator-type diversity for obfuscation purposes.

**Paper:** *"Operator Homogenization via the Exp–Minus–Log (EML) Function: Increasing Analysis Costs through Representation Uniformity"*
- **Transcendental approximations:** The current prototype uses abbreviated EML encodings for `sin` and `cos` to limit tree explosion. Full expansions are derived in Odrzywołek (2026) and can be substituted for production use.

## 📁 Repository Structure

├── src/ # Core compiler and metrics
│ ├── eml_compiler.py # Main transformation engine
│ ├── eml_rules.py # EML encoding templates
│ ├── ast_metrics.py # OOR/DEF calculation
│ └── utils.py # Helper functions
├── tests/ # Test cases (C source)
│ ├── test_expressions.c
│ ├── test_crypto.c
│ └── test_anticheat.c
├── eval/ # Evaluation scripts
│ ├── run_yara.py # YARA signature elimination
│ ├── run_angr.py # angr symbolic execution
│ └── yara_rules/ # Custom YARA rules
├── examples/ # Quick-start examples
└── output/ # Generated homogenized code

## 🚀 Quick Start

### 1. Clone and Install
```bash
git clone https://github.com/RanLi04/eml-obfuscator
cd eml-obfuscator
pip install -r requirements.txt](https://github.com/RanLi04/eml-obfuscator)
