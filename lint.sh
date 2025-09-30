#!/bin/bash
# Lint all Lua files in the current directory and subdirectories

find . -type f -name "*.lua" -print0 | xargs -0 luacheck
echo "--------------------------------------------------"

# Check naming conventions

python3 check_naming.py


echo "Would you like to fix luacheck unused local variable warnings automatically?"
read -p "Type 'y' to fix, or any other key to skip: " fixluacheck
if [ "$fixluacheck" = "y" ]; then
	python3 fix_luacheck.py
else
	echo "Skipping luacheck auto-fix."
fi

echo "Would you like to fix naming warnings?"
read -p "Type 'a' for All, 'i' for individually, or 's' to skip: " fixmode
if [ "$fixmode" = "a" ]; then
	python3 fix_naming.py all
elif [ "$fixmode" = "i" ]; then
	python3 fix_naming.py one
else
	echo "Skipping naming auto-fix."
fi
