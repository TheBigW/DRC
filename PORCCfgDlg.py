# -*- coding: utf-8 -*-
from gi.repository import Gtk, RB
import rb

class PORCCfgDlg():

    def __init__(self, parent):
        self.uibuilder = Gtk.Builder()
        self.uibuilder.add_from_file(
            rb.find_plugin_file(parent, "DRCUI.glade"))
        self.dlg = self.uibuilder.get_object("porcCfgDlg")
        okBtn = self.uibuilder.get_object("button_OKPORCDlg")
        okBtn.connect("clicked", self.on_Ok)
        cancelBtn = self.uibuilder.get_object("button_CancelPORCDlg")
        cancelBtn.connect("clicked", self.on_Cancel)

        self.checkbuttonMixedPhase = self.uibuilder.get_object(
            "checkbuttonMixedPhase")

    def on_Ok(self, param):
        self.dlg.response(Gtk.ResponseType.OK)
        self.dlg.set_visible(False)

    def on_Cancel(self, param):
        self.dlg.response(Gtk.ResponseType.CANCEL)
        self.dlg.set_visible(False)

    def getMixedPhaseEnabled(self):
        return self.checkbuttonMixedPhase.get_active()

    def run(self):
        print("running dlg...")
        return self.dlg.run()