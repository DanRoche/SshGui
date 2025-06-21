#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
######################################################
# Ssh Gui --  GTK GUI -- Configs Gui
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

import lib.data_config as dataconf

##########################################################################
#
#  CONFIGS GUI
#
##########################################################################
    
class ConfigsGui:

    def __init__(self, parent, maingui):

        self.data = dataconf.ConfigsData()
        self.maingui = maingui

        self.folded = True       # default

        self.data.initConfigList()

        self.page3 = Gtk.HBox()
        self.bbar3 = Gtk.VBox()

        self.page3.add(self.bbar3)
        self.page3.set_child_packing(self.bbar3, False, False, 10, 0)

        img_add = Gtk.Image.new_from_file('img/add_g.png')
        self.bb3b1 = button = Gtk.Button()
        self.bb3b1.set_image(img_add)
        self.bbar3.pack_start(self.bb3b1, False, False, 10)
        self.bb3b1.connect("clicked", self.action_config_add)

        img_inf = Gtk.Image.new_from_file('img/info_g.png')
        self.bb3b2 = button = Gtk.Button()
        self.bb3b2.set_image(img_inf)
        self.bbar3.pack_start(self.bb3b2, False, False, 10)
        self.bb3b2.connect("clicked", self.action_config_info)
        
        img_edi = Gtk.Image.new_from_file('img/edit_g.png')
        self.bb3b3 = button = Gtk.Button()
        self.bb3b3.set_image(img_edi)
        self.bbar3.pack_start(self.bb3b3, False, False, 10)
        self.bb3b3.connect("clicked", self.action_config_edit)
        
        img_del = Gtk.Image.new_from_file('img/bin_g.png')
        self.bb3b4 = button = Gtk.Button()
        self.bb3b4.set_image(img_del)
        self.bbar3.pack_start(self.bb3b4, False, False, 10)
        self.bb3b4.connect("clicked", self.action_config_del)

        img_fold = Gtk.Image.new_from_file('img/unfold_g.png')
        self.bb3b5 = button = Gtk.Button()
        self.bb3b5.set_image(img_fold)
        self.bbar3.pack_start(self.bb3b5, False, False, 10)
        self.bb3b5.connect("clicked", self.action_config_refold)

        img_term = Gtk.Image.new_from_file('img/term2_g.png')
        self.bb3b6 = button = Gtk.Button()
        self.bb3b6.set_image(img_term)
        self.bbar3.pack_start(self.bb3b6, False, False, 10)
        self.bb3b6.connect("clicked", self.action_config_gossh)

        self.pg3m = Gtk.VBox()
        self.page3.add(self.pg3m)
        self.page3.set_child_packing(self.pg3m, True, True, 10, 0)

        self.pg3m.set_homogeneous(False)
       
        self.pg3h = Gtk.HBox()
        self.pg3m.add(self.pg3h)
        self.pg3m.set_child_packing(self.pg3h, False, False, 4, 0)

        self.chi = Gtk.Image.new_from_file('img/search24_g.png')
        self.pg3h.add(self.chi)
        self.pg3h.set_child_packing(self.chi, False, False, 4, 0)
        
        self.ch3 = Gtk.Entry()
        self.pg3h.add(self.ch3)
        self.pg3h.set_child_packing(self.ch3, True, True, 4, 0)
        self.ch3.connect("changed", self.do_search)

        self.sw3 = Gtk.ScrolledWindow()
        self.sw3.set_vexpand(True)  # ???
        self.pg3m.add(self.sw3)
        self.pg3m.set_child_packing(self.sw3, True, True, 4, 0)
        
        self.config_store = Gtk.TreeStore(bool, str, str, str, str, str)
        self.populate_config_listbox(0)
        # Use internal non visible column = 0  for filtering
        self.filter = self.config_store.filter_new()
        self.filter.set_visible_column(0)
        
        self.ctv = Gtk.TreeView(model=self.filter)

        for i, column_title in enumerate(["category", "host", "hostname", "user", "port"]  ):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i+1)
            column.set_sort_column_id(i)
            self.ctv.append_column(column)
        #self.lb1.set_selection_mode(Gtk.SelectionMode.NONE)
        self.ctv.connect("row-activated", self.action_config_double_clicked)

        self.sw3.add_with_viewport(self.ctv)
        parent.add(self.page3)
        parent.set_child_packing(self.page3, True, True, 0, 0)




    def populate_config_listbox(self, cleanbefore):
        if cleanbefore == 1:
            self.config_store.clear()

        cnfl = self.data.getConfigList()
        if cnfl is None:
            return
        uncat = None
        for key in cnfl.keys():
            if 'sub' in cnfl[key]:
                cat = self.config_store.append(None, [True, key, "", "", "", "" ])
                sublist = cnfl[key]['sub']
                for subkey in sublist.keys():
                    elem = sublist[subkey]
                    # port may be unset
                    if not 'port' in elem:
                        elem['port'] = ""
                    self.__populate_one_config(cat, subkey, elem)
            else:
                if uncat is None:
                    uncat = self.config_store.append(None, [True, "_", "", "", "", "" ])
                elem = cnfl[key]
                # port may be unset
                if not 'port' in elem:
                    elem['port'] = ""
                self.__populate_one_config(uncat, key, elem)
        if not self.folded:
            self.ctv.expand_all()

    def __populate_one_config(self, vcat, vkey, elem):
        if 'hostname' in elem:
            hn = elem['hostname']
        else:
            hn = ''
        if 'user' in elem:
            uz = elem['user']
        else:
            uz = ''
        if 'port' in elem:
            pt = elem['port']
        else:
            pt = ''
        self.config_store.append(vcat, [True, "", vkey, hn, uz, pt ])    
        


    #==================================================================
    #
    #  SEARCH STUFF
    #
                
    def do_search(self, widget):
        searchfor = self.ch3.get_text().lower()
        self.config_store.foreach(self.tst_matches, searchfor)
        

    def tst_matches(self, model, path, iter, query):
        text1 = model.get_value(iter, 2).lower()    # the name
        text2 = model.get_value(iter, 3).lower()    # the hostname
        if query in text1 or query in text2 :
            self.config_store.set_value(iter, 0, True)
            parent = model.iter_parent(iter)
            if parent is not None:
                self.config_store.set_value(parent, 0, True)
                self.ctv.expand_all()
                self.folded = False
        else:
            self.config_store.set_value(iter, 0, False)
        return
               
    #==================================================================
    #
    #  CONFIGS ACTIONS
    #

    def action_config_double_clicked(self, arg1, arg2, arg3):
        self.action_config_info(None)

    def action_config_add(self, parent):
        (px,py) = self.maingui.w0.get_position()

        self.nc = Gtk.Dialog(title="New config")
        self.nc.move(px+80,py+100)
        self.nc.set_default_size(600,0)

        self.nc.add_buttons("Cancel", 1, "Add new config", 2)

        self.nc_gr = Gtk.Grid()
        self.nc_gr.set_border_width(10)

        row = 0
        self.nc_lc0 = Gtk.Label(label="category:")
        self.nc_lc0.set_halign(Gtk.Align.END)
        self.nc_gr.attach(self.nc_lc0, 0, row, 1, 1)

        categ_store = Gtk.ListStore(str)
        for cat in self.data.sublist:
            categ_store.append([cat])
        self.nc_ec0 = Gtk.ComboBox.new_with_model_and_entry(categ_store)
        self.nc_ec0.set_entry_text_column(0)
        self.nc_gr.attach(self.nc_ec0, 1, row, 2, 1)
        
        row +=1
        self.nc_ln0 = Gtk.Label(label="name:")
        self.nc_ln0.set_halign(Gtk.Align.END)
        self.nc_gr.attach(self.nc_ln0, 0, row, 1, 1)
        self.nc_en0 = Gtk.Entry(expand = True)
        self.nc_en0.set_text("")
        self.nc_en0.set_editable(True)
        self.nc_gr.attach(self.nc_en0, 1, row, 2, 1)
        
        self.nc_l = {}
        self.nc_e = {}
        for val in self.data.confvalues:
            row +=1
            self.nc_l[val] = Gtk.Label(label="{}:".format(self.data.confvalues[val]['rn']))
            self.nc_l[val].set_halign(Gtk.Align.END)
            self.nc_gr.attach(self.nc_l[val], 1, row, 1, 1)
            self.nc_e[val] = Gtk.Entry(expand = True)
            self.nc_e[val].set_text("")
            self.nc_e[val].set_placeholder_text(self.data.confvalues[val]['ph'])
            self.nc_e[val].set_editable(True)
            self.nc_gr.attach(self.nc_e[val], 2, row, 1, 1)

           
        self.nc_gr.set_column_homogeneous(False)
        self.nc_gr.set_row_homogeneous(False)
        self.nc_gr.set_column_spacing(5)
        self.nc_gr.set_row_spacing(20)

        self.nc.vbox.add(self.nc_gr)

        self.nc.show_all()
        res = self.nc.run()
        if res == 2:
            # fetch values
            combentry = self.nc_ec0.get_child()
            categ = combentry.get_text()
            name = self.nc_en0.get_text()
            newconf = {"categ":categ,"name":name}
            for val in self.data.confvalues:
               newconf[val] = self.nc_e[val].get_text() 
            self.data.add(newconf)
            self.populate_config_listbox(1)

        self.nc.destroy()
            

    def action_config_info(self, parent):
        selconf = self.get_selected_conf_info()
        if selconf == None:
            return

        conf1 = self.data.getOneConfig(selconf['categ'],selconf['name'])
        (px,py) = self.maingui.w0.get_position()

        self.ci = Gtk.Dialog(title="Config info")
        self.ci.move(px+80,py+100)
        self.ci.set_default_size(600,0)

        self.ci.add_buttons("OK", 1, "Edit", 2, "Go!", 3)

        self.ci_gr = Gtk.Grid()
        self.ci_gr.set_border_width(10)

        row = 0
        self.ci_l1 = Gtk.Label(expand=True)
        if conf1['categ'] is None:
            self.ci_l1.set_markup("<b>{} :</b>".format(conf1['name']))
        else:
            self.ci_l1.set_markup("<b>{}</b> / <b>{} :</b>".format(conf1['categ'],conf1['name']))
        self.ci_l1.set_halign(Gtk.Align.START)
        self.ci_gr.attach(self.ci_l1, 0, row, 2, 1)
        
        self.ci_l = {}
        self.ci_e = {}
        for val in self.data.confvalues:
            if val in conf1:
                row +=1
                self.ci_l[row] = Gtk.Label(label="{}:".format(self.data.confvalues[val]['rn']))
                self.ci_l[row].set_halign(Gtk.Align.END)
                self.ci_gr.attach(self.ci_l[row], 0, row, 1, 1)
                self.ci_e[row] = Gtk.Entry(expand = True)
                self.ci_e[row].set_text(conf1[val])
                self.ci_e[row].set_editable(False)
                self.ci_gr.attach(self.ci_e[row], 1, row, 1, 1)

           
        self.ci_gr.set_column_homogeneous(False)
        self.ci_gr.set_row_homogeneous(False)
        self.ci_gr.set_column_spacing(5)
        self.ci_gr.set_row_spacing(20)

        self.ci.vbox.add(self.ci_gr)

        self.ci.show_all()
        res = self.ci.run()
        self.ci.destroy()
        if res == 2:
            self.action_config_edit(parent)
        if res == 3:
            self.action_config_gossh(parent)


    def action_config_edit(self, parent):
        selconf = self.get_selected_conf_info()
        if selconf == None:
            return

        oldconf = self.data.getOneConfig(selconf['categ'],selconf['name'])
        (px,py) = self.maingui.w0.get_position()
        
        self.ec = Gtk.Dialog(title="Edit config")
        self.ec.move(px+80,py+100)
        self.ec.set_default_size(600,0)

        self.ec.add_buttons("Cancel", 1, "Save config", 2)

        self.ec_gr = Gtk.Grid()
        self.ec_gr.set_border_width(10)

        row = 0
        self.ec_lc0 = Gtk.Label(label="category:")
        self.ec_lc0.set_halign(Gtk.Align.END)
        self.ec_gr.attach(self.ec_lc0, 0, row, 1, 1)

        categ_store = Gtk.ListStore(str)
        for cat in self.data.sublist:
            categ_store.append([cat])
        self.ec_ec0 = Gtk.ComboBox.new_with_model_and_entry(categ_store)
        self.ec_ec0.set_entry_text_column(0)
        combentry = self.ec_ec0.get_child()
        if oldconf['categ'] is not None:
            combentry.set_text(oldconf['categ'])
        self.ec_gr.attach(self.ec_ec0, 1, row, 2, 1)
        
        row +=1
        self.ec_ln0 = Gtk.Label(label="name:")
        self.ec_ln0.set_halign(Gtk.Align.END)
        self.ec_gr.attach(self.ec_ln0, 0, row, 1, 1)
        self.ec_en0 = Gtk.Entry(expand = True)
        self.ec_en0.set_text(oldconf['name'])
        self.ec_en0.set_editable(True)
        self.ec_gr.attach(self.ec_en0, 1, row, 2, 1)
        
        self.ec_l = {}
        self.ec_e = {}
        for val in self.data.confvalues:
            row +=1
            self.ec_l[val] = Gtk.Label(label="{}:".format(self.data.confvalues[val]['rn']))
            self.ec_l[val].set_halign(Gtk.Align.END)
            self.ec_gr.attach(self.ec_l[val], 1, row, 1, 1)
            self.ec_e[val] = Gtk.Entry(expand = True)
            if val in oldconf:
                self.ec_e[val].set_text(oldconf[val])
            else:
                self.ec_e[val].set_text("")
            self.ec_e[val].set_placeholder_text(self.data.confvalues[val]['ph'])
            self.ec_e[val].set_editable(True)
            self.ec_gr.attach(self.ec_e[val], 2, row, 1, 1)

           
        self.ec_gr.set_column_homogeneous(False)
        self.ec_gr.set_row_homogeneous(False)
        self.ec_gr.set_column_spacing(5)
        self.ec_gr.set_row_spacing(20)

        self.ec.vbox.add(self.ec_gr)

        self.ec.show_all()
        res = self.ec.run()
        if res == 2:
            # fetch values
            combentry = self.ec_ec0.get_child()
            categ = combentry.get_text()
            name = self.ec_en0.get_text()
            newconf = {"categ":categ,"name":name}
            for val in self.data.confvalues:
               newconf[val] = self.ec_e[val].get_text() 
            self.data.modify(oldconf, newconf)
            self.populate_config_listbox(1)

        self.ec.destroy()


    def action_config_del(self, parent):
        selconf = self.get_selected_conf_info()
        if selconf == None:
            return

        (px,py) = self.maingui.w0.get_position()
        self.kk = Gtk.Dialog(title="Delete config")
        self.kk.move(px+80,py+100)
        self.kk.set_default_size(400,150)

        self.kk.add_buttons("Cancel", 1, "Delete config", 2)

        self.kk_l1 = Gtk.Label()
        if selconf['categ'] == "":
            self.kk_l1.set_markup("Confirm the suppression of config <b>{}</b> ?".format(selconf['name']))
        else:
            self.kk_l1.set_markup("Confirm the suppression of config <b>{} / {}</b> ?".format(selconf['categ'],selconf['name']))

        self.kk.vbox.add(self.kk_l1)
        self.kk.vbox.set_child_packing(self.kk_l1, True, True, 20, 0)

        self.kk.show_all()
        res = self.kk.run()
        self.kk.destroy()

        if res == 2:
            self.data.delete(selconf)
            self.populate_config_listbox(1)


    def action_config_refold(self, parent):
        if self.folded :
            self.ctv.expand_all()
            self.folded = False
        else:
            self.ctv.collapse_all()
            self.folded = True

    def action_config_gossh(self, parent):
        selconf = self.get_selected_conf_info()
        if selconf == None:
            return
        self.data.launchInTerminal(selconf['name'])
        

    #==================================================================
    #
    #  CONFIGS UTILITIES
    #

    def get_selected_conf_info(self):
        model, item = self.ctv.get_selection().get_selected()
        if item is None:
            return(None)
        row = model[item]
        name = row[2]
        if name == "":
            return(None)
        parent = row.get_parent()
        if parent is None:
            categ = ""
        else:
            categ = parent[1]
            if categ == '_':
                categ = ""
        retval={'categ':categ,'name':name}
        return(retval)

    def debug(self):
        self.data.dump()


    ##########################################################################
    #
    #  REINIT STUFF
    #
    #
    
    def reset(self, newtopdir):
        self.data.reset(newtopdir)
        self.data.initConfigList()
        self.populate_config_listbox(1)

