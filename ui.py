# -*- coding: utf-8 *-*
"""BBS1 GUI handling"""
# A tool to communicate with Peterson's BBS-1 metronome
# Copyright (C) 2012-2015 Raphaël Doursenaud <rdoursenaud@free.fr>
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

from copy import deepcopy

import communication
import device
import logging

try:
    # noinspection PyPackageRequirements,PyUnresolvedReferences
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gio
except ImportError:
    print("This script needs pygobject to run")
    raise


# noinspection PyUnusedLocal
class Bbs1App(Gtk.Application):
    """BBS1 main GUI application"""

    def __init__(self):
        """Application initialization"""
        self.window = None
        self.message = None
        self.hw_vers = ''
        self.fw_vers = ''
        self.com = None
        self.device = None
        self.tempofile = None
        self.tempofile_cache = None
        self.clear_confirm = True  # Ask for confirmation before clearing device

        Gtk.Application.__init__(self, application_id='apps.bbs1',
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)

        # Glade
        logging.debug('Loading glade file')
        self.builder = Gtk.Builder()
        self.builder.add_from_file('bbs1.glade')

        # Signals
        self.builder.connect_signals(self)
        self.connect('activate', self.on_activate)

    def on_activate(self, data=None):
        """
        Secondary initialization

        :param data: Optional data
        """

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
        """
        Initialize communication

        :param data: Optional data
        """
        logging.debug('Initializing communication')
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
        """
        Initialize the device

        :param data: Optional data
        """

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
            self.msg_print("BSS-1 connected! (" + mode + " mode)")
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
        self._refresh()

    def firmware(self):
        """Firmware mode handling"""
        # TODO
        raise NotImplementedError

    def on_action_new_activate(self, menuitem, data=None):
        self._unimplemented()

    def on_action_open_activate(self, menuitem, data=None):
        self._unimplemented()

    def on_action_save_as_activate(self, menuitem, data=None):
        self._unimplemented()

    def on_action_refresh_activate(self, menuitem, data=None):
        """
        Refresh tempo maps informations

        :param menuitem: The menuitem that received the signal
        :param data: Optional data
        :type menuitem: gtk.MenuItem
        """
        self._refresh()

    def _refresh(self):
        """Refresh UI informations"""
        self.tempofile = self.device.get_tempomaps()
        self.tempofile_cache = deepcopy(self.tempofile)
        logging.debug("Successfully cached tempo file: " + str(self.tempofile == self.tempofile_cache))
        self._refresh_ui()

    def _refresh_ui(self):
        # Compute and display free space
        # Free space is 4kB * 9 = 36kB
        # <=> 1018 bars * 9 = 9162
        free_space = 36864  # in bytes

        for i in range(0, self.tempofile.maps_count):
            igtk = str(i + 1)
            entryname = 'entry' + igtk
            entry = self.builder.get_object(entryname)
            entry.handler_block_by_func(self.on_changed)
            entry.set_text(self.tempofile.maps[i].name)
            entry.handler_unblock_by_func(self.on_changed)
            spinbuttonname = 'spinbutton' + igtk
            spinbutton = self.builder.get_object(spinbuttonname)
            spinbutton.handler_block_by_func(self.on_changed)
            spinbutton.set_value(self.tempofile.maps[i].count_in)
            spinbutton.handler_unblock_by_func(self.on_changed)
            switchname = 'switch' + igtk
            switch = self.builder.get_object(switchname)
            switch.handler_block_by_func(self.on_changed)
            switch.set_state(self.tempofile.maps[i].looping)
            switch.handler_unblock_by_func(self.on_changed)
            free_space -= self.tempofile.maps[i].length

        fraction_space = free_space / 36864
        logging.debug('Space available: ' + str(fraction_space))
        self.builder.get_object('free_space').set_fraction(fraction_space)

        self.builder.get_object('menu_apply').set_sensitive(not self.tempofile == self.tempofile_cache)

    def on_action_clear_activate(self, menuitem, data=None):
        """
        Handle clear all tempo maps button

        :param menuitem: The menuitem that received the signal
        :param data: Optional data
        :type menuitem: gtk.MenuItem
        """
        if self.clear_confirm:
            confirm = self.builder.get_object('clear_confirm_dialog')
            if confirm.run() == -8:
                self._clear()
            confirm.hide()
        else:
            self._clear()

    def _clear(self):
        """
        Clear all tempo maps
        """
        self.device.clear_tempomaps()
        self._refresh()

    def on_check_clear_toggled(self, widget, data=None):
        """
        Don't ask before device clearing callback

        :param widget: The checkbox that received the signal
        :param data: Optional data
        :type widget: gtk.CheckButton
        """
        self.clear_confirm = not widget.get_active()

    def on_action_apply_activate(self, menuitem, data=None):
        self._unimplemented()

    def on_action_about_activate(self, menuitem, data=None):
        """
        Show the about dialog

        :param menuitem: The menuitem that received the signal
        :param data: Optional data
        :type menuitem: gtk.MenuItem
        """
        about_dialog = self.builder.get_object('about_dialog')
        about_dialog.run()
        about_dialog.hide()

    def on_del_button_clicked(self, button, data=None):
        """
        Reset one entry

        :param button: Widget clicked
        :param data: Optional data
        :type button: gtk.Button
        """
        map_index = int(button.get_name()) - 1
        self.tempofile.maps[map_index].reset()
        self._refresh_ui()

    def on_changed(self, widget, data=None):
        """
        Update changed UI values

        :param widget: The changed widget
        :param data: Optional data
        :type widget: gtk.Widget
        """
        map_index = int(widget.get_name()) - 1
        if isinstance(widget, Gtk.Switch):
            self.tempofile.maps[map_index].looping = widget.get_active()
            logging.debug("Set looping for map #"
                          + str(map_index)
                          + ' to: '
                          + str(self.tempofile.maps[map_index].looping))
        elif isinstance(widget, Gtk.SpinButton):
            self.tempofile.maps[map_index].count_in = int(widget.get_text())
            logging.debug("Set count_in for map #"
                          + str(map_index)
                          + ' to: '
                          + str(self.tempofile.maps[map_index].count_in))
        elif isinstance(widget, Gtk.Entry):
            self.tempofile.maps[map_index].set_name(widget.get_text())
            logging.debug("Set name for map #"
                          + str(map_index)
                          + ' to: '
                          + str(self.tempofile.maps[map_index].name))
        else:
            raise TypeError("Unexpected widget")
        self._refresh_ui()

    def _unimplemented(self):
        unimplemented = self.builder.get_object('unimplemented_dialog')
        unimplemented.run()
        unimplemented.hide()
