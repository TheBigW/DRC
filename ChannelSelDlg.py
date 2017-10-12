# -*- coding: utf-8 -*-
import gi
from gi.repository import RB
from gi.repository import Gtk

from DependsWrapper import DependsWrapperImpl

class ChanelSelDlg():
    def __init__(self, parent):
        self.uibuilder = Gtk.Builder()
        self.uibuilder.add_from_file(
            DependsWrapperImpl.find_plugin_file(parent, "DRCUI.glade"))
        self.dlg = self.uibuilder.get_object("channel_no_dlg")
        self.check2ChanCombo = self.uibuilder.get_object(
            "comboboxtextChannels")
        self.check2ChanCombo.connect("changed", self.onChannelSelChanged)
        self.numChannels = 1
        okBtn = self.uibuilder.get_object("button_OK")
        okBtn.connect("clicked", self.on_Ok)
        cancelBtn = self.uibuilder.get_object("button_Cancel")
        cancelBtn.connect("clicked", self.on_Cancel)

    def onChannelSelChanged(self, combo):
        selText = self.check2ChanCombo.get_active_text()
        print("selected number of channels = " + selText)
        self.numChannels = int(selText)

    def on_Ok(self, param):
        self.dlg.response(Gtk.ResponseType.OK)
        self.dlg.set_visible(False)

    def on_Cancel(self, param):
        self.dlg.response(Gtk.ResponseType.CANCEL)
        self.dlg.set_visible(False)

    def run(self):
        print("running ChanelSelDlg...")
        return self.dlg.run()

    def getNumChannels(self):
        return self.numChannels