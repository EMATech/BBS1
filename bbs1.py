#!/usr/bin/env python2
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

# TODO: BBS-1 object
# TODO: extract tempo maps
# TODO: send tempo map
# TODO: send firmware update

import sys

try:
    from pygame import midi
except ImportError:
    print("This script needs pygame to run")
    sys.exit(1)
import re

# Reverse engineered SysEx Messages
# Commands to BBS-1
init =\
[0xF0, 0x00, 0x40, 0x70, 0x01, 0x02, 0x00, 0x20, 0x00, 0x00, 0x00, 0x00, 0xF7]
mode =\
[0xF0, 0x00, 0x40, 0x70, 0x01, 0x02, 0x00, 0x22, 0x00, 0x00, 0x00, 0x00, 0xF7]
firmware_version =\
[0xF0, 0x00, 0x40, 0x70, 0x01, 0x02, 0x00, 0x15, 0x00, 0x00, 0x00, 0x00, 0xF7]
hardware_version =\
[0xF0, 0x00, 0x40, 0x70, 0x01, 0x02, 0x00, 0x13, 0x00, 0x00, 0x00, 0x00, 0xF7]
get_tempomaps =\
[0xF0, 0x00, 0x40, 0x70, 0x01, 0x02, 0x00, 0x17, 0x00, 0x00, 0x00, 0x00, 0xF7]
#FIXME: is it really that ?
get_tempomaps_ack =\
[0xF0, 0x00, 0x40, 0x70, 0x01, 0x02, 0x00, 0x04, 0x7F, 0x7F, 0x00, 0x00, 0xF7]

# Replies from BBS-1
tempomap_receive_ack =\
[0xf0, 0x00, 0x40, 0x70, 0x01, 0x03, 0x00, 0x04, 0x7f, 0x7f, 0x00, 0x00, 0xf7]


# Initialize Pygame's MIDI
midi.init()

# Get number of MIDI devices
devices = midi.get_count()

# Search for the first BodyBeatSync input and output ports
for i in range(0, devices):
    info = midi.get_device_info(i)
    if(re.match('.*BodyBeatSYNC MIDI 1.*', str(info[1]))):
        if(info[2] >= 1):
            dev_in = i
        if(info[3] >= 1):
            dev_out = i

# Let's check if we got something
try:
    dev_in
except NameError:
    print("Couldn't find BodyBeatSync's input port")
    exit(1)

try:
    dev_out
except NameError:
    print("Couldn't find BodyBeatSync's output port")
    exit(1)

# Open input and output
midi_in = midi.Input(dev_in)
midi_out = midi.Output(dev_out)


def send(msg):
    """Sends out SysEx message"""
    midi_out.write_sys_ex(0, msg)


def get_data(msg):
    """Gets data from the hardware"""

    send(msg)

    # Wait for answer
    while not midi_in.poll():
        pass

    # Read answer
    raw_answers = list()
    answer = list()
    while midi_in.poll():
        raw_answers.append(midi_in.read(1))

    for raw_answer in raw_answers:
        for event in raw_answer:
            for data in event[0]:
                answer.append(data)
                # Strip remaining garbage data after sysex end
                if data == 0xF7:
                    break

    # TODO: Check answer

    return answer


def present():
    """Tests if the hardware is present and if communication is possible"""
    return get_data(init)


def get_mode():
    """Gets the current mode (Normal/Firmware upload)"""
    return get_data(mode)


def get_version(part):
    """Returns the version in human readable form"""
    raw_version = get_data(part)
    version = str(raw_version[12]) + '.'\
        + str(raw_version[14]) + '.' + str(raw_version[16])
    return version


def get_firmware_version():
    """Returns the firmware version in human readable form"""
    return get_version(firmware_version)


def get_hardware_version():
    """Returns the hardware version in human readable form"""
    return get_version(hardware_version)


# Raw tests
#print(present())
#print(get_mode())
#print(get_firmware_version())
#print(get_hardware_version())
#print(get_data(get_tempomaps))
