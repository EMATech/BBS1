#!/usr/bin/env python2
# -*- coding: utf-8 *-*
"""A tool to communicate with Peterson's BBS-1 metronome"""
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

# TODO: About dialog
# TODO: Send firmware update
# TODO: Check for firmware update
# TODO: Extract tempo maps
# TODO: Send tempo map
# TODO: Tempo map wizard
# TODO: i18n (getext)
# TODO: Wireless protocol

import logging
import ui

if __name__ == "__main__":
    APP = ui.Bbs1App()
    APP.run(None)
    logging.info('Application exit')
