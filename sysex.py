# -*- coding: utf-8 *-*
"""BBS1 MIDI SysEx protocol definitions"""
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

import logging
from binascii import hexlify

"""
BBS1 SysEx protocol
===================

General Format
--------------

::
[start][man_ID1][man_ID2 ][man_ID3][device_ID][command][reserved]
    [payload.. max  40 bytes..][end]
where:
[payload] = [ 5 command bytes]
    [ 2 - 35 encoded data bytes = 7 raw words = 28 raw bytes]
5 command bytes = [payload command] [ packet ID top byte 0-7F]
    [ packet ID low byte 0-7F] [ reserved] [reserved]
INT16u packetID = (packet ID top byte << 7) | packet ID low byte ;
    packetID 0x3FFF indicates last packet

Data formats
~~~~~~~~~~~~

::
INT16u (to a max 0x3FFF) will be packed in 2 bytes:
    top byte << 7) | low byte
INT32u will be packed in 5 bytes:
    [0000 topbit byte1, topbit byte 2, topbit byte 3 , topbit byte 4]
        [ byte1] [byte2][byte3][byte4]

Notes
-----
Firmware transfer sequence of events:

::
for each page till complete:
   CMD_PREPARE_FOR_FIRMWARE_PAGE will be sent
   data  = [INT16u page id]  [INT16u totalbytes] [INT32u checksum]  9 bytes
   NO ack required ?
   CMD_SENDING_FIRMWARE_PAGE
   Ack required.
"""

##
# Basics
##
_SYX_START = 0xf0
_SYX_END = 0xf7

##
# IDs
##
# Manufacturer
_MAN_ID1 = 0x00
_MAN_ID2 = 0x40
_MAN_ID3 = 0x70
# Device
_DEV_ID = 0x01

##
# Main commands
##
_CMD = 0x01  # Does not work ! Always use SEND_DATA
_DATA = 0x02
_ACK_OK = 0x03
_ACK_ERR = 0x04

##
# Reserved
##
_RESERVED = 0x00

##
# Payload commands
##
# Firmware transfer
_FW_PG = 0x01
_REQ_NEXT_FW_PG = 0x02
_TX_FW_PG = 0x03
# From BBS
_FW_TX_CMP = 0x04


# Version formats x.xx.xx sent as bytes not chars

# Hardware version
_REQ_HW_VERS = 0x13
# From BBS
_ANS_HW_VERS = 0x14

# Firmware version
_REQ_FW_VERS = 0x15
# From BBS
_ANS_FW_VERS = 0x16

# Tempomaps transfer
_REQ_TM = 0x17
_TX_TM_PG = 0x18
# From BBS
_TM_PG = 0x19

# Connection status
_REQ_CON = 0x20
# From BBS
_ACK_CON = 0x21

# Mode
_REQ_MODE = 0x22
# From BBS
_ANS_MODE = 0x23

# Erase tempomaps
_DEL_TM = 0x24

# Virtual keys / encoder
## These doesn't seem to work !
_VKEY = 0x40
_VENC = 0x41

class SysexMessage(object):
    """BBS1 System exclusive message"""


    @staticmethod
    def _build_msg_preamble():
        """
        Build BBS1 SysEx message preamble
        """
        return [_SYX_START, _MAN_ID1, _MAN_ID2, _MAN_ID3, _DEV_ID]

    @staticmethod
    def _build_msg_send_command():
        """
        Start BBS1 send command message

        Note: this seem to never work
        """
        message = SysexMessage._build_msg_preamble()[:]
        message.append(_CMD)
        message.append(_RESERVED)
        return message

    @staticmethod
    def _build_msg_send_data():
        """
        Start BBS1 send data message
        """
        message = SysexMessage._build_msg_preamble()[:]
        message.append(_DATA)
        message.append(_RESERVED)
        return message

    @staticmethod
    def build_msg_req_con():
        """
        Build a request connection status message
        """
        # Send command does not work
        message = SysexMessage._build_msg_send_data()[:]
        message.append(_REQ_CON)
        # Unused 4 padding bytes ignored
        message.append(_SYX_END)
        return message

    @staticmethod
    def build_msg_req_mode():
        """
        Build a request mode status message
        """
        # Send command does not work
        message = SysexMessage._build_msg_send_data()[:]
        message.append(_REQ_MODE)
        # Unused 4 padding bytes ignored
        message.append(_SYX_END)
        return message

    @staticmethod
    def build_msg_req_hw_vers():
        """
        Build a request hardware version message
        """
        # Send command does not work
        message = SysexMessage._build_msg_send_data()[:]
        message.append(_REQ_HW_VERS)
        # Unused 4 padding bytes ignored
        message.append(_SYX_END)
        return message

    @staticmethod
    def build_msg_req_fw_vers():
        """
        Build a request firmware version message
        """
        # Send command does not work
        message = SysexMessage._build_msg_send_data()[:]
        message.append(_REQ_FW_VERS)
        # Unused 4 padding bytes ignored
        message.append(_SYX_END)
        return message

    @staticmethod
    def build_msg_req_tm_infos():
        """
        Build a request tempo maps informations message
        """
        # Send command does not work
        message = SysexMessage._build_msg_send_data()[:]
        message.append(_REQ_TM)
        # Unused 4 padding bytes ignored
        message.append(_SYX_END)
        return message

    @staticmethod
    def build_msg_req_tm():
        """
        Build a request tempo maps message
        """
        # Send command does not work
        message = SysexMessage._build_msg_send_data()[:]
        message.append(0x00)  # BBS1 happily sends data whatever this value is
        message.append(0x7f)  # TODO: decode
        message.append(0x7f)  # TODO: decode
        # Unused 2 padding bytes ignored
        message.append(_SYX_END)
        return message

    @staticmethod
    def parse(message):
        """
        Parse BBS1 SysEx messages
        """

        logging.debug(hexlify(bytearray(message)))

        start = message[0]
        end = message[-1]

        if start != _SYX_START or end != _SYX_END:
            raise TypeError("Not a valid SysEx message")

        man_id_1 = message[1]
        man_id_2 = message[2]
        man_id_3 = message[3]

        if man_id_1 != _MAN_ID1 or man_id_2 != _MAN_ID2 or man_id_3 != _MAN_ID3:
            raise TypeError("Wrong manufacturer")

        dev_id = message[4]

        if dev_id != _DEV_ID:
            raise TypeError("Wrong device")

        logging.debug("Valid BBS1 SysEx message")

        msg_type = message[5]

        if msg_type == _CMD:
            logging.debug("Command")
            payload = SysexMessage.parse_payload(message[6:-1])
            return ('command', payload)
        elif msg_type == _DATA:
            logging.debug("Data")
            payload = SysexMessage.parse_payload(message[6:-1])
            return ('data', payload)
        elif msg_type == _ACK_OK:
            logging.debug("Acknowledge OK")
            payload = SysexMessage.parse_payload(message[6:-1])
            return ('ok', payload)
        elif msg_type == _ACK_ERR:
            logging.debug("Acknowledge error")
            payload = SysexMessage.parse_payload(message[6:-1])
            return ('err', payload)
        else:
            logging.error("Unknown message type")

    @staticmethod
    def parse_payload(data):
        """
        Parse BBS1 SysEx messages payloads
        """
        if data[0] != _RESERVED:
            logging.warning("Unknown SysEx message payload reserved field")

        # Requests
        if data[1] == _REQ_NEXT_FW_PG:
            logging.debug("Request next firware page")
            return
        elif data[1] == _REQ_HW_VERS:
            logging.debug("Request hardware version")
            return
        elif data[1] == _REQ_FW_VERS:
            logging.debug("Request firmware version")
            return
        elif data[1] == _REQ_TM:
            logging.debug("Request tempo map informations")
            return
        elif data[1] == _REQ_CON:
            logging.debug("Request connection status")
            return
        elif data[1] == _REQ_MODE:
            logging.debug("Request mode")
            return

        # Actions
        elif data[1] == _DEL_TM:
            logging.debug("Delete tempo maps")
            return

        # Bidir
        elif data[1] == _FW_PG:
            logging.debug("Firmware page")
            # TODO: code/decode
        elif data[1] == _TX_FW_PG:
            logging.debug("Transmit firware page")
            # TODO: code/decode
        elif data[1] == _TX_TM_PG:
            logging.debug("Transmit tempo map page")
            # TODO: code/decode
        elif data[1] == _TM_PG:
            logging.debug("Tempo map page")
            # TODO: code/decode

        # Answers
        elif data[1] == _FW_TX_CMP:
            logging.debug("Firmware transmit complete")
            # TODO: decode
        elif data[1] == _ANS_HW_VERS:
            logging.debug("Answer hardware version")
            # Ignore 4 bytes padding
            return SysexMessage.parse_version(data[5:])
        elif data[1] == _ANS_FW_VERS:
            logging.debug("Answer firmware version")
            # Ignore 4 bytes padding
            return SysexMessage.parse_version(data[5:])
        elif data[1] == _ANS_MODE:
            logging.debug("Answer mode")
            return SysexMessage.parse_mode(data[2:])

        # Acnowledgments
        elif data[1] == _ACK_CON:
            logging.debug("Acknowledge Connected")
            return 'connected'

        # Remaining data
        else:
            logging.error("Unknown payload")

        return logging.debug(data[2:])

    @staticmethod
    def parse_version(raw_version):
        """
        Human readable version string
        """
        version = str(raw_version[1]) + '.' + str(raw_version[3]) + '.' + str(raw_version[5])

        logging.debug("Version: " + version)

        return version

    @staticmethod
    def parse_mode(raw_mode):
        """
        Human readable mode
        """
        mode = 'unknown'
        if raw_mode[0] == 0x00:
            mode = 'normal'
        elif raw_mode[0] == 0x01:
            mode = 'firmware'

        logging.debug("Mode: " + mode)

        return mode
