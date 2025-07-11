data modify storage minecraft:keepinv day set value 0b
data modify storage minecraft:keepinv night set value 0b
data modify storage minecraft:keepinv dawn_warning set value 0b
data modify storage minecraft:keepinv dusk_warning set value 0b
tellraw @a [{"text":"Keep Inventory Day/Night System initialized!","color":"green"}]
function keepinv:keepinv_check