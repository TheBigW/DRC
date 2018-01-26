#!/bin/bash
AMPLITUDE="$1"
INPUT_HW="$2"
OUTPUT_HW="$3"
START_FREQ="$4"
END_FREQ="$5"
DURATION="$6"
IMP_OUT_FILE="$7"
REC_CHANNEL="$8"
SEPARATE_CHANNEL="$9"
NUM_CHANNELS="${10}"
SAMPLE_RATE="${11}"

dt=$(date '+%d%m%Y%H%M%S');
./measure1Channel 1 hw:1,0 hw:0,0 10 22050 15 ~/impout_$dt.wav 1 True 2 44100