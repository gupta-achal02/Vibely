# Vibely
Vibely is an app which creates a custom playlist for you on Spotify and also recommends movies to watch based on your mood. It is made with Flask + Jinja along with HTML, CSS and JavaScript. 

#### [Demo](https://vibely.herokuapp.com)
Note: The demo website is facing some issues, but it is enough to get the general gist of how the app works. I feel too lazy to fix it. :P

### Prerequisites

Since this app involves the use of Spotify, you'll first need to create a new app at [Spotify for Developers](https://developer.spotify.com/dashboard/applications) and then set these three as environment variables before running the application:

```powershell
SPOTIPY_CLIENT_ID='Client ID here'
SPOTIPY_CLIENT_SECRET='Client Secret here'
SPOTIPY_REDIRECT_URI='Redirect URI here' 
```

SPOTIPY_REDIRECT_URI must be added to your [app settings ](https://developer.spotify.com/dashboard/applications)and must contain a port (example: 'http://127.0.0.1:8080')



### Layout and working

I've made the frontend as minimalistic as possible with a lot of whitespaces, as my focus was on the 'Python' side of things.

In the first webpage you will be asked to Sign in with your Spotify account. After signing in, you'll have to click 'Agree' to permit Vibely to access your account data which will include your followed and liked artists.

After clicking 'Agree', you'll be redirected to the Homepage where you'll be asked about your current 'Feeling' and 'Mood'. The first form has an input slider ranging from 0 - 100; 0 implying that you are feeling 'Disconsolate' and 100 implying that you are feeling 'Elated'. This input will determine the choice of music in the custom playlist. Whereas the second form has a dropdown menu with various 'moods' that you might be experiencing viz. "Downhearted", "Distasteful", "Annoyed", "Thrilled", "Anxious", "Delighted", "Excited" and "Calm". This input will determine the choice of movies.

After clicking 'Submit', you'll be redirected to the Music tab of the webpage where you'll see a confirmation message that your custom playlist has been created for you. You can press the 'Take me to the Playlist!!' button to directly launch the Spotify app to view the contents of the playlist; it will be named as 'Vibely ' followed by the number you selected. In the webpage you can select the Movie tab to see your movie recommendations. Clicking on the name of any movie you like will redirect you to its IMDb page.

Now let's look at the various files in the repository.



### Files

#### movie_data.csv

This contains the data of the top 250 movies from IMDb. It contains four columns viz. title, genre, url and cover which are all self explanatory. 

So for extracting data for movies, I'd initially planned on web-scraping from the IMDb website itself, but instead I found an even more efficient tool called [IMDbPY](https://imdbpy.github.io/). It is a Python package for retrieving and managing the data of the IMDb movie database about movies and people. Something great about this package is that it provides everything from the movie's genre to it's cover page's URL which normally would have been difficult to obtain. 

This is the code I used to create this csv file:

```python
import imdb
import csv

# creating an instance of the IMDb class
imdb_access = imdb.IMDb()

# getting IMDB's top 250 movies
top_movies = imdb_access.get_top250_movies()
top_movies_id = list(top_movies[i].movieID for i in range(250))

# writing the data for each movie in a csv file
with open('movie_data.csv', mode='w') as movie_data:
    fieldnames = ['title', 'genre', 'url', 'cover']
    writer = csv.DictWriter(movie_data, fieldnames=fieldnames)
    writer.writeheader()
    for m in range(250):
        title = imdb_access.get_movie(top_movies_id[m])
        genre = list(title['genres'])
        cover = title.data['cover url']
        url = imdb_access.get_imdbURL(title)
        writer.writerow({'title': title, 'genre': genre, 'url': url, 'cover': cover})
```

**Note : There's no need to run this code as I've already created 'movie_data.csv'. This is just a demonstrative code of how I did it. Also, depending on your internet speed, this can take up to 10-15 minutes to run.**



#### functions.py

This might be the most important file of this project, it contains all the functions which are used for playlist creation and for movie selection. 

For interacting with the user's Spotify account I've used a Python library called [Spotipy](https://spotipy.readthedocs.io/en/2.18.0/#), it is a lightweight Python library for the [Spotify Web API](https://developer.spotify.com/web-api/). With *Spotipy* you get full access to all of the music data provided by the Spotify platform. 

All the functions for playlist creation are self explanatory but I want to add a point about this function:

`select_tracks()`

You'll notice that I've compared the feeling argument to a term 'valence':

`if (d["valence"] <= (feeling + 0.05))`

According to the official Spotify API documentation, Valence is a measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).

Initially, I'd planned on using 'Danceability' and 'Energy' too, but in my case the artists I followed didn't have much songs which met all the conditions during track selection, and thus I ended up with much smaller number of songs in my playlists (lowest being only two songs). Although the user is encouraged to change the code and play around with it to get more personalized results. 

Another function I want to focus upon is :

`get_movie_data()`

I've decided on choosing these following genres of movies for each mood:

```python
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
```

For this I asked around to know what kind of movies would someone watch in case their mood is any of these. Again, the user is encouraged to change the code if they want more personalized results.



#### application.py

This is where it all comes together. 

You'll notice that I've set a 'scope' variable:

`scope = 'user-library-read user-top-read playlist-modify-public user-follow-read'`

It is important to pass this as an argument when authenticating the user through spotipy; this will give the Spotify Web API the information and permissions we need from it.

One issue I had was that when trying to sign in from a different account after logging out, I was getting an internal server error. Apparently the method I was using to authenticate spotipy was not applicable for multiple users. After searching for it a bit, I found about the `cache_handler` method which is a part of the spotipy library. It allows spotipy to authenticate multiple sessions. For generating random ids I used uuid and then stored them in this path `'./.spotify_caches/'`.
