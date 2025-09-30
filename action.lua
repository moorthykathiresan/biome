local minerals = {"Wood", "Stone", "Iron", "Crystal"}

local function print_minerals(minerals)
    for i = 1, #minerals do
        print("Collected: " .. minerals[i])
    end
end



local add_minerals = function (...)
    local args = {...}
    for i = 1, #args do
        table.insert(minerals, args[i])
    end
end

print_minerals(minerals)


add_minerals("Gold", "Silver")

print("After adding Gold:")
print_minerals(minerals)