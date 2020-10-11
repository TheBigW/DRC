GST_PLUGIN_VERSION=1.16.2
apt-get source gstreamer1.0-plugins-good
#sudo apt-get install auto-apt
#sudo auto-apt update
#sudo auto-apt updatedb && sudo auto-apt update-local
sudo apt-get install libglib2.0-dev
sudo apt-get install libglib2.0-dev
sudo apt-get install libgstreamer1.0-dev
sudo apt-get install libgstreamer-plugins-base1.0-dev
sudo apt-get install liborc-0.4-dev
sudo apt-get install libxext-dev
sudo apt-get install automake
cp *.c ./gst-plugins-good1.0-$GST_PLUGIN_VERSION/gst/audiofx
cp *.h ./gst-plugins-good1.0-$GST_PLUGIN_VERSION/gst/audiofx
#sudo auto-apt run ./gst-plugins-good1.0-1.4.5/configure
cd ./gst-plugins-good1.0-$GST_PLUGIN_VERSION
./configure
sudo make && sudo make install
if [ -d "/usr/lib/i386-linux-gnu/gstreamer-1.0/" ]; then
    sudo cp /usr/local/lib/gstreamer-1.0/* /usr/lib/i386-linux-gnu/gstreamer-1.0/
else if [ -d "/usr/lib/arm-linux-gnueabihf/gstreamer-1.0/" ]; then
    sudo cp /usr/local/lib/gstreamer-1.0/* /usr/lib/arm-linux-gnueabihf/gstreamer-1.0/
else
    sudo cp /usr/local/lib/gstreamer-1.0/* /usr/lib/x86_64-linux-gnu/gstreamer-1.0/

fi
