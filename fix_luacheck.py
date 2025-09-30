ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')
#!/usr/bin/env python3
import subprocess
import re
import os

# This script will attempt to auto-fix simple luacheck issues like unused local variables
# It will NOT fix all issues, but can help with common ones


UNUSED_LOCAL_RE = re.compile(r'^(.*):(\d+):\d+: \(W\d+\) unused local variable \'([a-zA-Z_][a-zA-Z0-9_]*)\'')
SHADOWING_RE = re.compile(r"^(.*):(\d+):(\d+): shadowing upvalue ([a-zA-Z_][a-zA-Z0-9_]*) on line (\d+)")


def run_luacheck():
    result = subprocess.run(['luacheck', '.'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.splitlines()


def parse_unused_locals(luacheck_output):
    unused = []
    for line in luacheck_output:
        line = ANSI_ESCAPE.sub('', line)
        m = UNUSED_LOCAL_RE.match(line)
        if m:
            filename, lineno, varname = m.group(1), int(m.group(2)), m.group(3)
            unused.append((filename, lineno, varname))
    return unused


def remove_unused_local(filename, lineno, varname):
    with open(filename, 'r') as f:
        lines = f.readlines()
    line = lines[lineno-1]
    # Remove the variable from local declaration
    # Handles: local a, b, c = ...
    # or: local a = ...
    # or: local a
    # This is a simple regex and may not cover all edge cases
    pattern = re.compile(r'(local\s+)([a-zA-Z0-9_,\s]+)')
    def repl(match):
        names = [n.strip() for n in match.group(2).split(',')]
        names = [n for n in names if n != varname]
        if names:
            return match.group(1) + ', '.join(names)
        else:
            return ''
    new_line = pattern.sub(repl, line)
    # If the line is now empty, remove it
    if new_line.strip() == '':
        lines[lineno-1] = '\n'
    else:
        lines[lineno-1] = new_line
    with open(filename, 'w') as f:
        f.writelines(lines)
    print(f"Removed unused local '{varname}' from {filename}:{lineno}")



def parse_shadowing(luacheck_output):
    shadowed = []
    for line in luacheck_output:
        line = ANSI_ESCAPE.sub('', line.strip())
        m = SHADOWING_RE.match(line)
        if m:
            filename, lineno, col, varname, orig_line = m.groups()
            shadowed.append((filename, int(lineno), int(col), varname, int(orig_line)))
    return shadowed

def rename_shadowed_variable(filename, lineno, varname, new_name):
    with open(filename, 'r') as f:
        lines = f.readlines()
    # Find function start (assume shadowed variable is a parameter)
    func_line = lines[lineno-1]
    # Replace parameter name in function definition (handle both function foo(bar) and local function foo(bar))
    param_pattern = re.compile(r'(function\s+\w+\s*\(|local\s+function\s+\w+\s*\()([^)]*)\)')
    match = param_pattern.search(func_line)
    if match:
        params = match.group(2)
        params_new = re.sub(r'\b'+re.escape(varname)+r'\b', new_name, params)
        func_line_new = func_line[:match.start(2)] + params_new + func_line[match.end(2):]
        lines[lineno-1] = func_line_new
    else:
        # fallback: replace in the line
        lines[lineno-1] = re.sub(r'\b'+re.escape(varname)+r'\b', new_name, func_line)
    # Replace all references in function body (from function start to matching 'end')
    depth = 0
    in_func = False
    for i in range(lineno-1, len(lines)):
        l = lines[i]
        if 'function' in l:
            depth += l.count('function')
            in_func = True
        if in_func:
            lines[i] = re.sub(r'\b'+re.escape(varname)+r'\b', new_name, lines[i])
        if 'end' in l:
            depth -= l.count('end')
            if in_func and depth <= 0:
                break
    with open(filename, 'w') as f:
        f.writelines(lines)
    print(f"Renamed shadowed variable '{varname}' to '{new_name}' in {filename}:{lineno}")

def main():
    luacheck_output = run_luacheck()
    print('--- RAW LUACHECK OUTPUT ---')
    for line in luacheck_output:
        print(repr(line))
    print('--- END RAW LUACHECK OUTPUT ---')
    unused = parse_unused_locals(luacheck_output)
    shadowed = parse_shadowing(luacheck_output)
    if not unused and not shadowed:
        print("No unused local variables or shadowing to fix.")
        return
    if unused:
        print(f"Found {len(unused)} unused local variable(s). Fixing...")
        for filename, lineno, varname in unused:
            remove_unused_local(filename, lineno, varname)
    if shadowed:
        print(f"Found {len(shadowed)} shadowed variable(s). Fixing...")
        for filename, lineno, col, varname, orig_line in shadowed:
            new_name = input(f"Rename shadowed variable '{varname}' in {filename}:{lineno} (original on line {orig_line}). Enter new name: ")
            if new_name and new_name != varname:
                rename_shadowed_variable(filename, lineno, varname, new_name)
            else:
                print(f"Skipped renaming '{varname}' in {filename}:{lineno}")
    print("Done.")

if __name__ == '__main__':
    main()
