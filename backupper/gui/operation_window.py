import PySimpleGUI as sg
import threading
from copy import deepcopy

class SBT_Operation:
	def __init__(self, msg: str = "Pending operation...", pbMax: int = 100):
		layout = [
			[sg.Column([[sg.Text(msg, key="msg", font="_ 12", justification="c")]], vertical_alignment='center', justification='center',  k='-C-')],
			[sg.Sizer(0, 5)],
			[sg.ProgressBar(pbMax, s=(40, 15), key="bar")]
		]
		self.window = sg.Window("Spotify Backup Manager - Operation", layout, finalize=True)
		self.stopEvent = threading.Event()
		self.handle()

	def setProgress(self, n: int):
		pass

	def setMessage(self, msg: str):
		pass

	def close(self):
		self.stopEvent.set()

	def handle(self):
		while not self.stopEvent.isSet():
			event, values = self.window.read()
			if event == sg.WIN_CLOSED:
				self.stopEvent.set()
				break
		self.window.close()

if __name__ == "__main__":
	SBT_Operation("Processing...", 100)