from flask import Flask, send_from_directory
import threading, webbrowser

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def root():
    return send_from_directory('.', 'handover_dashboard.html')

if __name__ == '__main__':
    threading.Timer(1, lambda: webbrowser.open('http://127.0.0.1:5000/')).start()
    app.run()
