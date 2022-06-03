import os
import re
import json
import socket
import subprocess
import time
import struct
import fcntl
import psutil
import therm_widget
import iwlib
import primary_display
#import internet_widget

from plasma import Plasma
from qtile_extras.widget import GlobalMenu, WiFiIcon
from libqtile import qtile
from libqtile import bar, layout, widget, hook
from libqtile.config import Click, Drag, Group, Key, Match, Screen, EzKey, Rule
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal
from libqtile.widget import Spacer
from floating_window_snapping import move_snap_window
from graphical_notifications import Notifier
from powerline.bindings.qtile.widget import PowerlineTextBox
from typing import List  # noqa: F401from typing import List  # noqa: F401
from subprocess import call, check_output
from capnum import CapNum
from platforms import num_screens, hostname
from therm_widget import ThermalSensorCC
from primary_display import primary_disp
#from internet_widget import Internet 

## Utils

class Commands:
    update = 'sudo pacman -Syu'
    # volume_up = '-e pactl -- set-sink-volume 0 +1%'
    # volume_down = 'pactl -- set-sink-volume 0 -1%'
    # mute = 'pactl -- set-sink-volume 0 0%'
    def get_kernel_release(self):
        return check_output(['uname', '-r']).decode("utf-8").replace("\n", "")

    def get_uptime(self):
        return check_output(['uptime', '-p']).decode("utf-8").replace("\n", "")
        
    def get_name(self):
        return check_output(['whoami']).decode("utf-8").replace("\n", "")
        
    def get_host(self):
        return check_output(['hostnamectl', 'hostname']).decode("utf-8").replace("\n", "")

#    def get_cpu_temp(self):
#        return str(int(''.join(filter(str.isdigit, check_output(["cputemp"]).decode("utf-8").replace("\n",""))))/10) + "C"



commands = Commands() 


def kill_all_windows_minus_current():
	@lazy.function
	def __inner(qtile):
		for window in qtile.current_group.windows:
			if window != qtile.current_window:
				window.kill()
	return __inner

def window_to_prev_group(qtile):
    if qtile.currentWindow is not None:
        i = qtile.groups.index(qtile.currentGroup)
        qtile.currentWindow.togroup(qtile.groups[i - 1].name)

def window_to_next_group(qtile):
    if qtile.currentWindow is not None:
        i = qtile.groups.index(qtile.currentGroup)
        qtile.currentWindow.togroup(qtile.groups[i + 1].name)

def window_to_previous_screen(qtile):
    i = qtile.screens.index(qtile.current_screen)
    if i != 0:
        group = qtile.screens[i - 1].group.name
        qtile.current_window.togroup(group)

def window_to_next_screen(qtile):
    i = qtile.screens.index(qtile.current_screen)
    if i + 1 != len(qtile.screens):
        group = qtile.screens[i + 1].group.name
        qtile.current_window.togroup(group)

def switch_screens(qtile):
    i = qtile.screens.index(qtile.current_screen)
    group = qtile.screens[i - 1].group
    qtile.current_screen.set_group(group)

def to_urgent(qtile):
    cg = qtile.currentGroup
    for group in qtile.groupMap.values():
        if group == cg:
            continue
        if len([w for w in group.windows if w.urgent]) > 0:
            qtile.currentScreen.setGroup(group)
            return


def switch_to(name):
    def callback(qtile):
        for window in qtile.windowMap.values():
            if window.group and window.match(wname=name):
                qtile.currentScreen.setGroup(window.group)
                window.group.focus(window, False)
                break
    return callback


class SwapGroup(object):
    def __init__(self, group):
        self.group = group
        self.last_group = None

    def group_by_name(self, groups, name):
        for group in groups:
            if group.name == name:
                return group

    def __call__(self, qtile):
        group = self.group_by_name(qtile.groups, self.group)
        cg = qtile.currentGroup
        if cg != group:
            qtile.currentScreen.setGroup(group)
            self.last_group = cg
        elif self.last_group:
            qtile.currentScreen.setGroup(self.last_group)

def open_calendar():
    qtile.cmd_spawn('gsimplecal next_month')

mod = "mod4"
alt = "mod1"
terminal = "/usr/bin/kitty"  #guess_terminal()
file_Manager = "/usr/bin/nemo" # or what ever your file manager or app
notifier = Notifier()

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # [Custom]
    Key([mod, "control"], "f", lazy.spawn(file_Manager), desc="Launch Nemo File Manager"),
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "j", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "l", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.move_left(), desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.move_right(), desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.move_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.move_up(), desc="Move window up"),
    Key([mod], "a", lazy.layout.grow_width(30)),
    Key([mod], "z", lazy.layout.grow_width(-30)),
    Key([mod], "s", lazy.layout.grow_height(30)),
    Key([mod], "x", lazy.layout.grow_height(-30)),
    Key([mod, "shift"], "c", lazy.layout.mode_horizontal_split()),
    Key([mod, "shift"], "v", lazy.layout.mode_vertical_split()),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod, "shift"], "w", lazy.window.kill(), desc="Kill focused window"),
    Key([mod, alt], "w", kill_all_windows_minus_current(), desc="Kill focused window except this one"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control", "shift"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    Key([mod], "Print", lazy.spawn("scrot -e 'mv $f /home/zorthesosen/Pictures/screenshots/'")),
    #Key([], "XF86AudioRaiseVolume", lazy.spawn('pactl -- set-sink-volume 0 +2%')), # commented out b/c functionality is being more successfully handled by autostarting the volumeicon tray helper app 
    #Key([], "XF86AudioLowerVolume", lazy.spawn('pactl -- set-sink-volume 0 -2%')),
    #Key([], "XF86AudioMute", lazy.spawn('pactl -- set-sink-volume 0 0%')), 
    Key([mod, alt], "1", lazy.spawn('pactl -- set-sink-volume 0 10%')),
    Key([mod, alt], "2", lazy.spawn('pactl -- set-sink-volume 0 20%')),
    Key([mod, alt], "3", lazy.spawn('pactl -- set-sink-volume 0 30%')),
    Key([mod, alt], "4", lazy.spawn('pactl -- set-sink-volume 0 40%')),
    Key([mod, alt], "5", lazy.spawn('pactl -- set-sink-volume 0 50%')),
    Key([mod, alt], "6", lazy.spawn('pactl -- set-sink-volume 0 60%')),
    Key([mod, alt], "7", lazy.spawn('pactl -- set-sink-volume 0 70%')),
    Key([mod, alt], "8", lazy.spawn('pactl -- set-sink-volume 0 80%')),
    Key([mod, alt], "9", lazy.spawn('pactl -- set-sink-volume 0 90%')),
    Key([mod, alt], "0", lazy.spawn('pactl -- set-sink-volume 0 0%')),


    ### Switch focus of monitors
    Key([mod], "period",
        lazy.next_screen(),
        desc='Move focus to next monitor'
    ),
    Key([mod], "comma",
        lazy.prev_screen(),
        desc='Move focus to prev monitor'
    ),
    Key([mod, "shift"], "f",
        lazy.window.toggle_floating(),
        desc='toggle floating'
    ),
    Key([mod, alt], "v",
        lazy.spawn("midori"),
        # lazy.spawn("xdg-open https://vim.rtorr.com"),
        time.sleep(2),
        lazy.window.toggle_floating(),
        # desc='toggle floating'
    ),
    Key([mod, "shift", "control"], "h",
        lazy.layout.shuffle_down(),
        lazy.layout.section_down(),
        desc='Move windows down in current stack'
    ),
    Key([mod, "shift", "control"], "j",
        lazy.layout.shuffle_up(),
        lazy.layout.section_up(),
        desc='Move windows up in current stack'
    ),
]

# Changing the workspace names
groups = [
          Group('im', init=False, persist=False,
          matches=[Match(wm_instance_class=['im'])],
          position=2, exclusive=True),
          
          # Terminals
          Group("CLI", exclusive=True,
          matches=[Match(wm_class=['kitty', 'alacritty', "midori"])],
          position=1,layout='plasma'
          ),
          
          # Next groups do not autostart, and only launch if the rule matches
     	  Group('GFX', persist=False, init=False, layout='treetab',
          matches=[Match(wm_class=['gimp', 'org.gimp.GIMP', 'GNU Image Manipulation Program', 'Gimp-2.10'])]
          ),
     	  
     	  # Max Groups
          # --------------
          Group('DISC', init=False, persist=False, exclusive=True, layout='max', matches=[
              Match(wm_class=['discord'])
              ], position=3),
          Group('WWW', init=False, persist=False, exclusive=True, layout='treetab', matches=[
              Match(wm_class=['chromium-browser', 'firefox'],
                    role=['browser'])
              ], position=4),
          Group('YT', init=False, persist=False, exclusive=True, layout='max', matches=[
              Match(wm_class=['chromium'])
              ], position=5),
          Group('STEAM', init=False, persist=False, layout='max', matches=[
              Match(wm_class=['steam'])
              ]),
          Group('AUD', init=False, persist=False, layout='treetab',
                matches=[Match(wm_class=['pulsemixer'])]
                ),
          Group('QEMU', init=False, persist=False,
                matches=[Match(wm_class=['virt-manager'])]
                ),

          # Misc Groups Persist
          Group("MISC1", layout='treetab'),
          Group("MISC2", layout='plasma')]
          
# dgroup rules that not belongs to any group
dgroups_app_rules = [
    # Everything i want to be float, but don't want to change group
    Rule(Match(title=['nested', 'gscreenshot', 'Vim Cheat Sheet', 'Gsimplecal'],
               wm_class=['Guake.py', 'Exe', 'Gsimplecal', 'Onboard', 'Florence',
                         'Plugin-container', 'Terminal', 'Gpaint',
                         'Kolourpaint', 'Wrapper', 'Gcr-prompter',
                         'Ghost', 'feh', 'Gnuplot', 'Pinta', 'Midori'],
               ),
         float=True, intrusive=True),
    ]

from libqtile.dgroups import simple_key_binder
dgroups_key_binder = simple_key_binder("mod4")


layouts = [
    layout.TreeTab(sections=["1312","ACAB","161","AFA"]),
    layout.Columns(border_focus_stack=["#d75f5f", "#8f3d3d"], border_width=4),
    layout.Max(),
    layout.VerticalTile(),
    layout.Floating(
        border_normal='#03f4f3',
        border_focus='#00e891',
        border_normal_fixed='#03f4f3',
        border_focus_fixed='#00e8dc',
        border_width=1,
        border_width_single=1,
        margin=1,
    ),
    Plasma(
        border_normal='#333333',
        border_focus='#00e891',
        border_normal_fixed='#006863',
        border_focus_fixed='#00e8dc',
        border_width=1,
        border_width_single=0,
        margin=0
    ),
]

widget_defaults = dict(
    font="sans",
    fontsize=16,
    padding=3,
)
extension_defaults = widget_defaults.copy()

colors = [["#282c34", "#282c34"], # panel background
          ["#3d3f4b", "#434758"], # background for current screen tab
          ["#ffffff", "#ffffff"], # font color for group names
          ["#ff5555", "#ff5555"], # border line color for current tab
          ["#74438f", "#74438f"], # border line color for 'other tabs' and color for 'odd widgets'
          ["#4f76c7", "#4f76c7"], # color for the 'even widgets'
          ["#e1acff", "#e1acff"], # window name
          ["#ecbbfb", "#ecbbfb"]] # backbround for inactive screens

if str(primary_disp.get_prim_disp()) == "Disp":
    screens = [
        Screen(
            top=bar.Bar(
                [
                    widget.CurrentLayout(foreground="#da69c6"),
                    widget.GroupBox(
                        active="03f4fc", 
                        disable_drag=True, 
                        inactive="004045",
                        this_current_screen_border="#da69d6",
                        this_screen_border="#da69d6",
                        fontsize=14,
                        spacing=5
                        ),
                    widget.Prompt(),
                    widget.WindowName(foreground="#da69c6"),
                    widget.Chord(
                        chords_colors={
                            "launch": ("#ff0000", "#ffffff"),
                            },
                        name_transform=lambda name: name.upper(),
                        ),
                    widget.TextBox(
                        "╱╱╱ ACAB", 
                        foreground="#03f4fc",
                        mouse_callbacks={
                            'Button1': lazy.spawn('acab'),
                            'Button3': lazy.spawn('acab')
                            }
                        ),
                    widget.Systray(),
                    widget.Clock(
                        format="%Y-%m-%d %a ", 
                        foreground="#822a8b",
                        mouse_callbacks={
                            'Button1': open_calendar,
                            'Button3': lazy.spawn('gsimplecal prev_month')
                            }
                        ),
                    widget.Clock(format="%H:%M:%S", foreground="#da69c6"),
                    #internet_widget.Internet(),
                    widget.CheckUpdates(
                        update_interval = 30,
                        distro='Arch',
                        display_format='{updates} Updates',
                        colour_no_update=["00ff00"],
                        colour_have_updates=["ff0000"],
                        mouse_callbacks = {'Button1': lazy.spawn(terminal + '-e sudo pacman -Syu')},
                        # execute=commands.update
                        ),
                    widget.QuickExit(foreground="#822a8b"),
                    ],
                26,
                border_width=[0, 0, 1, 0],  # Draw top and bottom borders
                border_color=["000000", "000000", "bd92bb", "000000"]  # Borders are magenta
            ),
        ),
    Screen(
            bottom=bar.Bar(
                [
                    widget.CapsNumLockIndicator(foreground="#ff9ff9"),
                    widget.Spacer(length=50),
                    widget.TextBox(text=commands.get_name(), foreground=["#ff00c3"]),
                    widget.TextBox("@", foreground="#cab7c9"),  
                    widget.TextBox(text=commands.get_host(), foreground=["#ff00c3"]),
                    widget.Spacer(length=275),
                    widget.TextBox(text=commands.get_kernel_release(), foreground=["#03f4fc"]),
                    widget.Spacer(length=25),
                    widget.GenPollText(
                        func=commands.get_uptime,
                        update_interval=60,
                        foreground=["#ff9ff9"]
                        ),
                    widget.Spacer(length=275),
                    widget.TextBox(" mem:", foreground="#03f4fc"),               
                    widget.MemoryGraph(
                        #line_width=1,
                        #border_width=1,
                        #width=4,
                        #type='box',
                        graph_color=["#ff57f7"],
                        fill_color=["#ff57f7"]
                        ),
                    widget.Spacer(length=15),
                    widget.TextBox(" CPU:", foreground="#03f4fc"),
                    widget.CPUGraph(
                        graph_color=["#ff57f7"],
                        fill_color=["#ff57f7"]
                        ),
                    therm_widget.ThermalSensorCC(),
                    widget.Spacer(length=15),
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
        ),
    ]
else:
    screens = [
        Screen(
            top=bar.Bar(
                [
                    widget.CurrentLayout(foreground="#da69c6"),
                    widget.GroupBox(
                        active="03f4fc", 
                        disable_drag=True, 
                        inactive="004045",
                        this_current_screen_border="#da69d6",
                        this_screen_border="#da69d6",
                        fontsize=14,
                        spacing=5
                        ),
                    widget.Prompt(),
                    widget.WindowName(foreground="#da69c6"),
                    widget.Chord(
                        chords_colors={
                            "launch": ("#ff0000", "#ffffff"),
                            },
                        name_transform=lambda name: name.upper(),
                        ),
                    widget.TextBox(
                        "╱╱╱ ACAB", 
                        foreground="#03f4fc",
                        mouse_callbacks={
                            'Button1': lazy.spawn('acab'),
                            'Button3': lazy.spawn('acab')
                            }
                        ),
                    widget.Systray(),
                    widget.Clock(
                        format="%Y-%m-%d %a ", 
                        foreground="#822a8b",
                        mouse_callbacks={
                            'Button1': open_calendar,
                            'Button3': lazy.spawn('gsimplecal prev_month')
                            }
                        ),
                    widget.Clock(format="%H:%M:%S", foreground="#da69c6"),
                    #widget.Internet(),
                    widget.CheckUpdates(
                        update_interval = 30,
                        distro='Arch',
                        display_format='{updates} Updates',
                        colour_no_update=["00ff00"],
                        colour_have_updates=["ff0000"],
                        mouse_callbacks = {'Button1': lazy.spawn(terminal + '-e sudo pacman -Syu')},
                        # execute=commands.update
                        ),
                    widget.QuickExit(foreground="#822a8b"),
                    ],
                26,
                border_width=[0, 0, 1, 0],  # Draw top and bottom borders
                border_color=["000000", "000000", "bd92bb", "000000"]  # Borders are magenta
            ),
            bottom=bar.Bar(
                [
                    widget.CapsNumLockIndicator(foreground="#ff9ff9"),
                    widget.Spacer(length=50),
                    widget.TextBox(text=commands.get_name(), foreground=["#ff00c3"]),
                    widget.TextBox("@", foreground="#cab7c9"),  
                    widget.TextBox(text=commands.get_host(), foreground=["#ff00c3"]),
                    widget.Spacer(length=275),
                    widget.TextBox(text=commands.get_kernel_release(), foreground=["#03f4fc"]),
                    widget.Spacer(length=25),
                    widget.GenPollText(
                        func=commands.get_uptime,
                        update_interval=60,
                        foreground=["#ff9ff9"]
                        ),
                    widget.Spacer(length=275),
                    widget.TextBox(" mem:", foreground="#03f4fc"),               
                    widget.MemoryGraph(
                        #line_width=1,
                        #border_width=1,
                        #width=4,
                        #type='box',
                        graph_color=["#ff57f7"],
                        fill_color=["#ff57f7"]
                        ),
                    widget.Spacer(length=15),
                    widget.TextBox(" CPU:", foreground="#03f4fc"),
                    widget.CPUGraph(
                        graph_color=["#ff57f7"],
                        fill_color=["#ff57f7"]
                        ),
                    therm_widget.ThermalSensorCC(),
                    widget.Spacer(length=15),
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
        ),
    ]

# Drag floating layouts.
mouse = [
        Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
        Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
        Click([mod], "Button2", lazy.window.bring_to_front()),
        ]

# dgroups_app_rules = []  # type: list
follow_mouse_focus = False #don't have the cursor just follow wherever the mouse is, this is a fucking nightmare with multiple monitors, just typing shit all over the place. Fuck.
bring_front_click = True # Click into a window to change focus
cursor_warp = False
floating_layout = layout.Floating(
        float_rules=[
            # Run the utility of `xprop` to see the wm class and name of an X client.
            *layout.Floating.default_float_rules,
            Match(wm_class="confirmreset"),  # gitk
            Match(wm_class="Gsimplecal"),
            Match(wm_class="makebranch"),  # gitk
            Match(wm_class="maketag"),  # gitk
            Match(wm_class="ssh-askpass"),  # ssh-askpass
            Match(title="branchdialog"),  # gitk
            Match(title="pinentry"),  # GPG key password entry
            ]
        )
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"

## Define hook to run a startup script on qtile startup
@hook.subscribe.startup_once
def autostart():
    home = os.path.expanduser('~/.config/qtile/autostart.sh')
    subprocess.run([home])
