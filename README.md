# space-engineers-cheetah-radar
A simple script that predicts the detection range of Cheetah's Radar Mod

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/omnisciendus/space-engineers-cheetah-radar/master)

The original mod:
https://steamcommunity.com/sharedfiles/filedetails/?id=907384096

Details of how this all works are in how_radars_work.txt. In short, radars have several different ways they can detect targets, and the rules for these are complex. The python script allows you to specify the hardware on a hypothetical "Detector Ship," and an array of targets for it to find. The script output is the maximum distance the detector ship can see each target, and how far away a passively listening target can see the detector. Pseudocode for the radars is at the end of how_radars_work.txt.