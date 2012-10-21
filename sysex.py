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

##
# General Format
##

# [start][man_ID1][man_ID2 ][man_ID3][device_ID][command][reserved]
#    [payload.. max  40 bytes..][end]
# where:
# [payload] = [ 5 command bytes]
#    [ 2 - 35 encoded data bytes = 7 raw words = 28 raw bytes]
# 5 command bytes = [payload command] [ packet ID top byte 0-7F]
#    [ packet ID low byte 0-7F] [ reserved] [reserved]
# INT16u packetID = (packet ID top byte << 7) | packet ID low byte ;
#    packetID 0x3FFF indicates last packet

# Data formats

# INT16u (to a max 0x3FFF) will be packed in 2 bytes:
#    top byte << 7) | low byte
# INT32u will be packed in 5 bytes:
#    [0000 topbit byte1, topbit byte 2, topbit byte 3 , topbit byte 4]
#        [ byte1] [byte2][byte3][byte4]

##
# Notes
##
# Firmware transfer sequence of events:

# for each page till complete:
#    CMD_PREPARE_FOR_FIRMWARE_PAGE will be sent
#    data  = [INT16u page id]  [INT16u totalbytes] [INT32u checksum]  9 bytes
#    NO ack required ?
#    CMD_SENDING_FIRMWARE_PAGE
#    Ack required.

##
# Basics
##
_SYX_START = 0xf0
_SYX_END = 0xf7

##
# IDs
##
_MAN_ID1 = 0x00
_MAN_ID2 = 0x40
_MAN_ID3 = 0x70

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
_ANS_FW_TX_CMP = 0x04


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
_ACK_MODE = 0x23

# Erase tempomaps
_DEL_TM = 0x24

# Virtual keys / encoder
## These doesn't seem to work !
_VKEY = 0x40
_VENC = 0x41

##
# Helpers
##

# Preamble
_PREAMBLE = [_SYX_START, _MAN_ID1, _MAN_ID2, _MAN_ID3, _DEV_ID]

# Command
## Unused
_SEND_COMMAND = _PREAMBLE[:]
_SEND_COMMAND.append(_CMD)
_SEND_COMMAND.append(_RESERVED)

# Data
_SEND_DATA = _PREAMBLE[:]
_SEND_DATA.append(_DATA)
_SEND_DATA.append(_RESERVED)

# Connected
MSG_CONNECTED = _SEND_DATA[:]
MSG_CONNECTED.append(_REQ_CON)
## Unused 4 bytes ignored
MSG_CONNECTED.append(_SYX_END)

# Mode
MSG_MODE = _SEND_DATA[:]
MSG_MODE.append(_REQ_MODE)
## Unused 4 bytes ignored
MSG_MODE.append(_SYX_END)

# Hardware version
MSG_HW_VERS = _SEND_DATA[:]
MSG_HW_VERS.append(_REQ_HW_VERS)
## Unused 4 bytes ignored
MSG_HW_VERS.append(_SYX_END)

# Firmware version
MSG_FW_VERS = _SEND_DATA[:]
MSG_FW_VERS.append(_REQ_FW_VERS)
## Unused 4 bytes ignored
MSG_FW_VERS.append(_SYX_END)
