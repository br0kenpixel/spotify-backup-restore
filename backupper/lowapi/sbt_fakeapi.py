class SBT_LowAPI:
	""" Fake backend for testing the GUI. """

	DEF_REDIRECT_URI = "http://localhost:8888/callback"
	DEF_SCOPES       = [
		"user-modify-playback-state",
		"user-library-read",
		"user-library-modify",
		"playlist-modify-private",
		"playlist-read-private",
		"playlist-modify-public"
	]

	FAKE_PLAYLISTS = [
		{
			"name": "Classics",
			"id": "1234567890",
			"tracks": [
				{
					"name": "Never Gonna Give You Up",
					"id": "1111111111"
				},
				{
					"name": "Together Forever",
					"id": "1111111112"
				},
				{
					"name": "Why?",
					"id": "1111111113"
				},
				{
					"name": "Just Debugging",
					"id": "1111111114"
				}
			]
		},
		{
			"name": "Car songs",
			"id": "1234567891",
			"tracks": [
				{
					"name": "Shiny new car?!",
					"id": "1111111121"
				},
				{
					"name": "Hey??",
					"id": "1111111122"
				},
				{
					"name": "Need a new car",
					"id": "1111111123"
				},
				{
					"name": "Hello there!",
					"id": "1111111124"
				}
			]
		}
	]

	LIBRARY = [
		{
			"name": "Somewhere to Run",
			"id": "1234567892"
		},
		{
			"name": "zer0",
			"id": "1234567893"
		},
		{
			"name": "Circles",
			"id": "1234567894"
		},
		{
			"name": "No Regrets",
			"id": "1234567895"
		}
	]

	def __init__(self, client_id: str, redirect_uri=DEF_REDIRECT_URI) -> None:
		self.client_id = client_id
		self.auth_manager = None
		self.spotify = None

		# Trigger auth
		self.usercache = None

	def __repr__(self):
		return f"<SBT_FakeAPI user=\"Eggs Benedict\">"

	@property
	def display_name(self):
		return "Eggs Benedict"

	@property
	def id(self):
		return "1234567890"

	@property
	def user_url(self):
		return "https://spotify.com/"

	@property
	def user_followers(self):
		return 69

	@property
	def user_picture(self):
		return "https://spotify.com/"

	def iterPlaylists(self, *, limit: int = 1):
		for playlist in self.FAKE_PLAYLISTS:
			name = playlist["name"]
			id_ = playlist["id"]
			tracks = self.iterPlaylistTracks(id_)

			yield {"name": name, "id": id_, "tracks": tracks}

	def iterPlaylistTracks(self, playlist_id: str, *, limit: int = 1):
		playlist = next(playlist for playlist in self.FAKE_PLAYLISTS if playlist["id"] == playlist_id)
		yield from playlist["tracks"]

	def getPlaylistTracks(self, playlist_id: str) -> tuple:
		results = list()
		for result in self.iterPlaylistTracks(playlist_id, limit=100):
			results.append(result)
		return tuple(results)

	def getPlaylists(self, delay: int = 1) -> tuple:
		playlists = list()
		for playlist in self.iterPlaylists(limit=50):
			playlist["tracks"] = self.getPlaylistTracks(playlist["id"])
			playlists.append(playlist)
		return tuple(playlists)

	def iterSavedTracks(self, *, limit: int = 1):
		getter = self.LIBRARY

		for track in getter:
			id_ = track["track"]["id"]
			name = track["track"]["name"]
			#explicit = track["track"]["explicit"]
			#duration = track["track"]["duration_ms"]

			yield {
				"id": id_,
				"name": name,
				#"explicit": explicit,
				#"duration": duration
			}

	def getSavedTracks(self) -> tuple:
		tracks = list()
		for track in self.iterSavedTracks(limit=20):
			tracks.append(track)
		return tuple(tracks)


if __name__ == "__main__":
	print("Test mode")
	sbt = SBT_LowAPI("abcdefgh1234567890")
	print(sbt)