import os
import re
import random
import requests
import secrets
import spotipy
from time import time
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheHandler
from flask import url_for, session

class NoCacheHandler(CacheHandler):
    def get_cached_token(self):
        return None

    def save_token_to_cache(self, token_info):
        pass


class SpotifyService:
    def __init__(self):
        self._sp_oauth = SpotifyOAuth(
            client_id=os.getenv('CLIENT_ID'),
            client_secret=os.getenv('CLIENT_SECRET'),
            redirect_uri="http://127.0.0.1:5000/auth/callback",
            scope="user-library-read",
            cache_handler=NoCacheHandler())
        self._spotify_client = None

    def get_auth_url(self):
        state = secrets.token_hex(32)
        session['spotify_state'] = state
        self._sp_oauth.state = state
        return self._sp_oauth.get_authorize_url()

    def get_token_info(self, code):
        token_info = self._sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
        refresh_token = token_info['refresh_token']
        expires_at = token_info['expires_at']
        return access_token, refresh_token, expires_at

    def refresh_access_token_if_needed(self):
        if 'expires_at' in session and session['expires_at'] < time():
            token_info = self._sp_oauth.refresh_access_token(session['refresh_token'])
            session['access_token'] = token_info['access_token']
            session['expires_at'] = token_info['expires_at']
    
    def initialize_client(self, access_token):
        self._spotify_client = spotipy.Spotify(auth=access_token)

    def get_user_profile(self):
        user_info = self._spotify_client.current_user()
        display_name = user_info['display_name']
        images = user_info['images']
        image_url = images[0]['url'] if images else url_for('static', filename='img/account.svg')
        user_data = {'username': display_name, 'image_url': image_url}
        return user_data
    
    def get_saved_songs(self):
        limit = 10
        total_songs = self._spotify_client.current_user_saved_tracks(limit=1)['total']
        limit = min(limit, total_songs)
        offset = random.randint(0, total_songs - limit)

        saved_songs = self._spotify_client.current_user_saved_tracks(limit=limit, offset=offset)['items']
        return saved_songs


class LyricsService:
    def __init__(self):
        self.n_verses=2
        self.lyrics_api_url = os.getenv('LYRICS_API_URL')

    def _search_song(self, track_name, artist):
        try:
            response = requests.get(self.lyrics_api_url.format(artist=artist, track_name=track_name), timeout=0.5)
            response.raise_for_status()
            data = response.json()
            return data
        except:
            return {}

    def _get_random_lyrics(self, songs):
        data = {}
        while 'lyrics' not in data:  # Retry until a song is found (not all songs are available)
            random_track = random.choice(songs)['track']
            track_name = random_track['name']
            artist = random_track['artists'][0]['name']

            data = self._search_song(track_name, artist)

        lyrics = data['lyrics']
        return lyrics, track_name, artist
    
    def _get_fortune_verses(self, lyrics):
        lyrics = re.sub('\n\n','\n',lyrics)
        # Remove [section labels] and (chorus)
        lyrics = re.sub(' *[\[\(].*?[\]\)]','',lyrics)
        lyrics = re.sub('\n\n+','\n\n',lyrics)
        lyrics_cleaned = lyrics.strip()

        strophes = lyrics_cleaned.split('\n\n')
        strophes_verses = [strophe.split('\n') for strophe in strophes]

        verses_pairs = []
        for verses in strophes_verses:
            for i in range(0, len(verses) - 1, self.n_verses):
                verses_pair = '\n'.join(verses[i:i+self.n_verses])
                verses_pairs.append(verses_pair)

        return verses_pairs
    
    def get_random_verses(self, saved_songs):
        fortune_verses = []  # Retry until valid fortune verses are found (sometimes the result is empty)
        while not fortune_verses:
            lyrics, track_name, artist = self._get_random_lyrics(saved_songs)
            fortune_verses = self._get_fortune_verses(lyrics)

        verses = random.choice(fortune_verses)
        return {'verses':verses, 'track_name':track_name, 'artist':artist}