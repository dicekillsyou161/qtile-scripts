#!/bin/sh

./.screenlayout/default.sh
#screen -d -m ff
screen -d -m flameshot
screen -d -m yakuake
screen -d -m volumeicon
wal -R

feh --bg-fill .config/qtile/themes/cyangenta/MDN-MDC-1312-v2.jpg
#screen -d -m dc
#xscreensaver-command --restart
#xscreensaver -nosplash

picom --experimental-backends -b
