#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
######################################################
# Ssh Gui --  GTK GUI -- Main 
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

import lib.gui_key as guikey
import lib.gui_authkey as guiauthkey
import lib.gui_config as guiconfig
import lib.gui_knownhost as guiknownhost
import lib.data_main as datamain

##########################################################################
#
#  MAIN GUI
#
##########################################################################
    
class MainGui:

    def __init__(self):

        # ---- main window 
        self.w0 = Gtk.Window(title="Ssh GUI", type=Gtk.WindowType.TOPLEVEL)
        self.w0.connect("destroy", self.action_quit)
        self.w0.set_default_size(1000,600)

        self.data = datamain.MainData()
        
        # ---- main gui
        self.bx00 = Gtk.VBox()
        self.w0.add(self.bx00)

        self.mbar = Gtk.MenuBar()
        self.bx00.add(self.mbar)
        self.bx00.set_child_packing(self.mbar, False, False, 0, 0)

        # ---- menu 
        self.gui_menu()
        
        # ---- remote bar 
        self.gui_remote_bar()
        
        # ---- notebook
        self.gui_notebook()
        
        # ---- keys page
        self.gui_keys = guikey.KeysGui(self.pg1, self)

        # ---- authorized keys page
        self.gui_authkeys = guiauthkey.AuthKeysGui(self.pg2, self)

        # ---- configs page
        self.gui_configs = guiconfig.ConfigsGui(self.pg3, self)

        # ---- known_hosts page
        self.gui_knownhosts = guiknownhost.KnownHostsGui(self.pg4, self)

        # ---- custom css
        self.util_apply_custom_css()
        
        # ---- GO !
        self.w0.show_all()

    #  menu construction
    def gui_menu(self):
        self.m1=Gtk.Menu()
        self.m1i1=Gtk.MenuItem(label="App") 
        self.m1i1.set_submenu(self.m1)
        #self.m1i2=Gtk.ImageMenuItem.new_from_stock(stock_id="gtk-properties")
        #self.m1i2.connect("activate", self.action_conf)      
        #self.m1i5=Gtk.SeparatorMenuItem()
        self.m1i6=Gtk.ImageMenuItem.new_from_stock(stock_id="gtk-quit")
        #self.m1i6.set_image(self.ico['exit'])
        self.m1i6.connect("activate", self.action_quit)   
        #self.m1.append(self.m1i2)
        #self.m1.append(self.m1i5) 
        self.m1.append(self.m1i6) 
        self.mbar.append(self.m1i1)
        self.m2=Gtk.Menu()
        self.m2i1=Gtk.MenuItem(label="Help") 
        self.m2i1.set_submenu(self.m2)
        self.m2i2=Gtk.ImageMenuItem.new_from_stock(stock_id="gtk-about")
        self.m2i2.connect("activate", self.action_about)      
        #self.m2i3=Gtk.ImageMenuItem(label="Debug...")
        #self.m2i3.connect("activate", self.action_debug)      
        self.m2.append(self.m2i2)
        #self.m2.append(self.m2i3)
        self.mbar.append(self.m2i1)

    #  remote bar construction
    def gui_remote_bar(self):
        self.rem0=Gtk.HBox()
        self.bx00.add(self.rem0)
        self.bx00.set_child_packing(self.rem0, False, False, 4, 0)

        self.chi = Gtk.Image.new_from_file('img/rem24_g.png')
        self.rem0.add(self.chi)
        self.rem0.set_child_packing(self.chi, False, False, 4, 0)
        
        self.chm = Gtk.Entry()
        self.rem0.add(self.chm)
        self.rem0.set_child_packing(self.chm, True, True, 4, 0)
        self.chm.set_text(self.data.getCurrentUser())
        self.chm.connect("activate", self.action_remote_download)

        img_rdl = Gtk.Image.new_from_file('img/dl24_g.png')
        self.rdl = button = Gtk.Button()
        self.rdl.set_image(img_rdl)
        self.rem0.add(self.rdl)
        self.rdl.connect("clicked", self.action_remote_download)
        self.rem0.set_child_packing(self.rdl, False, False, 4, 0)
        
        img_rup = Gtk.Image.new_from_file('img/up24_g.png')
        self.rup = button = Gtk.Button()
        self.rup.set_image(img_rup)
        self.rem0.add(self.rup)
        self.rup.connect("clicked", self.action_remote_upload)
        self.rem0.set_child_packing(self.rup, False, False, 4, 0)
        
        img_qst = Gtk.Image.new_from_file('img/question_g.png')
        self.qst = button = Gtk.Button()
        self.qst.set_image(img_qst)
        self.rem0.add(self.qst)
        self.qst.connect("clicked", self.action_help)
        self.rem0.set_child_packing(self.qst, False, False, 4, 0)
        



    #  notebook construction
    def gui_notebook(self):
        self.nb = Gtk.Notebook()
        self.bx00.add(self.nb)
        self.bx00.set_child_packing(self.mbar, False, False, 0, 0)

        self.pg1 = Gtk.Box()
        self.pg1.set_border_width(10)
        self.nb.append_page(self.pg1, Gtk.Label(label="keys"))

        self.pg2 = Gtk.Box()
        self.pg2.set_border_width(10)
        self.nb.append_page(self.pg2, Gtk.Label(label="authorized keys") )
        
        self.pg3 = Gtk.Box()
        self.pg3.set_border_width(10)
        self.nb.append_page(self.pg3, Gtk.Label(label="configs") )
        
        self.pg4 = Gtk.Box()
        self.pg4.set_border_width(10)
        self.nb.append_page(self.pg4, Gtk.Label(label="known hosts") )

    #==================================================================
    #
    #  MAIN GUI ACTIONS
    #
    
    def loop(self):
        Gtk.main()

    def action_quit(self, widget):
        self.data.cleanRemoteCache()
        quit()
        
    def action_about(self, widget):
        (px,py) = self.w0.get_position()
        
        self.about = Gtk.AboutDialog()
        
        self.about.move(px+86,py+56)
        self.about.set_program_name("Ssh GUI")
        pb = GdkPixbuf.Pixbuf.new_from_file('img/ssh_logo.png')
        self.about.set_logo(pb)
        self.about.set_version("version 1.2")
        self.about.set_authors(["Daniel Roche <dan.y.roche@gmail.com>"])
        self.about.set_copyright("GPL")
        self.about.set_comments("Jun 2025")

        self.about.run()
        self.about.destroy()

    def action_remote_download(self, widget):
        tmp = self.chm.get_text()
        if tmp == "":
            tmp = self.data.getCurrentUser()
            self.chm.set_text(tmp)
        topdir = self.data.switch(tmp)

        self.gui_keys.reset(topdir)
        self.gui_authkeys.reset(topdir)
        self.gui_configs.reset(topdir)
        self.gui_knownhosts.reset(topdir)

        
    def action_remote_upload(self, widget):
        self.data.uploadRemoteCache()
        
    def action_help(self, widget):
        (px,py) = self.w0.get_position()

        self.hlp0 = Gtk.Dialog(title="Help")
        self.hlp0.move(px+80,py+100)
        self.hlp0.set_default_size(500, 400)

        self.hlp0.add_buttons("OK", 1 )

        self.hlpsw = Gtk.ScrolledWindow()
        self.hlpsw.set_hexpand(True)
        self.hlpsw.set_vexpand(True)

        self.hlp0.vbox.add(self.hlpsw)

        self.hlptx = Gtk.TextView()
        self.hlptx.set_editable(False)
        self.hlpbuf = self.hlptx.get_buffer()
        self.hlpbuf.set_text(self.data.getHelp())

        self.hlpsw.add(self.hlptx)
        
        self.hlp0.show_all()
        res = self.hlp0.run()    
        self.hlp0.destroy()



    ##########################################################################
    #
    #  MISC STUFF
    #
    #
    
    def action_debug(self,widget):
        #print("nothing")
        self.gui_authkeys.debug()

    
    def util_apply_custom_css(self):
        # Création de la feuille de style CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
          .error-mark {
            background-color: #FF8080;
          }
        """)
        # Application du css
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

