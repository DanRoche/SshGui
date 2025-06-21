#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
######################################################
# Ssh Gui --  GTK GUI -- Keys Gui
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

import lib.data_key as datakey

##########################################################################
#
#  KEYS GUI
#
##########################################################################
    
class KeysGui:

    def __init__(self, parent, maingui):

        self.data = datakey.KeysData()
        self.maingui = maingui

        self.page1 = Gtk.HBox()
        self.bbar1 = Gtk.VBox()

        self.page1.add(self.bbar1)
        self.page1.set_child_packing(self.bbar1, False, False, 10, 0)

        img_add = Gtk.Image.new_from_file('img/add_g.png')
        self.bb1b1 = button = Gtk.Button()
        self.bb1b1.set_image(img_add)
        self.bbar1.pack_start(self.bb1b1, False, False, 10)
        self.bb1b1.connect("clicked", self.action_key_add)

        img_inf = Gtk.Image.new_from_file('img/info_g.png')
        self.bb1b2 = button = Gtk.Button()
        self.bb1b2.set_image(img_inf)
        self.bbar1.pack_start(self.bb1b2, False, False, 10)
        self.bb1b2.connect("clicked", self.action_key_info)
        
        img_edi = Gtk.Image.new_from_file('img/edit_g.png')
        self.bb1b3 = button = Gtk.Button()
        self.bb1b3.set_image(img_edi)
        self.bbar1.pack_start(self.bb1b3, False, False, 10)
        self.bb1b3.connect("clicked", self.action_key_edit)
        
        img_del = Gtk.Image.new_from_file('img/bin_g.png')
        self.bb1b4 = button = Gtk.Button()
        self.bb1b4.set_image(img_del)
        self.bbar1.pack_start(self.bb1b4, False, False, 10)
        self.bb1b4.connect("clicked", self.action_key_del)

        self.sw1 = Gtk.ScrolledWindow()
        self.sw1.set_vexpand(True)  # ???

        self.page1.add(self.sw1)
        self.page1.set_child_packing(self.sw1, True, True, 10, 0)
        
        self.keys_store = Gtk.ListStore(str, str, str, str, str)
        self.populate_keys_listbox(self.keys_store, 0)
        
        self.ktv = Gtk.TreeView(model=self.keys_store)

        for i, column_title in enumerate(["file", "comment", "type", "size", "fingerprint"] ):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.set_sort_column_id(i)
            self.ktv.append_column(column)
        #self.lb1.set_selection_mode(Gtk.SelectionMode.NONE)
        self.ktv.connect("row-activated", self.action_key_double_clicked)

        self.sw1.add_with_viewport(self.ktv)
        parent.add(self.page1)
        parent.set_child_packing(self.page1, True, True, 0, 0)

    def populate_keys_listbox(self, store, cleanbefore):
        if cleanbefore == 1:
            store.clear()
        kl = self.data.getKeyList()
        for elem in kl:
            store.append([elem['file'],elem['comment'],elem['type'],elem['size'],elem['fingerprint']])

    #==================================================================
    #
    #  KEYS ACTIONS
    #
    
    def action_key_double_clicked(self, arg1, arg2, arg3):
        self.action_key_info(None)

    def action_key_add(self,widget):
        (px,py) = self.maingui.w0.get_position()
        
        self.nk = Gtk.Dialog(title="New key")
        self.nk.move(px+80,py+100)

        self.nk.add_buttons("Cancel", 1, "Create New Key", 2)

        self.nk_gr = Gtk.Grid()
        self.nk_gr.set_border_width(10)

        ktype = Gtk.ListStore(str, str)
        for elem in self.data.keyType:
            ktype.append([elem['type'], elem['label']])

        self.nk_l1 = Gtk.Label(label="Type:")
        self.nk_l1.set_halign(Gtk.Align.END)
        self.nk_gr.attach(self.nk_l1, 0, 0, 1, 1)
        self.nk_e1 = Gtk.ComboBox.new_with_model(ktype)
        renderer_text = Gtk.CellRendererText()
        self.nk_e1.pack_start(renderer_text, True)
        self.nk_e1.add_attribute(renderer_text, "text", 1)
        self.nk_e1.set_entry_text_column(1)
        self.nk_e1.set_active(0)   # default to the 1st in the list = ed25519
        self.nk_e1.connect("changed", self.newkey_type_changed)
        self.nk_gr.attach(self.nk_e1, 1, 0, 1, 1)

        defval = self.data.keyDefaultValues['ed25519']
        
        self.nk_l2 = Gtk.Label(label="file:")
        self.nk_l2.set_halign(Gtk.Align.END)
        self.nk_gr.attach(self.nk_l2, 0, 1, 1, 1)
        self.nk_e2 = Gtk.Entry(expand = True)
        self.nk_e2.set_text(defval['file'])
        self.nk_gr.attach(self.nk_e2, 1, 1, 1, 1)
        
        self.nk_l3 = Gtk.Label(label="Comment:")
        self.nk_l3.set_halign(Gtk.Align.END)
        self.nk_gr.attach(self.nk_l3, 0, 2, 1, 1)
        self.nk_e3 = Gtk.Entry(expand = True)
        self.nk_e3.set_text("user@somehost")
        self.nk_gr.attach(self.nk_e3, 1, 2, 1, 1)
        
        self.nk_l4a = Gtk.Label(label="Password:")
        self.nk_l4a.set_halign(Gtk.Align.END)
        self.nk_gr.attach(self.nk_l4a, 0, 3, 1, 1)
        self.nk_e4a = Gtk.Entry(expand = True)
        self.nk_e4a.set_text("")
        self.nk_e4a.set_visibility(False)
        self.nk_gr.attach(self.nk_e4a, 1, 3, 1, 1)

        self.nk_l4b = Gtk.Label(label="Password again:")
        self.nk_l4b.set_halign(Gtk.Align.END)
        self.nk_gr.attach(self.nk_l4b, 0, 4, 1, 1)
        self.nk_e4b = Gtk.Entry(expand = True)
        self.nk_e4b.set_text("")
        self.nk_e4b.set_visibility(False)
        self.nk_gr.attach(self.nk_e4b, 1, 4, 1, 1)

        self.nk_l5 = Gtk.Label(label="Size:")
        self.nk_l5.set_halign(Gtk.Align.END)
        self.nk_gr.attach(self.nk_l5, 0, 5, 1, 1)
        self.nk_e5 = Gtk.Entry(expand = True)
        self.nk_e5.set_text(defval['size'])
        self.nk_e5.set_editable(defval['sizmod'])
        self.nk_gr.attach(self.nk_e5, 1, 5, 1, 1)
        
        self.nk_gr.set_column_homogeneous(False)
        self.nk_gr.set_row_homogeneous(True)
        self.nk_gr.set_column_spacing(5)
        self.nk_gr.set_row_spacing(5)

        self.nk.vbox.add(self.nk_gr)

        self.nk.show_all()

        loopNewKey = True
        while loopNewKey:
            res = self.nk.run()

            if res == 2:
                newkeyparam = {}
                iter = self.nk_e1.get_active_iter()
                model = self.nk_e1.get_model()
                newkeyparam['type'] = model[iter][0]
                newkeyparam['file'] = self.nk_e2.get_text()
                newkeyparam['comment'] = self.nk_e3.get_text()
                newkeyparam['password'] = self.nk_e4a.get_text()
                newkeyparam['password2'] = self.nk_e4b.get_text()
                newkeyparam['size'] = self.nk_e5.get_text()
                
                if newkeyparam['password'] != newkeyparam['password2'] :
                    #self.nk_l4a.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(65535, 30000, 30000))  # deprecated
                    #self.nk_l4b.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(65535, 30000, 30000))  # deprecated
                    self.util_show_error_label(self.nk_l4a)
                    self.util_show_error_label(self.nk_l4b)
                else:
                    res = self.data.createKey(newkeyparam)
                    if res['retcode'] != 0:
                        self.display_error_message(res['msg'])
                    else:
                        self.populate_keys_listbox(self.keys_store, 1)
                        loopNewKey = False
            else:
                loopNewKey = False 
            
        self.nk.destroy()

    def newkey_type_changed(self,combo):
        iter = combo.get_active_iter()
        model = combo.get_model()
        ntyp =  model[iter][0]
        defval = self.data.keyDefaultValues[ntyp]
        self.nk_e2.set_text(defval['file'])
        self.nk_e5.set_text(defval['size'])
        self.nk_e5.set_editable(defval['sizmod'])


    def action_key_info(self,widget):
        model, item = self.ktv.get_selection().get_selected()
        if item is None:
            return
        (px,py) = self.maingui.w0.get_position()
        
        self.ki = Gtk.Dialog(title="Key info")
        self.ki.move(px+80,py+100)
        self.ki.set_default_size(600,300)

        self.ki.add_buttons("OK", 1, "Edit", 2)

        self.ki_gr = Gtk.Grid()
        self.ki_gr.set_border_width(10)

        row = 0
        self.ki_t1 = Gtk.Label()
        self.ki_t1.set_markup("<big><b>Private key infos :</b></big>")
        self.ki_gr.attach(self.ki_t1, 0, row, 2, 1)

        row +=1
        self.ki_l1 = Gtk.Label(label="file:")
        self.ki_l1.set_halign(Gtk.Align.END)
        self.ki_gr.attach(self.ki_l1, 0, row, 1, 1)
        self.ki_e1 = Gtk.Entry(expand = True)
        self.ki_e1.set_text(model[item][0])
        self.ki_e1.set_editable(False)
        self.ki_gr.attach(self.ki_e1, 1, row, 1, 1)

        row +=1
        self.ki_l2 = Gtk.Label(label="comment:")
        self.ki_l2.set_halign(Gtk.Align.END)
        self.ki_gr.attach(self.ki_l2, 0, row, 1, 1)
        self.ki_e2 = Gtk.Entry(expand = True)
        self.ki_e2.set_text(model[item][1])
        self.ki_e2.set_editable(False)
        self.ki_gr.attach(self.ki_e2, 1, row, 1, 1)

        row +=1
        self.ki_l3 = Gtk.Label(label="type:")
        self.ki_l3.set_halign(Gtk.Align.END)
        self.ki_gr.attach(self.ki_l3, 0, row, 1, 1)
        self.ki_e3 = Gtk.Entry(expand = True)
        self.ki_e3.set_text(model[item][2])
        self.ki_e3.set_editable(False)
        self.ki_gr.attach(self.ki_e3, 1, row, 1, 1)

        isPasswd = self.data.isKeyPassword(model[item][0])
        if isPasswd :
            passimg='img/check24.png'
        else:
            passimg='img/nocheck24.png'

        row +=1
        self.ki_l4 = Gtk.Label(label="password protected:")
        self.ki_l4.set_halign(Gtk.Align.END)
        self.ki_gr.attach(self.ki_l4, 0, row, 1, 1)
        #self.ki_e4 = Gtk.Entry(expand = True)
        #self.ki_e4.set_text(passmsg)
        #self.ki_e4.set_editable(False)
        self.ki_e4 = Gtk.Image.new_from_file(passimg)
        self.ki_e4.set_halign(Gtk.Align.START)
        self.ki_gr.attach(self.ki_e4, 1, row, 1, 1)

        row +=1
        self.ki_t2 = Gtk.Label()
        self.ki_t2.set_markup("<big><b>Public key:</b></big>")
        self.ki_gr.attach(self.ki_t2, 0, row, 2, 1)

        pubkdata = self.data.getPubKey(model[item][0])
        
        row +=1
        self.ki_pk = Gtk.TextView()
        self.ki_pktb = self.ki_pk.get_buffer()
        self.ki_pktb.set_text(pubkdata)
        self.ki_pk.set_editable(False)
        self.ki_pk.set_cursor_visible(False)
        self.ki_pk.set_wrap_mode(Gtk.WrapMode.CHAR)

        self.ki_gr.attach(self.ki_pk, 0, row, 2, 1)

        self.ki_gr.set_column_homogeneous(False)
        self.ki_gr.set_row_homogeneous(False)
        self.ki_gr.set_column_spacing(5)
        self.ki_gr.set_row_spacing(20)

        self.ki.vbox.add(self.ki_gr)

        self.ki.show_all()
        res = self.ki.run()
        self.ki.destroy()
        if res == 2:
            self.action_key_edit(widget)
        
    def action_key_edit(self,widget):
        model, item = self.ktv.get_selection().get_selected()
        if item is None:
            return
        (px,py) = self.maingui.w0.get_position()
        self.ek = Gtk.Dialog(title="Edit key")
        self.ek.move(px+80,py+100)

        keyparam = {}
        keyparam['file'] = model[item][0]
        keyparam['oldcomment'] = model[item][1]
        keyparam['ispasswd'] = self.data.isKeyPassword(model[item][0])

        self.ek.add_buttons("Cancel", 1, "Save", 2)

        self.ek_gr = Gtk.Grid()
        self.ek_gr.set_border_width(10)

        row = 0
        if keyparam['ispasswd']:
            row +=1
            self.ek_l0 = Gtk.Label(label="current password:")
            self.ek_l0.set_halign(Gtk.Align.END)
            self.ek_gr.attach(self.ek_l0, 0, row, 1, 1)
            self.ek_e0 = Gtk.Entry(expand = True)
            self.ek_e0.set_text("")
            self.ek_e0.set_visibility(False)
            self.ek_gr.attach(self.ek_e0, 1, row, 1, 1)

        row += 1    
        self.ek_l1 = Gtk.Label(label="comment:")
        self.ek_l1.set_halign(Gtk.Align.END)
        self.ek_gr.attach(self.ek_l1, 0, row, 1, 1)
        self.ek_e1 = Gtk.Entry(expand = True)
        self.ek_e1.set_text(keyparam['oldcomment'])
        self.ek_gr.attach(self.ek_e1, 1, row, 1, 1)

        row +=1
        self.ek_cb2 = Gtk.CheckButton(label="modify password ?")
        self.ek_cb2.set_halign(Gtk.Align.CENTER)
        self.ek_cb2.connect("toggled", self. editkey_passwd_changed )
        self.ek_gr.attach(self.ek_cb2, 0, row, 2, 1)
        
        self.new_passwd_row = row+1

        self.ek_gr.set_column_homogeneous(False)
        self.ek_gr.set_row_homogeneous(False)
        self.ek_gr.set_column_spacing(5)
        self.ek_gr.set_row_spacing(20)
      
        self.ek.vbox.add(self.ek_gr)

        self.ek.show_all()

        loopEditKey = True
        while loopEditKey:
            res = self.ek.run()
            if res == 2:
                keyparam['newcomment'] = self.ek_e1.get_text()
                if keyparam['ispasswd'] :
                    keyparam['curpasswd'] = self.ek_e0.get_text()
                if self.ek_cb2.get_active():
                    keyparam['newpasswd'] = self.ek_e3a.get_text()
                    keyparam['newpassw2'] = self.ek_e3b.get_text()
                    keyparam['changepass'] = True
                    if keyparam['newpasswd'] != keyparam['newpassw2'] :
                        self.util_show_error_label(self.ek_l3a)
                        self.util_show_error_label(self.ek_l3b)
                        res2 = {"retcode": -1}
                    else:
                        res2 = self.data.modifyKey(keyparam)
                else:
                    keyparam['changepass'] = False
                    res2 = self.data.modifyKey(keyparam)
                    
                if res2['retcode'] >= 0:
                    if res2['retcode'] != 0:
                        self.display_error_message(res2['msg'])
                    else:
                        self.populate_keys_listbox(self.keys_store, 1)
                        loopEditKey = False
            else:
                loopEditKey = False 
 
        self.ek.destroy()

    def editkey_passwd_changed(self,toggle):
        st = toggle.get_active()
        if st:
            row = self.new_passwd_row 
            self.ek_l3a = Gtk.Label(label="new password:")
            self.ek_l3a.set_halign(Gtk.Align.END)
            self.ek_gr.attach(self.ek_l3a, 0, row, 1, 1)
            self.ek_e3a = Gtk.Entry(expand = True)
            self.ek_e3a.set_text("")
            self.ek_e3a.set_visibility(False)
            self.ek_gr.attach(self.ek_e3a, 1, row, 1, 1)

            row +=1
            self.ek_l3b = Gtk.Label(label="new password again:")
            self.ek_l3b.set_halign(Gtk.Align.END)
            self.ek_gr.attach(self.ek_l3b, 0, row, 1, 1)
            self.ek_e3b = Gtk.Entry(expand = True)
            self.ek_e3b.set_text("")
            self.ek_e3b.set_visibility(False)
            self.ek_gr.attach(self.ek_e3b, 1, row, 1, 1)

            self.ek.show_all()
        else:
            self.ek_l3a.destroy()
            self.ek_e3a.destroy()
            self.ek_l3b.destroy()
            self.ek_e3b.destroy()
            
        
    def action_key_del(self,widget):
        model, item = self.ktv.get_selection().get_selected()
        if item is None:
            return
        (px,py) = self.maingui.w0.get_position()
        self.kk = Gtk.Dialog(title="Delete key")
        self.kk.move(px+80,py+100)
        self.kk.set_default_size(400,150)

        self.kk.add_buttons("Cancel", 1, "Delete Key", 2)

        self.kk_l1 = Gtk.Label()
        self.kk_l1.set_markup("Confirm the suppression of key <b>{}</b> ?".format(model[item][0]))

        self.kk.vbox.add(self.kk_l1)
        self.kk.vbox.set_child_packing(self.kk_l1, True, True, 20, 0)

        self.kk.show_all()
        res = self.kk.run()
        self.kk.destroy()

        if res == 2:
            res = self.data.deleteKey(model[item][0])
            # no need to test result ?
            self.populate_keys_listbox(self.keys_store, 1)

    ##########################################################################
    #
    #  MISC STUFF
    #
    #
    
    def util_show_error_label(self,label):
        # Appliquer un style CSS pour changer la couleur de fond
        label.get_style_context().add_class("error-mark")

    def display_error_message(self, message):

        (px,py) = self.maingui.w0.get_position()
        self.err = Gtk.Dialog(title="Error")
        self.err.move(px+150,py+150)
        self.err.set_default_size(400,150)

        self.err.add_buttons("OK", 1)

        self.err_l1 = Gtk.Label()
        self.err_l1.set_markup("<b>Error</b>:  {}".format(message))

        self.err.vbox.add(self.err_l1)
        self.err.vbox.set_child_packing(self.err_l1, True, True, 20, 0)

        self.err.show_all()
        self.err.run()
        self.err.destroy()

    ##########################################################################
    #
    #  REINIT STUFF
    #
    #
    
    def reset(self, newtopdir):
        self.data.reset(newtopdir)
        self.populate_keys_listbox(self.keys_store, 1)
        

