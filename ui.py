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

import sys
import device

try:
    from gi.repository import Gtk, Gio
except ImportError:
    print("This script needs pygobject to run")
    sys.exit(1)


class Bbs1App(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self, application_id='apps.bbs1',
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect('activate', self.on_activate)

    def on_activate(self, data=None):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('bbs1.glade')
        window = self.builder.get_object('BBS1')
        window.show_all()
        self.button = self.builder.get_object('button1')
        self.button.set_label("Reconnect")
        self.button.connect('clicked', self.init_device)
        self.add_window(window)
        self.init_device()

    def msg_print(self, msg):
        message_label = self.builder.get_object('label1')
        message_label.set_text(msg)

    def init_device(self, data=None):
        # FIXME: if the device is plugged, this only works half the time
        try:
            self.dev.__del__()
        except AttributeError:
            # self.dev might not exist. This is not an issue: keep going
            pass

        try:
            self.dev = device.Bbs1()
        except IOError:
            self.msg_print(
                "BBS-1 not found!\n"
                "Please check that:\n"
                " - it is properly connected\n"
                " - it is powered up")
        else:
            self.msg_print("BBS-1 found!\n"
                "Trying to connect…")
            self.connect_device()

    def connect_device(self):
        if self.dev.present():
            mode = self.dev.get_mode()
            self.msg_print("Connected to BBS-1!\n"
            "- mode: " + mode + "\n"
            "- revision: " + self.dev.get_hardware_version() + "\n"
            "- firmware version: " + self.dev.get_firmware_version())
            if mode == 'normal':
                self.normal()
            else:
                self.firmware()
        else:
            self.msg_print("BBS-1 not answering")

    def normal(self):
        # TODO
        pass

    def firmware(self):
        # TODO
        pass
