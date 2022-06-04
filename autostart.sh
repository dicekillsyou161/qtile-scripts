#!/bin/sh

./.screenlayout/default.sh
#screen -d -m ff
screen -d -m flameshot
screen -d -m yakuake
screen -d -m volumeicon
wal -R

screen -d -m feh --bg-fill Pictures/MDN-MDC-1312-v2.jpg
#screen -d -m dc
#xscreensaver-command --restart
#xscreensaver -nosplash
