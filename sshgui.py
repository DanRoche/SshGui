#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
######################################################
# Ssh Gui = GUI for managing  ~/.ssh
#
# dan.y.roche@gmail.com
#
# 202502  initial version
# 202503  gui separation
######################################################
"""

# -------------------------
# std import 

import os
import sys

# -------------------------
# app import 

import lib.gui_main as guimain

# -------------------------
# main

appgui = guimain.MainGui()

# ---- forever loop
appgui.loop()

