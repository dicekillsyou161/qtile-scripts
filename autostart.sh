#!/bin/sh

./.screenlayout/default.sh
screen -d -m flameshot
screen -d -m yakuake
screen -d -m volumeicon
wal -R

current_wallpaper=$(</home/zorthesosen/.config/qtile/themes/current_theme_wallpaper)
feh --bg-fill $current_wallpaper

picom --experimental-backends -b
