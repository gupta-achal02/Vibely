import random
import csv

# Get the top artists from the user's spotify account

def return_top_artists(spotify):
	
	artists_uri = []

	ranges = ['short_term', 'medium_term', 'long_term']

	for r in ranges:
		"""getting the top artists (max 50), this will include the user's favourite artists 
		   alongwith the artists they have been listening to recently"""
		top_data = spotify.current_user_top_artists(limit=50, time_range=r)
		artists_data = top_data['items']

		for d in artists_data:
			if d["uri"] not in artists_uri:		
				artists_uri.append(d['uri'])
	# getting the top followed artists (max 50)
	followed_data = spotify.current_user_followed_artists(limit=50)
	artists_data = followed_data['artists']

	for d in artists_data["items"]:
		if d["uri"] not in artists_uri:
			artists_uri.append(d['uri'])

	return artists_uri


# Get a list of tracks from each artist

def return_top_tracks(spotify, artists_uri):
	
	tracks_uri = []

	for artist in artists_uri:
		top_data = spotify.artist_top_tracks(artist)
		tracks_data = top_data['tracks']

		for d in tracks_data:
			tracks_uri.append(d['uri'])

	return tracks_uri

#  Select tracks which are ideal for the user

def select_tracks(spotify, tracks_uri, feeling):
	
	selected_tracks = []

	random.shuffle(tracks_uri)
	tracks_uri_grouped = list(tracks_uri[i:(i+50)] for i in range(0, len(tracks_uri), 50))

	#  getting each track's valence parameter and comparing it to the user's feeling

	for t in tracks_uri_grouped:
		tracks_data = spotify.audio_features(t)
		for d in tracks_data:
			try:
				if feeling < 0.10:
					if (d["valence"] <= (feeling + 0.05)):
						selected_tracks.append(d["uri"])					
				elif 0.10 <= feeling < 0.25:						
					if ((feeling - 0.05) <= d["valence"] <= (feeling + 0.05)):
						selected_tracks.append(d["uri"])
				elif 0.25 <= feeling < 0.50:						
					if ((feeling - 0.05) <= d["valence"] <= (feeling + 0.05)):
						selected_tracks.append(d["uri"])
				elif 0.50 <= feeling < 0.75:						
					if ((feeling - 0.05) <= d["valence"] <= (feeling + 0.05)):
						selected_tracks.append(d["uri"])
				elif 0.75 <= feeling < 0.90:						
					if ((feeling - 0.05) <= d["valence"] <= (feeling + 0.05)):
						selected_tracks.append(d["uri"])
				elif feeling >= 0.90:
					if ((feeling - 0.05) <= d["valence"] <= 1):
						selected_tracks.append(d["uri"])
			except TypeError as te:
				continue

	return selected_tracks			

# Create a playlist from the selected tracks

def create_playlist(spotify, selected_tracks, feeling):

	user_data = spotify.current_user()
	user_id = user_data["id"]

	playlist_data = spotify.user_playlist_create(user_id, "Vibely " + str(feeling))
	playlist_id = playlist_data["id"]
	playlist_uri = playlist_data["uri"]

	random.shuffle(selected_tracks)
	spotify.user_playlist_add_tracks(user_id, playlist_id, selected_tracks[0:30])

	return playlist_uri
    
# Get movie data ideal for the user's mood

def get_movie_data(mood): 
    c = 0
    output = []

	# comparing and selecting few selected movie genres with the user's mood

    if mood == "Downhearted":
        genre = "Romance"
    elif mood == "Distasteful":
        genre = "Musical"
    elif mood == "Annoyed":
        genre = "Family"
    elif mood == "Thrilled":
        genre = "Thriller"
    elif mood == "Anxious":
        genre = "Sport"
    elif mood == "Delighted":
        genre = "Comedy"
    elif mood == "Excited":
        genre = "Adventure"
    elif mood == "Calm":
        genre = "Music"

	# fetching the movie data from 'movie_data.csv' (max 5)

    with open('movie_data.csv') as movie_data:
        data = [{k: v for k, v in row.items()}
            for row in csv.DictReader(movie_data, skipinitialspace=True)]
        
        random.shuffle(data)

        for i in data:
            if genre in i['genre']:
                output.append(i)
                c += 1
            if c == 5:
                break
    
    return output