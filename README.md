DRC
============

A rhythmbox plugin for digital room correction.

As the room in which audio systems play influences the sound quite a bit the performasnce of speaker systems is usually degraded. Fortunately there are mechanisms that compensate for that: DRC (Digital Room Correction). It works in a way that a defined signal (log sweep) is played and its response is messured. From this the impulse response can be calculated to correct the influence of the room.
For a more advanced explanation google e.g. for the DRC tool documentation( "DRC: Digital Room Correction docu" ).

It can handle 32bit float mono filters as e.g. produced by PORC (search PORC on github) or DRCDesigner (also on github) and allows for one measuring/filter creation as well. Once the filter (from the plugin or external tools) is produced it can be loaded with this plugin to alow for music correction during play.

There are 3 steps in the process of DRC which can be executed independently. If no other tools are used (e.g. DRCDesigner, Room EQ Wizard, Dirac, Accurate) the complete steps from measurment, filter calculation and fillter usage can be done by this plugin.
In case of strating from scratch just exectute all 3 stages of the procedure. Each step produces the output of the next step.

<h3>1) measure room response</h3>

measuring plays a configurable sine sweep and measures its room response. For that purpose calibrated measurment equipment is needed. For DRC measurements it is recomended to have the microphone directed towards the speakers with its front centered at the usual listening position (middle of the head). I use a calibrated Behringer ECM8000 and a Focusrite 2i2 USB audio interface. The recording device needs to suport recording in the 32bit float format (S32_LE). All other devices will be shown but the measure-button will stay disabled. In case you already have a recorded Impulse response just proceed with step 2 (calculating your filter).
You need to select the proper input/output device and for input the correct channel where your microphone is connected. The recorded signal is monitored for quality and a dialog is shown with the evaluation results after measurement.

output: impulse response file which can be loaded to the filter correction

<h4>Caution:</h4>

It is advisable to start sweep play with lower volumes to not damage the equipment or you ears! The volume can be slowly turned up until a maximum is reached that does not make the furniture in your room vibrate as this will also cause artefacts.

Generally the longer and the louder the measurmenet is done the better the results (signal to noise ratio). Usually a 20s sweep gives good results already.

<h3>2) calculate the needed filter to correct room response </h3>

Calculating the filter depends on installed tools. Supported at the moment are PORC and DRC. Any way of created impulse response audio file can be used: either created by previous measurement step or by a another external tool.

output: a 32 bit audio file containing the filter than can be loaded for the room correction

<h3>3) apply the filter to the played music</h3>

load filter and enjoy :) --> no further dependencies

for installation just copy all files to ${HOME}/.local/share/rhythmbox/plugins/DRC or copy the complete package to any folder and install as super user with "make install".

<h4>Limitations</h4>

only fraction of DRC configurable capabilities is there, but files are available for edit in the plugin folder (for DRC adapt erb44100.drc)
		
<h3>Dependencies</h3>
genarly depends on python3-lxml for configuration support (needed to load the module). It is recommended to install audacity for direct evaluation of the recorded signal.
<h4>For measurment funtionality</h4>

depends on packages: sox, alsa-utils (uses aplay, arecord)
for installation on Ubuntu: sudo apt-get install alsa-utils sox
    
<h4>Filter creation functionality</h4>

	DRC :  depends on packages: sox, drc : sudo apt-get install sox drc
	PORC : depends on packages: sox, porc
	       for porc: sudo apt-get install python-numpy, python-scipy, python-matplotlib
            PORC can be found on github. To use it just download the complet package an get it running by installing all dependencies (mostly python libs). The plugin expects porc to be installed in
            the plugin folder under a separate folder (./porc/porc.py).

for those with some courage to try some new functionality: DRC supports multi channel correction, meaning a separate measure/filter per audio channel. To support this gstreamer plugins-good need to be patched as long as this change gets not a part of the gstreamer-plugins-good (see gst-plugins-good-patch folder) - I use it this way myself on Ubuntu 14.04/15.04.

<h4>experimenal functions and further development</h4>
There are 2 experimental functions which only work to a limited extend: brutefir support and iterative measurements. Both shall be understood as an outlook and are not fully supported yet. brutefir support at least creates a split of the current filter suitable for brutefir use directly in the home directory. Brutefir is a good way to achieve system wide DRC while the rhythmbox related application is limited just to RB. It works and I also ahve it in use on the PI and my PC, but brutefir setup needs still some manual steps (setup alsa-loop etc..)
<h3>averaged multi-measurements</h3>
Usually one good measurement approved by the QA - Dialog is sufficient to calculate a good correction filter (easiest default). It is possible to perform multiple measurements even across multiple positions and average the result. This can even be used to achieve a higher weight of the direct sounds vs the reflected sound. A good approach is to have one central measurement at the  listening position and multiple (up to 5) in 10 centimeter distance on the axis centered towards the speakers. The weight of the measurements shall be adapted according to the distance (central listening position measurement with the heighest weighting factor).

<h4>general notes on room accoustics</h4>
Even though DRC is a great tool to help with room accoustical problems it can't do miracles. It is recommended to do proper accoustical treatment for early reflections. All room correction only measures the sound getting toi the mic and cannot distinguish direct and reflected sound. For good stereo imaging it shall be evaluated to minimize early reflections. Accoustical treatment helps only in higher frequencies or at least is great effort (absorbers with huge volume) for deeper frequencies.

<h3>Bass in small rooms</h3>
Especially the bass response below 80Hz is critical as it is almost impossible to counter act with accoustical treatment. Speaker placement and/or usage of 2/4 subwoofers can help to minimize such problems. If needed I could (and will) describe in more detail how I achieved that in my listening room.

<h4>usage on the raspberry PI</h4>
Rhythmbox and room correction work on the raspberry PI! It can be insatlled on raspbian and the gstreamer as well as the brutefir FIR filtering works stable with no too significant CPU-load drain. Measuring on the PI works flawless. The PI only has issues with multi-channel USB soundcards.

<h4>Known issues</h4>
1) After measuring and filter calculation the filter can be directly applied. On some distributions this can cause audible issues and does not work. This can be worked around by just restarting rhythmbox.
2) for some reasons RB is not able to play continously once the FIR filter is set. A workaround got introduced that resets each track once started. That causes small gaps which are audible once continous tracks with gapless transition are played. Working on it :).

<h4>usage for home cinema measurements</h4>
The plugin now supports 5.1 maeasurements! See TODO for some limitations. 

<h4>TODO</h4>
- better documentation
- measurement sample rate shall be configurable
- 5.1 drc filter creation seems not yet to produce good result for the LFE channel, even with adapted target curve (for now just disabled correction for the LFE in the brutefir config)
- 5.1 measurement only supports digital output as AC3. TODO: also offer option for multichannel analog interfaces

Thanks to all the great guys doing amazing SW stuff in the web! This tool is just trying to put it together in an easy usable way.
