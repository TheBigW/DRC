DRC
============

A rhythmbox plugin for digital room correction.

As the room in which audio systems play influences the sound quite a bit the performasnce of speaker systems is usually degraded. Fortunately there are mechanisms that compensate for that: DRC (Digital Room Correction). It works in a way that a defined signal (log sweep) is played and its response is messured. From this the impulse response can be calculated to correct the influence of the room.
For a more advanced explanation google e.g. for the DRC tool documentation( "DRC: Digital Room Correction docu" ).

It can handle 32bit float mono filters as e.g. produced by PORC (search PORC on github) or DRCDesigner (also on github) and allows for one measuring/filter creation as well. Once the filter (from the plugin or external tools) is produced it can be loaded with this plugin to alow for music correction during play.

There are 3 steps in the process of DRC which can be executed independently. If no other tools are used (e.g. DRCDesigner, Room EQ Wizard, Dirac, Accurate) the complete steps from measurment, filter calculation and fillter usage can be done by this plugin.
In case of strating from scratch just exectute all 3 stages of the procedure. Each step produces the output of the next step.

<h3>1) measure room response</h3>

measuring plays a configurable sine sweep and measures its room response. For that purpose calibrated measurment equipment is needed. I use a calibrated Behringer ECM8000 and a Focusrite 2i2 USB audio interface. In any case the device needs to suport recording in the 32bit float format (S32_LE). All other devices will be shown but the measure-button will stay disabled. In case you already have a recorded Impulse response just proceed with step 2 (calculating your filter).
You need to select the proper input/output device and for input the correct channel where your microphone is corrected. The recorded signal is monitored for quality and a dialog is shown with the evaluation results after measurement.

output: impulse response file which can be loaded to the filter correction

<h4>Caution:</h4>

configure your sweep carefully. It makes obviously no sense to calibrate small desktop speakers for lower than 50Hz start frequency (read your speaker specs). It is also advisable to start sweep play with lower volumes to not damage the equipment or you ears! The volume can be slowly turned up until a maximum is reached that does not make the furniture in your room vibrate as this will also cause artefacts.

Generally the longer and the louder the measurmenet is done the better the results (signal to noise ratio). Usually a 20s sweep gives good results already.

<h3>2) calculate the needed filter to correct room response </h3>

Calculating the filter depends on installed tools. Supported at the moment are PORC and DRC. Any way of created impulse response audio file can be used: either created by previous measurement step or by a another external tool.

output: a 32 bit audio file containing the filter than can be loaded for the room correction

<h3>3) apply the filter to the played music</h3>

load filter and enjoy :) --> no further dependencies

for installation just copy all files to ${HOME}/.local/share/rhythmbox/plugins/DRC

<h4>Limitations</h4>

only fraction of DRC configurable capabilities is there, but files are available for edit in the plugin folder (for DRC adapt erb44100.drc)
		
<h3>Dependencies</h3>
genarly depends on python3-lxml for configuration support (needed to load the module)
<h4>For measurment funtionality</h4>

depends on packages: sox, alsa-utils (uses aplay, arecord)
for installation on Ubuntu: sudo apt-get install alsa-utils sox
    
<h4>Filter creation functionality</h4>

	DRC :  depends on packages: sox, drc : sudo apt-get install sox drc
	PORC : depends on packages: sox, porc
	       for porc: sudo apt-get install python-numpy, python-scipy, python-matplotlib
            PORC can be found on github. To use it just download the complet package an get it running by installing all dependencies (mostly python libs). The pugin expects porc to be installed in
            the plugin folder under a separate folder (./porc/porc.py).

for those with some courage to try some new functionality: DRC supports multi channel correction, meaning a separate measure/filter per audio channel. To support this gstreamer plugins-good need to be patched as long as this change gets not a part of the gstreamer-plugins-good (see gst-plugins-good-patch folder) - I use it this way myself on Ubuntu 14.04/15.04.

<h4>experimenal functions and further development</h4>
There are 2 experimental functions which only work to a limited extend: brutefir support and iterative measurements. Both shall be understood as an outlook and are not fully supported yet. brutefir support at least creates a split of the current filter suitable for brutefir use directly in the home directory. Brutefir is a good way to achieve szstem wide DRC while the rhythmbox related application is limited just to RB.

Thanks to all the great guys doing amazing SW stuff in the web! This tool is just trying to put it together in an easy usable way.
