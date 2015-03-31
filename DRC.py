# DRC.py
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

import os, sys, inspect, struct

from gi.repository import GObject, Gst, Peas, RB, Gtk, Gdk, GdkPixbuf
from DRCUi import DRCDlg

import DRC_rb3compat
from DRC_rb3compat import ActionGroup
from DRC_rb3compat import Action
from DRC_rb3compat import ApplicationShell

from DRCConfig import DRCConfig
import DRCFileTool

ui_string="""
<ui>
  <menubar name="MenuBar">
    <menu name="ControlMenu" action="Control">
      <placeholder name="PluginPlaceholder">
        <menuitem name="Digital Room Correction" action="DRC"/>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""

class DRCPlugin(GObject.Object, Peas.Activatable):
    object = GObject.property(type = GObject.Object)
    def __init__(self):
        super(DRCPlugin, self).__init__()

    def updateFilter(self, filterFileName, numChannels = None):
        try:
            self.remove_Filter()
            filter_array = DRCFileTool.LoadAudioFile(filterFileName, numChannels)
            #pass the filter data to the fir filter
            num_filter_coeff = len( filter_array )
            if num_filter_coeff > 0:
                self.fir_filter.set_property( 'latency', int(num_filter_coeff/2) )
                print( "num_filter_coeff", num_filter_coeff )
                kernel = self.fir_filter.get_property('kernel')
                kernel = []
                print( "kernel : ", kernel)
                for i in range(0, num_filter_coeff):
                    kernel.append( filter_array[i] )
                    #print( filter_array[i] )
                #TODO: check possibility to scale filter strength (configurable devisor etc...)
                self.fir_filter.set_property('kernel', kernel)
            self.set_filter()
        except Exception as inst:
            print( 'error updating filter',  sys.exc_info()[0], type(inst), inst )
            pass

    def do_activate(self):
        try:
            self.filterSet = False
            self.shell = self.object
            self.shell_player = self.shell.props.shell_player
            self.player = self.shell_player.props.player
            self.fir_filter = Gst.ElementFactory.make('audiofirfilter', 'MyFIRFilter')
            #open filter files
            aCfg = DRCConfig()
            self.updateFilter(aCfg.filterFile, aCfg.numFilterChanels)
            #print( str(dir( self.shell.props)) )
        except Exception as inst:
            print( 'filter not set',  sys.exc_info()[0], type(inst), inst )
            pass
        self.psc_id = self.shell_player.connect('playing-song-changed', self.playing_song_changed)
        #no possible workaround as somehow never reaches end of song :(
        #self.psc_id = self.shell_player.connect('elapsed-changed', self.elapsed_changed)
        #finally add UI
        self.add_ui( self, self.shell )

    def add_ui(self, plugin, shell):
        self.drcDlg = DRCDlg(self)
        print("starting add_ui")
        action_group = ActionGroup(shell, 'DRCActionGroup')
        action_group.add_action(func=self.drcDlg.show_ui,
            action_name='DRC', label=_('_DRC'),
            action_type='app')
        self._appshell = ApplicationShell(shell)
        self._appshell.insert_action_group(action_group)
        self._appshell.add_app_menuitems(ui_string, 'DRCActionGroup')
        print("add_ui done")

    def set_filter(self):
        try:
            if not self.filterSet:
                print( 'adding filter' )
                self.player.add_filter(self.fir_filter)
                print('done setting filter' )
            self.filterSet = True
        except Exception as inst:
            print( 'unexpected exception',  sys.exc_info()[0], type(inst), inst )
            pass

    def remove_Filter(self):
        try:
            if self.filterSet:
                self.player.remove_filter(self.fir_filter)
                print( 'filter disabled' )
            self.filterSet = False
        except:
            pass

    def do_deactivate(self):
        print( 'entering do_deactivate' )
        self.shell_player.disconnect(self.psc_id)

        try:
            self.remove_Filter()
            self._appshell.cleanup()
        except:
            pass

        del self.shell_player
        del self.shell
        del self.fir_filter

    def elapsed_changed(self, sp, elapsed):
        #workaround due to FIR filter issues during playing back multiple songs
        #switching as well as new song select in UI seems to fix that
        duration = sp.get_playing_song_duration()
        #print("duration: " + str(duration))
        #print("elapsed : " + str(elapsed) )
        diff = duration - elapsed
        #print("diff : " + str(diff))
        if diff <= 1:
            print("end of song reached : skip next")
            #time.sleep(0.5)
            sp.do_next()

    def playing_song_changed(self, sp, entry):
        if entry == None:
            return
        #workaround due to FIR filter issues during playing back multiple songs
        #switching as well as new song select in UI seems to fix that
        '''TODO: this will fail for manually selecting last song in list in UI
            clean way would be to check has-prev/has-next but seems to be useless:
            returns true even if no son is previous in current UI list...
        '''
        sp.do_next()
        sp.do_previous()

    def find_file(self, filename):
        info = self.plugin_info
        data_dir = info.get_data_dir()
        path = os.path.join(data_dir, filename)

        if os.path.exists(path):
            return path

        return RB.file(filename)
