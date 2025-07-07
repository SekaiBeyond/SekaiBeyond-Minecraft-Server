scoreboard objectives remove time_check
scoreboard objectives add time_check dummy
execute store result score #global time_check run time query daytime
execute if score #global time_check matches 0..12000 unless data storage minecraft:keepinv {day:1b} run function keepinv:enable_keepinv
execute if score #global time_check matches 12001..23999 unless data storage minecraft:keepinv {night:1b} run function keepinv:disable_keepinv
schedule function keepinv:keepinv_check 100t replace