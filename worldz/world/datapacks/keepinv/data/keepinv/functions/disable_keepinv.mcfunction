gamerule keepInventory false
tellraw @a [{"text":"Night falls! ","color":"dark_blue"},{"text":"Keep Inventory is now ","color":"white"},{"text":"DISABLED","color":"red","bold":true}]
data modify storage minecraft:keepinv day set value 0b
data modify storage minecraft:keepinv night set value 1b