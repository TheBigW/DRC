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
import subprocess
import struct
import math
from array import array


class WaveParams:
    def __init__(self, numChannels=None):
        if numChannels is     None:
            self.numChannels = 2
        else:
            self.numChannels = numChannels
        self.DataOffset = 0
        self.sampleByteSize = 4
        self.maxSampleValue = []
        self.minSampleValue = []
        self.maxSampleValuePos = []
        self.minSampleValuePos = []
        self.data = []
        for chanel in range(0, self.numChannels):
            dataArr = []
            self.data.append(dataArr)
            self.maxSampleValue.append(-1)
            self.minSampleValue.append(1)
            self.maxSampleValuePos.append(-1)
            self.minSampleValuePos.append(-1)


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
            print(("%s: " % (key), structHeaderFields[key]))
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
        print(("%s, " % (chunkName), ))
    # end for
    print("\n")
    # Dump data chunk information
    if dataChunkLocation != 0:
        fileIn.seek(dataChunkLocation)
        bufHeader = fileIn.read(8)
        print(("Data Chunk located at offset [%s] of data length [%s] bytes" %
              (dataChunkLocation, struct.unpack('<L', bufHeader[4:8])[0])))
    # endif
    # Print output
    stHeaderFields['Filename'] = os.path.basename(strWAVFile)
    DumpHeaderOutput(stHeaderFields)
    # Close file
    fileIn.close()
    params = WaveParams(int(stHeaderFields['NumChannels']))
    params.DataOffset = int(dataChunkLocation) + 8
    params.sampleByteSize = int(stHeaderFields['BitsPerSample'] / 8)
    return params


def dumpSoundDataToFile(data, filename, writeAsText=False):
    f = open(
        filename,
        'wb')
    print("convert to array")
    float_array = array('f', data)
    print("writing to file...")
    float_array.tofile(f)
    f.close()
    # dump textual representation too
    if writeAsText:
        theFile = open(
            filename + '.txt',
            'w')
        for item in data:
            theFile.write("%s\n" % item)
        theFile.close()


def LoadRawFile(filename, params):
    print(("LoadRawFile : ", filename, " numChanels : ", params.numChannels))
    filterFile = open(filename, "rb")

    filterFile.seek(params.DataOffset)
    readData = filterFile.read(params.sampleByteSize)
    while len(readData) == params.sampleByteSize:
        for chanel in range(0, params.numChannels):
            floatSample = float(struct.unpack('f', readData)[0])
            readData = filterFile.read(params.sampleByteSize)
            if math.isnan(floatSample):
                #print(("value is: ", floatSample, "resetting to 0"))
                floatSample = float(0.0)
            if params.maxSampleValue[chanel] < floatSample:
                params.maxSampleValue[chanel] = floatSample
                params.maxSampleValuePos[chanel] = len(params.data[chanel])
                #print("found max : ",params.maxSampleValue,
                #    params.maxSampleValuePos)
            if params.minSampleValue[chanel] > floatSample:
                params.minSampleValue[chanel] = floatSample
                params.minSampleValuePos[chanel] = len(params.data[chanel])
            params.data[chanel].append(floatSample)
    # dump the filter to check
    if params.numChannels > 1:
        print(("loaded r/l: " + str(len(params.data[0])) + "/" +
            str(len(params.data[1])) + " samples per channel successfully"))
    else:
        print(("loaded one chanel filter: " + str(len(params.data[0])) +
            " with samples successfully"))
    print(("numChanels : ", params.numChannels, "maxPos : ",
        str(params.maxSampleValuePos), "maxValue : ",
        str(params.maxSampleValue), "file: ", filename))

    #dumpSoundDataToFile(params.data[0], /tmp/filterdmp.pcm, True)
    return params


def WriteWaveFile(params, outFileName):
    #poor mans way to write a wave file - we write 2 temporary pcm files
    #and convert to wav using sox :)
    commandLine = ['sox', '-M']
    pcmParams = ['-traw', '-c1', '-r41100', '-efloat', '-b32']
    #TODO : do properly once prototype works
    for chanel in range(0, params.numChannels):
        strFileName = "/tmp/channel_" + str(chanel) + ".pcm"
        commandLine.extend(pcmParams)
        print(("numChanels : ", params.numChannels, "chanel: ", chanel))
        dumpSoundDataToFile(params.data[chanel], strFileName)
        commandLine.append(strFileName)
    if params.numChannels > 1:
        commandLine.extend(['-twav'])
    else:
        commandLine = ['sox', '-traw', '-c1', '-r41100',
            '-efloat', '-b32']
        commandLine.append(strFileName)
        commandLine.extend(['-twav'])
    commandLine.append(outFileName)
    print(("executing sox to create wave file : " + str(commandLine)))
    p = subprocess.Popen(commandLine, 0, None, None, subprocess.PIPE,
        subprocess.PIPE)
    (out, err) = p.communicate()
    print(("output from sox conversion : " + str(out) + " error : " + str(err)))


def LoadWaveFile(filename):
    params = PrintWavHeader(filename)
    print(("LoadWaveFile: numChannels : ", params.numChannels))
    params = LoadRawFile(filename, params)
    return params


def fillTestFilter(filter_kernel):
    filter_array = filter_kernel
    itFilter = iter(filter_array)
    next(itFilter)
    for i in itFilter:
        filter_array.insert(0, i)
        next(itFilter)
    print(("test filter : " + str(filter_array)))
    return filter_array


def LoadAudioFile(filename, numChannels):
    # return fillTestFilter( [0.25, 0.23, 0.15, 0.06, 0, -0.06, -0.06,
    # -0.02, 0.0, 0.01, 0.01, 0] ) + fillTestFilter([0.25, 0.06, 0, -0.06,
    # -0.06, -0.02, 0, 0.01, 0.01, 0.0, 0.0, 0.0])
    print(("LoadAudioFile: ", filename, " numChanels : ", numChannels))
    if filename != '':
        fileExt = os.path.splitext(filename)[-1]
        print("ext = " + fileExt)
        if fileExt == ".wav":
            return LoadWaveFile(filename)
        params = WaveParams(numChannels)
        return LoadRawFile(filename, params)

