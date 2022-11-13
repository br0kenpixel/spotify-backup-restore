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

from importlib_metadata import version as module_version
from os.path            import exists, expanduser
from platform           import python_version
from dataclasses        import dataclass
from datetime           import datetime
from random             import randrange
from time               import sleep
from enum               import auto

import PySimpleGUI as sg
import webbrowser
import json
import lzma
import gzip

# SBT backend
from .acctsetup_window import SBT_AccountSetup
from .export_window    import SBT_ExportWizard
# App version from Launcher
from __main__           import APP_VERSION

# Set the default theme (dark-green - Spotify-ish vibe)
sg.theme("DarkGrey")

@dataclass(frozen=True)
class PlaylistUID:
    name: str
    id: str

@dataclass(frozen=True)
class TrackUID:
    playlist: PlaylistUID
    name: str
    album: str
    artist: str
    id: str

LIBRARY_UID = PlaylistUID("library", auto())

class SBT_MainWindow:
    SYMBOL_DOWN_ARROW = "⇩"
    SYMBOL_CHECKED    = "✅"
    SYMBOL_UNCHECKED  = "☑️"

    ACCOUNT_DB_PATH = "~/sbt_accounts.json"

    TDATA = sg.TreeData()

    TITLE_IMAGE_COL = [[ sg.Image("gui/sbt_logo_mini.png", s=(100, 100)) ]]
    TITLE_TEXT_COL = [
        [sg.Text("Spotify Backupper Tool", font="_ 20")],
        [sg.Text(f"Version: {APP_VERSION}")],
        [sg.Text(f"Python version: {python_version()}", pad=(5, 0))],
        [sg.Text(f"SpotiPy version: {module_version('spotipy')}", pad=(5, 0))],
        [sg.Text(f"PySimpleGUI version: {module_version('PySimpleGUI')}", pad=(5, 0))],
        [sg.Text("Copyright (C) 2022 Fábián Varga - br0kenpixel", pad=(5, 3))]
    ]
    TITLE_GITHUB_COL = [[
        sg.Button(
            image_filename      = "gui/github_logo.png",
            mouseover_colors    = "darkblue",
            button_color        = "black",
            key                 = "git",
            image_subsample     = 14,
        )
    ]]

    TITLE_BAR = [
        [
            sg.Column(TITLE_IMAGE_COL), sg.Column(TITLE_TEXT_COL),
            sg.Column(TITLE_GITHUB_COL, element_justification="right", expand_x=True, expand_y=True)
        ]
    ]

    BODY = [
        [
            sg.Push(),
            sg.Frame("Mode", [
                [sg.Radio("Backup",  "mode", default=True,  key="mode_backup",  enable_events=True, disabled=True),
                 sg.Radio("Restore", "mode", default=False, key="mode_restore", enable_events=True, disabled=True)]
            ])
        ],
        [
            sg.Frame("Accounts", [
                [sg.Combo([], default_value="Please select...", s=(95, 1), readonly=True, key="accounts"),
                 sg.Button(SYMBOL_DOWN_ARROW, disabled_button_color="gray", key="acct_select"),
                 sg.Button("+", key="new", disabled_button_color="gray")]
            ], key="backup"),
            sg.Frame("Restore source", [
                [sg.Text("Please select a .SBT backup file...", s=(86, 1)), sg.FileBrowse("Browse...", key="file"),
                 sg.Button(SYMBOL_DOWN_ARROW, disabled_button_color="gray", key="acct_select"),
                 sg.Button("+", key="new", disabled_button_color="gray")]
            ], key="restore", visible=False)
        ],
        [
            sg.Frame("Tracks", [
                [
                    sg.Tree(data=TDATA,
                            key="tree",
                            headings=[""],
                            col_widths=[3],
                            col0_width=86,
                            expand_x=True,
                            expand_y=True,
                            enable_events=True,
                            auto_size_columns=False,
                            num_rows=20)
                ]
            ])
        ],
        [
            sg.Frame("Actions", [
                [sg.Button("Refresh",           key="refresh",          disabled=True, disabled_button_color="gray"),
                 sg.Button("Export",            key="export",           disabled=True, disabled_button_color="gray"),
                ]
            ])
        ]
    ]

    FOOTER = [
        [sg.StatusBar("Ready", key="status", s=(100, 1))],
    ]

    LAYOUT = [
        *TITLE_BAR,
        *BODY,
        *FOOTER
    ]

    UNFOCUS_TARGET = ["git", "accounts", "acct_select", "new", "file", "refresh", "export"]

    def __init__(self, backend = None):
        self.backend = backend
        self._selected = None
        
        self.window = sg.Window("Spotify Backup Manager", self.LAYOUT, finalize=True)
        self.window['tree'].Widget.configure(show='tree')
        self.TDATA.insert("", LIBRARY_UID, "💿 Liked Songs", ["✅"])
        
        self.refresh()
        self.loadAccounts()
        self.handle()

    def loadAccounts(self):
        if not exists(expanduser("~/sbt_accounts.json")):
            return
        
        try:
            storage = open(expanduser("~/sbt_accounts.json"), "r")
            accounts = json.load(storage)
            assert isinstance(accounts, list), "Invalid data type found, corrupt file?"
        except Exception:
            sg.popup_error_with_traceback("Error while reading account storage:", ex)
            exit(1)

        self.window["accounts"].update(values=accounts, value="Please select...")
        storage.close()

    def saveAccounts(self):
        accounts = self.getAccounts()
        if len(accounts) == 0:
            return

        try:
            storage = open(expanduser("~/sbt_accounts.json"), "w")
        except Exception as ex:
            sg.popup_error_with_traceback("Error while modifying account storage:", ex)
            exit(1)

        json.dump(accounts, storage)
        storage.flush()
        storage.close()

    def addAccount(self, client_id):
        accounts = self.getAccounts()
        if client_id in accounts:
            sg.popup_error(
                "That account already exists!",
                title="Error",
                font="_ 12",
                keep_on_top=True)
            return
        accounts.append(client_id)
        self.window["accounts"].update(values=accounts)

        if len(accounts) == 1:
            # Autoselect newly added account
            self.window["accounts"].update(value=accounts[0])
        self.saveAccounts()

    def newAccountSetup(self):
        setup = SBT_AccountSetup()
        client_id = setup.CLIENT_ID
        if client_id == None:
            # Cancel operation
            return

        self.addAccount(client_id)
        del setup

    def getAccounts(self):
        # Unofficial way
        return self.window["accounts"].Values

    def loadTracklist(self):
        track_count = 0
        
        self.setStatus("Fetching playlists...")
        playlists = self.lowapi.getPlaylists()
        self.setStatus("Sleeping to prevent API limits...")
        sleep(1)
        self.setStatus("Fetching Liked Songs...")
        library = self.lowapi.getSavedTracks()

        self.track_db = {"playlists": playlists, "library":library}

        for playlist in playlists:
            name = playlist["name"]
            id = playlist["id"]
            tracks = playlist["tracks"]
            uid = PlaylistUID(name, id)

            self.TDATA.insert("", uid, f"💿 {name}", ["✅"])
            for i, trackinfo in enumerate(tracks):
                #self.setStatus(f"Loading {name} - {i + 1}/{len(tracks)}")
                display = f"{trackinfo['name']} - {trackinfo['artist']}"
                self.TDATA.insert(
                    uid,
                    TrackUID(uid, trackinfo["name"], trackinfo["album"], trackinfo["artist"], trackinfo["id"]),
                    f"♫ {display}",
                    ["✅"])
                track_count += 1
        
        for i, trackinfo in enumerate(library):
            #self.setStatus(f"Loading Liked Songs - {i + 1}/unknown")
            display = f"{trackinfo['name']} - {trackinfo['artist']}"
            self.TDATA.insert(
                LIBRARY_UID,
                TrackUID(LIBRARY_UID, trackinfo["name"], trackinfo["album"], trackinfo["artist"], trackinfo["id"]),
                f"♫ {display}",
                ["✅"])
            track_count += 1
        self.updateElement("tree", values=self.TDATA)
        self.setStatus(f"Ready. Retrieved {track_count} tracks.")

    # Alias
    def refresh(self):
        self.window.refresh()

    def setStatus(self, msg: str):
        self.window["status"].update(msg)
        self.window.refresh()

    def updateElement(self, e, *args, **kwargs):
        self.window[e].update(*args, **kwargs)

    def _getItemSelection(self, uid):
        """ Return the selection state of an item. """
        return self.TDATA.tree_dict[uid].values[0] in ("✅", "⏹")

    def _setItemSelection(self, uid, mode):
        self.window["tree"].update(key=uid, value=[mode])
        self.TDATA.tree_dict[uid].values = [mode]

    def _findPlaylistTracks(self, playlist_uid):
        """ Yield tracks from the specified playlist. """
        for entry in self.TDATA.tree_dict.keys():
            if isinstance(entry, TrackUID):
                if entry.playlist == playlist_uid:
                    yield entry

    def _getPlaylistTrackSelections(self, playlist_uid):
        """ Yield selection modes for every track in a playlist. """
        for track_uid in self._findPlaylistTracks(playlist_uid):
            yield self._getItemSelection(track_uid)

    def _checkPlaylistSelection(self, playlist_uid):
        """ Check if all tracks in the specified playlist have the same selection mode. """
        modes = self._getPlaylistTrackSelections(playlist_uid)
        first = next(modes)
        return all(mode == first for mode in modes)

    def setPlaylistTrackSelection(self, playlist_uid, mode):
        """ Set selection mode for all tracks in the specified playlist. """
        for track in self._findPlaylistTracks(playlist_uid):
            self.TDATA.tree_dict[track].values[0] = mode
            self.window["tree"].update(key=track, value=[mode])

    def changeSelection(self, uid):
        current_mode = self.TDATA.tree_dict[uid].values[0]
        mode = "✅" if current_mode == "❌" else "❌"

        self._setItemSelection(uid, mode)

        if isinstance(uid, PlaylistUID):
            # Clicked on a playlist
            # Change selection for every track
            self.setPlaylistTrackSelection(uid, mode)
        else:
            # Clicked on a track
            playlist = uid.playlist

            if self._checkPlaylistSelection(playlist):
                self.setPlaylistTrackSelection(playlist, mode)
            else:
                mode = "⏹"
            self._setItemSelection(playlist, mode)

    def _getPlaylists(self):
        """ Yield all playlists. """
        for entry in self.TDATA.tree_dict.keys():
            if isinstance(entry, PlaylistUID) and entry != LIBRARY_UID:
                yield entry

    def _includeLibrary(self):
        return self._getItemSelection(LIBRARY_UID)

    def _obfuscated_account(self, mode):
        acct = list(self.lowapi.id)

        if mode == "Simple":
            for _ in range(6):
                pos = randrange(0, len(acct))
                acct[pos] = "*"
        elif mode == "Static":
            sums = tuple(map(int, acct))
            sums = zip(sums[::2], sums[1::2])
            sums = map(sum, sums)
            positions = map(lambda n: n % len(acct), set(sums))

            for pos in positions:
                acct[pos] = "*"
        elif mode == "Extreme":
            skip = (0, len(acct) - 1, len(acct) // 2)
            for pos in range(len(acct)):
                if pos not in skip:
                    acct[pos] = "*"
        return "".join(acct)

    def beginExport(self, opts: dict):
        self.setStatus("Exporting selected songs... Please wait!")

        time_info = datetime.now()      
        save_data = {
            "sbt": {
                "version": 2.0,
                "creation": str(time_info),
                "account": self._obfuscated_account(opts["account_obfuscation"]) if opts["account_id"] else None
            },
            "library": None,
            "playlists": None
        }

        if self._includeLibrary():
            save_data["library"] = []
            for i, track in enumerate(self._findPlaylistTracks(LIBRARY_UID)):
                if self._getItemSelection(track):
                    save_data["library"].append({
                        "pos": i + 1,
                        "name": track.name,
                        "album": track.album,
                        "artist": track.artist,
                        "id": track.id
                    })

        for playlist in self._getPlaylists():
            if self._getItemSelection(playlist):
                if save_data["playlists"] == None:
                    save_data["playlists"] = {}
                save_data["playlists"][playlist.name] = {"id": playlist.id, "tracks": []}
            for i, track in enumerate(self._findPlaylistTracks(playlist)):
                if self._getItemSelection(track):
                    save_data["playlists"][playlist.name]["tracks"].append({
                        "pos": i + 1,
                        "name": track.name,
                        "album": track.album,
                        "artist": track.artist,
                        "id": track.id
                    })
        
        save_data = json.dumps(save_data, indent=(4 if opts["prettify"] else 0)).encode()
        if opts["compress"]:
            if opts["compression"] == "LZMA":
                save_data = lzma.compress(save_data)
            elif opts["compression"] == "GZIP":
                save_data = gzip.compress(save_data)

        savef = open(opts["file"], "wb")
        savef.write(save_data)
        savef.flush()
        savef.close()
        self.setStatus("Export successful.")

    def handle(self):
        while True:
            event, values = self.window.read()
            #print(event, values)
            if event == sg.WIN_CLOSED:
                break

            if event == "git":
                webbrowser.open("https://github.com/br0kenpixel")

            if event == "new":
                for element in self.UNFOCUS_TARGET:
                    self.updateElement(element, disabled=True)
                self.setStatus("Setting up new account")
                self.newAccountSetup()
                for element in self.UNFOCUS_TARGET:
                    self.updateElement(element, disabled=False)
                self.setStatus("Ready")

            if event == "mode_backup":
                self.updateElement("restore", visible=False)
                self.updateElement("backup", visible=True)

            if event == "mode_restore":
                self.updateElement("restore", visible=True)
                self.updateElement("backup", visible=False)

            if event == "acct_select":
                for element in self.UNFOCUS_TARGET:
                    self.updateElement(element, disabled=True)
                try:
                    client_id = values["accounts"].split(" ", 1)[0] # Filter out name if present
                    self.setStatus(f"Connecting to account {client_id}...")
                    self.lowapi = self.backend(client_id)
                except Exception as ex:
                    sg.popup_error_with_traceback("Error while setting up backend:", ex)
                    break

                self.updateElement("accounts", value=f"{values['accounts']} - {self.lowapi.display_name}")
                self.setStatus("Loading tracks...")
                self.loadTracklist()
                for element in self.UNFOCUS_TARGET:
                    self.updateElement(element, disabled=False)

            if event == "tree":
                selection = values["tree"][0]
                if self._selected == selection:
                    self.changeSelection(selection)
                    self._selected = None
                else:
                    self._selected = selection

            if event == "export":
                for element in self.UNFOCUS_TARGET:
                    self.window[element].update(disabled=True)

                self.setStatus("Starting export wizard...")
                wizard = SBT_ExportWizard()
                opts = wizard.start()

                # Do the export here...
                self.beginExport(opts)

                for element in self.UNFOCUS_TARGET:
                    self.window[element].update(disabled=False)

        self.window.close()

if __name__ == "__main__":
    # For debugging only!
    SBT_MainWindow()