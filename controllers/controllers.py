import os
from flask import Blueprint, request, session, redirect, url_for, render_template, Response
from models.models import SpotifyService, LyricsService

auth = Blueprint('auth', __name__)
home = Blueprint('home', __name__)
fortune = Blueprint('fortune', __name__)
spotify = SpotifyService()
lyrics = LyricsService()

@auth.route('/auth/login')
def login():
    return redirect(spotify.get_auth_url())

@auth.route('/auth/callback')
def callback():
    if request.args.get('state') != session['spotify_state']:
        return "State mismatch - CSRF detected", 400
    code = request.args.get('code')
    if code:
        access_token, refresh_token, expires_at = spotify.get_token_info(code)
        session['access_token'] = access_token
        session['refresh_token'] = refresh_token
        session['expires_at'] = expires_at
        return redirect(url_for("index"))
    return 'Authentication failed'

@auth.route('/auth/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

@home.route('/home')
def connect():
    if 'access_token' not in session:
        return redirect(url_for('index'))
    else:
        spotify.refresh_access_token_if_needed()
        spotify.initialize_client(session['access_token'])
        profile_data  = spotify.get_user_profile()
        return render_template('home.html', profile_data=profile_data)
    
@fortune.route('/fortune/generate_new')
def generate_new():
    saved_songs = spotify.get_saved_songs()
    session['fortune'] = lyrics.get_random_verses(saved_songs)
    return Response(status=204)

@fortune.route('/fortune/get_fortune')
def get_fortune():
    if 'fortune' not in session:
        return "Error: No fortune message available. Please generate a new fortune message first.", 400
    else:
        return render_template('fortune.html', fortune_data=session['fortune'])
