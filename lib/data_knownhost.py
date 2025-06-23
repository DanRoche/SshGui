#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
######################################################
# Ssh Gui -- DATA -- KnownHosts
#
# dan.y.roche@gmail.com
#
# 202505  initial version
######################################################x
"""

# -------------------------
# std import 

import os
import glob
import pathlib
import subprocess

# -------------------------
# app import 
import lib.data_main as datamain

# -------------------------
#

class KnownHostsData(datamain.MainData):

    def __init__(self):

        super().__init__()
        

    def getKnownHost(self, name):

        command = "ssh-keygen -l -F {} -v -f {}/.ssh/known_hosts".format(name,self.topdir)
        ret = subprocess.run(command,capture_output=True, text=True, shell=True)
        data = ret.stdout
        if data == "":
            return(None)

        namlen= len(name)
        khdata = []
        lines = data.splitlines()
        curkh = {}
        for line in lines:
            if line[0:6] == "# Host" :
                linumpos = line.find("found: line ")
                if linumpos != -1 :
                    curkh['line'] = line[linumpos+12:]
            elif line[0:namlen] == name:
                tmp1 = line.split(" ")
                curkh['name'] = tmp1[0]
                curkh['type'] = tmp1[1]
                curkh['fingerprint'] = tmp1[2]
            elif line == "+----[SHA256]-----+":
                khdata.append(curkh)
                curkh = {}
            elif line[0:2] == "+-":
                p1=line.find("[")
                p2=line.find("]")
                tmp2 = line[p1+1:p2]
                tmp3 = tmp2.split(" ")
                curkh['typesize'] = tmp3[1]

        return(khdata)
                    
    def removeKnownHost(self, name):

        command = "ssh-keygen -R {} -f {}/.ssh/known_hosts".format(name,self.topdir)
        ret = subprocess.run(command,capture_output=True, text=True, shell=True)
        # ignore the output ?


    ##########################################################################
    #
    #  REINIT STUFF
    #
    #
    
    def reset(self, newtopdir):
        self.topdir = newtopdir
        
