import threading
import subprocess
import os
import sys
import requests
from flask import Flask, jsonify, request
import webview

# PyInstaller uyumlu dosya yolu
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Flask başlat
app = Flask(
    __name__,
    static_folder=resource_path('embedded/static'),
    static_url_path='/static'
)

# Programlar: id → (Görünen Ad, Gerçek Dosya Adı)
programs = {
    "booster": ("BoosterX", "booster.exe"),
    "visual": ("Kur Visual C++", "visual.exe"),
    "directx": ("Kur DirectX", "directx.exe"),
    "lasso": ("Kur Process Lasso", "lasso.exe"),
    "priority": ("Regedit Priority", "priority.reg"),
    "riva": ("Kur Riva Tuner", "riva.exe"),
    "gameloop": ("Kur GameLoop 32 Bit", "gameloop.exe"),
    "mktool": ("Mk Tool", "MK Tool.exe"),  # Büyük harfli ve boşluklu
    "antialag": ("ANTI LAG", "antilag.exe"),  # Küçük harfli ve birleşik
    "mouse": ("Kur X-Mouse Button", "mouse.exe")
}

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/get_programs')
def get_programs():
    return jsonify({"programs": {k: v[0] for k, v in programs.items()}})

@app.route('/check_update')
def check_update():
    try:
        r = requests.get(
            'https://raw.githubusercontent.com/CRTYPUBG/update_lass/main/update_info.json',
            timeout=5
        )
        r.raise_for_status()
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'has_update': False, 'error': str(e)}), 500

@app.route('/install', methods=['POST'])
def install_program():
    data = request.json
    choice = data.get('choice')

    if choice not in programs:
        return jsonify({"error": "Program bulunamadı"}), 404

    display_name, filename = programs[choice]
    filepath = resource_path(os.path.join("embedded", "programs", filename))

    if not os.path.exists(filepath):
        return jsonify({"error": f"{display_name} bulunamadı: {filename}"}), 404

    try:
        if filename.endswith(".reg"):
            subprocess.Popen(["regedit", "/s", filepath], shell=True)
        else:
            subprocess.Popen([filepath], shell=True)
        return jsonify({"message": f"{display_name} çalıştırılıyor..."})
    except Exception as e:
        return jsonify({"error": f"{display_name} başlatılamadı: {str(e)}"}), 500

def start_flask():
    app.run(host='127.0.0.1', port=8080, debug=False, threaded=True)

if __name__ == '__main__':
    threading.Thread(target=start_flask, daemon=True).start()

    webview.create_window(
        "CRTY Tweaks Installer",
        "http://127.0.0.1:8080",
        width=990,
        height=950,
        resizable=True,
        frameless=True
    )
    webview.start()
