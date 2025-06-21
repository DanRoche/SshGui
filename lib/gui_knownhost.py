#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
######################################################
# Ssh Gui --  GTK GUI -- Known Host Gui
#
# d.roche@girondenumerique.fr
#
# 202502   initial sshgui version
# 202503   gui separation
######################################################x
"""

# -------------------------
# std import 

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf

# -------------------------
# app import 
import lib.data_knownhost as dataknownhost


##########################################################################
#
#  Known Hosts GUI
#
##########################################################################
    
class KnownHostsGui:

    def __init__(self, parent, maingui):

        self.maingui = maingui
        self.data = dataknownhost.KnownHostsData()

        self.page4 = Gtk.VBox()
        self.page4.set_homogeneous(False)
 
        self.pg4h = Gtk.HBox()
        self.page4.add(self.pg4h)
        self.page4.set_child_packing(self.pg4h, False, False, 4, 0)

        self.chi = Gtk.Image.new_from_file('img/search24_g.png')
        self.pg4h.add(self.chi)
        self.pg4h.set_child_packing(self.chi, False, False, 4, 0)
        
        self.ch4 = Gtk.Entry()
        self.pg4h.add(self.ch4)
        self.pg4h.set_child_packing(self.ch4, True, True, 4, 0)
        self.ch4.set_placeholder_text("search for known host name or ip")
        self.ch4.connect("activate", self.action_knownhost_search)

        self.kh_store = Gtk.ListStore(str, str, str, str, str)
        
        self.khtv = Gtk.TreeView(model=self.kh_store)

        for i, column_title in enumerate(["name", "line", "type", "size", "fingerprint"] ):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.set_sort_column_id(i)
            self.khtv.append_column(column)

        self.page4.add(self.khtv)
        self.page4.set_child_packing(self.khtv, False, False, 4, 0)
      
        self.buttonRemoveCreated = False

        parent.add(self.page4)
        parent.set_child_packing(self.page4, True, True, 0, 0)

    #==================================================================
    #
    #  KNOWN HOST ACTIONS
    #

    def action_knownhost_search(self, parent):

        searchfor = self.ch4.get_text().lower()

        kh = self.data.getKnownHost(searchfor)
        if kh is not None:
            self.populate_knownhost_listbox(kh)
        else:
            self.empty_knownhost_listbox()

    def populate_knownhost_listbox(self, khlist):
        self.kh_store.clear()
        for elem in khlist:
            self.kh_store.append([elem['name'],elem['line'],elem['type'],elem['typesize'],elem['fingerprint']])
        self.show_remove()

    def empty_knownhost_listbox(self):
        self.kh_store.clear()
        self.hide_remove()

    def action_knownhost_remove(self, parent):
        toremove = self.ch4.get_text().lower()
        if toremove != "":
            self.data.removeKnownHost(toremove)
        self.ch4.set_text("")
        self.empty_knownhost_listbox()

    def show_remove(self):
        if not self.buttonRemoveCreated:
            self.pg4b1 = Gtk.Button(label="remove this host")
            self.page4.add(self.pg4b1)
            self.page4.set_child_packing(self.pg4b1, False, False, 25, 0)
            self.pg4b1.connect("clicked", self.action_knownhost_remove)
            self.buttonRemoveCreated = True
        self.pg4b1.set_visible(True)   

    def hide_remove(self):
        if self.buttonRemoveCreated:
            self.pg4b1.set_visible(False)


    ##########################################################################
    #
    #  REINIT STUFF
    #
    #
    
    def reset(self, newtopdir):
        self.data.reset(newtopdir)
        self.ch4.set_text("")
        self.empty_knownhost_listbox()
