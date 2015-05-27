# -*- coding: utf-8 *-*
"""BBS1 GUI handling"""
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

import communication
import device

try:
    # noinspection PyPackageRequirements
    from gi.repository import Gtk, Gio
except ImportError:
    print("This script needs pygobject to run")
    raise


class Bbs1App(Gtk.Application):
    """BBS1 main GUI application"""
    window = None
    message = None
    hw_vers = ''
    fw_vers = ''
    com = None
    device = None

    def __init__(self):
        """Application initialization"""
        Gtk.Application.__init__(self, application_id='apps.bbs1',
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)

        # Glade
        self.builder = Gtk.Builder()
        self.builder.add_from_file('bbs1.glade')

        # Signals
        self.builder.connect_signals(self)
        self.connect('activate', self.on_activate)

    def on_activate(self, data=None):
        """Secondary initialization"""

        # Main window
        self.window = self.builder.get_object('BBS1')
        self.window.show_all()
        self.add_window(self.window)

        # Status bar
        self.message = self.builder.get_object('message')

        # Version labels
        self.hw_vers = self.builder.get_object('hw_vers')
        self.fw_vers = self.builder.get_object('fw_vers')
        self.hw_vers.set_text("unknown")
        self.fw_vers.set_text("unknown")

        self.msg_print("Initializing")
        self.init_communication()

    def msg_print(self, msg):
        """Print a message in the statusbar

        :param msg: Message
        :type msg: str
        """
        context = self.message.get_context_id(msg)
        self.message.push(context, msg)

    def init_communication(self, data=None):
        """Initialize communication"""
        try:
            self.com.__del__()
        except AttributeError:
            # self.com may not exist. This is not an issue: keep going
            pass

        try:
            self.com = communication.Communication()
        except IOError:
            self.msg_print("Failed to initialize communication")
            self.show_alert_communication()
        else:
            self.msg_print("Communication initialized")
            self.init_device()

    def show_alert_communication(self):
        """Show an alert reporting failed communication initialization"""
        comm_alert = self.builder.get_object('comm_alert')
        if comm_alert.run() == -5:  # OK button
            comm_alert.hide()
            self.init_communication()
        else:
            self.quit()

    def init_device(self, data=None):
        """Initialize the device"""

        # Destroy any previous device
        try:
            self.device.__del__()
        except AttributeError:
            # self.dev may not exist. This is not an issue: keep going
            pass

        try:
            self.device = device.Bbs1(self.com)
        except IOError:
            self.msg_print("BBS-1 not found")
            self.show_alert_init()
        else:
            self.msg_print("BBS-1 found! Connecting…")
            self.connect_device()

    def show_alert_init(self):
        """Show an alert reporting failed device initialization"""
        init_alert = self.builder.get_object('init_alert')
        if init_alert.run() == -5:  # OK button
            init_alert.hide()
            self.init_communication()
        else:
            self.quit()

    def connect_device(self):
        """Connect to the device"""
        if self.device.present():
            mode = self.device.get_mode()
            self.msg_print("BSS-1 connected!")
            self.hw_vers.set_text(self.device.get_hardware_version())
            self.fw_vers.set_text(self.device.get_firmware_version())
            if mode == 'normal':
                self.normal()
            else:
                self.firmware()
        else:
            self.msg_print("BBS-1 not connected!")
            self.show_alert_connect()

    def show_alert_connect(self):
        """Show an alert reporting failed device communication"""
        connect_alert = self.builder.get_object('connect_alert')
        if connect_alert.run() == -5:  # OK button
            connect_alert.hide()
            self.init_communication()
        else:
            self.quit()

    def normal(self):
        """Normal mode handling"""
        # TODO
        raise NotImplementedError

    def firmware(self):
        """Firmware mode handling"""
        # TODO
        raise NotImplementedError

    def on_menu_about_clicked(self, menuitem, data=None):
        """Show the about dialog"""
        about_dialog = self.builder.get_object("about_dialog")
        about_dialog.run()
        about_dialog.hide()
