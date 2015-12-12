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
import subprocess
import re
import datetime
import threading

from gi.repository import Gtk, RB

from DRCConfig import DRCConfig
import DRCFileTool
import rb
from DRCTargetCurveUI import EQControl


class ChanelSelDlg():
    def __init__(self, parent):
        self.uibuilder = Gtk.Builder()
        self.uibuilder.add_from_file(
            rb.find_plugin_file(parent, "DRCUI.glade"))
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


class DRCCfgDlg():

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
        self.filechooserbuttonMicCalFile.set_current_folder(
            "/usr/share/drc/mic")
        self.comboboxtext_norm_method = self.uibuilder.get_object(
            "comboboxtext_norm_method")
        self.filechooserbuttonBaseCfg = self.uibuilder.get_object(
            "filechooserbuttonBaseCfg")
        self.filechooserbuttonBaseCfg.set_current_folder(
            "/usr/share/drc/config/44.1 kHz")
        self.filechooserbuttonBaseCfg.set_filename(
            "/usr/share/drc/config/44.1 kHz/erb-44.1.drc")

    def on_Ok(self, param):
        self.dlg.response(Gtk.ResponseType.OK)
        self.dlg.set_visible(False)

    def on_Cancel(self, param):
        self.dlg.response(Gtk.ResponseType.CANCEL)
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


class InputVolumeProcess():
    def __init__(self, updateProgressBar):
        self.progressBar = updateProgressBar
        self.proc = None
        self.t = None

    def reader_thread(self):
        for line in iter(self.proc.stdout.readline, b''):
            strLine = str(line)
            # print("reader_thread : " + strLine)
            result = self.pattern.findall(strLine)
            if len(result) > 0:
                # print("arecord: result : "+str(result))
                iValue = int(result[0])
                self.progressBar.set_fraction(iValue / 100)

    def start(self, recHW, chanel, mode=None):
        try:
            self.stop()
            if mode is None:
                mode = "S32_LE"
            # maybe using plughw and see if it removes the dependencies to
            # use that at all
            volAlsaCmd = ["arecord", "-D" + recHW, "-c" + chanel, "-d0",
                          "-f" + mode, "/dev/null", "-vvv"]
            print("starting volume monitoring with : " + str(volAlsaCmd))
            self.proc = subprocess.Popen(volAlsaCmd, stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT)
            self.pattern = re.compile("(\d*)%", re.MULTILINE)
            self.t = threading.Thread(None, target=self.reader_thread).start()
        except Exception as inst:
            print('unexpected exception', sys.exc_info()[0], type(inst), inst)

    def stop(self):
        print("stoping volume monitoring")
        if self.t is not None:
            self.t.terminate()
        if self.proc is not None:
            self.proc.terminate()
        self.progressBar.set_fraction(0.0)
        self.proc = None
        self.t = None


class MeasureQADlg():
    def __init__(self, parent, genSweepFile, measSweepFile, impRespFile,
                 sweep_level):
        self.uibuilder = Gtk.Builder()
        self.uibuilder.add_from_file(
            rb.find_plugin_file(parent, "DRCUI.glade"))
        self.dlg = self.uibuilder.get_object("measureQualityDlg")
        okBtn = self.uibuilder.get_object("button_OKMeasQA")
        okBtn.connect("clicked", self.on_Ok)

        btnViewAudacity = self.uibuilder.get_object("buttonViewRecSweep")
        btnViewAudacity.connect("clicked", self.on_viewRecSweep)

        audioParams = DRCFileTool.LoadAudioFile(genSweepFile, 1)
        self.setEvalData(audioParams, "labelInputSweepData")
        self.measSweepFile = measSweepFile
        audioParams = DRCFileTool.LoadAudioFile(measSweepFile, 1)
        minMaxRec = self.setEvalData(audioParams,
                                     "labelRecordedSweepData")
        audioParams = DRCFileTool.LoadAudioFile(impRespFile, 1)
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

    def on_Ok(self, param):
        self.dlg.response(Gtk.ResponseType.OK)
        self.dlg.set_visible(False)

    def run(self):
        print("running dlg...")
        return self.dlg.run()


def getDeviceListFromAlsaOutput(command):
    p = subprocess.Popen([command, "-l"], 0, None, None, subprocess.PIPE,
                         subprocess.PIPE)
    (out, err) = p.communicate()
    pattern = re.compile(
        "\w* (\d*):\s.*?\[(.*?)\],\s.*?\s(\d*):.*?\s\[(.*?)\]", re.MULTILINE)
    alsaHardwareList = pattern.findall(str(out))
    print("found pattern : " + str(alsaHardwareList))
    return alsaHardwareList


def fillComboFromDeviceList(combo, alsaHardwareList, active):
    for i in range(0, len(alsaHardwareList)):
        combo.append_text(
            alsaHardwareList[i][1] + ": " + alsaHardwareList[i][3])
    combo.set_active(active)


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

        self.entryStartFrequency = self.uibuilder.get_object(
            "entryStartFrequency")
        self.entryEndFrequency = self.uibuilder.get_object("entryEndFrequency")
        self.entrySweepDuration = self.uibuilder.get_object(
            "entrySweepDuration")
        self.entryStartFrequency.set_text(str(aCfg.startFrequency))
        self.entryEndFrequency.set_text(str(aCfg.endFrequency))
        self.entrySweepDuration.set_text(str(aCfg.sweepDuration))

        self.progressbarInputVolume = self.uibuilder.get_object(
            "progressbarInputVolume")

        self.alsaPlayHardwareCombo = self.uibuilder.get_object("comboOutput")
        self.alsaRecHardwareCombo = self.uibuilder.get_object("comboRecord")

        self.execMeasureBtn = self.uibuilder.get_object("buttonMeassure")
        self.execMeasureBtn.connect("clicked", self.on_execMeasure)

        self.alsaPlayHardwareList = getDeviceListFromAlsaOutput("aplay")
        self.alsaRecHardwareList = getDeviceListFromAlsaOutput("arecord")
        fillComboFromDeviceList(self.alsaPlayHardwareCombo,
                                self.alsaPlayHardwareList,
                                aCfg.playHardwareIndex)
        fillComboFromDeviceList(self.alsaRecHardwareCombo,
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

        self.impResponseFileChooserBtn = self.uibuilder.get_object(
            "impResponseFileChooserBtn")
        self.impResponseFileChooserBtn.set_current_folder(
            self.getMeasureResultsDir())
        self.impResponseFileChooserBtn.set_filter(audioFileFilter)
        self.filechooserbuttonTargetCurve = self.uibuilder.get_object(
            "filechooserbuttonTargetCurve")
        self.filechooserbuttonTargetCurve.set_current_folder(
            "/usr/share/drc/target/44.1 kHz")
        self.comboDRC = self.uibuilder.get_object("combo_drc_type")
        # TODO: check availibility of PORC & DRC and fill combo accordingly
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

        self.uibuilder.get_object("buttonEditTargetCurve").connect("clicked",
                                                self.on_editTargetCurve)

        self.exec_2ChannelMeasure = self.uibuilder.get_object(
            "checkbutton_2ChannelMeasure")
        self.exec_2ChannelMeasure.set_sensitive(True)

        self.entryMeasureIterations = self.uibuilder.get_object(
            "spinIterations")

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

    def __init__(self, parent):
        self.parent = parent

    def on_editTargetCurve(self, widget):
        editDlg = EQControl(self.filechooserbuttonTargetCurve.get_filename(),
                            self.parent)
        if editDlg.run() == Gtk.ResponseType.OK:
            self.filechooserbuttonTargetCurve.set_filename(
                editDlg.getTargetCurveFile())

    def getRecordingDeviceInfo(self):
        try:
            params = ['arecord', '-D', self.getAlsaRecordHardwareString(),
                      '--dump-hw-params', '-d 1']
            print("executing: " + str(params))
            p = subprocess.Popen(params, 0, None, None, subprocess.PIPE,
                                 subprocess.PIPE)
            (out, err) = p.communicate()
            print("hw infos : err : " + str(err) + " out : " + str(out))
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

    def startInputVolumeUpdate(self, channel=None):
        if channel is None:
            channel = self.comboInputChanel.get_active_text()
        if not self.volumeUpdateBlocked:
            self.inputVolumeUpdate.start(self.getAlsaRecordHardwareString(),
                                         channel, self.mode)

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
            self.filechooserbuttonTargetCurve.set_filename(
                "/usr/share/drc/target/44.1 kHz/bk-44.1.txt")
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
            self.filechooserbuttonTargetCurve.set_filename()

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
        aCfg.startFrequency = int(self.entryStartFrequency.get_text())
        aCfg.endFrequency = int(self.entryEndFrequency.get_text())
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
        p = subprocess.Popen(updateBruteFIRScript, 0, None, None,
            subprocess.PIPE, subprocess.PIPE)
        (out, err) = p.communicate()
        print(("output from bruteFIR update script : " + str(out)))

    def on_applyFilterBruteFIR(self):
        self.updateBruteFIRCfg(True)
        self.saveSettings()
        self.set_filter()
        self.checkbuttonEnableFiltering.set_active(True)

    def on_applyFilterGST(self):
        self.comboboxFIRFilterMode.set_active(1)
        self.saveSettings()
        self.set_filter()
        self.updateBruteFIRCfg(False)
        self.checkbuttonEnableFiltering.set_active(True)

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

    def getAlsaPlayHardwareString(self):
        if len(self.alsaPlayHardwareList) < 1:
            print("no sound hardware detected")
            return
        alsHardwareSelIndex = self.alsaPlayHardwareCombo.get_active()
        alsaDevicePlayback = "hw:" + str(
            self.alsaPlayHardwareList[alsHardwareSelIndex][0]) + "," + str(
            self.alsaPlayHardwareList[alsHardwareSelIndex][2])
        print("alsa output device : " + alsaDevicePlayback)
        return alsaDevicePlayback

    def getAlsaRecordHardwareString(self):
        if len(self.alsaRecHardwareList) < 1:
            print("no sound hardware detected")
            return
        alsHardwareSelIndex = self.alsaRecHardwareCombo.get_active()
        alsaDeviceRec = "hw:" + str(
            self.alsaRecHardwareList[alsHardwareSelIndex][0]) + "," + str(
            self.alsaRecHardwareList[alsHardwareSelIndex][2])
        print("alsa input device : " + alsaDeviceRec)
        return alsaDeviceRec

    def getMeasureResultsDir(self):
        cachedir = RB.user_cache_dir() + "/DRC"
        measureResultsDir = cachedir + "/MeasureResults"
        if not os.path.exists(measureResultsDir):
            os.makedirs(measureResultsDir)
        return measureResultsDir

    def calculateAvgImpResponse(self):
        numIterations = int(self.entryMeasureIterations.get_value())
        if numIterations > 1:
            numChanels = 2
            if not self.exec_2ChannelMeasure.get_active():
                numChanels = 1
            chanelSel = ['l', 'r']
            maxValueStartOffset = 100
            maxValueEndOffset = 20000
            avgImpulseLength = maxValueEndOffset + maxValueStartOffset
            #loop over all impulse responses for all chanels and
            #calculate average response
            result = DRCFileTool.WaveParams()
            for chanel in range(0, numChanels):
                avgData = []
                for index in range(0, avgImpulseLength):
                    avgData.append(float(0.0))
                for i in range(0, numIterations):
                    strfilename = "/tmp/ImpResp_" + chanelSel[chanel] + "_" + \
                        str(i) + ".pcm"
                    params = DRCFileTool.LoadRawFile(strfilename,
                        DRCFileTool.WaveParams(1))
                    impulseStart = params.maxSampleValuePos[0] - \
                        maxValueStartOffset
                    #impulseEnd = params.maxSampleValuePos + maxValueEndOffset
                    for index in range(0, avgImpulseLength):
                        avgData[index] += params.data[0][impulseStart + index]
                #finally normalize the result
                for index in range(0, avgImpulseLength):
                    avgData[index] = avgData[index] / float(numIterations)
                #write the avg result to the result
                result.data[chanel] = avgData
            impOutputFile = self.getMeasureResultsDir() + "/impOutputFile"\
                + datetime.datetime.now().strftime("%Y%m%d%H%M%S_") + \
                str(self.entryStartFrequency.get_text()) + \
                "_" + str(self.entryEndFrequency.get_text()) + \
                "_" + str(self.entrySweepDuration.get_text()) + "_avg.wav"
            DRCFileTool.WriteWaveFile(result, impOutputFile)

    def on_execMeasure(self, param):
        self.inputVolumeUpdate.stop()

        # TODO: make the measure script output the volume and parse from
        # there during measurement
        scriptName = rb.find_plugin_file(self.parent, "measure1Channel")
        impOutputFile = self.getMeasureResultsDir() + "/impOutputFile" + \
                        datetime.datetime.now().strftime("%Y%m%d%H%M%S_") + \
                        str(self.entryStartFrequency.get_text()) + \
                        "_" + str(self.entryEndFrequency.get_text()) + \
                        "_" + str(self.entrySweepDuration.get_text()) + ".wav"
        # execute measure script to generate filters
        commandLine = [scriptName, str(self.sweep_level),
                       self.getAlsaRecordHardwareString(),
                       self.getAlsaPlayHardwareString(),
                       str(self.entryStartFrequency.get_text()),
                       str(self.entryEndFrequency.get_text()),
                       str(self.entrySweepDuration.get_text()),
                       impOutputFile,
                       self.comboInputChanel.get_active_text(),
                       str(self.exec_2ChannelMeasure.get_active()),
                       str(int(self.entryMeasureIterations.get_value()))]
        p = subprocess.Popen(commandLine, 0, None, None, subprocess.PIPE,
                             subprocess.PIPE)
        (out, err) = p.communicate()
        print("output from measure script : " + str(out) + " error : " + str(
            None))
        self.uibuilder.get_object("impResponseFileChooserBtn").set_filename(
            impOutputFile)
        # TODO: check for errors
        # quality check:sweep file and measured result
        # TODO: do multi channel check
        strResultSuffix = ""
        if self.exec_2ChannelMeasure.get_active():
            strResultSuffix = "l"
        raw_sweep_file_base_name = "/tmp/msrawsweep.pcm"
        raw_sweep_recorded_base_name = "/tmp/msrecsweep" + strResultSuffix + \
                                       ".pcm"
        evalDlg = MeasureQADlg(self.parent, raw_sweep_file_base_name,
                               raw_sweep_recorded_base_name, impOutputFile,
                               self.sweep_level)
        evalDlg.run()
        self.notebook.next_page()
        self.calculateAvgImpResponse()

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

    def prepareDRC(self, impRespFile, filterResultFile):
        drcScript = [rb.find_plugin_file(self.parent, "calcFilterDRC")]
        drcCfgFileName = os.path.basename(self.drcCfgDlg.getBaseCfg())
        print("drcCfgBaseName : " + drcCfgFileName)
        drcCfgSrcFile = self.drcCfgDlg.getBaseCfg()
        drcCfgDestFile = self.getTmpCfgDir() + "/" + drcCfgFileName
        drcScript.append(drcCfgDestFile)
        print("drcCfgDestFile : " + drcCfgDestFile)
        # update filter file
        srcDrcCfgFile = open(drcCfgSrcFile, "r")
        srcData = srcDrcCfgFile.read()
        micCalFile = self.drcCfgDlg.getMicCalibrationFile()
        normMethod = self.drcCfgDlg.getNormMethod()
        changeCfgFileArray = [["BCInFile", impRespFile],
                              ["PSPointsFile",
                            self.filechooserbuttonTargetCurve.get_filename()],
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
                "DRC cache dir does not exist : creating -> " +
                filterResultsDir)
            os.makedirs(filterResultsDir)
        return filterResultsDir

    def on_calculateDRC(self, param):
        drcMethod = self.comboDRC.get_active_text()
        drcScript = [rb.find_plugin_file(self.parent, "calcFilterDRC")]
        pluginPath = os.path.dirname(os.path.abspath(drcScript[0]))
        filterResultFile = self.getFilterResultsDir() + "/Filter" + str(
            drcMethod) + datetime.datetime.now().strftime(
            "%Y%m%d%H%M%S") + ".wav"
        impRespFile = self.impResponseFileChooserBtn.get_filename()
        if impRespFile is None:
            self.showMsgBox("no file loaded")
            return
        if drcMethod == "DRC":
            drcScript = self.prepareDRC(impRespFile, filterResultFile)
        elif drcMethod == "PORC":
            drcScript = [rb.find_plugin_file(self.parent, "calcFilterPORC")]
            porcCommand = pluginPath + "/porc/porc.py"
            if not os.path.isfile(porcCommand):
                self.showMsgBox(
                    "porc.py not found. Please download from github and "
                    "install in the DRC plugin subfolder 'porc'")
                return
            drcScript.append(porcCommand)
            if self.porcCfgDlg.getMixedPhaseEnabled():
                drcScript.append("--mixed")
            drcScript.append(self.filechooserbuttonTargetCurve.get_filename())
        # execute measure script to generate filters
        # last 2 parameters for all scripts allways impulse response and
        # result filter
        drcScript.append(impRespFile)
        drcScript.append(filterResultFile)
        print("drc command line: " + str(drcScript))
        p = subprocess.Popen(drcScript, 0, None, None, subprocess.PIPE,
                             subprocess.PIPE)
        (out, err) = p.communicate()
        print("output from filter calculate script : " + str(out))
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
