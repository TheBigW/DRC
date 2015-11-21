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
import os
import struct
import math
from array import array


class WaveParams:
    def __init__(self):
        self.DataOffset = 0
        self.numChannels = 0
        self.sampleByteSize = 0


# WavHeader.py
#   Extract basic header information from a WAV file
# ...taken from http://blog.theroyweb.com/extracting-wav-file-header
# -information-using-a-python-script
#   slightly modified to pass out parse result
def PrintWavHeader(strWAVFile):
    """ Extracts data in the first 44 bytes in a WAV file and writes it
            out in a human-readable format
    """

    def DumpHeaderOutput(structHeaderFields):
        for key in structHeaderFields.keys():
            print("%s: " % (key), structHeaderFields[key])
            # end for

    # Open file
    fileIn = open(strWAVFile, 'rb')
    # end try
    # Read in all data
    bufHeader = fileIn.read(38)
    # Verify that the correct identifiers are present
    # print( "bufHeader[0:4]", bufHeader[0:4].decode("utf-8"), " : ",
    # str(bufHeader[0:4].decode("utf-8")) == 'RIFF' )
    if (bufHeader[0:4].decode("utf-8") != "RIFF") or \
            (bufHeader[12:16].decode("utf-8") != "fmt "):
        print("Input file not a standard WAV file")
        return
    # endif
    stHeaderFields = {'ChunkSize': 0, 'Format': '',
                      'Subchunk1Size': 0, 'AudioFormat': 0,
                      'NumChannels': 0, 'SampleRate': 0,
                      'ByteRate': 0, 'BlockAlign': 0,
                      'BitsPerSample': 0, 'Filename': ''}
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
    fileIn.seek(0, 2)  # Seek to end of file
    inputFileSize = fileIn.tell()
    nextChunkLocation = 12  # skip the RIFF header
    while 1:
        # Read subchunk header
        fileIn.seek(nextChunkLocation)
        bufHeader = fileIn.read(8)
        if bufHeader[0:4].decode("utf-8") == "data":
            print("data section found at : ", fileIn.tell())
            dataChunkLocation = nextChunkLocation
        # endif
        nextChunkLocation += (8 + struct.unpack('<L', bufHeader[4:8])[0])
        chunksList.append(bufHeader[0:4])
        if nextChunkLocation >= inputFileSize:
            break
            # endif
    # end while
    # Dump subchunk list
    print("Subchunks Found: ")
    for chunkName in chunksList:
        print("%s, " % (chunkName), )
    # end for
    print("\n")
    # Dump data chunk information
    if dataChunkLocation != 0:
        fileIn.seek(dataChunkLocation)
        bufHeader = fileIn.read(8)
        print("Data Chunk located at offset [%s] of data length [%s] bytes" %
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
    params.sampleByteSize = int(stHeaderFields['BitsPerSample'] / 8)
    return params


def debugDumpAppliedFilter(filter_array):
    f = open(
        '/tmp/appliedFilter.raw',
        'wb')
    print("convert to array")
    float_array = array('f', filter_array)
    print("writing to file...")
    float_array.tofile(f)
    f.close()
    # dump textual representation too
    theFile = open(
        '/tmp/appliedFilter.txt',
        'w')
    for item in filter_array:
        theFile.write("%s\n" % item)
    theFile.close()


def LoadRawFile(filename, numChanels, sampleByteSize=4, offset=0):
    print("numChanels : ", numChanels)
    filterFile = open(filename, "rb")
    filter_array = []
    for chanel in range(0, numChanels):
        channel_filter = []
        filter_array.append(channel_filter)
    filterFile.seek(offset)
    readData = filterFile.read(sampleByteSize)
    while len(readData) == sampleByteSize:
        for chanel in range(0, numChanels):
            floatSample = struct.unpack('f', readData)[0]
            readData = filterFile.read(sampleByteSize)
            if math.isnan(floatSample):
                # print( "value is NaN : resetting to 0" )
                floatSample = 0
            filter_array[chanel].append(floatSample)
    # dump the filter to check
    print(("loaded r/l: " + str(len(filter_array[0])) + "/" +
        str(len(filter_array[1])) + " samples per channel successfully"))
    #debugDumpAppliedFilter(filter_array[0])
    return filter_array


def LoadWaveFile(filename):
    params = PrintWavHeader(filename)
    numChanels = params.numChanels
    print("numChanels : ", numChanels)
    return LoadRawFile(filename, numChanels, params.sampleByteSize,
                       params.DataOffset)


def fillTestFilter(filter_kernel):
    filter_array = filter_kernel
    itFilter = iter(filter_array)
    next(itFilter)
    for i in itFilter:
        filter_array.insert(0, i)
        next(itFilter)
    print("test filter : " + str(filter_array))
    return filter_array


def LoadAudioFile(filename, numChannels):
    filter_array = [[]]
    # return fillTestFilter( [0.25, 0.23, 0.15, 0.06, 0, -0.06, -0.06,
    # -0.02, 0.0, 0.01, 0.01, 0] ) + fillTestFilter([0.25, 0.06, 0, -0.06,
    # -0.06, -0.02, 0, 0.01, 0.01, 0.0, 0.0, 0.0])
    if filename != '':
        fileExt = os.path.splitext(filename)[-1]
        print("ext = " + fileExt)
        if fileExt == ".wav":
            filter_array = LoadWaveFile(filename)
        else:
            filter_array = LoadRawFile(filename, numChannels)
    return filter_array
