import os
from flask import Flask, session, request, redirect
from flask.templating import render_template
from flask_session import Session
import spotipy
import uuid
from functions import return_top_artists, return_top_tracks, select_tracks, create_playlist, get_movie_data



""" 
    First create a new app at 'Spotify for Developers' (https://developer.spotify.com/dashboard/applications)
    set these three as environment variables before running the application:

    SPOTIPY_CLIENT_ID='Client ID here'
    SPOTIPY_CLIENT_SECRET='Client Secret here'
    SPOTIPY_REDIRECT_URI='Redirect URI here' // must contain a port (example: 'http://127.0.0.1:8080')

    SPOTIPY_REDIRECT_URI must be added to your [app settings](https://developer.spotify.com/dashboard/applications)
"""



# setting the scope (the information we need from the Spotify API)
scope = 'user-library-read user-top-read playlist-modify-public user-follow-read'

# Configure application

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
# Configure session to use filesystem
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'

Session(app)


caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

# Ensure templates are auto-reloaded

app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route('/', methods=["GET", "POST"])
def index():
    global state
    global playlist
    global movie_data

    state = False
    playlist = ''
    movie_data = []

    if not session.get('uuid'):
        # If user is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())
        

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())

    # authenticating Spotify request
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope, cache_handler=cache_handler, show_dialog=True)

    if request.args.get("code"):
        # Redirect from Spotify auth page after retrieving the token
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Prompt the user to sign in if no token is found
        auth_url = auth_manager.get_authorize_url()
        return render_template("login.html", auth_url=auth_url)
    
    
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    
    # User reached route via POST
    if request.method == "POST":
        
        # render 'noinput.html' if no value is given to the 'Mood' field
        if not request.form.get("mood"):
            state = False
            return render_template("noinput.html")
        # if a value is given then change state to True
        state = True

        # getting the value for 'feeling'
        feeling = float(request.form.get("feeling"))/100

        # getting the value for 'mood'
        mood = request.form.get("mood")

        # getting user's top artists from Spotify
        top_artists = return_top_artists(spotify)

        # getting the top tracks for each artist
        top_tracks = return_top_tracks(spotify, top_artists)

        # selecting the ideal tracks
        selected_tracks = select_tracks(spotify, top_tracks, feeling)

        # creating a playlist from the selected tracks
        playlist = create_playlist(spotify, selected_tracks, feeling)

        # getting movie data from 'movie_data.csv' and comparing it with the user's 'mood'
        movie_data = get_movie_data(mood)
        
        # render 'music.html'
        return render_template("music.html", playlist=playlist)

    # render 'index.html'
    return render_template("index.html", name=spotify.me()["display_name"])


@app.route('/logout')
def logout():
    global state
    global playlist
    global movie_data 
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
        state = False
        playlist = ''
        movie_data = []
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


@app.route('/music')
def music():
    global playlist

    # if state is True then render 'music.html' else render 'noinput.html'
    if state:
        return render_template("music.html", playlist=playlist)
    else:
        return render_template("noinput.html")


@app.route('/movie')
def movie():
    global movie_data

    # getting the length of the list of movie data
    length = len(movie_data)

    # if state is True then render 'movie.html' else render 'noinput.html'
    if state:
        return render_template("movie.html", movie_data=movie_data, length=length)
    else:
        return render_template("noinput.html")


'''Following lines allow application to be run more conveniently with
`python app.py` (Make sure you're using python3)
(Also includes directive to leverage pythons threading capacity.)
'''
if __name__ == '__main__':
    app.run(threaded=True, port=int(os.environ.get("PORT", 5000)))



