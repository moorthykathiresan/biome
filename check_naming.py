#!/usr/bin/env python3
import re
import sys
import os

SNAKE_CASE = re.compile(r'^[a-z_][a-z0-9_]*$')

# Patterns to match local variable and function definitions
def_patterns = [
    re.compile(r'local\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*='),  # local var =
    re.compile(r'local\s+function\s+([a-zA-Z_][a-zA-Z0-9_]*)'),  # local function name
    re.compile(r'function\s+([a-zA-Z_][a-zA-Z0-9_\.]*)'),  # function name
]


def check_file(filename, warnings):
    with open(filename, 'r') as f:
        for lineno, line in enumerate(f, 1):
            for pat in def_patterns:
                for match in pat.finditer(line):
                    name = match.group(1)
                    # Ignore module.function style
                    if '.' in name:
                        continue
                    if not SNAKE_CASE.match(name):
                        print(f"{filename}:{lineno}: warning: '{name}' is not snake_case")
                        warnings.append((filename, lineno, name))


def main():
    warnings = []
    file_count = 0
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.lua'):
                file_count += 1
                check_file(os.path.join(root, file), warnings)
    print("\nNaming convention Linting Summary")
    print(f"Total: {len(warnings)} warning(s) / 0 errors in {file_count} file(s)\n")

if __name__ == '__main__':
    main()
