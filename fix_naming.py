#!/usr/bin/env python3
import re
import os
import sys

SNAKE_CASE = re.compile(r'^[a-z_][a-z0-9_]*$')
def_patterns = [
    re.compile(r'local\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*='),
    re.compile(r'local\s+function\s+([a-zA-Z_][a-zA-Z0-9_]*)'),
    re.compile(r'function\s+([a-zA-Z_][a-zA-Z0-9_\.]*)'),
]

def to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()

def find_warnings(filename):
    warnings = []
    with open(filename, 'r') as f:
        for lineno, line in enumerate(f, 1):
            for pat in def_patterns:
                for match in pat.finditer(line):
                    name = match.group(1)
                    if '.' in name:
                        continue
                    if not SNAKE_CASE.match(name):
                        warnings.append((filename, lineno, name))
    return warnings


def fix_workspace(renames):
    # renames: dict of old_name -> new_name
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.lua'):
                filename = os.path.join(root, file)
                with open(filename, 'r') as f:
                    lines = f.readlines()
                changed = False
                for i, line in enumerate(lines):
                    orig = line
                    for old_name, new_name in renames.items():
                        line = re.sub(r'\b'+re.escape(old_name)+r'\b', new_name, line)
                    if line != orig:
                        changed = True
                    lines[i] = line
                if changed:
                    with open(filename, 'w') as f:
                        f.writelines(lines)
                    print(f"Updated references in {filename}")

def main():
    all_warnings = []
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.lua'):
                all_warnings.extend(find_warnings(os.path.join(root, file)))
    if not all_warnings:
        print("No naming warnings to fix.")
        return
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    renames = {}
    if mode == 'all':
        for filename, lineno, name in all_warnings:
            new_name = to_snake_case(name)
            renames[name] = new_name
    elif mode == 'one':
        for filename, lineno, name in all_warnings:
            new_name = to_snake_case(name)
            ans = input(f"Fix {filename}:{lineno} '{name}' to '{new_name}'? (y = fix / n = skip): ")
            if ans.lower().startswith('y'):
                renames[name] = new_name
            else:
                print(f"Skipped {filename}:{lineno} '{name}'")
    else:
        print("Unknown mode. Use 'all' or 'one'.")
        return
    if renames:
        fix_workspace(renames)
        print(f"Fixed {len(renames)} name(s) across workspace.")

if __name__ == '__main__':
    main()
