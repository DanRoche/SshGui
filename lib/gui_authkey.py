#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
######################################################
# Ssh Gui --  GTK GUI -- Authorized_keys Gui
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

import lib.data_authkey as dataauthkey

##########################################################################
#
#  AUTHORIZED_KEYS GUI
#
##########################################################################
    
class AuthKeysGui:

    def __init__(self, parent, maingui):

        self.data = dataauthkey.AuthKeysData()
        self.maingui = maingui

        self.page2 = Gtk.HBox()
        self.bbar2 = Gtk.VBox()

        self.page2.add(self.bbar2)
        self.page2.set_child_packing(self.bbar2, False, False, 10, 0)

        img_add = Gtk.Image.new_from_file('img/add_g.png')
        self.bb2b1 = button = Gtk.Button()
        self.bb2b1.set_image(img_add)
        self.bbar2.pack_start(self.bb2b1, False, False, 10)
        self.bb2b1.connect("clicked", self.action_authkey_add)

        img_inf = Gtk.Image.new_from_file('img/info_g.png')
        self.bb2b2 = button = Gtk.Button()
        self.bb2b2.set_image(img_inf)
        self.bbar2.pack_start(self.bb2b2, False, False, 10)
        self.bb2b2.connect("clicked", self.action_authkey_info)
        
        img_edi = Gtk.Image.new_from_file('img/edit_g.png')
        self.bb2b3 = button = Gtk.Button()
        self.bb2b3.set_image(img_edi)
        self.bbar2.pack_start(self.bb2b3, False, False, 10)
        self.bb2b3.connect("clicked", self.action_authkey_edit)
        
        img_del = Gtk.Image.new_from_file('img/bin_g.png')
        self.bb2b4 = button = Gtk.Button()
        self.bb2b4.set_image(img_del)
        self.bbar2.pack_start(self.bb2b4, False, False, 10)
        self.bb2b4.connect("clicked", self.action_authkey_del)

        self.pg2m = Gtk.VBox()
        self.page2.add(self.pg2m)
        self.page2.set_child_packing(self.pg2m, True, True, 10, 0)

        self.pg2m.set_homogeneous(False)
       
        self.pg2h = Gtk.HBox()
        self.pg2m.add(self.pg2h)
        self.pg2m.set_child_packing(self.pg2h, False, False, 4, 0)

        self.chh = Gtk.Image.new_from_file('img/search24_g.png')
        self.pg2h.add(self.chh)
        self.pg2h.set_child_packing(self.chh, False, False, 4, 0)
        
        self.ch2 = Gtk.Entry()
        self.pg2h.add(self.ch2)
        self.pg2h.set_child_packing(self.ch2, True, True, 4, 0)
        self.ch2.connect("changed", self.do_search)

        self.sw2 = Gtk.ScrolledWindow()
        self.sw2.set_vexpand(True)  # ???
        self.pg2m.add(self.sw2)
        self.pg2m.set_child_packing(self.sw2, True, True, 4, 0)

        self.authkeys_store = Gtk.ListStore(bool, str, str, str, str, str)
        self.populate_authkeys_listbox(self.authkeys_store, 0)
        # Use internal non visible column = 0  for filtering
        self.filter = self.authkeys_store.filter_new()
        self.filter.set_visible_column(0)
       
        #self.aktv = Gtk.TreeView(model=self.authkeys_store)
        self.aktv = Gtk.TreeView(model=self.filter)

        for i, column_title in enumerate(["comment", "options", "type", "size", "fingerprint"] ):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i+1)
            column.set_sort_column_id(i)
            self.aktv.append_column(column)
        #self.lb1.set_selection_mode(Gtk.SelectionMode.NONE)
        self.aktv.connect("row-activated", self.action_authkey_double_clicked)

        self.sw2.add_with_viewport(self.aktv)
        parent.add(self.page2)
        parent.set_child_packing(self.page2, True, True, 0, 0)

    def populate_authkeys_listbox(self, store, cleanbefore):
        if cleanbefore == 1:
            store.clear()
        akl = self.data.getAuthKeyList()
        if akl is None:
            return
        for elem in akl:
            optdisp = self.authkeys_options_short_display(elem['options'])
            store.append([True, elem['comment'],optdisp,elem['type'],elem['size'],elem['fingerprint']])

    def authkeys_options_short_display(self, options):
        optdisp = ""
        if options is None:
            return(optdisp)
        for ok in options.keys():
            match ok:
                case "command":
                    optdisp = "{}C".format(optdisp)
                case "from":
                    optdisp = "{}F".format(optdisp)
                case "environment":
                    optdisp = "{}E".format(optdisp)
                case "expiry-time":
                    optdisp = "{}T".format(optdisp)
                case "agent-forwarding":
                    optdisp = "{}A".format(optdisp)
                case "no-agent-forwarding":
                    optdisp = "{}a".format(optdisp)
                case "pty":
                    optdisp = "{}P".format(optdisp)
                case "no-pty":
                    optdisp = "{}p".format(optdisp)
                case "port-forwarding":
                    optdisp = "{}W".format(optdisp)
                case "no-port-forwarding":
                    optdisp = "{}w".format(optdisp)
                case "X11-forwarding":
                    optdisp = "{}X".format(optdisp)
                case "no-X11-forwarding":
                    optdisp = "{}x".format(optdisp)
                case _:
                    optdisp = "{}*".format(optdisp)
        return(optdisp)

    #==================================================================
    #
    #  AUTHKEY SEARCH STUFF
    #
                
    def do_search(self, widget):
        searchfor = self.ch2.get_text().lower()
        self.authkeys_store.foreach(self.tst_matches, searchfor)
        #self.debug()
        

    def tst_matches(self, model, path, iter, query):
        text1 = model.get_value(iter, 1).lower()    # the comment
        if query in text1 :
            self.authkeys_store.set_value(iter, 0, True)
        else:
            self.authkeys_store.set_value(iter, 0, False)
        return
               
    #==================================================================
    #
    #  AUTHORIZED_KEYS ACTIONS
    #

    def action_authkey_double_clicked(self, arg1, arg2, arg3):
        self.action_authkey_info(None)

    def action_authkey_add(self, parent):
        (px,py) = self.maingui.w0.get_position()
        
        self.nak = Gtk.Dialog(title="New Authorized key")
        self.nak.move(px+80,py+100)
        #self.nak.set_default_size(600,300)

        self.nak.add_buttons("Cancel", 1, "Add new Authorized Key", 2)

        self.nak_gr = Gtk.Grid()
        self.nak_gr.set_border_width(10)

        row = 0
        self.nak_l1 = Gtk.Label(expand=False)
        self.nak_l1.set_markup("<b>public key:</b>")
        self.nak_l1.set_halign(Gtk.Align.START)
        self.nak_gr.attach(self.nak_l1, 0, row, 3, 1)

        row +=1
        self.nak_pk = Gtk.TextView(expand=True)
        self.nak_pktb = self.nak_pk.get_buffer()
        self.nak_pk.set_editable(True)
        self.nak_pk.set_size_request(600,80) 
        self.nak_pk.set_cursor_visible(True)
        self.nak_pk.set_wrap_mode(Gtk.WrapMode.CHAR)
        self.nak_gr.attach(self.nak_pk, 0, row, 3, 1)

        row +=1
        self.nak_t2 = Gtk.Label()
        self.nak_t2.set_markup("<b>Options:</b>")
        self.nak_t2.set_halign(Gtk.Align.START)
        self.nak_gr.attach(self.nak_t2, 0, row, 1, 1)
            
        opts = Gtk.ListStore(str)
        for opt1 in self.data.authKeyOptions.keys():
            opts.append([opt1])

        self.nak_e1 = Gtk.ComboBox.new_with_model(opts)
        renderer_text = Gtk.CellRendererText()
        self.nak_e1.pack_start(renderer_text, True)
        self.nak_e1.add_attribute(renderer_text, "text", 0)
        self.nak_e1.set_entry_text_column(0)
        self.nak_e1.set_active(0)   # default to the 1st in the list = ed25519
        #self.nak_e1.connect("changed", self.newkey_type_changed)
        self.nak_gr.attach(self.nak_e1, 1, row, 1, 1)

        self.nak_oba = Gtk.Button(label="+")
        self.nak_oba.set_halign(Gtk.Align.END)
        self.nak_gr.attach(self.nak_oba, 2, row, 1, 1)
        self.nak_oba.connect("clicked", self.authkey_option_add)
       
        self.nak_data = {}
        self.nak_data['row'] = row
        self.nak_data['optlist'] = []
        
        self.nak_gr.set_column_homogeneous(False)
        self.nak_gr.set_row_homogeneous(False)
        self.nak_gr.set_column_spacing(5)
        self.nak_gr.set_row_spacing(5)

        self.nak.vbox.add(self.nak_gr)

        self.nak.show_all()

        res = self.nak.run()

        if res == 2:
            # fetch pubkey  from gui
            txb = self.nak_pk.get_buffer()
            start_iter = txb.get_start_iter()
            end_iter = txb.get_end_iter()
            pubkey = txb.get_text(start_iter, end_iter, True).strip()
            # fetch options from gui
            newopts = {}
            for elem in self.nak_data['optlist']:
                optk = elem['otyp']
                if elem['entry'] is not None:
                    optv = elem['entry'].get_text()
                else:
                    optv = True
                newopts[optk] = optv
            newauthkey = {'pubkey':pubkey,'options':newopts}
            self.data.AddNewAuthKey(newauthkey)
            self.populate_authkeys_listbox(self.authkeys_store, 1)
            
        self.nak.destroy()

    def authkey_option_add(self, parent):
        iter = self.nak_e1.get_active_iter()
        model = self.nak_e1.get_model()
        nopt =  model[iter][0]

        if self.data.authOptionsVerifyExistingCategory(self.nak_data['optlist'], nopt):
            return

        self.nak_data['row'] += 1        
        tmp_l = Gtk.Label(label="{}:".format(nopt))
        tmp_l.set_halign(Gtk.Align.END)
        self.nak_gr.attach(tmp_l, 0, self.nak_data['row'], 1, 1)
        if self.data.authKeyOptions[nopt]['val']:
            tmp_e = Gtk.Entry(expand = True)
            self.nak_gr.attach(tmp_e, 1, self.nak_data['row'], 1, 1)
        else:
            tmp_e = None
        tmp_b = Gtk.Button(label="-")
        tmp_b.set_halign(Gtk.Align.END)
        self.nak_gr.attach(tmp_b, 2, self.nak_data['row'], 1, 1)
        tmp_b.connect("clicked", self.authkey_option_del, nopt)

        self.nak_data['optlist'].append({'otyp':nopt, 'label': tmp_l, 'entry':tmp_e, 'button':tmp_b})

        self.nak_gr.set_row_homogeneous(False)
        self.nak_gr.set_row_spacing(5)
        self.nak.show_all()

    def authkey_option_del(self, parent, delopt):
        print("opt del : {}".format(delopt))
        oinf = self.data.authOptionsDeleteOne(self.nak_data['optlist'], delopt)
        oinf['label'].destroy()
        oinf['button'].destroy()
        if oinf['entry'] is not None:
            oinf['entry'].destroy()
        return
         
    def action_authkey_info(self, parent):
        model, item = self.aktv.get_selection().get_selected()
        if item is None:
            return
        (px,py) = self.maingui.w0.get_position()

        fp = model[item][5]
        infos = self.data.getAuthKeyInfos(fp)
        
        self.aki = Gtk.Dialog(title="Authorized key info")
        self.aki.move(px+80,py+100)
        self.aki.set_default_size(600,0)

        self.aki.add_buttons("OK", 1, "Edit", 2)

        self.aki_gr = Gtk.Grid()
        self.aki_gr.set_border_width(10)

        row = 0
        #self.aki_t1 = Gtk.Label(expand=True)
        #self.aki_t1.set_markup("<big><b>Authorized key :</b></big>")
        #self.aki_gr.attach(self.aki_t1, 0, row, 2, 1)

        row = 0
        self.aki_l1 = Gtk.Label(expand=True)
        self.aki_l1.set_markup("<b>public key:</b>")
        self.aki_l1.set_halign(Gtk.Align.START)
        self.aki_gr.attach(self.aki_l1, 0, row, 2, 1)

        row +=1
        self.aki_pk = Gtk.TextView()
        self.aki_pktb = self.aki_pk.get_buffer()
        self.aki_pktb.set_text(infos['pubkey'])
        self.aki_pk.set_editable(False)
        self.aki_pk.set_cursor_visible(False)
        self.aki_pk.set_wrap_mode(Gtk.WrapMode.CHAR)
        self.aki_gr.attach(self.aki_pk, 0, row, 2, 1)

        opts = infos['options']
        if opts is not None:

            row +=1
            self.aki_t2 = Gtk.Label()
            self.aki_t2.set_markup("<b>Options:</b>")
            self.aki_t2.set_halign(Gtk.Align.START)
            self.aki_gr.attach(self.aki_t2, 0, row, 2, 1)

            oi = 0
            self.aki_lo = {}
            self.aki_eo = {}
            for ok, ov in opts.items():
                row +=1
                self.aki_lo[oi] = Gtk.Label(label="{}:".format(ok))
                self.aki_lo[oi].set_halign(Gtk.Align.END)
                self.aki_gr.attach(self.aki_lo[oi], 0, row, 1, 1)
                if ov is not True:
                    self.aki_eo[oi] = Gtk.Entry(expand = True)
                    self.aki_eo[oi].set_text(ov)
                    self.aki_eo[oi].set_editable(False)
                    self.aki_gr.attach(self.aki_eo[oi], 1, row, 1, 1)
                else:
                    self.aki_eo[oi] = Gtk.Image.new_from_file('img/check24.png')
                    self.aki_eo[oi].set_halign(Gtk.Align.START)
                    self.aki_gr.attach(self.aki_eo[oi], 1, row, 1, 1)


        self.aki_gr.set_column_homogeneous(False)
        self.aki_gr.set_row_homogeneous(False)
        self.aki_gr.set_column_spacing(5)
        self.aki_gr.set_row_spacing(20)

        self.aki.vbox.add(self.aki_gr)

        self.aki.show_all()
        res = self.aki.run()
        self.aki.destroy()
        if res == 2:
            self.action_authkey_edit(parent)


    def action_authkey_edit(self, parent):
        model, item = self.aktv.get_selection().get_selected()
        if item is None:
            return
        (px,py) = self.maingui.w0.get_position()

        fp = model[item][5]
        infos = self.data.getAuthKeyInfos(fp)

        # store the fingerprint in object for later use
        self.akm_data_fp = fp
        
        self.akm = Gtk.Dialog(title="Authorized key edit")
        self.akm.move(px+80,py+100)
        self.akm.set_default_size(650,0)

        self.akm.add_buttons("Cancel", 1, "Save", 2)

        self.akm_gr = Gtk.Grid()
        self.akm_gr.set_border_width(10)

        row = 0
        #self.akm_t1 = Gtk.Label(expand=True)
        #self.akm_t1.set_markup("<big><b>Authorized key :</b></big>")
        #self.akm_gr.attach(self.akm_t1, 0, row, 2, 1)

        self.akm_l1 = Gtk.Label(expand=True)
        self.akm_l1.set_markup("<b>public key:</b>")
        self.akm_l1.set_halign(Gtk.Align.START)
        self.akm_gr.attach(self.akm_l1, 0, row, 3, 1)

        row +=1
        self.akm_pk = Gtk.TextView()
        self.akm_pktb = self.akm_pk.get_buffer()
        self.akm_pktb.set_text(infos['pubkey'])
        self.akm_pk.set_editable(False)
        self.akm_pk.set_cursor_visible(False)
        self.akm_pk.set_wrap_mode(Gtk.WrapMode.CHAR)
        self.akm_gr.attach(self.akm_pk, 0, row, 3, 1)

        row +=1
        self.akm_l2 = Gtk.Label(label="comment:")
        self.akm_l2.set_halign(Gtk.Align.END)
        self.akm_gr.attach(self.akm_l2, 0, row, 1, 1)
        self.akm_e2 = Gtk.Entry(expand = True)
        self.akm_e2.set_text(infos['comment'])
        self.akm_gr.attach(self.akm_e2, 1, row, 1, 1)

        row +=1
        self.akm_l3 = Gtk.Label()
        self.akm_l3.set_markup("<b>Options:</b>")
        self.akm_l3.set_halign(Gtk.Align.START)
        self.akm_gr.attach(self.akm_l3, 0, row, 3, 1)

        opts = Gtk.ListStore(str)
        for opt1 in self.data.authKeyOptions.keys():
            opts.append([opt1])

        self.akm_e1 = Gtk.ComboBox.new_with_model(opts)
        renderer_text = Gtk.CellRendererText()
        self.akm_e1.pack_start(renderer_text, True)
        self.akm_e1.add_attribute(renderer_text, "text", 0)
        self.akm_e1.set_entry_text_column(0)
        self.akm_e1.set_active(0)   
        self.akm_gr.attach(self.akm_e1, 1, row, 1, 1)

        self.akm_oba = Gtk.Button(label="+")
        self.akm_oba.set_halign(Gtk.Align.END)
        self.akm_gr.attach(self.akm_oba, 2, row, 1, 1)
        self.akm_oba.connect("clicked", self.authkey_option_madd)
       
        self.akm_data = {}
        self.akm_data['row'] = row
        self.akm_data['optlist'] = []
        
        opts = infos['options']
        if opts is not None:

            oi = 0
            for ok, ov in opts.items():
                self.akm_data['row'] +=1
                tmp_l = Gtk.Label(label="{}:".format(ok))
                tmp_l.set_halign(Gtk.Align.END)
                self.akm_gr.attach(tmp_l, 0, self.akm_data['row'], 1, 1)
                if ov is not True:
                    tmp_e = Gtk.Entry(expand = True)
                    tmp_e.set_text(ov)
                    tmp_e.set_editable(True)
                    self.akm_gr.attach(tmp_e, 1, self.akm_data['row'], 1, 1)
                else:
                    tmp_e = None
                tmp_b= Gtk.Button(label="-")
                tmp_b.set_halign(Gtk.Align.END)
                self.akm_gr.attach(tmp_b, 2, self.akm_data['row'], 1, 1)
                tmp_b.connect("clicked", self.authkey_option_mdel, ok)

                self.akm_data['optlist'].append({'otyp':ok, 'label': tmp_l, 'entry':tmp_e, 'button':tmp_b})


        self.akm_gr.set_column_homogeneous(False)
        self.akm_gr.set_row_homogeneous(False)
        self.akm_gr.set_column_spacing(5)
        self.akm_gr.set_row_spacing(20)

        self.akm.vbox.add(self.akm_gr)

        self.akm.show_all()
        res = self.akm.run()
        
        if res == 2:
            # retrieve the stored fingerprint
            # fetch pubkey and comment from gui
            txb = self.akm_pk.get_buffer()
            start_iter = txb.get_start_iter()
            end_iter = txb.get_end_iter()
            pubkey = txb.get_text(start_iter, end_iter, True)
            ncomm = self.akm_e2.get_text()
            # fetch options from gui
            newopts = {}
            for elem in self.akm_data['optlist']:
                optk = elem['otyp']
                if elem['entry'] is not None:
                    optv = elem['entry'].get_text()
                else:
                    optv = True
                newopts[optk] = optv

            self.data.ModifyAuthKey(self.akm_data_fp, pubkey, ncomm, newopts)
            self.populate_authkeys_listbox(self.authkeys_store, 1)
            
        self.akm.destroy()


    def authkey_option_madd(self, parent):
        iter = self.akm_e1.get_active_iter()
        model = self.akm_e1.get_model()
        nopt =  model[iter][0]

        if self.data.authOptionsVerifyExistingCategory(self.akm_data['optlist'], nopt):
            return

        self.akm_data['row'] += 1        
        tmp_l = Gtk.Label(label="{}:".format(nopt))
        tmp_l.set_halign(Gtk.Align.END)
        self.akm_gr.attach(tmp_l, 0, self.akm_data['row'], 1, 1)
        if self.data.authKeyOptions[nopt]['val']:
            tmp_e = Gtk.Entry(expand = True)
            self.akm_gr.attach(tmp_e, 1, self.akm_data['row'], 1, 1)
        else:
            tmp_e = None
        tmp_b = Gtk.Button(label="-")
        tmp_b.set_halign(Gtk.Align.END)
        self.akm_gr.attach(tmp_b, 2, self.akm_data['row'], 1, 1)
        tmp_b.connect("clicked", self.authkey_option_del, nopt)

        self.akm_data['optlist'].append({'otyp':nopt, 'label': tmp_l, 'entry':tmp_e, 'button':tmp_b})

        self.akm_gr.set_row_homogeneous(False)
        self.akm_gr.set_row_spacing(5)
        self.akm.show_all()

    def authkey_option_mdel(self, parent, delopt):
        oinf = self.data.authOptionsDeleteOne(self.akm_data['optlist'], delopt)
        oinf['label'].destroy()
        oinf['button'].destroy()
        if oinf['entry'] is not None:
            oinf['entry'].destroy()
        return
         
    def action_authkey_del(self, parent):
        model, item = self.aktv.get_selection().get_selected()
        if item is None:
            return
        (px,py) = self.maingui.w0.get_position()
        self.akk = Gtk.Dialog(title="Delete authorized_key")
        self.akk.move(px+80,py+100)
        self.akk.set_default_size(650,150)

        self.akk.add_buttons("Cancel", 1, "Delete Authorized_key", 2)

        self.akk_l1 = Gtk.Label()
        self.akk_l1.set_markup("Confirm the suppression of authorized_key <b>{} ({})</b> ?".format(model[item][1],model[item][3]))

        self.akk.vbox.add(self.akk_l1)
        self.akk.vbox.set_child_packing(self.akk_l1, True, True, 20, 0)

        self.akk.show_all()
        res = self.akk.run()
        self.akk.destroy()

        if res == 2:
            self.data.DeleteAuthKey(model[item][5])
            self.populate_authkeys_listbox(self.authkeys_store, 1)


    def debug(self):
        for elem in self.authkeys_store:
            print("-> {}".format(elem))


    ##########################################################################
    #
    #  REINIT STUFF
    #
    #
    
    def reset(self, newtopdir):
        self.data.reset(newtopdir)
        self.populate_authkeys_listbox(self.authkeys_store, 1)
