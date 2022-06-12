#  Set up the bars and widgets


import os
import re
import json
import socket
import subprocess
import time

from libqtile import qtile
from libqtile import bar, layout, widget, hook
from libqtile.config import Click, Drag, Group, Key, Match, Screen, EzKey, Rule
from libqtile.lazy import lazy
from libqtile.widget import Spacer
from subprocess import call, check_output
from platforms import num_screens, hostname

## Utils

class Commands:
    update = 'sudo pacman -Syu'
    def get_kernel_release(self):
        return check_output(['uname', '-r']).decode("utf-8").replace("\n", "")

    def get_uptime(self):
        return check_output(['uptime', '-p']).decode("utf-8").replace("\n", "")

commands = Commands() 


top_primary=bar.Bar(
    [
        widget.CurrentLayout(),
        widget.GroupBox(),
        widget.Prompt(),
        widget.WindowName(),
        widget.Chord(
            chords_colors={
                "launch": ("#ff0000", "#ffffff"),
            },
            name_transform=lambda name: name.upper(),
        ),
        widget.TextBox("ACAB", foreground="#ff0000"),
        widget.Systray(),
        widget.Clock(format="%Y-%m-%d %a %H:%M"),
        widget.CheckUpdates(
           update_interval = 30,
           distro='Arch',
           display_format='{updates} Updates',
           colour_no_update=["00ff00"],
           colour_have_updates=["ff0000"],
           mouse_callbacks = {'Button1': lambda: qtile.cmd_spawn(myTerm + 'sudo pacman -Syu')},
           # execute=commands.update
        ),
        widget.QuickExit(),
      ],
      26,
      border_width=[0, 0, 1, 0],  # Draw top and bottom borders
      border_color=["000000", "000000", "ff9ff9", "000000"]  # Borders are magenta
  ),
bottom_primary=bar.Bar(
   [
        widget.CapsNumLockIndicator(foreground="#9803fc"),
        widget.TextBox(text=commands.get_kernel_release(), foreground=["#03f4fc"]),
        widget.GenPollText(
            func=commands.get_uptime,
            update_interval=60,
            foreground=["#ff9ff9"]
            ),
        widget.TextBox(" mem:", foreground="#03f4fc"),               
        widget.MemoryGraph(
            #line_width=1,
            #border_width=1,
            #width=4,
            #type='box',
            graph_color=["#ff57f7"],
            fill_color=["#ff57f7"]
            ),
        widget.TextBox(" CPU:", foreground="#03f4fc"),
        widget.CPUGraph(
            graph_color=["#ff57f7"],
            fill_color=["#ff57f7"]
            ),
        widget.ThermalSensor(),
        widget.TextBox(" net:", foreground="#03f4fc"),
        widget.NetGraph(
            graph_color=["#ff57f7"],
            fill_color=["#ff57f7"]
            ),
      ],
      24,
      border_width=[1, 0, 0, 0],  # Draw top borders
      border_color=["bd92bb", "000000", "000000", "000000"]  # Borders are pink/grey
  ),
