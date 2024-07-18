from flask import Flask, render_template
import subprocess
import time
import pyautogui
import pygetwindow as gw
import webbrowser    
import socket
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

app = Flask(__name__)

hostname = socket.gethostname()
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

a={0: -65.25, 1: -56.99, 2: -51.67, 3: -47.74, 4: -44.62, 5: -42.03, 6: -39.82, 7: -37.89, 8: -36.17, 9: -34.63, 10: -33.24,
 11: -31.96, 12: -30.78, 13: -29.68, 14: -28.66, 15: -27.7, 16: -26.8, 17: -25.95, 18: -25.15, 19: -24.38, 20: -23.65,
 21: -22.96, 22: -22.3, 23: -21.66, 24: -21.05, 25: -20.46, 26: -19.9, 27: -19.35, 28: -18.82, 29: -18.32, 30: -17.82,
 31: -17.35, 32: -16.88, 33: -16.44, 34: -16.0, 35: -15.58, 36: -15.16, 37: -14.76, 38: -14.37, 39: -13.99, 40: -13.62,
 41: -13.26, 42: -12.9, 43: -12.56, 44: -12.22, 45: -11.89, 46: -11.56, 47: -11.24, 48: -10.93, 49: -10.63, 50: -10.33,
 51: -10.04, 52: -9.75, 53: -9.47, 54: -9.19, 55: -8.92, 56: -8.65, 57: -8.39, 58: -8.13, 59: -7.88, 60: -7.63,
 61: -7.38, 62: -7.14, 63: -6.9, 64: -6.67, 65: -6.44, 66: -6.21, 67: -5.99, 68: -5.76, 69: -5.55, 70: -5.33,
 71: -5.12, 72: -4.91, 73: -4.71, 74: -4.5, 75: -4.3, 76: -4.11, 77: -3.91, 78: -3.72, 79: -3.53, 80: -3.34,
 81: -3.15, 82: -2.97, 83: -2.79, 84: -2.61, 85: -2.43, 86: -2.26, 87: -2.09, 88: -1.91, 89: -1.75, 90: -1.58,
 91: -1.41, 92: -1.25, 93: -1.09, 94: -0.93, 95: -0.77, 96: -0.61, 97: -0.46, 98: -0.3, 99: -0.15, 100: 0.0}

htm="""
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stream Deck</title>
    <style>
        /* 全局樣式 */
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: black;
        }

        /* 上方按鈕樣式 */
        .button.upper {
            margin-bottom: 20%;
        }

        /* 下方按鈕樣式 */
        .button.lower {
            margin-top: 80%;
        }

        .frame {
            width: 90%;
            margin: 40px auto;
            text-align: center;
        }


        .custom-btn {
            display: inline-flex;
            /* 將display設置為inline-block，讓按鈕水平排列 */
            /* padding: 14.5% 14.5%;*/
            padding: 9% 9%;
            /* 調整padding以放大按鈕 */
            margin: 1%;
            border-radius: 30px;
            /* 圓角大小 */
            text-align: center;
            text-decoration: none;
            font-size: 18px;

            /* 按鈕背景顏色 */
            cursor: pointer;
            outline: none;
        }

        .btn1 {
            background-image: url(https://play-lh.googleusercontent.com/0oO5sAneb9lJP6l8c6DH4aj6f85qNpplQVHmPmbbBxAukDnlO7DarDW0b-kEIHa8SQ);
            background-position: center;
            background-size: cover;
        }

        .btn3 {
            background-image: url(https://play-lh.googleusercontent.com/MfOmDw_wbHCE7D1ZKSsAbzMojq1cHsEH7CxBye2nQ0w6WeAf9NWaRIMBONgxl-eyW9PG);
            background-position: center;
            background-size: cover;
        }

        .btn2 {
            background-image: url(https://images-eds-ssl.xboxlive.com/image?url=4rt9.lXDC4H_93laV1_eHM0OYfiFeMI2p9MWie0CvL99U4GA1gf6_kayTt_kBblFwHwo8BW8JXlqfnYxKPmmBRXp912Lw.0Yxg2DfVOh1gnKXRQeKb8m8DA2Jkx6Xwk0yYA23Ude.JrHx3QjJv9hvUNKZhFYJFJP2QtF6zREDZk-&format=source);
            background-position: center;
            background-size: cover;
        }

        .btn4 {
            background-image: url(https://play-lh.googleusercontent.com/ZU9cSsyIJZo6Oy7HTHiEPwZg0m2Crep-d5ZrfajqtsH-qgUXSqKpNA2FpPDTn-7qA5Q);
            background-position: center;
            background-size: cover;
        }

        .btn5 {
            background-image: url(data:image/png;base64,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);
            background-position: center;
            background-size: cover;
        }

        .btn6 {
            background-image: url(https://play-lh.googleusercontent.com/VYvJqGnrQiKkbbyLyMeiL-GM3go4tBIA64uVEGQazLXD4p_M3F45kHyt42o_6d5VXA);
            background-position: center;
            background-size: cover;
        }

        .btn7 {
            background-image: url(https://yt3.googleusercontent.com/csWzXL4KY7svMbPXMObNJmDSzXta1VstzOl3dpWkXSDGkDNGNd_yEVSflEbGVOls0MLX0ayj=s900-c-k-c0x00ffffff-no-rj);
            background-position: center;
            background-size: cover;
        }

        .btn8 {
            background-image: url(https://play-lh.googleusercontent.com/WNWZaxi9RdJKe2GQM3vqXIAkk69mnIl4Cc8EyZcir2SKlVOxeUv9tZGfNTmNaLC717Ht);
            background-position: center;
            background-size: cover;
        }
        .btn9 {
            background-image: url(https://cdn0.iconfinder.com/data/icons/phosphor-bold-vol-4/256/x-square-bold-512.png);
            background-position: center;
            background-size: cover;
        }
        .btn10 {
            background-image: url(https://cdn0.iconfinder.com/data/icons/phosphor-bold-vol-3/256/speaker-simple-slash-bold-512.png);
            background-position: center;
            background-size: cover;
        }
        .btn11 {
            background-image: url(https://cdn0.iconfinder.com/data/icons/phosphor-bold-vol-3/256/speaker-simple-low-bold-512.png);
            background-position: center;
            background-size: cover;
        }
        .btn12 {
            background-image: url(https://cdn0.iconfinder.com/data/icons/phosphor-bold-vol-3/256/speaker-simple-high-bold-512.png);
            background-position: center;
            background-size: cover;
        }
    </style>
</head>

<body>

    <!--
    {% for button_number, action_function in button_actions.items() %}
    <button><a href="{{ url_for('button_click', button_number=button_number) }}">Button {{ button_number }} - {{
            action_function }}</a></button>
    {% endfor %}
    -->
    <!-- 上方按鈕 -->
    <div class="frame">
        <button data-id="1" class="custom-btn btn1 myButton"></button>
        <button data-id="2" class="custom-btn btn2 myButton"></button>
        <button data-id="3" class="custom-btn btn3 myButton"></button>
        <button data-id="4" class="custom-btn btn4 myButton"></button>
        <br>
        <!-- 下方按鈕 -->
        <button data-id="5" class="custom-btn btn5 myButton"></button>
        <button data-id="6" class="custom-btn btn6 myButton"></button>
        <button data-id="7" class="custom-btn btn7 myButton"></button>
        <button data-id="8" class="custom-btn btn8 myButton"></button>
        <br>
        <!-- 下方按鈕 -->
        <button data-id="9" class="custom-btn btn9 myButton"></button>
        <button data-id="10" class="custom-btn btn10 myButton"></button>
        <button data-id="11" class="custom-btn btn11 myButton"></button>
        <button data-id="12" class="custom-btn btn12 myButton"></button>
    </div>
</body>
<script>
    // 获取所有带有类名 "myButton" 的按钮
    var buttons = document.querySelectorAll(".myButton");

    // 为每个按钮添加点击事件监听器
    buttons.forEach(function (button) {
        button.addEventListener("click", function () {
            // 获取按钮上的 data-id 属性值，用于构建URL
            var buttonId = button.getAttribute("data-id");

            // 构建要发送的HTTP GET请求的URL
            var url = "/button/" + buttonId; // 例如："https://example.com/button/1"

            // 使用XMLHttpRequest对象发送GET请求
            var xhr = new XMLHttpRequest();
            xhr.open("GET", url, true);

            // 设置回调函数，处理请求的响应
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    // 请求成功，可以在这里处理响应的数据
                    console.log(xhr.responseText);
                }
            };

            // 发送GET请求
            xhr.send();
        });
    });
</script>

</html>
"""
# 定义每个按钮对应的功能
button_actions = {
    1: "button1",
    2: "button2",
    3: "button3",
    4: "button4",
    5: "button5",
    6: "button6",
    7: "button7",
    8: "button8",
    9: "button9",
    10: "button10",
    11: "button11",
    12: "button12",
}

def get_vl():
    v=round(volume.GetMasterVolumeLevel(),2)
    print(v)
    for i in a:
        if a[i]==v:
            print(i)
            return i
# 按钮对应的功能实现
def button1():
    webbrowser.get('windows-default').open_new("discord://")
def button2():
    webbrowser.get('windows-default').open_new("vscode://")

def button3():
    process = subprocess.Popen(["C:\Program Files (x86)\Steam\steam.exe"])
    time.sleep(1)
    app_window = gw.getWindowsWithTitle("steam")[0]
    app_window.maximize()
    app_window.setTopmost()

    
def button4():
    webbrowser.get('windows-default').open_new("tg://")

def button5():
    webbrowser.get('windows-default').open_new("spotify://")
    
def button6():
    process = subprocess.Popen(["C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"])
    time.sleep(1)
    app_window = gw.getWindowsWithTitle("edge")[0]
    app_window.maximize()
    app_window.setTopmost()
    
def button7():
    process = subprocess.Popen(["C:\Program Files\Feather Launcher\Feather Launcher.exe"])
    time.sleep(1)
    app_window = gw.getWindowsWithTitle("Discord")[0]
    app_window.maximize()
    app_window.setTopmost()
    
def button8():
    webbrowser.get('windows-default').open_new("https://www.roblox.com/home")
    
def button9():
    pyautogui.keyDown("Alt")
    pyautogui.keyDown("F4")
    pyautogui.keyUp("F4")
    pyautogui.keyUp("Alt")

def button10():
    volume.SetMasterVolumeLevel(-65.25, None)

def button11():
    vl = get_vl()
    volume.SetMute(0, None)
    awa=vl-2
    volume.SetMasterVolumeLevel(a[awa], None)

def button12():
    vl = get_vl()
    volume.SetMute(0, None)
    awa=vl+2
    volume.SetMasterVolumeLevel(a[awa], None)
    

# 路由，用于处理按钮点击事件
@app.route('/button/<int:button_number>')
def button_click(button_number):
    action_function = button_actions.get(button_number)
    if action_function:
        globals()[action_function]()
        return f"Button {button_number} clicked, performing {action_function}!"
    else:
        return f"Button {button_number} does not have a defined action."

# 主页，显示按钮列表
@app.route('/')
def home():
    return htm
    return render_template('index.html', button_actions=button_actions)

app.run(debug=True,host="0.0.0.0",port=8787)
