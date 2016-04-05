# -*- coding: utf-8 *-*
"""BBS1 device definitions"""
# A tool to communicate with Peterson's BBS-1 metronome
# Copyright (C) 2012-2015 Raphaël Doursenaud <rdoursenaud@free.fr>
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

import logging

from sysex import SysexMessage


class Bbs1(object):
    """BBS1 device and associated commands"""

    def __init__(self, com):
        """Initialize device"""
        self.__hw_vers = "unknown"
        self.__fw_vers = "unknown"
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
        reply = self.com.get_data(SysexMessage.build_msg_req_con())
        if reply == ('ok', 'connected'):
            return True
        return False

    def get_mode(self):
        """Gets the current mode (Normal/Firmware upload)"""
        logging.debug("Get mode?")
        reply = self.com.get_data(SysexMessage.build_msg_req_mode())
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
        self.__hw_vers = self._get_version(SysexMessage.build_msg_req_hw_vers())
        return self.__hw_vers

    def get_firmware_version(self):
        """Returns the firmware version in human readable form"""
        logging.debug("Get FW version?")
        self.__fw_vers = self._get_version(SysexMessage.build_msg_req_fw_vers())
        return self.__fw_vers

    def get_tempomaps(self):
        """Get tempo maps from the device"""
        logging.debug("Get tempo maps?")
        infos = self.com.get_data(SysexMessage.build_msg_req_tm())
        # TODO: decode infos (seem to always be 13 zeros)
        tm = self.com.get_data(SysexMessage.build_msg_ack_ok(), SysexMessage.is_last_tm_page)
        tempofile = SysexMessage.parse_tempo_maps_pages(tm)
        return tempofile

    def clear_tempomaps(self):
        """Clear the device's tempo maps storage"""
        logging.debug("Clear tempo maps")
        self.com.send(SysexMessage.build_msg_del_tm())
