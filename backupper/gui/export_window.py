# Copyright (C) 2022 Fábián Varga
#
# This file is part of Spotify Backup Tool.
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
# along with this program. If not, see <https://www.gnu.org/licenses/>

import PySimpleGUI as sg
from copy import deepcopy

# Set the default theme (dark-green - Spotify-ish vibe)
sg.theme("DarkGrey")

class SBT_ExportWizard:
	SPOTIPY_GUIDE_LINK = "https://spotipy.readthedocs.io/en/master/#getting-started"
	ID_LEN = 32

	LAYOUT = [
		[sg.Text("SBT - Export Wizard", font="_ 18")],
		[sg.Sizer(0, 5)],
		[sg.Text(
			"Please choose how you'd like to save your selected songs.", font="_ 11")],
		[sg.Sizer(0, 5)],
		[sg.Text("File:"), sg.Push(), sg.Text("Please select file..."), sg.FileSaveAs(button_text="Browse", file_types = (("SBT Backup Files", "*.sbf"),), default_extension="sbf")],
		[sg.Text("Format:"), sg.Push(), sg.Combo(["JSON"], default_value="JSON", disabled=True)],
		[sg.Text("Prettify:"), sg.Push(), sg.Checkbox("Yes", key="prettify", default=True)],
		[sg.Text("Compression:"), sg.Push(), sg.Checkbox("Enable", key="cmp", enable_events=True), sg.Combo(["LZMA", "GZIP"], default_value="LZMA", visible=False, key="cmp_sel", readonly=True)],
		[sg.Text("Include account ID:"), sg.Push(), sg.Checkbox("Yes", key="aid", default=True, enable_events=True), sg.Text("Obfuscation:", key="obf_label"), sg.Combo(["None", "Simple", "Static", "Extreme"], default_value="Simple", key="obf_mode", readonly=True)],
		[sg.Sizer(0, 5)],
		[sg.Button("Export", key="export")]
	]

	def __init__(self):
		self.window = sg.Window("Spotify Backup Manager - Export Wizard", deepcopy(self.LAYOUT), finalize=True)

	def start(self):
		self.handle()
		return {
			"file": self._ret_vals["Browse"],
			"format": self._ret_vals[0], # Unused for now, JSON is forced
			"prettify": self._ret_vals["prettify"],
			"compress": self._ret_vals["cmp"],
			"compression": self._ret_vals["cmp_sel"] or None,
			"account_id": self._ret_vals["aid"],
			"account_obfuscation": self._ret_vals["obf_mode"] if self._ret_vals["aid"] else None
		}

	def handle(self):
		while True:
			event, values = self.window.read()
			if event == sg.WIN_CLOSED:
				self._ret_vals = values
				break
			if event == "cmp":
				self.window["cmp_sel"].update(visible=values["cmp"], value=values["cmp_sel"])
			if event == "aid":
				self.window["obf_label"].update(visible=values["aid"])
				self.window["obf_mode"].update(visible=values["aid"])
			if event == "export":
				if values["Browse"] == "":
					sg.popup_error("No savefile selected!", title="Error", keep_on_top=True)
					continue
				self._ret_vals = values
				break
		self.window.close()

if __name__ == "__main__":
	print(SBT_ExportWizard().start())