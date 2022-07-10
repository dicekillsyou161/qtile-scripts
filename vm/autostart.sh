#!/bin/sh

./.screenlayout/default.sh
# screen -d -m flameshot #Don't need this with using the alacritty floating terminals now so easily
screen -d -m yakuake
screen -d -m volumeicon
wal -R                                                                                #set the last used theme settings from pywal's cache

current_wallpaper=$(</home/zorthesosen/.config/qtile/themes/current_theme_wallpaper)  #Read the path of the last loaded wallpaper into a variable
feh --bg-fill $current_wallpaper                                                      #re-set the wallpaper after a reboot

picom -b                                                      #use picom for fancy UI elements (such as transparency)
