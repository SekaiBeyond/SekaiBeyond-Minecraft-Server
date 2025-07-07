gamerule keepInventory true
tellraw @a [{"text":"Dawn breaks! ","color":"yellow"},{"text":"Keep Inventory is now ","color":"white"},{"text":"ENABLED","color":"green","bold":true}]
data modify storage minecraft:keepinv day set value 1b
data modify storage minecraft:keepinv night set value 0b