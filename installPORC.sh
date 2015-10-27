#!/bin/bash

PORC_DIR="$1"

if [ -z "$PORC_DIR" ]; then
    PORC_DIR="./"
fi

read -p "Do you want to install PORC and dependencies (Y/N)? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo apt-get install git python-numpy python-scipy python-matplotlib
    sudo mkdir $PORC_DIR
    cd $PORC_DIR
    sudo git clone https://github.com/zzzzrrr/porc.git
fi
