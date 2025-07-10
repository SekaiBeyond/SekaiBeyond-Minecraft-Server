tellraw @a [{"text":"Warning: ","color":"gold","bold":true},{"text":"Dusk approaches! Keep Inventory will be ","color":"orange"},{"text":"DISABLED","color":"red","bold":true},{"text":" in 1 minute.","color":"orange"}]
data modify storage minecraft:keepinv dusk_warning set value 1b
data modify storage minecraft:keepinv dawn_warning set value 0b
schedule function keepinv:disable_keepinv 1200t replace
