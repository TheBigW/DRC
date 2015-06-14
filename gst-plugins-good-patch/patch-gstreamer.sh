sudo apt-get source gst
cp *.c ./gst-plugins-good1.0-1.2.4/gst/audiofx
cp *.h ./gst-plugins-good1.0-1.2.4/gst/audiofx
sudo make && sudo make install && sudo cp /usr/local/lib/gstreamer-1.0/* /usr/lib/i386-linux-gnu/gstreamer-1.0/ 
