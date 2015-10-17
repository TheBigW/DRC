apt-get source gstreamer1.0-plugins-good
#sudo apt-get install auto-apt
#sudo auto-apt update
#sudo auto-apt updatedb && sudo auto-apt update-local
sudo apt-get install libglib2.0-dev
sudo apt-get install libgstreamer1.0-dev
sudo apt-get install libgstreamer-plugins-base1.0-dev
sudo apt-get install liborc-0.4-dev
sudo apt-get install automake
cp *.c ./gst-plugins-good1.0-1.4.5/gst/audiofx
cp *.h ./gst-plugins-good1.0-1.4.5/gst/audiofx
#sudo auto-apt run ./gst-plugins-good1.0-1.4.5/configure
./gst-plugins-good1.0-1.4.5/configure
cd ./gst-plugins-good1.0-1.4.5/gst/audiofx
sudo make && sudo make install && sudo cp /usr/local/lib/gstreamer-1.0/* /usr/lib/i386-linux-gnu/gstreamer-1.0/ 

