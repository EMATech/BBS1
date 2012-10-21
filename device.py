# -*- coding: utf-8 *-*

# A tool to communicate with Peterson's BBS-1 metronome
# Copyright (C) 2012 Raphaël Doursenaud <rdoursenaud@free.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import midi
import sysex


class BBS1():
#    midi
#    mode
#    hw_version
#    fw_version
    def __init__(self):
        self.com = midi.Midi()

    def present(self):
        """Tests if the hardware is present and if communication is possible"""
        return self.com.get_data(sysex.MSG_CONNECTED)

    def get_mode(self):
        """Gets the current mode (Normal/Firmware upload)"""
        return self.com.get_data(sysex.MSG_MODE)

    def get_version(self, part):
        """Returns the version in human readable form"""
        raw_version = self.com.get_data(part)
        version = str(raw_version[12]) + '.'\
            + str(raw_version[14]) + '.' + str(raw_version[16])
        return version

    def get_hardware_version(self):
        """Returns the hardware version in human readable form"""
        return self.get_version(sysex.MSG_HW_VERS)

    def get_firmware_version(self):
        """Returns the firmware version in human readable form"""
        return self.get_version(sysex.MSG_FW_VERS)
