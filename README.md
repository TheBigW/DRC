DRC
============

A rhythmbox plugin for digital room correction.

As the room in which audio systems play influences the sound quite a bit the performasnce of speaker systems is usually degraded. Fortunately there are mechanisms that compensate for that: DRC (Digital Room Correction). It works in a way that a defined signal (log sweep) is played and its response is messured. From this the impulse response can be calculated to correct the influence of the room. 

It can handle 32bit float mono filters as e.g. produced by PORC (search PORC on github) or DRCDesigner (also on github). Once the filter is produced it can be loaded with this plugin to aloow for music correction during play.

There are 3 steps in the process of DRC

1) measure room response

measuring plays a configurable sine sweep and measres its room response. For that purpose calibrated measurment equipment is needed. I use a calibrated Behringer ECM8000 and a Focusrite 2i2 USB audio interface. 
Caution: configure your sweep carefully. It makes obviously no sense to calibrate small desktop speakers for lower than 50Hz (read your speaker specs).

2) calculate the needed filter to correct room response 

Calculating the filter depends on installed tools. Supported at the moment are PORC and DRC. PORC can be found on github. To use it just download the complet package an get it running by installing all dependencies (mostly python libs). The pugin expects porc to be installed in the plugin folder under a separate folder (./porc/porc.py).
DRC is part of the default Ubuntu repositories. Once installed it works out of the box.

3) apply the filter to the played music (load filter and enjoy :) )

The tool adresses all 3 areas and all can be used independently. E.g. if you measured your room response with a different tool (e.g. REW - RoomEQWizard) it's exported output can also be used at the next step. If you have a filter from a different program (e.g. Dirac, Accurate, PORC, DRC) you can load it directly.


for installation just copy all files to HOME/.local/share/rhythmbox/plugins/DRC
