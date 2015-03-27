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
from gi.repository import Gtk, Gio, Gdk, GdkPixbuf, Gst, RB
import os, sys, inspect, subprocess, re
import datetime
from DRCConfig import DRCConfig
import rb

class ChanelSelDlg():
    def __init__(self, parent):
        self.uibuilder = Gtk.Builder()
        self.uibuilder.add_from_file(rb.find_plugin_file(parent, "DRCUI.glade"))
        self.dlg = self.uibuilder.get_object("channel_no_dlg")
        okBtn = self.uibuilder.get_object("button_OK")
        okBtn.connect( "clicked", self.on_Ok )
        cancelBtn = self.uibuilder.get_object("button_Cancel")
        cancelBtn.connect( "clicked", self.on_Cancel )

    def on_Ok(self, param):
        self.dlg.response(Gtk.ResponseType.OK)
        self.dlg.destroy()
    def on_Cancel(self, param):
        self.dlg.response(Gtk.ResponseType.CANCEL)
        self.dlg.destroy()
    def run(self):
        print("running dlg...")
        return self.dlg.run()
    def getNumChannels(self):
        numChanels = 1
        check2Chan = self.uibuilder.get_object("radiobutton_2Channel")
        if check2Chan.get_active() == True:
            numChanels = 2
        return numChanels

class DRCCfgDlg():
    def __init__(self, parent):
        self.uibuilder = Gtk.Builder()
        self.uibuilder.add_from_file(rb.find_plugin_file(parent, "DRCUI.glade"))
        self.dlg = self.uibuilder.get_object("drcCfgDlg")
        okBtn = self.uibuilder.get_object("button_OKDRCDlg")
        okBtn.connect( "clicked", self.on_Ok )
        cancelBtn = self.uibuilder.get_object("button_CancelDRCDlg")
        cancelBtn.connect( "clicked", self.on_Cancel )
        self.filechooserbuttonMicCalFile = self.uibuilder.get_object("filechooserbuttonMicCalFile")
        self.filechooserbuttonMicCalFile.set_current_folder("/usr/share/drc/mic")
    def on_Ok(self, param):
        self.dlg.response(Gtk.ResponseType.OK)
        self.dlg.set_visible(False)
    def on_Cancel(self, param):
        self.dlg.response(Gtk.ResponseType.CANCEL)
        self.dlg.set_visible(False)
    def getMicCalibrationFile(self):
        return self.filechooserbuttonMicCalFile.get_filename()
    def run(self):
        print("running dlg...")
        return self.dlg.run()

def getDeviceListFromAlsaOutput( command ):
    p = subprocess.Popen([command, "-l"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    pattern = re.compile("\w* (\d*):\s.*?\[(.*?)\],\s.*?\s(\d*):.*?\s\[(.*?)\]", re.MULTILINE)
    alsaHardwareList = pattern.findall(str(out))
    print("found pattern : " + str(alsaHardwareList) )
    return alsaHardwareList

def fillComboFromDeviceList(combo, alsaHardwareList):
    for i in range(0, len(alsaHardwareList)):
        combo.append_text( alsaHardwareList[i][1] + ": " + alsaHardwareList[i][3] )
    combo.set_active(0)

class DRCDlg:
    def __init__(self, parent):
        #super(Gtk.Dialog, self).__init__()
        self.parent = parent
        aCfg = DRCConfig()
        self.uibuilder = Gtk.Builder()
        self.uibuilder.add_from_file( rb.find_plugin_file(parent, "DRCUI.glade") )
        self.dlg = self.uibuilder.get_object("DRCDlg")
        self.filechooserbtn = self.uibuilder.get_object("drcfilterchooserbutton")
        self.filechooserbtn.set_filename(aCfg.filterFile)
        self.filechooserbtn.connect("file-set", self.on_file_selected)
        self.filechooserbtn.set_current_folder( self.getFilterResultsDir() )

        self.entryStartFrequency = self.uibuilder.get_object("entryStartFrequency")
        self.entryEndFrequency = self.uibuilder.get_object("entryEndFrequency")
        self.entrySweepDuration = self.uibuilder.get_object("entrySweepDuration")
        self.entryStartFrequency.set_text( str(aCfg.startFrequency) )
        self.entryEndFrequency.set_text( str(aCfg.endFrequency) )
        self.entrySweepDuration.set_text( str(aCfg.sweepDuration) )

        self.alsaPlayHardwareCombo = self.uibuilder.get_object("comboOutput")
        self.alsaRecHardwareCombo = self.uibuilder.get_object("comboRecord")

        self.alsaPlayHardwareList = getDeviceListFromAlsaOutput("aplay")
        self.alsaRecHardwareList = getDeviceListFromAlsaOutput("arecord")
        fillComboFromDeviceList(self.alsaPlayHardwareCombo, self.alsaPlayHardwareList)
        fillComboFromDeviceList( self.alsaRecHardwareCombo, self.alsaRecHardwareList)

        execMeasureBtn = self.uibuilder.get_object("buttonMeassure")
        execMeasureBtn.connect( "clicked", self.on_execMeasure )

        calcDRCBtn = self.uibuilder.get_object("buttonCalculateFilter")
        calcDRCBtn.connect( "clicked", self.on_calculateDRC )

        slider = self.uibuilder.get_object("scaleSweepAmplitude")
        slider.set_range( 0.1, 1 )
        slider.set_value_pos( Gtk.PositionType.TOP )
        self.sweep_level = aCfg.recordGain
        slider.set_value(self.sweep_level)
        slider.connect( "value_changed", self.slider_changed )

        apply_closeBtn = self.uibuilder.get_object("apply_closeBtn")
        apply_closeBtn.connect( "clicked", self.on_apply_settings )
        print(" alsa play HW : ", self.getAlsaPlayHardwareString())

        cancel_closeBtn = self.uibuilder.get_object("cancelButton")
        cancel_closeBtn.connect( "clicked", self.on_Cancel )

        self.impResponseFileChooserBtn = self.uibuilder.get_object("impResponseFileChooserBtn")
        self.impResponseFileChooserBtn.set_current_folder( self.getMeasureResultsDir() )

        self.comboDRC = self.uibuilder.get_object("combo_drc_type")
        #TODO: check availibility of PORC & DRC and fill combo accordingly
        self.cfgDRCButton = self.uibuilder.get_object("cfgDRCButton")
        self.cfgDRCButton.connect( "clicked", self.on_cfgDRC )
        self.comboDRC.append_text("DRC")
        self.comboDRC.append_text("PORC")
        self.comboDRC.set_active(0)
        self.comboDRC.connect("changed", self.on_DRCTypeChanged)
        self.drcCfgDlg = DRCCfgDlg(self.parent)

    def on_cfgDRC(self,button):
        self.drcCfgDlg.run()

    def on_DRCTypeChanged(self, combo):
        drcMethod = combo.get_active_text()
        if drcMethod == "DRC":
            self.cfgDRCButton.show()
        else:
            self.cfgDRCButton.hide()

    def slider_changed(self, hscale):
        self.sweep_level = hscale.get_value();

    def on_file_selected(self, widget):
        DrcFilename= widget.get_filename()
        fileExt = os.path.splitext(DrcFilename)[-1]
        numChanels = None
        print("ext = " + fileExt)
        if fileExt != ".wav":
            dlg = ChanelSelDlg(self.parent)
            if dlg.run() == Gtk.ResponseType.OK:
                numChanels = dlg.getNumChannels()
        self.parent.updateFilter(DrcFilename, numChanels)
        self.saveSettings(numChanels)

    def saveSettings(self, numChanels=None):
        aCfg = DRCConfig()
        aCfg.filterFile = self.filechooserbtn.get_filename()
        aCfg.recordGain = self.sweep_level
        aCfg.startFrequency = int( self.entryStartFrequency.get_text() )
        aCfg.endFrequency = int( self.entryEndFrequency.get_text() )
        aCfg.sweepDuration = int( self.entrySweepDuration.get_text() )
        if numChanels != None:
            aCfg.numFilterChanels = numChanels
        aCfg.save()
    def on_apply_settings(self, some_param):
        self.saveSettings()
        self.dlg.set_visible(False)

    def getAlsaPlayHardwareString(self):
        if len(self.alsaPlayHardwareList) < 1:
            print("no sound hardware detected")
            return
        alsHardwareSelIndex = self.alsaPlayHardwareCombo.get_active()
        alsaDevicePlayback = "hw:" + str(self.alsaPlayHardwareList[alsHardwareSelIndex][0]) + "," + str(self.alsaPlayHardwareList[alsHardwareSelIndex][2])
        print("alsa output device : " + alsaDevicePlayback)
        return alsaDevicePlayback

    def getAlsaRecordHardwareString(self):
        if len(self.alsaRecHardwareList) < 1:
            print("no sound hardware detected")
            return
        alsHardwareSelIndex = self.alsaRecHardwareCombo.get_active()
        alsaDeviceRec = "hw:" + str(self.alsaRecHardwareList[alsHardwareSelIndex][0]) + "," + str(self.alsaRecHardwareList[alsHardwareSelIndex][2])
        print("alsa input device : " + alsaDeviceRec)
        return alsaDeviceRec

    def getMeasureResultsDir(self):
        cachedir = RB.user_cache_dir() + "/DRC"
        measureResultsDir = cachedir + "/MeasureResults"
        if not os.path.exists(measureResultsDir):
            os.makedirs(measureResultsDir)
        return measureResultsDir

    def on_execMeasure(self, param):
        scriptName = rb.find_plugin_file(self.parent, "measure1Channel")
        impOutputFile = self.getMeasureResultsDir() + "/impOutputFile" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") +".pcm"
        #execute measure script to generate filters
        commandLine = [scriptName, str(self.sweep_level),
                                self.getAlsaRecordHardwareString(),
                                self.getAlsaPlayHardwareString(),
                                str(self.entryStartFrequency.get_text()),
                                str(self.entryEndFrequency.get_text()),
                                str(self.entrySweepDuration.get_text()),
                                impOutputFile]
        p = subprocess.Popen(commandLine, stdout=subprocess.PIPE)
        out, err = p.communicate()
        print( "output from measure script : " + str(out) )
        #TODO: check for errors
        self.uibuilder.get_object("impResponseFileChooserBtn").set_filename(impOutputFile)

    def changeCfgParamDRC(self, bufferStr, changeArray):
        newBuff = bufferStr
        for i in range(0,len(changeArray)):
            changeParams = changeArray[i]
            searchStr = changeParams[0] + " = "
            paramStart = bufferStr.find( searchStr )
            if paramStart > -1:
                paramEnd = bufferStr.find( "\n", paramStart )
                if paramEnd > -1:
                    newBuff = bufferStr[0:paramStart + len(searchStr)] + changeParams[1] + bufferStr[paramEnd:len(bufferStr)]
            bufferStr = newBuff
        return newBuff

    def getTmpCfgDir(self):
        cachedir = RB.user_cache_dir() + "/DRC"
        tmpCfgDir = cachedir + "/TmpDRCCfg"
        if not os.path.exists(tmpCfgDir ):
            os.makedirs(tmpCfgDir)
        return tmpCfgDir

    def prepareDRC( self, impRespFile, filterResultFile ):
        drcScript = [rb.find_plugin_file(self.parent, "calcFilterDRC")]
        drcCfgFileName = "erb44100.drc"
        drcCfgSrcFile = rb.find_plugin_file(self.parent, drcCfgFileName)
        drcCfgDestFile = self.getTmpCfgDir() + "/" + drcCfgFileName
        drcScript.append( drcCfgDestFile )
        print("drcCfgDestFile : " + drcCfgDestFile )
        #update filter file
        srcDrcCfgFile = open( drcCfgSrcFile, "r" )
        srcData = srcDrcCfgFile.read()
        micCalFile = self.drcCfgDlg.getMicCalibrationFile()
        changeCfgFileArray = [["BCInFile", impRespFile], ["PSPointsFile", rb.find_plugin_file(self.parent, "pa-44100.txt")]]
        if micCalFile != None:
            changeCfgFileArray.append( ["MCFilterType","M"] )
            changeCfgFileArray.append( ["MCPointsFile",micCalFile] )
        else:
            changeCfgFileArray.append( ["MCFilterType","N"] )
        destData = self.changeCfgParamDRC(srcData, changeCfgFileArray)
        destDrcCfgFile = open( drcCfgDestFile, "w" )
        destDrcCfgFile.write(destData)
        return drcScript

    def showMsgBox(self, msg):
        dlg = Gtk.MessageDialog(self.dlg, Gtk.DialogFlags.MODAL, Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE, msg)
        dlg.run()
        dlg .destroy()

    def getFilterResultsDir(self):
        cachedir = RB.user_cache_dir() + "/DRC"
        filterResultsDir = cachedir + "/DRCFilters"
        if not os.path.exists(filterResultsDir):
            os.makedirs(filterResultsDir)
        return filterResultsDir

    def on_calculateDRC(self, param):
        drcMethod = self.comboDRC.get_active_text()
        drcScript = [rb.find_plugin_file(self.parent, "calcFilterDRC")]
        pluginPath = os.path.dirname(os.path.abspath(drcScript[0] ))
        filterResultFile = self.getFilterResultsDir() + "/Filter" + str(drcMethod) + datetime.datetime.now().strftime("%Y%m%d%H%M%S") +".pcm"
        impRespFile = self.impResponseFileChooserBtn.get_filename()
        if impRespFile == None:
            self.showMsgBox("no file loaded")
            return
        if drcMethod == "DRC":
            drcScript = self.prepareDRC(impRespFile,filterResultFile)
        elif drcMethod == "PORC":
            drcScript = [rb.find_plugin_file(self.parent, "calcFilterPORC")]
            porcCommand = pluginPath+"/porc/porc.py"
            if not os.path.isfile(porcCommand):
                self.showMsgBox("porc.py not found. Please download from github and install in the DRC plugin subfolder 'porc'")
                return
            drcScript.append(porcCommand)
        #execute measure script to generate filters
        #last 2 parameters for all scripts allways impulse response and result filter
        drcScript.append(impRespFile)
        drcScript.append(filterResultFile)
        print( "drc command line: " + str(drcScript) )
        p = subprocess.Popen( drcScript, stdout=subprocess.PIPE)
        out, err = p.communicate()
        print( "output from filter calculate script : " + str(out) )
        self.filechooserbtn.set_filename(filterResultFile)

    def on_close(self, shell):
        print( "closing ui")
        self.dlg.set_visible(False)
        return True

    def show_ui(self, shell, state, dummy):
        print("showing UI")
        self.dlg.show_all()
        self.dlg.present()
        print( "done showing UI" )

    def on_destroy(self, widget, data):
        self.on_close(None)
        return True

    def on_Cancel(self, some_param):
        self.dlg.set_visible(False)
