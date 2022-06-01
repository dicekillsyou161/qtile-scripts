#!/usr/bin/env python
# coding=utf-8

import os
import subprocess

from os import system
from subprocess import call, check_output

prim_disp = str("")
class primary_disp:

    def __init__(self):
        self.prim_disp = prim_disp

    def get_prim_disp(self):
        prim_disp = str(check_output(["primary_display"]).decode("utf-8").replace("\n",""))
        prim_disp = str(prim_disp[0:4])
        return prim_disp

primary_disp = primary_disp()
