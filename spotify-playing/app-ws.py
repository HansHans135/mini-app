from flask import Flask, session, jsonify, render_template, redirect, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json

app = Flask(__name__)
app.secret_key = 'awa'
app.config['SESSION_COOKIE_NAME'] = 'awa'
socketio = SocketIO(app)

SETTING=open("setting.json")
# Spotify API 設置
client_id = SETTING["client_id"]
client_secret = SETTING["client_secret"]
redirect_uri = SETTING["redirect_uri"]
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
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Spotify Currently Playing</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #121212;
                color: white;
            }
            .player {
                display: flex;
                flex-direction: row;
                align-items: center;
                background-color: #1e1e1e;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
                width: 80%;
                max-width: 1200px;
            }
            .album-cover {
                width: 100%;
                max-width: 300px;
                height: auto;
                border-radius: 10px;
                object-fit: cover;
                margin-right: 20px;
            }
            .info-controls {
                display: flex;
                flex-direction: column;
                width: 100%;
            }
            .track-info {
                text-align: left;
                margin-bottom: 20px;
            }
            .track-info h1, .track-info h2 {
                margin: 5px 0;
            }
            .progress-container {
                display: flex;
                align-items: center;
                width: 100%;
                margin-bottom: 20px;
            }
            progress {
                width: 100%;
                margin: 0 10px;
            }
            .controls {
                display: flex;
                justify-content: space-around;
                width: 100%;
            }
            .controls button {
                background: none;
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="player">
            <img id="album-cover" class="album-cover" src="" alt="Album Cover">
            <div class="info-controls">
                <div class="track-info">
                    <h1 id="track-name">目前沒有曲目正在播放</h1>
                    <h2 id="artist-name"></h2>
                </div>
                <div class="progress-container">
                    <span id="current-time">0:00</span>
                    <progress id="progress-bar" value="0" max="100"></progress>
                    <span id="duration-time">0:00</span>
                </div>
                <div class="controls">
                    <button id="shuffle-button">🔀</button>
                    <button id="prev-button">⏮</button>
                    <button id="play-pause-button">⏯</button>
                    <button id="next-button">⏭</button>
                    <button id="like-button">❤️</button>
                </div>
            </div>
        </div>
        <script src="https://cdn.socket.io/4.0.1/socket.io.min.js"></script>
        <script>
            const socket = io();

            socket.on('track_info', function(data) {
                const trackName = document.getElementById('track-name');
                const artistName = document.getElementById('artist-name');
                const albumCover = document.getElementById('album-cover');
                const progressBar = document.getElementById('progress-bar');
                const currentTime = document.getElementById('current-time');
                const durationTime = document.getElementById('duration-time');

                if (data.is_playing) {
                    trackName.innerHTML = data.track_name;
                    artistName.innerHTML = data.artist_name;
                    albumCover.src = data.album_cover_url;
                    const progress = (data.progress_ms / data.duration_ms) * 100;
                    progressBar.value = progress;
                    currentTime.innerHTML = formatTime(data.progress_ms);
                    durationTime.innerHTML = formatTime(data.duration_ms);
                } else {
                    trackName.innerHTML = '目前沒有曲目正在播放';
                    artistName.innerHTML = '';
                    albumCover.src = 'https://play-lh.googleusercontent.com/IHoystBSDWqQJ705ZUYRK8Jb5trzQnem6FpWY2Z1dfbgCGITJSlJ5z0jRVQSeibycOw';
                    progressBar.value = 0;
                    currentTime.innerHTML = '0:00';
                    durationTime.innerHTML = '0:00';
                }
            });

            function formatTime(ms) {
                const totalSeconds = Math.floor(ms / 1000);
                const minutes = Math.floor(totalSeconds / 60);
                const seconds = totalSeconds % 60;
                return `${minutes}:${seconds.toString().padStart(2, '0')}`;
            }

            socket.emit('user_connect', {'user_id': 'your_user_id'}); // 假設用戶ID已經在前端可用
        </script>
    </body>
    </html>
    '''


@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/callback')
def callback():
    global user_tokens
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_id = sp.current_user()['id']
    user_tokens[user_id] = token_info
    return redirect('/')


def fetch_track_info(user_id):
    while True:
        socketio.sleep(1)
        if user_id in user_tokens:
            token_info = user_tokens[user_id]
            if sp_oauth.is_token_expired(token_info):
                token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])

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


@socketio.on('user_connect')
def handle_connect(data):
    user_id = data['user_id']
    join_room(user_id)
    if user_id not in user_tokens:
        emit('auth_required', room=user_id)
    else:
        socketio.start_background_task(fetch_track_info, user_id)


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True, port=8888)