# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from gi.repository import Gtk, RB
import os
import rb

from DRCTargetCurveUI import EQControl
import DRCFileTool


class TargetCurveLine():

    def __init__(self, grid, filename, channelNumber, noOfControls):
        super(TargetCurveLine, self).__init__()
        self.fileChooser = Gtk.FileChooserButton()
        audioFileFilter = Gtk.FileFilter()
        audioFileFilter.add_pattern("*.txt")
        self.fileChooser.set_filter(audioFileFilter)
        self.fileChooser.set_current_folder(
            "/usr/share/drc/target/44.1 kHz")
        if filename is not None:
            self.fileChooser.set_filename(filename)
        self.channelLabel = Gtk.Label()
        self.channelLabel.set_text(str(channelNumber))
        grid.add(self.channelLabel)
        grid.attach_next_to(self.fileChooser, self.channelLabel,
            Gtk.PositionType.RIGHT, 2, 1)
        grid.show_all()
        self.rowNumber = channelNumber + 1
        grid.insert_row(self.rowNumber)

    def remove(self, grid):
        grid.remove(self.channelLabel)
        self.channelLabel = None
        grid.remove(self.fileChooser)
        self.fileChooser = None
        grid.remove_row(self.rowNumber)

    def getTargetCurveFileName(self):
        return self.fileChooser.get_filename()


class TargetCurveDlg():

    def __init__(self, parent):
        self.uibuilder = Gtk.Builder()
        self.uibuilder.add_from_file(
            rb.find_plugin_file(parent, "DRCUI.glade"))
        self.dlg = self.uibuilder.get_object("TargetCurveSelDlg")
        self.uibuilder.get_object("button_OKTargetCurve").connect(
            "clicked", self.on_Ok)
        self.elementGrid = self.uibuilder.get_object("elementGridTargetCurve")
        self.parent = parent
        self.uibuilder.get_object("buttonEditTargetCurve").connect("clicked",
                                                self.on_editTargetCurve)
        self.impRespFile = None
        self.defaultTargetCurveFile = "/usr/share/drc/target/44.1 kHz/flat-44.1.txt"
        self.channelControls = []

    def setImpRespFile(self, impRespFile):
        #build target curve list form number of channels in
        #the impRespFile
        self.removeAll()
        numChannels = DRCFileTool.getNumChannels(impRespFile)

        for currChannel in range(0, numChannels):
            newChannelControls = TargetCurveLine(self.elementGrid,
                self.defaultTargetCurveFile, currChannel, numChannels)
            self.channelControls.append(newChannelControls)

    def removeAll(self):
        for control in self.channelControls:
            control.remove(self.elementGrid)
        self.channelControls = []

    def getTargetCurveFileName(self, currChannel):
        targetCurveFileName = self.defaultTargetCurveFile
        if(len(self.channelControls) > currChannel):
            targetCurveFileName = self.channelControls[currChannel].\
                getTargetCurveFileName()
        return targetCurveFileName

    def on_Ok(self, param):
        self.dlg.response(Gtk.ResponseType.OK)
        self.dlg.set_visible(False)

    def run(self):
        return self.dlg.run()

    def on_editTargetCurve(self, widget):
        #TODO take the selected channel
        editDlg = EQControl(self.getTargetCurveFileName(0),
                            self.parent)
        editDlg.run()