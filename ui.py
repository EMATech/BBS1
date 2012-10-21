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
        Gtk.Application.__init__(self, application_id="apps.bbs1",
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.on_activate)

    def on_activate(self, data=None):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('bbs1.glade')
        window = self.builder.get_object('BBS1')
        window.show_all()
        self.add_window(window)
        try:
            self.dev = device.Bbs1()
        except:
            self.msg_print('BBS-1 not found')
            return
        self.is_here()

    def is_here(self):
        if self.dev.present():
            self.msg_print('BBS-1 found')
        else:
            self.msg_print('BBS-1 not answering')

    def msg_print(self, msg):
        label = self.builder.get_object('label1')
        label.set_text(msg)
