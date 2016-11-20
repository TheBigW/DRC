# -*- coding: utf-8 -*-
from gi.repository import Gtk, RB
import os
from DRCConfig import DRCConfig
import rb

class DRCCfgDlg():

    def applyConfig(self):
        aCfg = DRCConfig()
        if os.path.exists(aCfg.MicCalibrationFile):
            self.filechooserbuttonMicCalFile.set_filename(
                aCfg.MicCalibrationFile)
        else:
            self.filechooserbuttonMicCalFile.set_current_folder(
                "/usr/share/drc/mic")

    def __init__(self, parent):
        self.uibuilder = Gtk.Builder()
        self.uibuilder.add_from_file(
            rb.find_plugin_file(parent, "DRCUI.glade"))
        self.dlg = self.uibuilder.get_object("drcCfgDlg")
        okBtn = self.uibuilder.get_object("button_OKDRCDlg")
        okBtn.connect("clicked", self.on_Ok)
        cancelBtn = self.uibuilder.get_object("button_CancelDRCDlg")
        cancelBtn.connect("clicked", self.on_Cancel)
        self.filechooserbuttonMicCalFile = self.uibuilder.get_object(
            "filechooserbuttonMicCalFile")
        self.uibuilder.get_object(
            "resetBtn").connect("clicked", self.on_ResetToDefaults)
        self.applyConfig()
        self.comboboxtext_norm_method = self.uibuilder.get_object(
            "comboboxtext_norm_method")
        self.filechooserbuttonBaseCfg = self.uibuilder.get_object(
            "filechooserbuttonBaseCfg")
        self.filechooserbuttonBaseCfg.set_current_folder(
            "/usr/share/drc/config/44.1 kHz")
        self.filechooserbuttonBaseCfg.set_filename(
            "/usr/share/drc/config/44.1 kHz/erb-44.1.drc")

    def on_ResetToDefaults(self, param):
        self.filechooserbuttonMicCalFile.unselect_all()
        self.filechooserbuttonMicCalFile.set_current_folder(
            "/usr/share/drc/mic")

    def on_Ok(self, param):
        self.dlg.response(Gtk.ResponseType.OK)
        aCfg = DRCConfig()
        aCfg.MicCalibrationFile = self.filechooserbuttonMicCalFile.\
            get_filename()
        aCfg.save()
        self.dlg.set_visible(False)

    def on_Cancel(self, param):
        self.dlg.response(Gtk.ResponseType.CANCEL)
        self.applyConfig()
        self.dlg.set_visible(False)

    def getMicCalibrationFile(self):
        return self.filechooserbuttonMicCalFile.get_filename()

    def getNormMethod(self):
        return self.comboboxtext_norm_method.get_active_text()

    def getBaseCfg(self):
        return self.filechooserbuttonBaseCfg.get_filename()

    def run(self):
        print("running dlg...")
        return self.dlg.run()