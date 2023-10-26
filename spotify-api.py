import os
import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

# Assign Spotify API credentials
client_id = 'XXXXXXXXXX'
client_secret = 'XXXXXXXXXXX'
redirect_uri='http://localhost:3000'
scope='user-read-recently-played'

# Authenticate with the Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope))

# Create a function to handle empty URIs
def error_handler_uri(argument):
    if argument is None:
        return 'N/A'
    else:
        return argument

### DATASET 1  - Recently Listened Songs ###

# Define which data I am pulling from the API
recent_songs = sp.current_user_recently_played(limit=25)

# Create empty lists to hold different data
twenty_recent_songs = []
song_duration = [] 
twenty_recent_artists = [] 
artist_popularity_score = [] 
time_played_at=[] 
album = [] 
album_type = [] 
album_image = [] 
album_release_date = [] 
total_tracks_on_album = [] 
uri = [] 

# Use a for loop to iterate through the enumerated object and append values to the appropiate list
for key, value in enumerate(recent_songs['items']):
    twenty_recent_songs.append(value['track']['name'])
    twenty_recent_artists.append(value['track']['artists'][0]['name'])
    album.append(value['track']['album']['name'])
    time_played_at.append(value['played_at'])
    song_duration.append(value['track']['duration_ms'])
    artist_popularity_score.append(value['track']['popularity'])
    album_type.append(value['track']['album']['album_type'])
    album_image.append(value['track']['album']['images'][0]['url'])
    album_release_date.append(value['track']['album']['release_date'])
    total_tracks_on_album.append(value['track']['album']['total_tracks'])
    if error_handler_uri(recent_songs['items'][key]['context'])=='N/A':
        uri.append('No URI Available')
    else:
        uri.append(value['context']['uri'])

# Declare a Pandas dataframe to create a table with data
recent_songs_df = pd.DataFrame(list(zip(twenty_recent_songs, song_duration, time_played_at, twenty_recent_artists, 
                           artist_popularity_score, album, album_type, album_release_date, total_tracks_on_album, 
                           album_image, uri)),
                  columns=['Song', 'Song Duration', 'Time Played At', 'Artist', 'Artist Popularity Score', 
                           'Album', 'Album Type', 'Album Release Date', 'Total Tracks on Album', 'Album Cover',
                           'URI'])

### DATASET 2 - Favorite Artists Short/Medium/Long Term ###

# Define a new data scope and listening history ranges
scope = 'user-top-read'
ranges = ['short_term', 'medium_term', 'long_term']

# Ensure credentials are correct
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri, scope=scope))
# Create empty lists to hold different data
short_term_list=[]
medium_term_list=[]
long_term_list=[]
short_term_genre=[]
medium_term_genre=[]
long_term_genre=[]

# Use a nested for loop to iterate through and append results to appropiate list
for sp_range in ranges:
    #print("range:", sp_range)
    results = sp.current_user_top_artists(time_range=sp_range, limit=25)

    for i, item in enumerate(results['items']):
        if sp_range=='short_term':
            short_term_list.append(item['name'])
            short_term_genre.append(", ".join(item['genres']))
        if sp_range=='medium_term':
            medium_term_list.append(item['name'])
            medium_term_genre.append(", ".join(item['genres']))
        if sp_range=='long_term':
            long_term_list.append(item['name'])
            long_term_genre.append(", ".join(item['genres']))

# Declare a Pandas dataframe to create dataset
time_period_trends_df = pd.DataFrame(list(zip(short_term_list, short_term_genre, medium_term_list, medium_term_genre, long_term_list, long_term_genre)),columns=['Short_Term', 'Short_Term_Genre', 'Medium_Term', 'Medium_Term_Genre', 'Long_Term', 'Long_Term_Genre'])

# Pivot data
pivoted_table = time_period_trends_df.melt(var_name=['Time Period'])

# Rename columns
pivoted_table.rename(columns={"value": "Arist"})

### DATASET 3 - Recently Saved Songs ###

# Define the scope
scope = 'user-library-read'

# Ensure credentials are correct
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri, scope=scope))
# Define which data I am pulling from the API
user_saved_tracks = sp.current_user_saved_tracks(limit=50)

# Define empty lists
saved_tracks = []
song_duration = [] 
time_added_at = []
artists = [] 
artist_popularity_score = [] 
album = [] 
album_type = [] 
album_image = [] 
album_release_date = [] 
total_tracks_on_album = [] 
uri = [] 

# Iterate through the enumerated object and append to appropiate list
for key, value in enumerate(user_saved_tracks['items']):
    saved_tracks.append(value['track']['name'])
    artists.append(value['track']['artists'][0]['name'])
    time_added_at.append(value['added_at'])
    album.append(value['track']['album']['name'])
    song_duration.append(value['track']['duration_ms'])
    artist_popularity_score.append(value['track']['popularity'])
    album_type.append(value['track']['album']['album_type'])
    album_image.append(value['track']['album']['images'][0]['url'])
    album_release_date.append(value['track']['album']['release_date'])
    total_tracks_on_album.append(value['track']['album']['total_tracks'])
    if error_handler_uri(user_saved_tracks['items'][key]['track']['uri'])=='N/A':
        uri.append('No URI Available')
    else:
        uri.append(value['track']['uri'])

# Declare a Pandas dataframe to create a dataset
recent_saved_tracks_df = pd.DataFrame(list(zip(saved_tracks, song_duration, time_added_at, artists, 
                           artist_popularity_score, album, album_type, album_release_date, total_tracks_on_album, 
                           album_image, uri)),
                  columns=['Song', 'Song Duration', 'Time Added At', 'Artist', 'Artist Popularity Score', 
                           'Album', 'Album Type', 'Album Release Date', 'Total Tracks on Album', 'Album Cover',
                           'URI'])

# Use Pandas function ExcelWriter to save all 3 dataframes to 1 Excel file
with pd.ExcelWriter('Spotify_API_Data.xlsx') as writer:
    recent_songs_df.to_excel(writer, sheet_name='Recent Songs')
    time_period_trends_df.to_excel(writer, sheet_name='Time Period Trends')
    recent_saved_tracks_df.to_excel(writer, sheet_name='Liked Songs')
