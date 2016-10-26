# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from gi.repository import Gtk, RB
import os
import rb


class ImpResLine():

    def __init__(self, grid, measureResultsDir, filename, noOfControls):
        super(ImpResLine, self).__init__()
        self.grid = grid
        self.fileChooser = Gtk.FileChooserButton()
        self.fileChooser.set_current_folder(
            measureResultsDir)
        audioFileFilter = Gtk.FileFilter()
        audioFileFilter.add_pattern("*.wav")
        audioFileFilter.add_pattern("*.pcm")
        audioFileFilter.add_pattern("*.raw")
        self.fileChooser.set_filter(audioFileFilter)
        if filename is not None:
            self.fileChooser.set_filename(filename)
        grid.add(self.fileChooser)
        self.entry = Gtk.Entry()
        grid.attach_next_to(self.entry, self.fileChooser,
            Gtk.PositionType.RIGHT, 2, 1)
        grid.show_all()
        grid.insert_row(noOfControls)

class ImpRespDlg():

    def __init__(self, parent, resultsDir):
        self.uibuilder = Gtk.Builder()
        self.resultsDir = resultsDir
        self.uibuilder.add_from_file(
            rb.find_plugin_file(parent, "DRCUI.glade"))
        self.dlg = self.uibuilder.get_object("impRespSelDlg")
        self.uibuilder.get_object("button_OKImpRespSelDlg").connect(
            "clicked", self.on_Ok)
        self.uibuilder.get_object("openFiles").connect(
            "clicked", self.on_AddFiles)
        self.uibuilder.get_object("buttonRemoveFile").connect(
            "clicked", self.on_RemoveFile)
        self.elementGrid = self.uibuilder.get_object("elementGrid")
        self.parent = parent
        self.mesureResultsDir = self.parent.drcDlg.getMeasureResultsDir()
        self.fileControlList = []

    def loadAllImpRespFromFolder(self, directory):
        allFiles = os.listdir(directory)
        wavFiles = []
        for filename in allFiles:
            if filename.endswith(".wav"):
                wavFiles.append(filename)
        self.setFiles(wavFiles)

    def on_RemoveFile(self, button):
        numFiles = len(self.fileControlList)
        del self.fileControlList[-1]
        self.elementGrid.remove_row(numFiles)

    def on_AddFiles(self, fileChooserBtn):
        impRespFilesDlg = Gtk.FileChooserDialog("Please choose a file",
            self.dlg, Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        impRespFilesDlg.set_current_folder(self.mesureResultsDir)
        impRespFilesDlg.set_select_multiple(True)
        impRespFilesDlg.run()
        allFiles = impRespFilesDlg.get_filenames()
        self.setFiles(allFiles)
        impRespFilesDlg.destroy()

    def setFiles(self, fileList):
        numFiles = len(fileList)
        for impRespFile in fileList:
            impRespL = ImpResLine(
                self.elementGrid, self.mesureResultsDir,
                impRespFile, numFiles)
            self.fileControlList.append(impRespL)
            impRespL.entry.set_text(str( 1.0 / float(numFiles) ))

    def on_Ok(self, param):
        self.dlg.response(Gtk.ResponseType.OK)
        self.dlg.set_visible(False)

    def getImpRespFiles(self):
        impRespFiles = []
        for fileControl in self.fileControlList:
            impRespPair = []
            impRespPair.append(fileControl.fileChooser.get_filename())
            impRespPair.append(float(fileControl.entry.get_text()))
            impRespFiles.append(impRespPair)
        return impRespFiles

    def run(self):
        print("running dlg...")
        return self.dlg.run()