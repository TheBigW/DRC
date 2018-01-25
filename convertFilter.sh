#!/bin/bash

# Get command line parameters
RATE="44100"
WAV_FILTER_FILE="$1"

SOXI_RESULT="$(soxi $WAV_FILTER_FILE)"
regex="Channels       : ([0-9])"
[[ $SOXI_RESULT =~ $regex ]]
NUM_WAV_CHANNELS=${BASH_REMATCH[1]}
echo "runnign sox to create pcm filters for "$NUM_WAV_CHANNELS" channels"	
for ((i=1;i<=NUM_WAV_CHANNELS;i++));
do
	CURRENT_FILE=./filter_$i.pcm
	sox $WAV_FILTER_FILE -t raw -c 1 $CURRENT_FILE remix $i
done

#rebuild new wave filters
sox -t raw -r $RATE -c 1 -e float -b32 filter_1.pcm -t wav /tmp/filter_l.wav
sox -t raw -r $RATE -c 1 -e float -b32 filter_2.pcm -t wav /tmp/filter_r.wav
sox -M /tmp/filter_l.wav /tmp/filter_r.wav ./new_filter.wav
