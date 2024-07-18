from flask import Flask, session, jsonify, render_template_string, redirect, request, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import logging
import uuid

app = Flask(__name__)
app.secret_key = 'your_secure_secret_key'  
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
socketio = SocketIO(app)

logging.basicConfig(level=logging.INFO)

with open("setting.json", "r") as f:
    SETTING = json.load(f)

client_id = SETTING["client_id"]
client_secret = SETTING["client_secret"]
redirect_uri = SETTING["redirect_uri"]
scope = "user-read-currently-playing"

user_tokens = {}

def create_spotify_oauth(session_id):
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        cache_path=f".cache-{session_id}",
        show_dialog=True
    )

html_template = """
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
        #login-button {
            position: absolute;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            background-color: #1DB954;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="player">
        <img id="album-cover" class="album-cover" src="https://play-lh.googleusercontent.com/IHoystBSDWqQJ705ZUYRK8Jb5trzQnem6FpWY2Z1dfbgCGITJSlJ5z0jRVQSeibycOw" alt="Album Cover">
        <div class="info-controls">
            <div class="track-info">
                <h1 id="track-name">目前没有曲目正在播放</h1>
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
    <button id="login-button" style="display: none;">登入 Spotify</button>
    <script src="https://cdn.socket.io/4.0.1/socket.io.min.js"></script>
    <script>
        const socket = io();
        const loginButton = document.getElementById('login-button');
        const sessionId = "{{ session_id }}";

        socket.on('connect', function() {
            console.log('WebSocket connected');
            socket.emit('user_connect', {'session_id': sessionId});
        });

        socket.on('auth_required', function() {
            console.log('Authentication required');
            loginButton.style.display = 'block';
        });

        loginButton.addEventListener('click', function() {
            window.location.href = '/login';
        });

        socket.on('track_info', function(data) {
            if (data.session_id !== sessionId) return;
            
            console.log('Received track info:', data);
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
                trackName.innerHTML = '目前没有曲目正在播放';
                artistName.innerHTML = '';
                albumCover.src = 'https://play-lh.googleusercontent.com/IHoystBSDWqQJ705ZUYRK8Jb5trzQnem6FpWY2Z1dfbgCGITJSlJ5z0jRVQSeibycOw';
                progressBar.value = 0;
                currentTime.innerHTML = '0:00';
                durationTime.innerHTML = '0:00';
            }
        });

        socket.on('connect_error', function(error) {
            console.error('Connection error:', error);
        });

        function formatTime(ms) {
            const totalSeconds = Math.floor(ms / 1000);
            const minutes = Math.floor(totalSeconds / 60);
            const seconds = totalSeconds % 60;
            return `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template_string(html_template, session_id=session['session_id'])

@app.route('/login')
def login():
    session_id = session.get('session_id')
    if not session_id:
        return redirect(url_for('index'))
    
    app.logger.info(f'用戶 {session_id} 嘗試登入 Spotify')
    sp_oauth = create_spotify_oauth(session_id)
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    session_id = session.get('session_id')
    if not session_id:
        return redirect(url_for('index'))
    
    app.logger.info(f'收到 Spotify 登入資料，ID: {session_id}')
    sp_oauth = create_spotify_oauth(session_id)
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    user_tokens[session_id] = token_info
    app.logger.info(f'用戶 {session_id} 授權成功')
    return redirect(url_for('index'))

def fetch_track_info(session_id):
    app.logger.info(f'開始幫用戶 {session_id} 取得播放狀態')
    while True:
        socketio.sleep(1)
        if session_id in user_tokens:
            sp_oauth = create_spotify_oauth(session_id)
            token_info = user_tokens[session_id]
            if sp_oauth.is_token_expired(token_info):
                token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
                user_tokens[session_id] = token_info

            sp = spotipy.Spotify(auth=token_info['access_token'])
            try:
                current_track = sp.current_user_playing_track()
            except Exception as e:
                app.logger.error(f'取得狀態錯誤，用戶 {session_id}：{str(e)}')
                continue

            if current_track and current_track['item']:
                artist_name = current_track['item']['artists'][0]['name']
                track_name = current_track['item']['name']
                progress_ms = current_track['progress_ms']
                duration_ms = current_track['item']['duration_ms']
                album_cover_url = current_track['item']['album']['images'][0]['url']
                socketio.emit('track_info', {
                    'session_id': session_id,
                    'is_playing': True,
                    'artist_name': artist_name,
                    'track_name': track_name,
                    'progress_ms': progress_ms,
                    'duration_ms': duration_ms,
                    'album_cover_url': album_cover_url
                }, room=session_id)
            else:
                socketio.emit('track_info', {'session_id': session_id, 'is_playing': False}, room=session_id)

@socketio.on('user_connect')
def handle_connect(data):
    session_id = data['session_id']
    app.logger.info(f'用戶 {session_id} 連接')
    join_room(session_id)
    if session_id not in user_tokens:
        app.logger.info(f'用戶 {session_id} 需要授權')
        emit('auth_required', room=session_id)
    else:
        app.logger.info(f'開始為用戶 {session_id} 取得播放狀態')
        socketio.start_background_task(fetch_track_info, session_id)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True, port=25731)