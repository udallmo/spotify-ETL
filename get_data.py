from dataclasses import field
from datetime import datetime
import spotipy
import csv
import boto3
from cred import CLIENT_ID, CLIENT_SECRET
from spotipy.oauth2 import SpotifyClientCredentials
from playlist import spotify_playlists

auth_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

PLAYLIST = "top_hits"
playlists = sp.user_playlists('spotify')


def gather_data_local():
    final_data_dictionary = {
        'Year Released': [],
        'Album Length': [],
        'Album Name': [],
        'Artist': []
    }
    with open("top_hits_albums.csv", 'w') as file:
        header = list(final_data_dictionary.keys())
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        albums_obtained = []

        artists = get_artists_from_playists(spotify_playlists()[PLAYLIST])
        for artist in list(artists.keys()):
            artists_albums = sp.artist_albums(
                artist, album_type='album', limit=50)

            for album in artists_albums['items']:
                if 'GB' and 'US' in album['available_markets']:
                    key = album['name'] + album['artists'][0]['name'] + \
                        album['release_date'][:4]

                    if key not in albums_obtained:
                        albums_obtained.append(key)
                        album_data = sp.album(album['uri'])
                        # For evey song in the album
                        album_length_ms = 0
                        for song in album_data['tracks']['items']:
                            album_length_ms = song['duration_ms'] + \
                                album_length_ms
                        writer.writerow(
                            {
                                'Year Released': album_data['release_date'][:4],
                                'Album Length': album_length_ms,
                                'Album Name': album_data['name'],
                                'Artist': album_data['artists'][0]['name']
                            })
                        final_data_dictionary['Year Released'].append(
                            album_data['release_date'][:4])
                        final_data_dictionary['Album Length'].append(
                            album_length_ms)
                        final_data_dictionary['Album Name'].append(
                            album_data['name'])
                        final_data_dictionary['Artist'].append(
                            album_data['artists'][0]['name'])

        return final_data_dictionary


def gather_data():
    with open("/tmp/top_hits_albums.csv", 'w') as file:
        header = ['Year Released', 'Album Length', 'Album Name', 'Artist']
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        albums_obtained = []

        artists = get_artists_from_playists(spotify_playlists()[PLAYLIST])
        for artist in list(artists.keys()):
            print(artist)
            artists_albums = sp.artist_albums(
                artist, album_type='album', limit=50)

            for album in artists_albums['items']:
                if 'GB' and 'US' in album['available_markets']:
                    key = album['name'] + album['artists'][0]['name'] + \
                        album['release_date'][:4]

                    if key not in albums_obtained:
                        albums_obtained.append(key)
                        album_data = sp.album(album['uri'])
                        # For evey song in the album
                        album_length_ms = 0
                        for song in album_data['tracks']['items']:
                            album_length_ms = song['duration_ms'] + \
                                album_length_ms
                        writer.writerow(
                            {
                                'Year Released': album_data['release_date'][:4],
                                'Album Length': album_length_ms,
                                'Album Name': album_data['name'],
                                'Artist': album_data['artists'][0]['name']
                            })

        s3_resources = boto3.resource('s3')
        date = datetime.now()
        filename = f'{date.year}/{date.month}/{date.day}/top_hits_albums.csv'
        response = s3_resources.Object(
            'spotify-analysis-data-udall', filename).upload_file("/tmp/top_hits_albums.csv")

        return response


def get_artists_from_playists(playlist_uri):
    '''
    :pram playlist_uri: Playlist to analyze
    :return: A dictionary(artist uri: artist name) of all primary artists in a playlist
    '''
    artists = {}
    playlist_tracks = sp.playlist_tracks(playlist_id=playlist_uri)
    for song in playlist_tracks['items']:
        if(song['track']):
            artists[song['track']['artists'][0]['uri']
                    ] = song['track']['artists'][0]['name']
    return artists


def lambda_handler(event, context):
    gather_data()


if __name__ == '__main__':
    # gather_data_local()
    gather_data()
