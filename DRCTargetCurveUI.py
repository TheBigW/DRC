# DRCTargetCurveUI.py
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
import rb

def loadTargetCurveFile(targetCurveFile):
    pattern = re.compile("\n?(\d\.?\d*)\s+(.*)\n?")
    curveValueArray = []

    with open(targetCurveFile) as fp:
        for line in fp:
            print("searching line:" + line )
            values = pattern.findall(line)
            print("found data:" + str(values))
            curveValueArray.append( values[0] )
    return curveValueArray

def writeTargetCurveFile(targetCurveFile, data):
    '''
    TODO:enforce DRC curve limitations : The first line must have a frequency equal
    to 0, the last line must have a frequency equal to BCSampleRate / 2 . A post
    filter definition file must have the following format:'''
    with open(targetCurveFile) as fp:
        for lineData in data:
            fp.write("%i %f\n" % lineData[0], lineData[1])

class LabeledEdit:
    def __init__(self, box, text, value, strDescription = None):
        label = Gtk.Label( text )
        box.add(label)
        self.entry = Gtk.Entry()
        if strDescription != None:
            self.entry.set_tooltip_text( strDescription )
            label.set_tooltip_text( strDescription )
        self.entry.set_text( value )
        box.add( self.entry )
        newToolTip = Gtk.Tooltip()
        print( inspect.getdoc(newToolTip) )
        #newToolTip.set_tip(self.entry, "some tooltip")

class AddDialog(Gtk.Dialog):
    params = []
    def __init__(self, parent, params = None):
        if None != params:
            self.params = params
        super(Gtk.Dialog, self).__init__()
        okBtn = self.add_button(Gtk.STOCK_OK,Gtk.ResponseType.OK)
        okBtn.connect( "clicked", self.on_ok )
        self.set_default_size(150, 100)
        box = self.get_content_area()
        self.freqLE = LabeledEdit( box, "frequency", str(self.params.frequency), "Frequency of the EQBand" )
        self.gainLE = LabeledEdit( box, "Gain", str(self.params.gain), "Gain of the EQBand" )
        self.show_all()
    def on_ok(self, param):
        self.params.append( (float(self.gainLE.entry.get_text()), float(self.freqLE.entry.get_text())) )

class EQGroupControl(Gtk.VBox):
    def __init__(self, frequency, amplitude, parent):
        super(Gtk.VBox, self).__init__(False)
        self.parent = parent
        self.slider = Gtk.VScale()
        self.slider.set_range( -100, 0 )
        self.slider.set_inverted(True)
        self.slider.set_value_pos( Gtk.PositionType.TOP )
        self.slider.set_size_request( 100, 300 )
        self.slider.set_value(amplitude)
        self.labelFreq = Gtk.Label( "f=" + str(frequency) + "Hz" )
        remBtn = Gtk.Button( "Remove" )
        remBtn.connect( "clicked", self.on_remove_band )
        self.add(self.slider)
        self.add(self.labelFreq)
        self.add(remBtn)
        self.show_all()
    def on_remove_band(self, param):
        self.parent.on_remove_band(self)
    def getAmplitude(self):
        return self.slider.get_value()
    def getFrequency(self):
        return int(self.labelFreq.entry.get_text())

class EQControl():
    def __init__(self, targetCurveFile, parent):
        #self.set_title( "N Bands parametric EQ" )
        addBtn = self.uibuilder = Gtk.Builder()
        self.uibuilder.add_from_file( rb.find_plugin_file(parent, "DRCUI.glade") )
        self.dlg = self.uibuilder.get_object("EQDlg")
        addBtn = self.uibuilder.get_object("buttonAddEQBand")
        addBtn.connect( "clicked", self.add_new_eq_band )
        closeBtn = self.uibuilder.get_object("button_CloseEQ")
        closeBtn.connect( "clicked", self.on_Ok )
        saveTargetCurveButton = self.uibuilder.get_object("saveTargetCurveButton")
        data = loadTargetCurveFile(targetCurveFile)
        self.eqBox = self.uibuilder.get_object("EQBox")
        self.rebuild_eq_controls(data)

    def rebuild_eq_controls(self, params):
        numEqBands = len(params)
        for i in range(0,numEqBands):
            self.eqBox.add(EQGroupControl( params[i][0], float(params[i][1]), self ))
        self.eqBox.show_all()
    def on_apply_settings(self, some_param):
        params = self.getEqParamListFromUI()
        #open file safe dialog and safe
        writeTargetCurveFile("/tmp/testCurve.txt", params)
    def getEqParamListFromUI(self ):
        params = []
        eqBandctrls = self.eqBox.get_children()
        print("children : ", len(eqBandctrls))
        numBands = len(eqBandctrls)
        for i in range(0,numBands):
            control = eqBandctrls[i]
            params.append( control.getFrequency(), control.getAmplitude() )
            #update UI in case of loudnes adaptation
        print("num bands :", len(params) )
        return params
    def add_new_eq_band(self, param):
        dlg = AddDialog(self)
        if dlg.run() == Gtk.ResponseType.OK :
            params=self.getEqParamListFromUI()
            params.append( dlg.params )
            numBands = len(params)
            self.rebuild_eq_controls(params)
        dlg.destroy()
    def on_remove_band(self,eqbandCtrl):
        params=self.getEqParamListFromUI()
        numParams = len(params)
        param = None
        for i in range(0,numParams):
            if eqbandCtrl.params.frequency == params[i].frequency:
                param = params[i]
                break
        params.remove(param)
        self.rebuild_eq_controls(params)
        self.gain_changed()
    def on_Ok(self, param):
        self.dlg.response(Gtk.ResponseType.OK)
        self.dlg.set_visible(False)
    def run(self):
        print("running dlg...")
        return self.dlg.run()