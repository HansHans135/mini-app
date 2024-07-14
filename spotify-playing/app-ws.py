from flask import Flask, session, jsonify, render_template, redirect, request, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from urllib.parse import urlparse, parse_qs
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import threading

app = Flask(__name__)
app.secret_key = 'awa'
app.config['SESSION_COOKIE_NAME'] = 'awa'
socketio = SocketIO(app)

with open("setting.json", "r") as f:
    setting = json.load(f)

# Spotify API 設置
client_id = setting["client_id"]
client_secret = setting["client_secret"]
redirect_uri = setting["redirect_uri"]
scope = "user-read-currently-playing"

# 建立 SpotifyOAuth 實例
sp_oauth = SpotifyOAuth(client_id=client_id,
                        client_secret=client_secret,
                        redirect_uri=redirect_uri,
                        scope=scope)

# 用戶授權信息字典
user_tokens = {}


@app.route('/')
def index():
    token_info = session.get('token_info')
    if token_info:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))


@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return render_template('login.html', auth_url=auth_url)


@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_id = sp.current_user()['id']
    session['user_id'] = user_id
    user_tokens[user_id] = token_info  # Save token_info in a global variable
    return redirect(url_for('index'))


def fetch_track_info(user_id, token_info):
    while True:
        socketio.sleep(1)
        if sp_oauth.is_token_expired(token_info):
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            user_tokens[user_id] = token_info

        sp = spotipy.Spotify(auth=token_info['access_token'])
        current_track = sp.current_user_playing_track()

        if current_track and current_track['item']:
            artist_name = current_track['item']['artists'][0]['name']
            track_name = current_track['item']['name']
            progress_ms = current_track['progress_ms']
            duration_ms = current_track['item']['duration_ms']
            album_cover_url = current_track['item']['album']['images'][0]['url']
            socketio.emit('track_info', {
                'user_id': user_id,
                'is_playing': True,
                'artist_name': artist_name,
                'track_name': track_name,
                'progress_ms': progress_ms,
                'duration_ms': duration_ms,
                'album_cover_url': album_cover_url
            }, room=user_id)
        else:
            socketio.emit('track_info', {'user_id': user_id, 'is_playing': False}, room=user_id)


@socketio.on('get_user_id')
def handle_get_user_id():
    user_id = session.get('user_id')
    if user_id:
        emit('user_id', user_id)
    else:
        emit('user_id', None)


@socketio.on('user_connect')
def handle_connect(data):
    user_id = data.get('user_id')
    print(f"User connected: {user_id}")
    join_room(user_id)
    if user_id not in user_tokens:
        print(f"User {user_id} not found in user_tokens.")
        emit('auth_redirect', {'url': url_for('login')}, room=data['user_id'])
    else:
        token_info = user_tokens[user_id]
        print(f"Starting background task for user {user_id}.")
        socketio.start_background_task(fetch_track_info, user_id, token_info)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True, port=8888, allow_unsafe_werkzeug=True)
