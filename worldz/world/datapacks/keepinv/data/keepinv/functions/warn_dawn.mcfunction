tellraw @a [{"text":"Warning: ","color":"gold","bold":true},{"text":"Dawn approaches! Keep Inventory will be ","color":"yellow"},{"text":"ENABLED","color":"green","bold":true},{"text":" in 1 minute.","color":"yellow"}]
data modify storage minecraft:keepinv dawn_warning set value 1b
data modify storage minecraft:keepinv dusk_warning set value 0b
schedule function keepinv:enable_keepinv 1200t replace
