#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
######################################################
# Ssh Gui -- DATA -- Config
#
# dan.y.roche@gmail.com
#
# 202503  initial version
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

class ConfigsData(datamain.MainData):

    def __init__(self):
        super().__init__()
        self.confvalues = {
            'hostname': {'rn':"Hostname",'len':8, 'ph':"target name or ip"},
            'user': {'rn':"User",'len':4, 'ph':"loginUser"},
            'port': {'rn':"Port",'len':4, 'ph':"22"},
            'identityfile': {'rn':"IdentityFile",'len':12, 'ph':"~/path/to/priv/key"},
            'proxycommand': {'rn':"ProxyCommand",'len':12, 'ph':"ssh gateway nc %h %p"},
            'proxyjump': {'rn':"ProxyJump",'len':9, 'ph':"intermediateConfigName"},
            'localforward': {'rn':"LocalForward",'len':12, 'ph':"localPort distantHost:distantPort"},
            'remoteforward': {'rn':"RemoteForward",'len':13, 'ph':"distantPort localHost:localPort"},
            'dynamicforward': {'rn':"DynamicForward",'len':14, 'ph':"localSockProxyPort"},
            'forwardagent': {'rn':"ForwardAgent",'len':12, 'ph':"yes/no"},
            'ciphers': {'rn':"Ciphers",'len':7, 'ph':"+xxxx-yyyy"}
        }
        self.sublist = []
        self.subcateg_separator = '.'    #   by default
        

    def initConfigList(self):
        self.clist = self.__getOneFile("config", "")
        if self.clist is None:
            # no config file
            self.clist = {}
        return(self.clist)

    def getConfigList(self):
        return(self.clist)

    def getOneConfig(self, categ, name):
        if not self.clist:
            self.initConfigList()
        if categ == "":
            theconf = self.clist[name]
        else:
            sub = self.clist[categ]['sub']
            theconf = sub[name]
        # add the given name
        theconf['name'] = name
        return(theconf)
    
    ###############################################
    #
    # SIMPLE CONFIG FILE
    #
    #

    def __getOneFile(self, file, category):

        cnfpath = "{}/.ssh/{}".format(self.topdir, file)

        if not os.path.isfile(cnfpath) :
            return(None)

        with open(cnfpath, "r") as fd:
            cnflines = fd.readlines()
            fd.close()

        cnflist = {}
        current = None
        for lin0 in cnflines:
            if lin0 == "\n":
                continue
            if lin0[:5].lower() == "host ":
                if current is not None:
                    cnflist[current] = tmp
                current = lin0[5:].strip()
                # categ, hostname, user, port must always be initialized
                tmp = {"categ":category,"hostname":"","user":"","port":""}
            elif lin0[:8].lower() == "include ":
                subfile = lin0[8:].strip(' "\n')
                if subfile[0:6] != 'config':
                    # bad include line format
                    continue
                self.subcateg_separator = subfile[6]
                subcateg = subfile[7:]
                self.sublist.append(subcateg)
                subdata = self.__getOneFile(subfile, subcateg)
                cnflist[subcateg] = {"sub":subdata}
            else:
                line = lin0.strip()
                if line[0] == "#":
                    continue
                for opt in self.confvalues.keys():
                    len = self.confvalues[opt]['len']
                    if line[:len].lower() == opt:
                        tmp[opt] = line[len+1:]

        # the last entry at end of file
        if current is not None:
            cnflist[current] = tmp
          

        return(cnflist)
        
    ###############################################
    #
    # CONFIG CRUD
    #
    #

    def add(self, cinfo):
        categ=cinfo['categ']
        name=cinfo['name']
        syncinfo = {}
        if categ == '':
            self.clist[name] = self.__dataify(cinfo)
            syncinfo['_main_'] = 'mod'
        else:
            if categ in self.sublist:
                syncinfo[categ] = 'mod'
                self.clist[categ]['sub'][name] = self.__dataify(cinfo)
            else:
                syncinfo[categ] = 'cre'
                syncinfo['_main_'] = 'mod'
                self.sublist.append(categ)
                self.clist[categ] = {'sub':{}}
                self.clist[categ]['sub'][name] = self.__dataify(cinfo)
        self.__synchro(syncinfo)

        
    def modify(self, cold, cnew):
        #print("config modify ")
        #print("   old : {}".format(cold))
        #print("   new : {}".format(cnew))
        ocateg=cold['categ']
        oname=cold['name']
        ncateg=cnew['categ']
        nname=cnew['name']
        syncinfo = {}
        if ocateg == ncateg :
            if oname == nname :
                if ocateg == '' :
                    self.clist[oname] = self.__dataify(cnew)
                    syncinfo['_main_'] = 'mod'
                else:
                    self.clist[ocateg]['sub'][oname] = self.__dataify(cnew)
                    syncinfo[ocateg] = 'mod'
            else:
                if ocateg == '' :
                    del(self.clist[oname])
                    self.clist[nname] = self.__dataify(cnew)
                    syncinfo['_main_'] = 'mod'
                else:
                    del(self.clist[ocateg]['sub'][oname])
                    self.clist[ocateg]['sub'][nname] = self.__dataify(cnew)
                    syncinfo[ocateg] = 'mod'
        else:
            if ocateg != '':
                del(self.clist[ocateg]['sub'][oname])
                if len(self.clist[ocateg]['sub']) == 0:
                    syncinfo[ocateg] = 'del'
                    del(self.clist[ocateg])
                    self.sublist.remove(ocateg)
                    syncinfo['_main_'] = 'mod'
                else:
                    syncinfo[ocateg] = 'mod'
            else:
                del(self.clist[oname])
                syncinfo['_main_'] = 'mod'
            if ncateg == '':
                self.clist[nname] = self.__dataify(cnew)
                syncinfo['_main_'] = 'mod'
            else:
                if ncateg in self.sublist:
                    syncinfo[ncateg] = 'mod'
                    self.clist[ncateg]['sub'][nname] = self.__dataify(cnew)
                else:
                    syncinfo[ncateg] = 'cre'
                    syncinfo['_main_'] = 'mod'
                    self.sublist.append(ncateg)
                    self.clist[ncateg] = {'sub':{}}
                    self.clist[ncateg]['sub'][nname] = self.__dataify(cnew)
        self.__synchro(syncinfo)

    def __dataify(self,info):
        res = {}
        for ik,iv in info.items():
            if ik == 'name':
                continue
            if ik == 'categ' and iv == '':
                res[ik] = None
                continue
            if iv != '':
                res[ik] = iv
        return(res)
        
    def delete(self, cinfo):
        categ=cinfo['categ']
        name=cinfo['name']
        syncinfo = {}
        if categ != '':
            del(self.clist[categ]['sub'][name])
            if len(self.clist[categ]['sub']) == 0:
                syncinfo[categ] = 'del'
                del(self.clist[categ])
                self.sublist.remove(categ)
                syncinfo['_main_'] = 'mod'
            else:
                syncinfo[categ] = 'mod'
        else:
            del(self.clist[name])
            syncinfo['_main_'] = 'mod'
        self.__synchro(syncinfo)

        
    ###############################################
    #
    # CONFIG RAM->FILE SYNCHRO
    #
    #

    def __synchro(self, syncinfo):
        #print("sync info : {}".format(syncinfo))
        for k,v in syncinfo.items():
            if k == "_main_" :
                cnfpath = "{}/.ssh/config".format(self.topdir)
                if v == 'mod' or v == 'cre':
                    with open(cnfpath, "w") as fd:
                        # first includes ( categories )
                        for categ in self.sublist:
                            fd.write("include config{}{}\n".format(self.subcateg_separator, categ))
                            fd.write("\n")
                        # next uncategorized entry
                        for item in self.clist:
                            if 'sub' in self.clist[item]:
                                continue
                            infos = self.clist[item]
                            self.__writeOneEntry(fd, item, infos)
                        fd.close()
                        os.chmod(cnfpath,0o600)
                else:        # del main config,  should not happen !
                    print("should not happen")
            else:
                cnfpath = "{}/.ssh/config{}{}".format(self.topdir, self.subcateg_separator, k)
                if v == 'mod' or v == 'cre':
                    sublist = self.clist[k]['sub']
                    with open(cnfpath, "w") as fd:
                        for entry in sublist:
                            infos = sublist[entry]
                            self.__writeOneEntry(fd, entry, infos)
                        fd.close()
                        os.chmod(cnfpath,0o600)
                else:             # del case
                    os.remove(cnfpath)

    def __writeOneEntry(self, fd, entry, infos):
        fd.write("Host {}\n".format(entry))
        for param in self.confvalues.keys():
            if param in infos and infos[param] != "" :
                fd.write("  {} {}\n".format(self.confvalues[param]['rn'], infos[param]))
        fd.write("\n")
                
        
    ###############################################
    #
    # CONFIG MISC
    #
    #

    def dump(self):

        print("config list:")
        for categ in self.sublist:
            sublist = self.clist[categ]['sub']
            nbsub = len(sublist)
            print("{} : {}".format(categ.upper(),nbsub))
            for entry in sublist:
                print("    {}:".format(entry))
                infos = sublist[entry]
                for param in infos:
                    print("        {} = {}".format(param, infos[param]))
        # reloop entry without categ
        print("NO_CATEG : ")
        for item in self.clist:
            if 'sub' in self.clist[item]:
                continue
            print("    {}:".format(item))
            infos = self.clist[item]
            for param in infos:
                print("        {} = {}".format(param, infos[param]))


    ##########################################################################
    #
    #  REINIT STUFF
    #
    #
    
    def reset(self, newtopdir):
        self.topdir = newtopdir

        self.sublist = []
        self.subcateg_separator = '.'    #   by default
        self.clist = None
