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

        self.window = self.builder.get_object('BBS1')
        self.window.show_all()
        self.add_window(self.window)

        self.message = self.builder.get_object('message')

        self.hw_vers = self.builder.get_object('hw_vers')
        self.fw_vers = self.builder.get_object('fw_vers')

        self.init_alert = self.builder.get_object('init_alert')

        self.connect_alert = self.builder.get_object('connect_alert')

        self.msg_print("Detecting BBS-1…")
        self.init_device()

    def msg_print(self, msg):
        context = self.message.get_context_id(msg)
        self.message.push(context, msg)

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
                "BBS-1 not found!")
            self.show_alert_init()
        else:
            self.msg_print("BBS-1 found! "
            "Connecting…")
            self.connect_device()

    def show_alert_init(self):
        if self.init_alert.run() != -5:
            self.quit()
        else:
            self.init_alert.hide()
            self.init_device()

    def connect_device(self):
        if self.dev.present():
            mode = self.dev.get_mode()
            self.msg_print("BSS-1 connected!")
            self.hw_vers.set_text(self.dev.get_hardware_version())
            self.fw_vers.set_text(self.dev.get_firmware_version())
            if mode == 'normal':
                self.normal()
            else:
                self.firmware()
        else:
            self.msg_print("BBS-1 not connected!")

    def show_alert_connect(self):
        if self.connect_alert.run() != -5:
            self.quit()
        else:
            self.connect_alert.hide()
            self.connect_device()

    def normal(self):
        # TODO
        pass

    def firmware(self):
        # TODO
        pass
