import PySimpleGUI as sg
from copy import deepcopy
import webbrowser
import string

# Set the default theme (dark-green - Spotify-ish vibe)
sg.theme("DarkGrey")

class SBT_AccountSetup:
	SPOTIPY_GUIDE_LINK = "https://spotipy.readthedocs.io/en/master/#getting-started"
	ID_LEN = 32

	LAYOUT = [
		[sg.Text("SBT - Account setup", font="_ 18")],
		[sg.Sizer(0, 10)],
		[sg.Text(
			"Welcome to SBT's account setup wizard. This application will help you\n" + \
			"set up you Spotify account with Spotify Backupper Tool.",
		font="_ 12")],
		[sg.Sizer(0, 5)],
		[sg.Text(
			"To start off, please follow",
			expand_y=False, expand_x=False,
			pad=(0, 0), font="_ 12"),
		 sg.Text(
		 	"Spotipy's \"Getting started guide.\"",
		 	tooltip=SPOTIPY_GUIDE_LINK,
		 	enable_events=True, key="guide", font="_ 12",
		 	expand_y=True, expand_x=True, pad=(0, 0))],
		 [sg.Text("After you've set up your application, please type your CLIENT_ID below:", font="_ 12", pad=(0, 0))],
		 [sg.Input(key="client_id", s=(30, 1), font="_ 12", enable_events=True)],
		 [sg.Button("Submit", key="submit", font="_ 12")]
	]

	def __init__(self, backend = None):
		self.backend = backend
		self.window = sg.Window("Spotify Backup Manager - Account setup", deepcopy(self.LAYOUT), finalize=True)
		self.CLIENT_ID = None
		self.handle()

	def checkInput(self, client_id):
		if len(client_id) == 0:
			sg.popup_error(
				"Client ID field is empty!",
				title = "Error",
				font = "_ 12",
				keep_on_top = True)
			return False
		if len(client_id) != self.ID_LEN:
			sg.popup_error(
				"Client ID is too long or short! It should be 32 characters long.",
				title="Error",
				font="_ 12",
				keep_on_top=True)
			return False
		if not all(c in (string.ascii_letters + string.digits) for c in client_id):
			sg.popup_error(
				"Client ID contains non-aplha characters!",
				title="Error",
				font="_ 12",
				keep_on_top=True)
			return False
		return True

	def handle(self):
		while True:
			event, values = self.window.read()
			print(event, values)
			if event == sg.WIN_CLOSED or event == 'Cancel':
				break
			if event == "guide":
				webbrowser.open(self.SPOTIPY_GUIDE_LINK)
			if event == "client_id":
				if len(values[event]) > 32:
					self.window[event].update(value=values[event][:32])
			if event == "submit":
				if self.checkInput(values["client_id"]):
					self.CLIENT_ID = values["client_id"]
					break
		self.window.close()

if __name__ == "__main__":
	SBT_AccountSetup()