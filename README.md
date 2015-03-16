DRC
============

A rhythmbox plugin for digital room correction.

As the room in which audio systems play influences the sound quite a bit the performasnce of speaker systems is usually degraded. Fortunately there are mechanisms that compensate for that: DRC (Digital Room Correction). It works in a way that a defined signal (log sweep) is played and its response is messured. From this the impulse response can be calculated to correct the influence of the room. This Plugin so fas only supports for loading the produced filters. It can handle 32bit float mono filters as e.g. produced by PORC (search PORC on github) or DRCDEsigner (also on github). Once the filter is produced it can be loaded with this plugin to aloow for music correction during play.
