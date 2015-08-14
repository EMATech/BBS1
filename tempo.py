# -*- coding: utf-8 *-*
"""BBS1 tempo definitions"""
# A tool to communicate with Peterson's BBS-1 metronome
# Copyright (C) 2015 Raphaël Doursenaud <rdoursenaud@free.fr>
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

class File(object):
    """
    Tempo file
    """
    MAGIC = [0x42, 0x42, 0x53]  # == 'BBS'
    version = 2
    size = 0  # in bits
    maps_count = 9
    maps = [None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None]  # list of Maps

    def __init__(self, maps=None):
        if maps is not None:
            self.maps = maps
            # Compute maps count
            self.maps_count = len(maps)

    def set_version(self, version):
        if version != 1 and version != 2:
            raise TypeError("Unknown tempo maps version: " + str(version))
        logging.debug("Tempo maps version " + str(version))
        self.version = version


class Map(object):
    """
    Tempo map
    """
    start_offset = 0
    length = 0
    name = ''
    looping = False
    count_in = 0  # 0-8
    bars = []  # List of Bars

    def __init__(self, bars=None, name='', looping=False, count_in=0):
        self.bars = bars
        self.name = name
        self.looping = looping
        self.count_in = count_in


class Bar(object):
    """
    Tempo Bar
    """
    beats_per_bar = 4
    beat_value = 4
    repeats = 0  # 0-255 with 0 = hold
    tempo = 12000  # BPM * 100

    def __init__(self, beats_per_bar=4, beat_value=4, repeats=0, bpm=120):
        self.beats_per_bar = beats_per_bar
        self.beat_value = beat_value
        self.repeats = repeats
        self.tempo = bpm * 100
