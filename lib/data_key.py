#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
######################################################
# Ssh Gui -- DATA -- Keys
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

# -------------------------
# app import 
import lib.data_main as datamain

# -------------------------
#

class KeysData(datamain.MainData):

    def __init__(self):

        super().__init__()
        
        # key type and default values
        self.keyType = [
            {"type":"ed25519","label":"ED25519"},
            {"type":"ed25519-sk","label":"ED25519 with Yubikey"},
            {"type":"rsa","label":"RSA (to be used with old system)"},
            {"type":"ecdsa","label":"ECDSA (better not use this)"},
            {"type":"ecdsa-sk","label":"ECDSA with Yubikey (better not use this)"},
            {"type":"dsa","label":"DSA (better not use this)"}
            ]
        self.keyDefaultValues = {
            "ed25519": {"file":"id_ed25519","size":"-","sizmod":False},
            "ed25519-sk": {"file":"id_ed25519_sk","size":"-","sizmod":False},
            "rsa": {"file":"id_rsa","size":"3072","sizmod":True},
            "ecdsa": {"file":"id_ecdsa","size":"384","sizmod":True},
            "ecdsa-sk": {"file":"id_ecdsa_sk","size":"-","sizmod":False},
            "dsa": {"file":"id_dsa","size":"1024","sizmod":False}
            }

    def getKeyList(self):

        kglob = "{}/.ssh/*".format(self.topdir)
        klist = []

        for file in glob.glob(kglob):
            if os.path.isdir(file) :
                continue
            bn = os.path.basename(file)
            if bn[0:10] == "authorized":
                continue
            if bn[0:11] == "known_hosts":
                continue
            if bn[0:6] == "config":
                continue
            if bn[-4:] == ".pub":
                continue
            pubpath = "{}.pub".format(file)
            if not os.path.isfile(pubpath) :
                # no .pub, probably not a key
                continue
            command = "ssh-keygen -l -f {}".format(file)
            ret = subprocess.run(command,capture_output=True, text=True, shell=True)
            data = ret.stdout
            if data == "":
                continue
            elem = self.parseFingerprintKeygenOutput(data.strip())
            elem['file'] = bn
            klist.append(elem)

        return(klist)


    def getPubKey(self, private):
        pubpath = "{}/.ssh/{}.pub".format(self.topdir, private)

        if os.path.isfile(pubpath) :
            with open(pubpath, "r") as fd:
                pubkey = fd.read()
        else:
            pubkey="no public key found"

        return(pubkey)


    def isKeyPassword(self, private):

        keypath = "{}/.ssh/{}".format(self.topdir, private)

        if os.path.isfile(keypath) :
            command ="ssh-keygen -y -f {} -P \"\" > /dev/null 2>&1".format(keypath)
            ret = subprocess.run(command,capture_output=False, text=False, shell=True)
            if ret.returncode != 0:
                return(True)
            else:
                return(False)
        else:
            return(-1)


    def createKey(self, kinfo):

        kpath = "{}/.ssh/{}".format(self.topdir, kinfo['file'])
        
        if os.path.isfile(kpath) :
            return({"retcode":1,"msg":"key already exists"})

        if kinfo['size'] != "-":
            extraparam = "-b {}".format(kinfo['size'])
        else:
            extraparam = ""
       
        command ="ssh-keygen -q -t {} {} -C \"{}\" -f {} -N \"{}\" ".format(kinfo['type'],extraparam,kinfo['comment'], kpath, kinfo['password'])

        ret = subprocess.run(command,capture_output=False, text=False, shell=True)
        if ret.returncode != 0:
            return({"retcode":2,"msg":"key creation failed"})
        else:
            return({"retcode":0,"msg":"ok"})

    def deleteKey(self, kname):

        kpath1 = "{}/.ssh/{}".format(self.topdir, kname)
        kpath2 = "{}/.ssh/{}.pub".format(self.topdir, kname)
        
        cnt = 0
        if os.path.isfile(kpath1) :
            os.remove(kpath1)
            cnt += 1

        if os.path.isfile(kpath2) :
            os.remove(kpath2)
            cnt += 1

        if cnt == 0:
            return({"retcode":0,"msg":"nothing to delete"})
        else:
            return({"retcode":0,"msg":"ok, {} keys deleted".format(cnt)})


    def modifyKey(self, kinfo):

        kpath = "{}/.ssh/{}".format(self.topdir, kinfo['file'])

        if not os.path.isfile(kpath) :
            return({"retcode":1,"msg":"key do not exists"})

        errcnt = 0
        errmsg = ""
        if kinfo['oldcomment'] != kinfo['newcomment']:
            if kinfo['ispasswd']:
                extraparam = "-P \"{}\"".format(kinfo['curpasswd'])
            else:
                extraparam = ""

            command ="ssh-keygen -q -c -C \"{}\" -f {} {} >/dev/null 2>&1".format(kinfo['newcomment'],kpath,extraparam)
            ret = subprocess.run(command,capture_output=False, text=False, shell=True)
            if ret.returncode != 0:
                errcnt += 1
                errmsg = "{} cannot change comment".format(errmsg)

        if kinfo['changepass'] :    
            if kinfo['ispasswd']:
                extraparam = "-P \"{}\"".format(kinfo['curpasswd'])
            else:
                extraparam = ""
       
            command ="ssh-keygen -q -p -f {} -N \"{}\" {} >/dev/null 2>&1".format(kpath,kinfo['newpasswd'],extraparam)
            ret = subprocess.run(command,capture_output=False, text=False, shell=True)
            if ret.returncode != 0:
                errcnt += 1
                errmsg = "{} cannot change passwd".format(errmsg)

        return({"retcode":errcnt,"msg":errmsg})


    ##########################################################################
    #
    #  REINIT STUFF
    #
    #
    
    def reset(self, newtopdir):
        self.topdir = newtopdir
