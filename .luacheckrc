-- .luacheckrc
-- LuaCheck configuration file for best practice naming conventions

std = "lua51"

-- Ignore the global 'print' and 'table' as they are standard
ignore = {"print", "table"}

-- Enable all warnings
all = true

-- Naming convention: warn if variable or function names are not snake_case
-- Note: As of now, luacheck does not natively support naming convention enforcement.
-- This section is for documentation and future use if luacheck adds this feature.

-- You can use 'globals' and 'read_globals' to control allowed global names

-- Example:
-- globals = {"my_global_var"}
-- read_globals = {"my_readonly_global"}

-- For stricter checks, consider using an additional linter or custom scripts.
