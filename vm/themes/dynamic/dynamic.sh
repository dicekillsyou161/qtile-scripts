#!/bin/bash

cp /home/zorthesosen/dynamic-theme-loader/theme.jpg /home/zorthesosen/.config/qtile/themes/dynamic/dynamic-theme.jpg
cp /home/zorthesosen/dynamic-theme-loader/wallpaper.jpg /home/zorthesosen/.config/qtile/themes/dynamic/dynamic-wallpaper.jpg

wal -i /home/zorthesosen/.config/qtile/themes/dynamic/dynamic-theme.jpg
screen -d -m feh --bg-fill /home/zorthesosen/.config/qtile/themes/dynamic/dynamic-wallpaper.jpg
