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

import logging
import re

try:
    from pygame import midi
except ImportError:
    print("This script needs pygame to run")
    raise ImportError


class Communication():

    def __init__(self):
        """Initialize a MIDI communication channel"""
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
            logging.warning("Couldn't find BodyBeatSync's input port")
            raise IOError

        try:
            dev_out
        except NameError:
            logging.warning("Couldn't find BodyBeatSync's output port")
            raise IOError

        # Open input and output
        self.midi_in = midi.Input(dev_in)
        self.midi_out = midi.Output(dev_out)

    def __del__(self):
        midi.quit()

    def send(self, msg):
        """Sends out SysEx message"""
        self.midi_out.write_sys_ex(0, msg)

    def get_data(self, msg):
        """Gets reply from the hardware after sending a message"""
        self.send(msg)

        # Wait for answer
        while not self.midi_in.poll():
            pass

        # Read answer
        raw_answers = list()
        answer = list()

        while self.midi_in.poll():
            raw_answers.append(self.midi_in.read(1))

        for raw_answer in raw_answers:
            for event in raw_answer:
                for data in event[0]:
                    answer.append(data)
                    # Strip remaining garbage data after sysex end
                    if data == 0xf7:
                        break

        # TODO: Check answer
        # TODO: Timeout on no reply

        return answer
