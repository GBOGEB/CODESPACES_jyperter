from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='.')

@app.route('/')
def root():
    return app.send_static_file('handover_dashboard.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    app.run(port=8000)
