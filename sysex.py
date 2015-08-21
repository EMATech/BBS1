# -*- coding: utf-8 *-*
"""BBS1 MIDI SysEx protocol definitions"""
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
from binascii import hexlify

import tempo

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
# These doesn't seem to work !
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
        Start send command message

        Note: this seem to never work
        """
        message = SysexMessage._build_msg_preamble()
        message.append(_CMD)
        message.append(_RESERVED)
        return message

    @staticmethod
    def _build_msg_send_data():
        """
        Start send data message
        """
        message = SysexMessage._build_msg_preamble()
        message.append(_DATA)
        message.append(_RESERVED)
        return message

    @staticmethod
    def _build_msg_send_ack_ok():
        """
        Start send acknowlege OK
        """
        message = SysexMessage._build_msg_preamble()
        message.append(_ACK_OK)
        message.append(_RESERVED)
        return message

    @staticmethod
    def _build_msg_send_ack_err():
        """
        Start send acknowlege error
        """
        message = SysexMessage._build_msg_preamble()
        message.append(_ACK_ERR)
        message.append(_RESERVED)
        return message

    @staticmethod
    def build_msg_ack_ok():
        """
        Build a request tempo maps message
        """
        message = SysexMessage._build_msg_send_ack_ok()  # BBS1 happily sends data whatever the message type
        message.append(_SYX_END)
        return message

    @staticmethod
    def build_msg_del_tm():
        """
        Build a delete tempo maps message
        """
        # Send command does not work
        message = SysexMessage._build_msg_send_data()
        message.append(_DEL_TM)
        message.append(_SYX_END)
        return message

    @staticmethod
    def build_msg_req_con():
        """
        Build a request connection status message
        """
        # Send command does not work
        message = SysexMessage._build_msg_send_data()
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
        message = SysexMessage._build_msg_send_data()
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
        message = SysexMessage._build_msg_send_data()
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
        message = SysexMessage._build_msg_send_data()
        message.append(_REQ_FW_VERS)
        # Unused 4 padding bytes ignored
        message.append(_SYX_END)
        return message

    @staticmethod
    def build_msg_req_tm():
        """
        Build a request tempo maps informations message
        """
        # Send command does not work
        message = SysexMessage._build_msg_send_data()
        message.append(_REQ_TM)
        # Unused 4 padding bytes ignored
        message.append(_SYX_END)
        return message

    @staticmethod
    def parse(message):
        """
        Parse BBS1 SysEx messages

        :param message: Raw device data
        :type message: list
        :return: 'command', payload
        :rtype: str, mixed
        """
        logging.debug(hexlify(bytearray(message)))

        start = message[0]
        end = message[-1]

        if start != _SYX_START or end != _SYX_END:
            raise TypeError("Not a valid SysEx message")

        man_id = message[1:4]

        if man_id != [_MAN_ID1, _MAN_ID2, _MAN_ID3]:
            raise TypeError("Wrong manufacturer")

        dev_id = message[4]

        if dev_id != _DEV_ID:
            raise TypeError("Wrong device")

        logging.debug("Valid BBS1 SysEx message")

        msg_type = message[5]

        if msg_type == _CMD:
            logging.debug("Command")
            payload = SysexMessage.parse_payload(message[6:-1])
            return 'command', payload
        elif msg_type == _DATA:
            logging.debug("Data")
            payload = SysexMessage.parse_payload(message[6:-1])
            return 'data', payload
        elif msg_type == _ACK_OK:
            logging.debug("Acknowledge OK")
            payload = SysexMessage.parse_payload(message[6:-1])
            return 'ok', payload
        elif msg_type == _ACK_ERR:
            logging.debug("Acknowledge error")
            payload = SysexMessage.parse_payload(message[6:-1])
            return 'err', payload
        else:
            logging.error("Unknown message type")

    @staticmethod
    def parse_payload(data):
        """
        Parse BBS1 SysEx messages payloads

        :param data: Raw payload data
        :type data: list
        :return: Parsed payload data
        :rtype: mixed
        """
        if data[0] == 0x23:
            logging.debug("Tempo map payload")
        elif data[0] != _RESERVED:
            logging.warning("Unknown SysEx message payload reserved field")

        if len(data) == 1:
            logging.debug("Empty payload")
            return

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
            logging.debug("Request tempo maps")
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
            return
        elif data[1] == _TX_FW_PG:
            logging.debug("Transmit firware page")
            # TODO: code/decode
            return
        elif data[1] == _TX_TM_PG:
            logging.debug("Transmit tempo map page")
            # TODO: code/decode
            return
        elif data[1] == _TM_PG:
            logging.debug("Tempo map page")
            # TODO: try to code/decode from here
            return data[2:]

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
        logging.error("Unknown payload")
        logging.debug(hexlify(bytearray(data[2:])))
        return data[2:]

    @staticmethod
    def parse_version(raw_version):
        """
        Human readable version string

        :param raw_version: Raw version message
        :type raw_version: list
        :return: Human readable version
        :rtype: str
        """
        version = str(raw_version[1]) \
            + '.' + str(raw_version[2]) + str(raw_version[3]) \
            + '.' + str(raw_version[4]) + str(raw_version[5])

        logging.debug("Version: " + version)

        return version

    @staticmethod
    def parse_mode(raw_mode):
        """
        Human readable mode

        :param raw_mode: Raw mode message
        :type raw_mode: list
        :return: Human readable mode
        :rtype: str
        """
        mode = 'unknown'
        if raw_mode[0] == 0x00:
            mode = 'normal'
        elif raw_mode[0] == 0x01:
            mode = 'firmware'

        logging.debug("Mode: " + mode)

        return mode

    @staticmethod
    def parse_tempo_maps_pages(result):
        """
        Parse tempo maps

        :param result: Raw results from get_data()
        :type result: list
        :return: Tempo file
        :rtype: tempo.File
        """
        logging.debug("Parse tempo maps pages")

        """
        Tempo maps format
        =================

        IMPORTANT NOTE: wire protocol introduce 1 padding byte after every 4 bytes

        Pages
        -----

        5 bytes

        ::
        byte 0
            [0] => page
            [127] => last page
        byte 1
            [0-126] => page #
            [127] => last page
        bytes 2-4
            [0, 0, 0] padding?

        if page == 0:
            bytes 5-12
                Header data
        bytes n-n'
            Entries data

        Header
        ------

        8 bytes

        ::
        bytes 0-2
            "BBS" magic number
        byte 3
            [?] Version? 0x01 or 0x02
        bytes 4-5
            [LSB, MSB] file size in bytes
        byte 6
            [9] Number of tempo maps entries (Should be <= 9)
        byte 7
            [0] Padding

        Entry format
        ------------

        Up to 9 entries can be stored


        Infos
        ~~~~~

        20 to 24 bytes repeated as needed

        ::
        bytes 0-1
            [MSB, LSB] Start offset?
        bytes 2-3
            [MSB, LSB] bars length in bytes
        byte 4-19
            Name 16 bytes
        if version == 2:
            byte 20
                [?] Count-in bars
                    Top bit: looping flag
                    Lower bits: number of bars to count-in (0-8)
            byte 21-23
                padding!

        Bars
        ~~~~

        4 bytes

        Repeated as needed
        See info start offset and length

        ::
        byte 0
            [?] Time signature
                Top 4 bits: beats per bar (1-16)
                Lower bits: beat value (2, 4, 8, 16 or 32)
        byte 1
            [?] Repeats
                0: hold
                1-255: number of repeats
        bytes 2-3
            [LSB, MSB] tempo (= BPM * 100)
        """

        # Extract pages
        pages = [pages[1] for pages in result if pages[1] is not None]

        tempofile = tempo.File()

        # Parse header
        maps = []
        for p in pages:
            # p[0]?
            page_num = int(p[1])
            logging.debug("Received page #" + str(page_num))
            # p[2] always 0
            # p[3] always 0
            maps += p[4:]

        SysexMessage._parse_file_header(maps[0:10], tempofile)

        index = SysexMessage._parse_maps(maps[10:], tempofile)

        SysexMessage._parse_bars(maps[index:])

        return tempofile

    @staticmethod
    def _parse_file_header(header, tempofile):
        """
        Parse tempo map file informations

        :parm tempofile:
        :type tempofile: tempo.File
        """

        # 4 bytes padding
        # file_info[0]

        # Magic number
        if header[1:4] != tempofile.MAGIC:
            raise TypeError("Not tempo maps data")
        else:
            logging.debug("Valid tempo maps data found")

        # Version
        tempofile.set_version(int(header[4]))

        # 4 bytes padding
        # file_info[5]

        # File size (in bits)
        tempofile.size = header[6] + header[7] * 256
        logging.debug("Detected size " + str(tempofile.size) + " bytes")

        # Tempo map entries
        tempofile.entries_count = header[8]
        logging.debug("Found " + str(tempofile.entries_count) + " tempo maps")

        # Padding!
        # file_info[9]

    @staticmethod
    def _parse_maps(maps_data, tempofile):
        """
        Parse maps data

        :param maps_data: Raw maps data
        :param tempofile: Tempo file
        :type maps_data: list
        :type tempofile: tempo.File
        :return: Next data index
        :rtype: int
        """

        index = 0
        for i in range(0, tempofile.maps_count):
            logging.debug("Parsing map #" + str(i))
            (inc, tempomap) = SysexMessage._parse_map(maps_data[index:], tempofile)
            index += inc
            tempofile.maps[i] = tempomap

        return index

    @staticmethod
    def _parse_map(mapdata, tempofile):
        """
        Parse one map from raw data

        :param mapdata: Raw map data
        :param tempofile: Tempo file
        :type mapdata: list
        :type tempofile: tempo.file
        :return: (index, tempomap)
        :rtype: (int, tempo.Map)
        """
        tempomap = tempo.Map()

        # 4 bytes padding
        # mapdata[0]

        # Start offset
        tempomap.start_offset = mapdata[1] + mapdata[2] * 256
        logging.debug("Start offset: " + str(tempomap.start_offset))

        # Length (in bytes)
        tempomap.length = mapdata[3] + mapdata[4] * 256
        logging.debug("Map length: " + str(tempomap.length) + " bytes")

        # 4 bytes padding
        # mapdata[5]

        # Name (1)
        try:
            tempomap.name = ''.join(unichr(c) for c in mapdata[6:10])
        except NameError:
            # We must be running Python 3
            tempomap.name = ''.join(chr(c) for c in mapdata[6:10])

        # 4 bytes padding
        # mapping[10]

        # Name (2)
        try:
            tempomap.name += ''.join(unichr(c) for c in mapdata[11:15])
        except NameError:
            # We must be running Python 3
            tempomap.name += ''.join(chr(c) for c in mapdata[11:15])

        # 4 bytes padding
        # mapping[15]

        # Name (3)
        try:
            tempomap.name += ''.join(unichr(c) for c in mapdata[16:20])
        except NameError:
            # We must be running Python 3
            tempomap.name += ''.join(chr(c) for c in mapdata[16:20])

        # 4 bytes padding
        # mapping[20]

        # Name (4)
        try:
            tempomap.name += ''.join(unichr(c) for c in mapdata[21:25])
        except NameError:
            # We must be running Python 3
            tempomap.name += ''.join(chr(c) for c in mapdata[21:25])

        logging.debug("Map name: " + tempomap.name)

        index = 25
        if tempofile.version == 2:
            # Loop
            tempomap.looping = mapdata[25] == 8
            logging.debug("Looping is " + str(tempomap.looping))

            # Count-in
            tempomap.count_in = mapdata[26]
            logging.debug("Count-in " + str(tempomap.count_in) + " bars")

            # Padding!
            # mapdata[27:30]
            index = 30

        return index, tempomap

    @staticmethod
    def _parse_bars(bars_data):
        """
        Parse bars from raw data

        :param bars_data: Raw bars data
        :type bars_data: list
        """
        # TODO
        pass

    @staticmethod
    def _parse_bar(bardata):
        """
        Parse one bar from raw data

        :param bardata: Raw bar data
        :type bardata: list
        """
        # TODO
        pass

    @staticmethod
    def is_last_tm_page(answer):
        """
        Check if it is the last tempo maps page

        :param answer: Answer data
        :type answer: str, list
        :return: Last tempo map page status
        :rtype: bool
        """
        if answer[1] is not None:
            if len(answer[1]) > 1:
                if answer[1][0:2] == [0x7f, 0x7f]:
                    return True
        return False
