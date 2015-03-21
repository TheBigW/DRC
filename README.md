DRC
============

A rhythmbox plugin for digital room correction.

As the room in which audio systems play influences the sound quite a bit the performasnce of speaker systems is usually degraded. Fortunately there are mechanisms that compensate for that: DRC (Digital Room Correction). It works in a way that a defined signal (log sweep) is played and its response is messured. From this the impulse response can be calculated to correct the influence of the room. 

It can handle 32bit float mono filters as e.g. produced by PORC (search PORC on github) or DRCDesigner (also on github). Once the filter is produced it can be loaded with this plugin to aloow for music correction during play.

There are 3 steps in the process of DRC

1) measure room response

2) calculate the needed filter to correct room response

3) apply the filter to the played music

The tool adresses all 3 areas and all can be used independently. E.g. if you measured your room response with a different tool (e.g. REW - RoomEQWizard) it's exported output can also be used at the next step. If you have a filter from a different program (e.g. Dirac or Accurate) you can load it directly.

TODO: add dependencies (PORC, DRC, sox...)

for installation just copy all files to HOME/.local/share/rhythmbox/plugins/DRC
