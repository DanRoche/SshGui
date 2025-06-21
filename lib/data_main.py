#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
######################################################
# Ssh Gui -- DATA -- Main
#
# dan.y.roche@gmail.com
#
# 202502  initial version
# 202503  data separation
######################################################x
"""

# -------------------------
# std import 

import os
import glob
import pathlib
import subprocess
import tempfile

# -------------------------
# app import 

# -------------------------
#

class MainData:

    def __init__(self):

        self.homedir = str(pathlib.Path.home())
        self.topdir = self.homedir      # true at init

       
    def parseFingerprintKeygenOutput(self, str):

        pos1 = str.find("(")
        sub1 = str[0:pos1-1]
        sub2 = str[pos1:].strip("()")
        part = sub1.split(" ")
        elem = {}
        elem['size'] = part[0]
        del(part[0])
        elem['fingerprint'] = part[0]
        del(part[0])
        remain = " ".join(part)
        if remain[0:8] == "command=":
            # case of no comment
            elem['comment'] = ""
        else:
            elem['comment'] = remain
        elem['type'] = sub2

        return(elem)

    def launchInTerminal(self, confnam):
        if os.path.isfile("/bin/gnome-terminal"):
            command="gnome-terminal -- ssh {}".format(confnam)
        elif os.path.isfile("/bin/xcfe4-terminal"):
            command="xfce4-terminal -e \"ssh {}\"".format(confnam)
        elif os.path.isfile("/bin/xterm"):
            command="xterm -e \"ssh {}\"".format(confnam)
        else:
            print("no terminal found !")
            return
        subprocess.run(command,capture_output=False, text=True, shell=True)


    def switch(self, name):
        self.cleanRemoteCache()

        curu = self.getCurrentUser()
        if name == curu:
            # back to homedir
            self.topdir = self.homedir

        else:
            # fetch remote ssh conf
            tmpdir = tempfile.mkdtemp(prefix="sshgui_")
            cmd = "rsync -a {}:~/.ssh {}".format(name, tmpdir)
            subprocess.run(cmd,capture_output=False, text=True, shell=True)
            self.currentUser = name
            self.topdir = tmpdir

        return(self.topdir)

    def cleanRemoteCache(self):
        if self.topdir != self.homedir:
            # remove previous topdir if not home
            cmd = "rm -rf {}".format(self.topdir)
            subprocess.run(cmd,capture_output=False, text=True, shell=True)


    def uploadRemoteCache(self):
        if self.topdir != self.homedir:
            cmd = "rsync -a {}/.ssh {}:~".format(self.topdir, self.currentUser)
            subprocess.run(cmd,capture_output=False, text=True, shell=True)


    def getHelp(self):
        with open("doc/help.txt", "r") as fd:
            help = fd.read()
            fd.close()
        return(help)

    def getCurrentUser(self):
        user = os.getlogin()
        host = 'localhost'    # hardcoded for now
        full = "{}@{}".format(user,host)
        return(full)
