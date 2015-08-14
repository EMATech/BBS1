# -*- coding: utf-8 *-*
"""BBS1 device definitions"""
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

import sysex
import logging


class Bbs1(object):
    """BBS1 device and associated commands"""
    __hw_vers = "unknown"
    __fw_vers = "unknown"

    def __init__(self, com):
        """Initialize device"""
        try:
            com.connect()
        except IOError:
            raise IOError
        self.com = com

    def __del__(self):
        """Delete device"""
        try:
            self.com.__del__()
        except AttributeError:
            # self.com may not exist. This is not an issue: keep going
            pass

    def present(self):
        """Tests if the hardware is present and if communication is possible"""
        logging.debug("Hardware Present?")
        reply = self.com.get_data(sysex.MSG_CONNECTED)
        if reply == ('ok', 'connected'):
            return True
        return False

    def get_mode(self):
        """Gets the current mode (Normal/Firmware upload)"""
        logging.debug("Get mode?")
        reply = self.com.get_data(sysex.MSG_MODE)
        if reply[0] == 'ok':
            return reply[1]
        else:
            raise Warning

    def _get_version(self, part):
        """Returns the version in human readable form"""
        reply = self.com.get_data(part)
        if reply[0] == 'ok':
            return reply[1]
        else:
            raise Warning

    def get_hardware_version(self):
        """Returns the hardware version in human readable form"""
        logging.debug("Get HW version?")
        self.__hw_vers = self._get_version(sysex.MSG_HW_VERS)
        return self.__hw_vers

    def get_firmware_version(self):
        """Returns the firmware version in human readable form"""
        logging.debug("Get FW version?")
        self.__fw_vers = self._get_version(sysex.MSG_FW_VERS)
        return self.__fw_vers
