import os
import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth

# Define Spotify API credentials
# You need to define your own client id and secret. I removed mine for privacy reasons.
client_id = 'XXXXXXXXXX'
client_secret = 'XXXXXXXXXXX'
redirect_uri = 'http://localhost:3000'
scopes = ['user-read-recently-played', 'user-top-read', 'user-library-read']

# Function to authenticate with Spotify API
def authenticate_with_spotify(scope):
    return spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

# Authenticate with the Spotify API for each scope
sp_recent = authenticate_with_spotify('user-read-recently-played')
sp_top = authenticate_with_spotify('user-top-read')
sp_saved = authenticate_with_spotify('user-library-read')

# Define a function to handle empty URIs
def error_handler_uri(argument):
    return argument if argument is not None else 'N/A'

# Function to extract recent songs data
def extract_recent_songs_data():
    recent_songs = sp_recent.current_user_recently_played(limit=25)
    data = []
    for item in recent_songs['items']:
        data.append({
            'Song': item['track']['name'],
            'Song Duration': item['track']['duration_ms'],
            'Time Played At': item['played_at'],
            'Artist': item['track']['artists'][0]['name'],
            'Artist Popularity Score': item['track']['popularity'],
            'Album': item['track']['album']['name'],
            'Album Type': item['track']['album']['album_type'],
            'Album Release Date': item['track']['album']['release_date'],
            'Total Tracks on Album': item['track']['album']['total_tracks'],
            'Album Cover': item['track']['album']['images'][0]['url'],
            'URI': error_handler_uri(item['context']['uri'])
        })
    return pd.DataFrame(data)

# Function to extract my top artists data
def extract_top_artists_data():
    ranges = ['short_term', 'medium_term', 'long_term']
    data = {range: [] for range in ranges}
    for sp_range in ranges:
        results = sp_top.current_user_top_artists(time_range=sp_range, limit=25)
        for item in results['items']:
            data[sp_range].append({'Artist': item['name'], 'Genres': ', '.join(item['genres'])})
    return pd.DataFrame(data)

# Function to extract my recent saved tracks data
def extract_saved_tracks_data():
    user_saved_tracks = sp_saved.current_user_saved_tracks(limit=50)
    data = []
    for item in user_saved_tracks['items']:
        data.append({
            'Song': item['track']['name'],
            'Song Duration': item['track']['duration_ms'],
            'Time Added At': item['added_at'],
            'Artist': item['track']['artists'][0]['name'],
            'Artist Popularity Score': item['track']['popularity'],
            'Album': item['track']['album']['name'],
            'Album Type': item['track']['album']['album_type'],
            'Album Release Date': item['track']['album']['release_date'],
            'Total Tracks on Album': item['track']['album']['total_tracks'],
            'Album Cover': item['track']['album']['images'][0]['url'],
            'URI': error_handler_uri(item['track']['uri'])
        })
    return pd.DataFrame(data)

# Run each function
recent_songs_df = extract_recent_songs_data()
time_period_trends_df = extract_top_artists_data()
recent_saved_tracks_df = extract_saved_tracks_data()

# Use Pandas function ExcelWriter to save all 3 dataframes to 1 Excel file
with pd.ExcelWriter('Spotify_API_Data.xlsx') as writer:
    recent_songs_df.to_excel(writer, sheet_name='Recent Songs', index=False)
    time_period_trends_df.to_excel(writer, sheet_name='Time Period Trends', index=False)
    recent_saved_tracks_df.to_excel(writer, sheet_name='Liked Songs', index=False)
