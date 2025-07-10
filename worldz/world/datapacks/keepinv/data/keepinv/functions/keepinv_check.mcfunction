scoreboard objectives remove time_check
scoreboard objectives add time_check dummy
execute store result score #global time_check run time query daytime

# Check for 1-minute warnings (1200 ticks before transition)
# Warning for dawn (1 minute before day starts at tick 0) - so at tick 22799
execute if score #global time_check matches 22799..23799 unless data storage minecraft:keepinv {dawn_warning:1b} run function keepinv:warn_dawn

# Warning for dusk (1 minute before night starts at tick 23) - so at tick 11342  
execute if score #global time_check matches 11342..12342 unless data storage minecraft:keepinv {dusk_warning:1b} run function keepinv:warn_dusk

# Enable keep inventory at dawn (tick 0-12541) if not already enabled and no pending warning
execute if score #global time_check matches 0..12541 unless data storage minecraft:keepinv {day:1b} run function keepinv:enable_keepinv

# Disable keep inventory at dusk (tick 12542-23999) if not already disabled and no pending warning
execute if score #global time_check matches 12542..23999 unless data storage minecraft:keepinv {night:1b} run function keepinv:disable_keepinv

schedule function keepinv:keepinv_check 20t replace