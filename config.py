import os
import re
import json
import socket
import subprocess

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
from subprocess import call

## Utils


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

mod = "mod4"
terminal = "/usr/bin/kitty"  #guess_terminal()
file_Manager = "/usr/bin/nemo" # or what ever your file manager or app
notifier = Notifier()

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # [Custom]
    Key([mod, "shift"], "f", lazy.spawn(file_Manager), desc="Launch Nemo File Manager"),
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
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
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    Key([mod], "Print", lazy.spawn("scrot -e 'mv $f /home/zorthesosen/Pictures/screenshots/'")),
]

# Changing the workspace names
groups = [
          Group('im', init=False, persist=False,
          matches=[Match(wm_instance_class=['im'])],
          position=2, exclusive=True),
          
          # Terminals
          Group("CLI", exclusive=True,
          matches=[Match(wm_class=['kitty', 'alacritty'])],
          position=1,layout='plasma'
          ),
          
          # Next groups do not autostart, and only launch if the rule matches
     	  Group('GFX', persist=False, init=False, layout='treetab',
          matches=[Match(wm_class=['gimp'])]
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
    Rule(Match(title=['nested', 'gscreenshot'],
               wm_class=['Guake.py', 'Exe', 'Onboard', 'Florence',
                         'Plugin-container', 'Terminal', 'Gpaint',
                         'Kolourpaint', 'Wrapper', 'Gcr-prompter',
                         'Ghost', 'feh', 'Gnuplot', 'Pinta'],
               ),
         float=True, intrusive=True),
    ]

##commented out old group name and enumeration arguments
#def init_groups():
#    return [Group(name, **kwargs) for name, kwargs in group_names]

#if __name__ in ["config", "__main__"]:
#    group_names = init_group_names()
#    groups = init_groups()

# Allow MODKEY+[0 through 9] to bind to groups, see https://docs.qtile.org/en/stable/manual/config/groups.html
# MOD4 + index Number : Switch to Group[index]
# MOD4 + shift + index Number : Send active window to another Group
from libqtile.dgroups import simple_key_binder
dgroups_key_binder = simple_key_binder("mod4")

##commented out old group keybind arguments
#for i, (name, kwargs) in enumerate(group_names, 1):
#    keys.append(Key([mod], str(i), lazy.group[name].toscreen()))	#switch to another group
#    keys.append(Key([mod, "shift"], str(i), lazy.window.togroup(name)))	#send current window to another group

layouts = [
    layout.TreeTab(),
    layout.Columns(border_focus_stack=["#d75f5f", "#8f3d3d"], border_width=4),
    layout.Max(),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=4),
    # layout.Bsp(),
    layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    layout.VerticalTile(),
    layout.Zoomy(),
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

screens = [
    Screen(
        top=bar.Bar(
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
                # widget.GlobalMenu(),
                widget.CapsNumLockIndicator(foreground="#9803fc"),
                widget.TextBox("net:", foreground="#03f4fc"),
                widget.NetGraph(),
                widget.TextBox("ACAB", foreground="#ff0000"),
                # widget.TextBox("Press &lt;M-r&gt; to spawn", foreground="#d75f5f"),
                widget.Systray(),
                widget.Clock(format="%Y-%m-%d %a %H:%M"),
                widget.TextBox("CPU:", foreground="#03f4fc"),
                widget.CPUGraph(),
                widget.ThermalSensor(),
                widget.QuickExit(),
                #PowerlineTextBox(update_interval=2, side='left'),
                #Spacer(),
                #PowerlineTextBox(update_interval=2, side='right'),
            ],
            32,
            # border_width=[2, 0, 2, 0],  # Draw top and bottom borders
            # border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
        ),
    ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_app_rules = []  # type: list
follow_mouse_focus = False #don't have the cursor just follow wherever the mouse is, this is a fucking nightmare with multiple monitors, just typing shit all over the place. Fuck.
bring_front_click = True # Click into a window to change focus
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
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
