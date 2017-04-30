# DRCUi.py
# Copyright (C) 2013 - Tobias Wenig
#            tobiaswenig@yahoo.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
import os
import sys
import re
import datetime
import subprocess
from shutil import copyfile


from gi.repository import Gtk, RB

from DRCConfig import DRCConfig
from MeasureQADlg import MeasureQADlg
from MeasureQADlg import MeasureQARetVal
from TargetCurveDlg import TargetCurveDlg
from ChannelSelDlg import ChanelSelDlg
from PORCCfgDlg import PORCCfgDlg
from DRCCfgDlg import DRCCfgDlg
from ImpRespDlg import ImpRespDlg
from alsaTools import InputVolumeProcess
import alsaTools

import DRCFileTool
import rb


class DRCDlg:
    def initUI(self):
        aCfg = DRCConfig()
        self.uibuilder = Gtk.Builder()
        self.uibuilder.add_from_file(
            rb.find_plugin_file(self.parent, "DRCUI.glade"))
        self.dlg = self.uibuilder.get_object("DRCDlg")
        self.dlg.connect("close", self.on_close)
        audioFileFilter = Gtk.FileFilter()
        audioFileFilter.add_pattern("*.wav")
        audioFileFilter.add_pattern("*.pcm")
        audioFileFilter.add_pattern("*.raw")
        self.filechooserbtn = self.uibuilder.get_object(
            "drcfilterchooserbutton")
        self.filechooserbtn.set_filter(audioFileFilter)
        if os.path.isfile(aCfg.filterFile):
            self.filechooserbtn.set_filename(aCfg.filterFile)
        else:
            self.filechooserbtn.set_current_folder(self.getFilterResultsDir())

        self.filechooserbtn.connect("file-set", self.on_file_selected)
        self.entrySweepDuration = self.uibuilder.get_object(
            "entrySweepDuration")
        self.entrySweepDuration.set_text(str(aCfg.sweepDuration))

        self.progressbarInputVolume = self.uibuilder.get_object(
            "progressbarInputVolume")

        self.alsaPlayHardwareCombo = self.uibuilder.get_object("comboOutput")
        self.alsaRecHardwareCombo = self.uibuilder.get_object("comboRecord")

        self.execMeasureBtn = self.uibuilder.get_object("buttonMeassure")
        self.execMeasureBtn.connect("clicked", self.on_execMeasure)

        self.alsaPlayHardwareList = alsaTools.getDeviceListFromAlsaOutput(
            "aplay")
        self.alsaRecHardwareList = alsaTools.getDeviceListFromAlsaOutput(
            "arecord")
        alsaTools.fillComboFromDeviceList(self.alsaPlayHardwareCombo,
                                self.alsaPlayHardwareList,
                                aCfg.playHardwareIndex)
        alsaTools.fillComboFromDeviceList(self.alsaRecHardwareCombo,
                                self.alsaRecHardwareList,
                                aCfg.recHardwareIndex)
        self.alsaRecHardwareCombo.connect("changed", self.on_recDeviceChanged)
        self.comboInputChanel = self.uibuilder.get_object("comboInputChanel")
        self.comboInputChanel.set_active(aCfg.recHardwareChannelIndex)
        # fill the number of input channels
        self.updateRecDeviceInfo()
        self.comboInputChanel.connect("changed", self.on_InputChanelChanged)

        calcDRCBtn = self.uibuilder.get_object("buttonCalculateFilter")
        calcDRCBtn.connect("clicked", self.on_calculateDRC)

        slider = self.uibuilder.get_object("scaleSweepAmplitude")
        slider.set_range(0.1, 1)
        slider.set_value_pos(Gtk.PositionType.TOP)
        self.sweep_level = aCfg.recordGain
        slider.set_value(self.sweep_level)
        slider.connect("value_changed", self.slider_changed)

        apply_closeBtn = self.uibuilder.get_object("apply_closeBtn")
        apply_closeBtn.connect("clicked", self.on_apply_settings)

        cancel_closeBtn = self.uibuilder.get_object("cancelButton")
        cancel_closeBtn.connect("clicked", self.on_Cancel)

        self.buttonSetImpRespFile = self.uibuilder.get_object(
            "buttonSetImpRespFile")

        self.buttonSetImpRespFile.connect("clicked", self.on_setImpRespFiles)

        self.comboDRC = self.uibuilder.get_object("combo_drc_type")
        self.cfgDRCButton = self.uibuilder.get_object("cfgDRCButton")
        self.cfgDRCButton.connect("clicked", self.on_cfgDRC)
        self.comboDRC.append_text("DRC")
        self.comboDRC.append_text("PORC")
        self.comboDRC.set_active(0)
        self.comboDRC.connect("changed", self.on_DRCTypeChanged)
        self.on_DRCTypeChanged(self.comboDRC)
        self.drcCfgDlg = DRCCfgDlg(self.parent)
        self.porcCfgDlg = PORCCfgDlg(self.parent)
        self.channelSelDlg = ChanelSelDlg(self.parent)
        self.impRespDlg = ImpRespDlg(self.parent, self.getMeasureResultsDir())
        self.targetCurveDlg = TargetCurveDlg(self.parent)

        self.exec_2ChannelMeasure = self.uibuilder.get_object(
            "checkbutton_2ChannelMeasure")
        self.exec_2ChannelMeasure.set_sensitive(True)

        self.spinbutton_NumChannels = self.uibuilder.get_object(
            "spinbutton_NumChannels")

        self.notebook = self.uibuilder.get_object("notebook1")
        self.volumeUpdateBlocked = False
        self.mode = None
        self.inputVolumeUpdate = InputVolumeProcess(
            self.progressbarInputVolume)
        self.comboboxFIRFilterMode = self.uibuilder.get_object(
            "comboboxFIRFilterMode")
        self.comboboxFIRFilterMode.set_active(aCfg.FIRFilterMode)
        self.comboboxFIRFilterMode.connect("changed",
            self.on_FIRFilterModeChanged)

        self.uibuilder.get_object("buttonTargetCurve").connect("clicked",
            self.on_EditTargetCurve)

    def __init__(self, parent):
        self.parent = parent

    def on_EditTargetCurve(self, button):
        impRespFile = self.impRespDlg.getImpRespFiles()[0].fileName
        self.targetCurveDlg.setImpRespFile(impRespFile)
        self.targetCurveDlg.run()

    def startInputVolumeUpdate(self, channel=None):
        if channel is None:
            channel = self.comboInputChanel.get_active_text()
        if not self.volumeUpdateBlocked:
            self.inputVolumeUpdate.start(self.getAlsaRecordHardwareString(),
                                         channel, self.mode)

    def on_setImpRespFiles(self, button):
        self.impRespDlg.run()

    def on_InputChanelChanged(self, combo):
        self.startInputVolumeUpdate(combo.get_active_text())

    def updateRecDeviceInfo(self):
        self.volumeUpdateBlocked = True
        recDeviceInfo = self.getRecordingDeviceInfo()
        if recDeviceInfo is None:
            return
        self.comboInputChanel.remove_all()
        # TODO: at the moment just 32 bit recording is supported. Maybe
        # check if other bitdepths make sense too
        self.mode = "S32_LE"
        if "S32_LE" in recDeviceInfo[1]:
            self.execMeasureBtn.set_sensitive(True)
        else:
            if len(recDeviceInfo[1]) < 1:
                print("no mode extracted : assuming S16_LE in that case")
                self.mode = "S16_LE"
            else:
                self.mode = recDeviceInfo[1][0]
            self.showMsgBox(
                "Recording device does not support 32 bit recording(S32_LE)")
            self.execMeasureBtn.set_sensitive(False)
        start = 0
        end = int(recDeviceInfo[0][0])
        if len(recDeviceInfo[0]) > 1:
            start = max(int(recDeviceInfo[0][0]) - 1, 0)
            end = int(recDeviceInfo[0][1])
        for chanel in range(start, end):
            self.comboInputChanel.append_text(str(chanel + 1))
        self.volumeUpdateBlocked = False
        self.comboInputChanel.set_active(0)
        return self.mode

    def on_recDeviceChanged(self, combo):
        self.updateRecDeviceInfo()

    def on_cfgDRC(self, button):
        drcMethod = self.comboDRC.get_active_text()
        if drcMethod == "DRC":
            self.drcCfgDlg.run()
        else:
            self.porcCfgDlg.run()

    def on_DRCTypeChanged(self, combo):
        drcMethod = combo.get_active_text()
        if drcMethod == "DRC":
            self.cfgDRCButton.set_label("configure DRC")
        else:
            self.cfgDRCButton.set_label("configure PORC")
            drcScript = [rb.find_plugin_file(self.parent, "calcFilterDRC")]
            pluginPath = os.path.dirname(os.path.abspath(drcScript[0]))
            porcTargetCurve = pluginPath + "/porc/data/tact30f.txt"
            if not os.path.exists(porcTargetCurve):
                print("installing PORC")
                installScript = rb.find_plugin_file(self.parent,
                                                    "installPORC.sh")
                pluginPath = os.path.dirname(installScript)
                porcInstCommand = "xterm -e " + installScript + " " + \
                                  pluginPath
                subprocess.call(porcInstCommand, shell=True)

    def slider_changed(self, hscale):
        self.sweep_level = hscale.get_value()

    def set_filter(self):
        DrcFilename = self.filechooserbtn.get_filename()
        self.parent.updateFilter(DrcFilename)

    def on_file_selected(self, widget):
        filterFile = widget.get_filename()
        if os.path.isfile(filterFile):
            self.saveSettings()

    def saveSettings(self):
        aCfg = DRCConfig()
        aCfg.filterFile = self.filechooserbtn.get_filename()
        aCfg.recordGain = self.sweep_level
        aCfg.sweepDuration = int(self.entrySweepDuration.get_text())
        aCfg.FIRFilterMode = self.comboboxFIRFilterMode.get_active()
        aCfg.playHardwareIndex = self.alsaPlayHardwareCombo.get_active()
        aCfg.recHardwareIndex = self.alsaRecHardwareCombo.get_active()
        aCfg.recHardwareChannelIndex = self.comboInputChanel.get_active()
        fileExt = os.path.splitext(aCfg.filterFile)[-1]
        print(("ext = " + fileExt))
        if fileExt != ".wav":
            if self.channelSelDlg.run() == Gtk.ResponseType.OK:
                aCfg.numFilterChanels = self.channelSelDlg.getNumChannels()
        aCfg.save()

    def on_apply_settings(self, some_param):
        self.saveSettings()
        self.dlg.set_visible(False)

    def updateBruteFIRCfg(self, enable):
        updateBruteFIRScript = [rb.find_plugin_file(self.parent,
                "updateBruteFIRCfg")]
        if enable is True:
            self.comboboxFIRFilterMode.set_active(2)
            updateBruteFIRScript.append(self.getAlsaPlayHardwareString())
            updateBruteFIRScript.append(self.filechooserbtn.get_filename())
        print('create bruteFIRConfig and start/install bruteFIR')
        updateBruteFIRCommand = "xterm -e " + " ".join(updateBruteFIRScript)
        subprocess.call(updateBruteFIRCommand, shell=True)

    def on_applyFilterBruteFIR(self):
        self.updateBruteFIRCfg(True)
        self.saveSettings()
        self.set_filter()

    def on_applyFilterGST(self):
        self.comboboxFIRFilterMode.set_active(1)
        self.saveSettings()
        self.set_filter()
        self.updateBruteFIRCfg(False)

    def disableFiltering(self):
        self.comboboxFIRFilterMode.set_active(0)
        self.saveSettings()
        self.set_filter()
        self.updateBruteFIRCfg(False)

    def on_FIRFilterModeChanged(self, some_param):
        FIRFilterMode = self.comboboxFIRFilterMode.get_active()
        if FIRFilterMode is 0:
            self.disableFiltering()
        elif FIRFilterMode is 1:
            self.on_applyFilterGST()
        else:
            self.on_applyFilterBruteFIR()

    def getRecordingDeviceInfo(self):
        try:
            params = ['arecord', '-D', self.getAlsaRecordHardwareString(),
                      '--dump-hw-params', '-d 1']
            print(("executing: " + str(params)))
            p = subprocess.Popen(params, 0, None, None, subprocess.PIPE,
                                 subprocess.PIPE)
            (out, err) = p.communicate()
            print(("hw infos : err : " + str(err) + " out : " + str(out)))
            # I rely on channels as it seems to be not translated
            pattern = re.compile("CHANNELS:\s\[?(\d{1,2})\s?(\d{1,2})?\]?",
                                 re.MULTILINE)
            numChanels = pattern.findall(str(err))
            # workaround to remove empty match in case of just single number
            # because I was not clever enough to have a clean
            # conditional regex...
            if len(numChanels[0]) > 1 and not numChanels[0][1]:
                print("only channel number present -> truncate")
                numChanels = [numChanels[0][0]]
            else:
                numChanels = [numChanels[0][0], numChanels[0][1]]
            pattern = re.compile("(\D\d+_\w*)", re.MULTILINE)
            supportedModes = pattern.findall(str(err))

            print(("numChannels : " + str(numChanels)))
            print(("supportedModes : " + str(supportedModes)))
            print(("No. supported Modes : " + str(len(supportedModes))))
            return [numChanels, supportedModes]
        except Exception as inst:
            print((
                'failed to get rec hardware info...',
                sys.exc_info()[0], type(inst), inst))
        return None

    def getAlsaPlayHardwareString(self):
        if len(self.alsaPlayHardwareList) < 1:
            print("no sound hardware detected")
            return
        alsHardwareSelIndex = self.alsaPlayHardwareCombo.get_active()
        alsaDevicePlayback = "hw:" + str(
            self.alsaPlayHardwareList[alsHardwareSelIndex][0]) + "," + str(
            self.alsaPlayHardwareList[alsHardwareSelIndex][2])
        print(("alsa output device : " + alsaDevicePlayback))
        return alsaDevicePlayback

    def getAlsaRecordHardwareString(self):
        if len(self.alsaRecHardwareList) < 1:
            print("no sound hardware detected")
            return
        alsHardwareSelIndex = self.alsaRecHardwareCombo.get_active()
        alsaDeviceRec = "hw:" + str(
            self.alsaRecHardwareList[alsHardwareSelIndex][0]) + "," + str(
            self.alsaRecHardwareList[alsHardwareSelIndex][2])
        print(("alsa input device : " + alsaDeviceRec))
        return alsaDeviceRec

    def getMeasureResultsDir(self):
        cachedir = RB.user_cache_dir() + "/DRC"
        measureResultsDir = cachedir + "/MeasureResults"
        if not os.path.exists(measureResultsDir):
            os.makedirs(measureResultsDir)
        return measureResultsDir

    def on_execMeasure(self, param):
        self.inputVolumeUpdate.stop()

        # TODO: make the measure script output the volume and parse from
        # there during measurement
        scriptName = rb.find_plugin_file(self.parent, "measure1Channel")
        #create new folder for this complete measurement
        strResultsDir = self.getMeasureResultsDir() + "/" +\
                        datetime.datetime.now().strftime("%Y%m%d%H%M%S_") + \
                        str(self.entrySweepDuration.get_text())
        os.makedirs(strResultsDir)
        raw_sweep_file_base_name = "/tmp/msrawsweep.pcm"
        raw_sweep_recorded_base_name = "/tmp/msrecsweep0.pcm"
        evalDlg = MeasureQADlg(self.parent, raw_sweep_file_base_name,
                           raw_sweep_recorded_base_name, self.sweep_level)
        iterLoopMeasure = 0
        acquiredImpResFiles = []
        while(True):
            impOutputFile = strResultsDir + "/" + str(iterLoopMeasure) + ".wav"
            # execute measure script to generate filters
            commandLine = [scriptName, str(self.sweep_level),
                       self.getAlsaRecordHardwareString(),
                       self.getAlsaPlayHardwareString(),
                       "10",
                       "21000",
                       str(self.entrySweepDuration.get_text()),
                       impOutputFile,
                       self.comboInputChanel.get_active_text(),
                       str(self.exec_2ChannelMeasure.get_active()),
                       str(int(self.spinbutton_NumChannels.get_value()))]
            p = subprocess.Popen(commandLine, 0, None, None, subprocess.PIPE,
                             subprocess.PIPE)
            (out, err) = p.communicate()
            print(("output from measure script : " + str(out) + " error : "
                + str(None)))
            # quality check:sweep file and measured result
            evalDlg.setImpRespFileName(impOutputFile)
            evalDlg.run()
            iterLoopMeasure += 1
            if evalDlg.Result == MeasureQARetVal.Reject:
                continue
            acquiredImpResFiles.append(evalDlg.impRespFile)
            if evalDlg.Result == MeasureQARetVal.Done:
                break
        self.impRespDlg.removeAll()
        self.impRespDlg.setFiles(acquiredImpResFiles)
        self.notebook.next_page()

    def changeCfgParamDRC(self, bufferStr, changeArray):
        newBuff = bufferStr
        for i in range(0, len(changeArray)):
            changeParams = changeArray[i]
            searchStr = changeParams[0] + " = "
            paramStart = bufferStr.find(searchStr)
            if paramStart > -1:
                paramEnd = bufferStr.find("\n", paramStart)
                if paramEnd > -1:
                    newBuff = bufferStr[0:paramStart + len(searchStr)] + \
                              changeParams[1] + bufferStr[
                                                paramEnd:len(bufferStr)]
            bufferStr = newBuff
        return newBuff

    def getTmpCfgDir(self):
        cachedir = RB.user_cache_dir() + "/DRC"
        tmpCfgDir = cachedir + "/TmpDRCCfg"
        if not os.path.exists(tmpCfgDir):
            os.makedirs(tmpCfgDir)
        return tmpCfgDir

    def prepareDRC(self, impRespFile, filterResultFile, targetCurveFile):
        drcScript = [rb.find_plugin_file(self.parent, "calcFilterDRC")]
        drcCfgFileName = os.path.basename(self.drcCfgDlg.getBaseCfg())
        print(("drcCfgBaseName : " + drcCfgFileName))
        drcCfgSrcFile = self.drcCfgDlg.getBaseCfg()
        drcCfgDestFile = self.getTmpCfgDir() + "/" + drcCfgFileName
        drcScript.append(drcCfgDestFile)
        print(("drcCfgDestFile : " + drcCfgDestFile))
        # update filter file
        srcDrcCfgFile = open(drcCfgSrcFile, "r")
        srcData = srcDrcCfgFile.read()
        micCalFile = self.drcCfgDlg.getMicCalibrationFile()
        normMethod = self.drcCfgDlg.getNormMethod()
        changeCfgFileArray = [["BCInFile", impRespFile],
                              ["PSPointsFile",
                                targetCurveFile],
                              ["PSNormType", normMethod]
                             ]
        if micCalFile is not None:
            changeCfgFileArray.append(["MCFilterType", "M"])
            changeCfgFileArray.append(["MCPointsFile", micCalFile])
        else:
            changeCfgFileArray.append(["MCFilterType", "N"])
        destData = self.changeCfgParamDRC(srcData, changeCfgFileArray)
        destDrcCfgFile = open(drcCfgDestFile, "w")
        destDrcCfgFile.write(destData)
        destDrcCfgFile.close()
        return drcScript

    def showMsgBox(self, msg):
        dlg = Gtk.MessageDialog(self.dlg, Gtk.DialogFlags.MODAL,
                                Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                msg)
        dlg.run()
        dlg.destroy()

    def getFilterResultsDir(self):
        cachedir = RB.user_cache_dir() + "/DRC"
        filterResultsDir = cachedir + "/DRCFilters"
        if not os.path.exists(filterResultsDir):
            print(
                ("DRC cache dir does not exist : creating -> " +
                filterResultsDir))
            os.makedirs(filterResultsDir)
        return filterResultsDir

    def getSampleShift(self, distanceInCentimeter):
        return int((1.2849 * distanceInCentimeter) + 0.5)

    def calculateAvgImpResponse(self, files):
        projectDir = os.path.dirname(os.path.abspath(files[0].fileName))
        impOutputFile = projectDir + "/impOutputFile"\
                + datetime.datetime.now().strftime("%Y%m%d%H%M%S_") + "avg.wav"
        maxValueStartOffset = 100
        maxValueEndOffset = 20000
        avgImpulseLength = maxValueEndOffset + maxValueStartOffset
        #loop over all impulse responses for all chanels and
        #calculate average response
        result = DRCFileTool.WaveParams()
        avgData = []
        for currFileInfo in files:
            params = DRCFileTool.LoadWaveFile(currFileInfo.fileName)
            result = DRCFileTool.WaveParams(params.numChannels)
            for chanel in range(0, params.numChannels):
                if len(avgData) <= chanel:
                    arr = [float(0.0)] * avgImpulseLength
                    avgData.append(arr)
                impulseStart = params.maxSampleValuePos[chanel] - \
                        maxValueStartOffset + self.getSampleShift(
                            currFileInfo.centerDistanceInCentimeter)
                print(("impulseStart:", impulseStart))
                for index in range(0, avgImpulseLength):
                    avgData[chanel][index] += float(params.data[chanel][
                        impulseStart + index] *
                            currFileInfo.weightingFactor)
                    #print(("avgData[chanel][index] : ",
                    #    avgData[chanel][index],
                    #    params.data[chanel][impulseStart + index]))
        #write the avg result to the result
        result.data = avgData
        print(("numChans Avg :", params.numChannels, result.numChannels,
            impOutputFile))
        DRCFileTool.WriteWaveFile(result, impOutputFile)
        return impOutputFile

    def on_calculateDRC(self, param):
        drcMethod = self.comboDRC.get_active_text()
        drcScript = [rb.find_plugin_file(self.parent, "calcFilterDRC")]
        pluginPath = os.path.dirname(os.path.abspath(drcScript[0]))
        filterResultFile = self.getFilterResultsDir() + "/Filter" + str(
            drcMethod) + datetime.datetime.now().strftime(
            "%Y%m%d%H%M%S") + ".wav"
        impRespFiles = self.impRespDlg.getImpRespFiles()
        #get number of channels from impRespFiles and loop over
        numChannels = DRCFileTool.getNumChannels(impRespFiles[0].fileName)
        soxMergeCall = ["sox", "-M"]
        channelFilterFile = ""
        for currChannel in range(0, numChannels):
            channelFilterFile = "/tmp/filter" + str(currChannel) + ".wav"
            soxMergeCall.append(channelFilterFile)
            #go through all impRespFiles, average them and pass the
            #result to the impRespFile
            avgImpRespFile = self.calculateAvgImpResponse(impRespFiles)
            #get target curve filename per channel
            targetCurveFileName = self.targetCurveDlg.getTargetCurveFileName(
                currChannel)
            if avgImpRespFile is None:
                self.showMsgBox("no file loaded")
                return
            if drcMethod == "DRC":
                drcScript = self.prepareDRC(avgImpRespFile, channelFilterFile,
                    targetCurveFileName)
                drcScript.append(avgImpRespFile)
                drcScript.append(channelFilterFile)
                drcScript.append(str(currChannel))
            elif drcMethod == "PORC":
                drcScript = [rb.find_plugin_file(self.parent, "calcFilterPORC")]
                porcCommand = pluginPath + "/porc/porc.py"
                if not os.path.isfile(porcCommand):
                    self.showMsgBox(
                        "porc.py not found. Please download from github and "
                        "install in the DRC plugin subfolder 'porc'")
                    return
                drcScript.append(porcCommand)
                drcScript.append(avgImpRespFile)
                drcScript.append(channelFilterFile)
                drcScript.append(str(currChannel))
                drcScript.append(targetCurveFileName)
                if self.porcCfgDlg.getMixedPhaseEnabled():
                    drcScript.append("--mixed")
            print(("drc command line: " + str(drcScript)))
            p = subprocess.Popen(drcScript, 0, None, None, subprocess.PIPE,
                                 subprocess.PIPE)
            (out, err) = p.communicate()
            print(("output from filter calculate script : " + str(out)))
        #use sox to merge all results to one filtefile
        soxMergeCall.append(filterResultFile)
        p = subprocess.Popen(soxMergeCall, 0, None, None, subprocess.PIPE,
            subprocess.PIPE)
        print(("output from sox filter merge : " + str(out)))
        self.filechooserbtn.set_filename(filterResultFile)
        self.set_filter()
        self.notebook.next_page()

    def on_close(self, shell):
        print("closing ui")
        self.inputVolumeUpdate.stop()
        self.dlg.set_visible(False)
        return True

    def show_ui(self, shell, state, dummy):
        print("showing UI")
        self.initUI()
        self.startInputVolumeUpdate()
        self.dlg.show_all()
        self.dlg.present()
        self.inputVolumeUpdate.stop()
        print("done showing UI")

    def on_destroy(self, widget, data):
        self.on_close(None)
        return True

    def on_Cancel(self, some_param):
        self.dlg.set_visible(False)
        self.inputVolumeUpdate.stop()
