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
from DRCUi import DRCDlg, ChanelSelDlg

import DRC_rb3compat
import math
import wave
from DRC_rb3compat import ActionGroup
from DRC_rb3compat import Action
from DRC_rb3compat import ApplicationShell

from DRCConfig import DRCConfig

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

class WaveParams:

    def __init__(self):
        self.DataOffset = 0
        self.numChannels = 0
        self.sampleByteSize = 0

# WavHeader.py
#   Extract basic header information from a WAV file
#...taken from http://blog.theroyweb.com/extracting-wav-file-header-information-using-a-python-script
#   slightly modified to pass out parse result
def PrintWavHeader(strWAVFile):
    """ Extracts data in the first 44 bytes in a WAV file and writes it
            out in a human-readable format
    """
    def DumpHeaderOutput(structHeaderFields):
        for key in structHeaderFields.keys():
            print( "%s: " % (key), structHeaderFields[key])
        # end for
    # Open file
    fileIn = open(strWAVFile, 'rb')
    # end try
    # Read in all data
    bufHeader = fileIn.read(38)
    # Verify that the correct identifiers are present
    #print( "bufHeader[0:4]", bufHeader[0:4].decode("utf-8"), " : ", str(bufHeader[0:4].decode("utf-8")) == 'RIFF' )
    if (bufHeader[0:4].decode("utf-8") != "RIFF") or \
       (bufHeader[12:16].decode("utf-8") != "fmt "):
         print("Input file not a standard WAV file")
         return
    # endif
    stHeaderFields = {'ChunkSize' : 0, 'Format' : '',
        'Subchunk1Size' : 0, 'AudioFormat' : 0,
        'NumChannels' : 0, 'SampleRate' : 0,
        'ByteRate' : 0, 'BlockAlign' : 0,
        'BitsPerSample' : 0, 'Filename': ''}
    # Parse fields
    stHeaderFields['ChunkSize'] = struct.unpack('<L', bufHeader[4:8])[0]
    stHeaderFields['Format'] = bufHeader[8:12]
    stHeaderFields['Subchunk1Size'] = struct.unpack('<L', bufHeader[16:20])[0]
    stHeaderFields['AudioFormat'] = struct.unpack('<H', bufHeader[20:22])[0]
    stHeaderFields['NumChannels'] = struct.unpack('<H', bufHeader[22:24])[0]
    stHeaderFields['SampleRate'] = struct.unpack('<L', bufHeader[24:28])[0]
    stHeaderFields['ByteRate'] = struct.unpack('<L', bufHeader[28:32])[0]
    stHeaderFields['BlockAlign'] = struct.unpack('<H', bufHeader[32:34])[0]
    stHeaderFields['BitsPerSample'] = struct.unpack('<H', bufHeader[34:36])[0]
    # Locate & read data chunk
    chunksList = []
    dataChunkLocation = 0
    fileIn.seek(0, 2) # Seek to end of file
    inputFileSize = fileIn.tell()
    nextChunkLocation = 12 # skip the RIFF header
    while 1:
        # Read subchunk header
        fileIn.seek(nextChunkLocation)
        bufHeader = fileIn.read(8)
        if bufHeader[0:4].decode("utf-8") == "data":
            print("data section found at : ", fileIn.tell() )
            dataChunkLocation = nextChunkLocation
        # endif
        nextChunkLocation += (8 + struct.unpack('<L', bufHeader[4:8])[0])
        chunksList.append(bufHeader[0:4])
        if nextChunkLocation >= inputFileSize:
            break
        # endif
    # end while
    # Dump subchunk list
    print( "Subchunks Found: ")
    for chunkName in chunksList:
        print( "%s, " % (chunkName),)
    # end for
    print("\n")
    # Dump data chunk information
    if dataChunkLocation != 0:
        fileIn.seek(dataChunkLocation)
        bufHeader = fileIn.read(8)
        print("Data Chunk located at offset [%s] of data length [%s] bytes" % \
            (dataChunkLocation, struct.unpack('<L', bufHeader[4:8])[0]))
    # endif
    # Print output
    stHeaderFields['Filename'] = os.path.basename(strWAVFile)
    DumpHeaderOutput(stHeaderFields)
    # Close file
    fileIn.close()
    params = WaveParams()
    params.DataOffset = int(dataChunkLocation) + 8
    params.numChanels = int(stHeaderFields['NumChannels'])
    params.sampleByteSize = int(stHeaderFields['BitsPerSample']/8)
    return params

def LoadRawFile(filename, numChanels, sampleByteSize = 4, offset = 0):
    #print(os.getcwd() + "\n")
    print("numChanels : ", numChanels)
    filterFile = open( filename, "rb" )
    #filter_data_right = open( aCfg.filterFile, "r" )
    #read the pcm data as 32 bit float
    filter_array = []
    filterFile.seek(offset)
    #debug
    #tmpData = filterFile.read()
    #filterFile.seek(offset)
    #tmpFilterFileName = "/home/tobias/.local/share/rhythmbox/plugins/DRC/tmpFilter.raw"
    #tmpFilterFile = open( tmpFilterFileName, "wb" )
    #tmpFilterFile.write(tmpData)
    #end debug
    readData = filterFile.read( sampleByteSize )
    count = 0
    while len(readData) == sampleByteSize:
        floatSample = 1.0
        for chanel in range(0, numChanels):
            #print("readData : " + str(len(readData)), str(readData) )
            #if chanel == 0:
            floatSample = floatSample * struct.unpack( 'f', readData )[0]
            readData = filterFile.read( sampleByteSize )
        if math.isnan(floatSample):
            print( "value is NaN : resetting to 0" )
            floatSample = 0
        if floatSample > 1 or floatSample < -1:
            print( "detected value probably out of range : ", floatSample )
        #TODO: check possibility to scale filter strength (configurable devisor etc...)
        filter_array.append( floatSample )

    #dump the filter to check
    #s = struct.pack('f'*len(filter_array), *filter_array)
    #f = open('/home/tobias/.local/share/rhythmbox/plugins/DRC/appliedFilter.raw','wb')
    #f.write(s)
    #f.close()
    return filter_array

def LoadWaveFile(filename):
    filter_array = []
    params = PrintWavHeader(filename)
    numChanels = params.numChanels
    print("numChanels : ", numChanels)
    return LoadRawFile( filename, numChanels, params.sampleByteSize, params.DataOffset )

class DRCPlugin(GObject.Object, Peas.Activatable):
    object = GObject.property(type = GObject.Object)
    def __init__(self):
        super(DRCPlugin, self).__init__()

    def updateFilter(self, filterFileName):
        filter_array = []
        if filterFileName != '':
            fileExt = os.path.splitext(filterFileName)[-1]
            print("ext = " + fileExt)
            if fileExt == ".wav":
                filter_array = LoadWaveFile(filterFileName)
            else:
                dlg = ChanelSelDlg(self)
                if dlg.run() == Gtk.ResponseType.OK:
                    filter_array = LoadRawFile(filterFileName, dlg.getNumChannels())
            #pass the filter data to the fir filter
            #print inspect.getdoc( self.fir_filter )
        num_filter_coeff = len( filter_array )
        if num_filter_coeff > 0:
            self.fir_filter.set_property( 'latency', int(num_filter_coeff /2) )
            print( "num_filter_coeff", num_filter_coeff )
            kernel = self.fir_filter.get_property('kernel')
            #print( "kernel : ", kernel)
            for i in range(0, num_filter_coeff):
                kernel.append( filter_array[i] )
                #print( filter_array[i] )
            self.fir_filter.set_property('kernel', kernel)

    def do_activate(self):
        try:
            self.shell = self.object
            self.shell_player = self.shell.props.shell_player
            self.player = self.shell_player.props.player
            #audioiirfilter
            self.fir_filter = Gst.ElementFactory.make('audiofirfilter', 'MyFIRFilter')
            print( "audiofirfilter :" + str(self.fir_filter) )
            #open filter files
            aCfg = DRCConfig()
            self.updateFilter(aCfg.filterFile)
            #print( inspect.getdoc( kernel ) )
            self.set_filter()
            print( "filter succesfully set" )
        except Exception as inst:
            print( 'filter not set',  sys.exc_info()[0], type(inst), inst )
            pass
        self.psc_id = self.shell_player.connect('playing-song-changed', self.playing_song_changed)
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
            print( 'adding filter' )
            self.player.add_filter(self.fir_filter)
            print('done setting filter' )
        except Exception as inst:
            print( 'unexpected exception',  sys.exc_info()[0], type(inst), inst )
            pass

    def do_deactivate(self):
        print( 'entering do_deactivate' )
        self.shell_player.disconnect(self.psc_id)

        try:
            self.player.remove_filter(self.fir_filter)
            print( 'filter disabled' )
            shell = self.object
            self._appshell.cleanup()
        except:
            pass

        del self.shell_player
        del self.shell
        del self.fir_filter

    def playing_song_changed(self, sp, entry):
        if entry == None:
            return
        genre = entry.get_string(RB.RhythmDBPropType.GENRE)
        print( "genre : ", str(genre) )
         #print( entry.get_string(RB.RhythmDBPropType.ALBUM) )
        #print( entry.get_string(RB.RhythmDBPropType.TITLE) )

    def find_file(self, filename):
        info = self.plugin_info
        data_dir = info.get_data_dir()
        path = os.path.join(data_dir, filename)

        if os.path.exists(path):
            return path

        return RB.file(filename)
