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


class Bar(object):
    """
    Tempo Bar
    """
    def __init__(self, beats_per_bar=4, beat_value=4, repeats=0, bpm=120):
        self.beats_per_bar = beats_per_bar
        self.beat_value = beat_value
        self.repeats = repeats
        self.tempo = bpm * 100

        def __eq__(self, other):
            return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

        def __ne__(self, other):
            return not self.__eq__(other)


class Map(object):
    """
    Tempo map
    """

    def __init__(self, bars=None, name=''.ljust(16, '\x00'),
                 looping=False, count_in=0):
        self.start_offset = 0
        self.length = 0
        self.bars = []  # List of bars
        if bars is not None:
            self.bars = bars
        self.name = name
        self.looping = looping
        if not 0 <= count_in <= 8:
            raise TypeError("Count-in must be between 0 and 8")
        self.count_in = count_in

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__
                and all([bar == otherbar for bar, otherbar in zip(self.bars, other.bars)]))

    def __ne__(self, other):
        return not self.__eq__(other)

    def reset(self):
        """
        Resets the map
        """
        self.bars = []
        self.name = ''.ljust(16, '\x00')
        self.looping = False
        self.count_in = 0

    def set_name(self, name):
        """
        Set the map name correctly padded
        """
        self.name = name.ljust(16, '\x00')

class File(object):
    """
    Tempo file
    """
    MAGIC = [0x42, 0x42, 0x53]  # == 'BBS'

    def __init__(self, maps=None):
        self.version = 2
        self.size = 0  # in bits (TODO: compute)
        self.maps = [Map(),
                     Map(),
                     Map(),
                     Map(),
                     Map(),
                     Map(),
                     Map(),
                     Map(),
                     Map()]  # list of Maps
        if maps is not None:
            self.maps = maps
        # Compute maps count (generally 9)
        maps_count = len(self.maps)
        if not 0 <= maps_count <= 9:
            raise TypeError("Files can only have 0 to 9 maps")
        self.maps_count = maps_count

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__
                and self.maps == other.maps
                and all([tmap == othertmap for tmap, othertmap in zip(self.maps, other.maps)]))

    def __ne__(self, other):
        return not self.__eq__(other)

    def set_version(self, version):
        """
        Set tempo maps structure version

        :param version: Version number
        :type version: int
        """
        if version != 1 and version != 2:
            raise TypeError("Unknown tempo maps version: " + str(version))
        logging.debug("Tempo maps version " + str(version))
        self.version = version
