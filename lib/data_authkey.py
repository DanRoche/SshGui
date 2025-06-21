#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
######################################################
# Ssh Gui -- DATA -- Authorized_Keys
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

class AuthKeysData(datamain.MainData):

    def __init__(self):

        super().__init__()

        self.authKeyOptions = {
            "command": {"cat":"cmd","val":True},
            "from": {"cat":"frm","val":True},
            "environment": {"cat":"env","val":True},
            "expiry-time": {"cat":"tim","val":True},
            "agent-forwarding": {"cat":"afg","val":False},
            "no-agent-forwarding": {"cat":"agf","val":False},
            "pty": {"cat":"pty","val":False},
            "no-pty": {"cat":"pty","val":False},
            "port-forwarding": {"cat":"prt","val":False},
            "no-port-forwarding": {"cat":"prt","val":False},
            "X11-forwarding": {"cat":"x11","val":False},
            "no-X11-forwarding": {"cat":"x11","val":False}
            }

    def getAuthKeyList(self):

        akpath = "{}/.ssh/authorized_keys".format(self.topdir)

        if not os.path.isfile(akpath) :
            return(None)

        with open(akpath, "r") as fd:
            aklines = fd.readlines()
            fd.close()

        self.akcache = {}
            
        aklist = []
        for line in aklines:
            elems = self.parseAuthKeyLine(line)
            if elems is not None:
                aklist.append(elems)
                self.akcache[elems['fingerprint']] = elems
            
        return(aklist)

    def getAuthKeyInfos(self, fingerprint):

        return(self.akcache[fingerprint])

    ###############################################
    #
    # AUTHORIZED KEYS UTILITIES
    #
    #
    def aklineSeparateOptions(self, line):

        # carefull,  the order matters !
        for i,type in enumerate(["sk-ssh-ed25519@openssh.com", "ssh-ed25519","ssh-rsa","ssh-dss",
                                 "sk-ecdsa-sha2-nistp256@openssh.com","ecdsa-sha2-nistp256",
                                 "ecdsa-sha2-nistp384","ecdsa-sha2-nistp521"]):
            ind = line.find(type)
            if ind != -1:
                break
        if ind == -1:
            # this is not a correct authorized_keys line
            return(None)
        options = line[0:ind].strip()
        pubkey = line[ind:]
        return({'pubkey':pubkey,'options':options})
    
    
    def parseAuthKey1Option(self, str):
        theopt = {}
        p =  str.find("=")
        if p == -1:
            theopt[str] = True
        else:
            theopt[str[0:p]] = str[p+1:].strip('"')
        return(theopt)
        
    def parseAuthKeyAllOptions(self, str):
        if str == '':
            return(None)
        start=0
        inquote=False
        options={}
        ind=0
        for c in str:
            if c == '"':
                inquote = not inquote
            if c == ',' and not inquote:
                elem = self.parseAuthKey1Option(str[start:ind])
                options = options | elem
                start=ind+1
            ind += 1
        elem = self.parseAuthKey1Option(str[start:])
        options = options | elem
        return(options)

    ## probably useless function, we already have comment
    def separatePubKeyElems(self, pubkey):
        pke = {}
        part = pubkey.split(" ")
        pke['type'] = part[0]
        pke['key'] = part[1]
        if len(part) == 2:
            pke['comment'] = 'no_comment'
        else:
            pke['comment'] = part[2]
        return(pke)

    def parseAuthKeyLine(self, line):

        res1 = self.aklineSeparateOptions(line.strip())
        if res1 is None:
            return(None)

        command = "echo \"{}\" | ssh-keygen -l -f -".format(res1['pubkey'])
        ret = subprocess.run(command,capture_output=True, text=True, shell=True)
        data = ret.stdout
        if data == "":
            return(None)

        infos = self.parseFingerprintKeygenOutput(data.strip())
        infos['options'] = self.parseAuthKeyAllOptions(res1['options'])
        # infos['pubkey'] = self.separatePubKeyElems(res1['pubkey'])  ## probably useless
        infos['pubkey'] = res1['pubkey']
                                                  
        return(infos)

    ###############################################
    #
    # AUTHORIZED KEYS OPTIONS UTILITIES
    #
    #

    def authOptionsVerifyExistingCategory(self, optlist, newopt):
        newcat = self.authKeyOptions[newopt]['cat']
        found = False
        for elem in optlist:
            thecat = self.authKeyOptions[elem['otyp']]['cat']
            if thecat == newcat:
                found = True
                break
        return(found)

    def authOptionsDeleteOne(self, optlist, delopt):
        found = -1
        ind = 0
        for elem in optlist:
            thecat = self.authKeyOptions[elem['otyp']]['cat']
            if elem['otyp'] == delopt:
                found = ind
            ind += 1
        if found != -1:
            oinfo = optlist[found]
            optlist.pop(found)
        else:
            oinfo = None
        return(oinfo)

    ###############################################
    #
    # AUTHORIZED KEYS CRUD
    #
    #

    def AddNewAuthKey(self, authkey):

        line = self.GenerateAuthKeyLine(authkey['pubkey'], authkey['options'])
        akpath = "{}/.ssh/authorized_keys".format(self.topdir)

        with open(akpath, "a+") as fd:
            fd.write(line)
            fd.write("\n")
            fd.close()
            os.chmod(akpath,0o600)   # needed if file was not existing
        
    def DeleteAuthKey(self, fingerprint):

        #print("DeleteAuthKey : {}".format(fingerprint))
        del(self.akcache[fingerprint])

        self.RewriteAuthKeyCache()

        
    def ModifyAuthKey(self, fingerprint, pubkey, comment, options):

        #print("ModifyAuthKey")
        #print(" FP = {}".format(fingerprint))
        #print(" PK = {}".format(pubkey))
        #print(" NCOM = {}".format(comment))
        #print(" OPTS = {}".format(options))
        
        # change the comment in pubkey
        pkel = pubkey.split(" ")
        if len(pkel) == 3:
            pkel[2] = comment
        else:
            pkel.append(comment)
        newpk = " ".join(pkel)

        # update the AK cache
        self.akcache[fingerprint]['comment'] = comment
        self.akcache[fingerprint]['pubkey'] = newpk
        self.akcache[fingerprint]['options'] = options
        
        self.RewriteAuthKeyCache()
        

        
    ###############################################
    #
    # AUTHORIZED KEYS UTILITIES
    #
    #

    def GenerateAuthKeyLine(self, pubkey, options):

        if options is None:
            line = pubkey
            return(line)
        
        opts = []
        for ok,ov in options.items():
            if ov != True:
                tmp = '{}="{}"'.format(ok,ov)
            else:
                tmp = ok
            opts.append(tmp)
        stropt = ",".join(opts)
        if stropt == "":
            line = pubkey
        else:
            line = "{} {}".format(stropt,pubkey)
        return(line)

    
    def RewriteAuthKeyCache(self):

        akpath = "{}/.ssh/authorized_keys".format(self.topdir)

        with open(akpath, "w") as fd:
            for ak in self.akcache.values():
                line = self.GenerateAuthKeyLine(ak['pubkey'], ak['options'])
                fd.write(line)
                fd.write("\n")
            fd.close()
            os.chmod(akpath,0o600)
            
    ###############################################
    #
    # AUTHKEY MISC
    #
    #

    def dump(self):
        print("ak list:")
        for elem in self.akcache:
            print("-> {} ".format(elem))
            print("  {}".format(self.akcache[elem]))


    ##########################################################################
    #
    #  REINIT STUFF
    #
    #
    
    def reset(self, newtopdir):
        self.topdir = newtopdir
        self.akcache = {}
        
