# -*- coding: utf-8 -*-
import re
import os
import subprocess
from enum import Enum

from gi.repository import Gtk, RB

import DRCFileTool
import rb


class MeasureQARetVal(Enum):
            Done = 0
            Reject = 1
            Proceed = 2


class MeasureQADlg():

    def __init__(self, parent, genSweepFile, measSweepFile,
                 sweep_level):
        self.uibuilder = Gtk.Builder()
        self.uibuilder.add_from_file(
            rb.find_plugin_file(parent, "DRCUI.glade"))
        self.dlg = self.uibuilder.get_object("measureQualityDlg")
        self.uibuilder.get_object("button_doneMeasQA").connect(
            "clicked", self.on_button_doneMeasQA)
        self.uibuilder.get_object("button_rejectMeasQA").connect(
            "clicked", self.on_button_rejectMeasQA)
        self.uibuilder.get_object("button_ProceedMeasQA").connect(
            "clicked", self.on_button_ProceedMeasQA)
        btnViewAudacity = self.uibuilder.get_object("buttonViewRecSweep")
        btnViewAudacity.connect("clicked", self.on_viewRecSweep)
        self.genSweepFile = genSweepFile
        self.measSweepFile = measSweepFile

    def evalData(self):
        audioParams = DRCFileTool.LoadAudioFile(self.genSweepFile, 1)
        self.setEvalData(audioParams, "labelInputSweepData")
        audioParams = DRCFileTool.LoadAudioFile(self.measSweepFile, 1)
        minMaxRec = self.setEvalData(audioParams,
                                     "labelRecordedSweepData")
        audioParams = DRCFileTool.LoadAudioFile(self.impRespFile, 1)
        self.setEvalData(audioParams, "labelImpResponseData")
        # TODO: add evaluation
        label = self.uibuilder.get_object("labelRecomendationResult")
        result = "check values : recorded results seem to be fine to proceed"
        if (minMaxRec[1] - minMaxRec[0]) < 0.1:
            result = "check values : recorded volume seems to be quite low: " \
                     "check proper input device or adjust gain"
        label.set_text(result)

    def on_viewRecSweep(self, param):
        scriptName = "audacity"
        measSweepWaveFile = os.path.splitext(self.measSweepFile)[0] + ".wav"
        commandLine = [scriptName, measSweepWaveFile]
        subprocess.Popen(commandLine)

    def setEvalData(self, dataInfo, labelID):
        label = self.uibuilder.get_object(labelID)
        text = "Min/Pos: " + str(dataInfo.minSampleValue) + "/" + \
            str(dataInfo.minSampleValuePos) + \
            " Max/Pos: " + str(dataInfo.maxSampleValue) + "/" + \
            str(dataInfo.maxSampleValuePos)
        label.set_text(text)
        return [dataInfo.minSampleValue[0], dataInfo.maxSampleValue[0]]

    def setImpRespFileName(self, impRespFile):
        self.impRespFile = impRespFile
        self.uibuilder.get_object("entryImpRespFileName").set_text(
            self.impRespFile)

    def on_button_doneMeasQA(self, param):
        self.Result = MeasureQARetVal.Done
        self.dlg.response(Gtk.ResponseType.OK)
        self.dlg.set_visible(False)

    def on_button_rejectMeasQA(self, param):
        self.Result = MeasureQARetVal.Reject
        os.remove(self.impRespFile)
        self.dlg.response(Gtk.ResponseType.OK)
        self.dlg.set_visible(False)

    def on_button_ProceedMeasQA(self, param):
        self.Result = MeasureQARetVal.Proceed
        self.dlg.response(Gtk.ResponseType.OK)
        self.dlg.set_visible(False)

    def run(self):
        print("running dlg...")
        self.evalData()
        retVal = self.dlg.run()
        impRespFileName = self.uibuilder.get_object(
            "entryImpRespFileName").get_text()
        #TODO file hanlding specific on return code
        if impRespFileName != self.impRespFile:
            os.rename(self.impRespFile, impRespFileName)
        self.impRespFile = impRespFileName
        print(("returning : " + str(retVal) + "result: ", self.Result))
        return retVal