bbs1
====
A tool to communicate with Peterson's BBS-1 metronome

Status
------
**Under development**

About
-----
This is mainly an experiment involving reverse engineering a cool piece of harware and a pretext for learning Python, pygobject (GTK+ 3), getext and pygame midi.

Thanks
------
Thanks to Peterson's Vice President Patrick Bovenizer for sending me the protocol's documentation even if somewhat outdated.

Implemented
-----------
- Basic GUI
- Autodetection of the device (usbmidi)
- Reconnection to the device
- Error handling (midi initialization, device not connected or not responding)
- Displaying bootup mode and hardware/firmware versions

Todo
----
- About dialog
- Send firmware update
- Check for firmware update
- Extract tempo maps
- Send tempo map
- Tempo map wizard
- i18n (getext)
- Wireless protocol

Dependencies
------------
- Python 2.x
- pygame
- pygobject

Licence
-------
Copyright (C) 2012 Raphaël Doursenaud <rdoursenaud@free.fr>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
