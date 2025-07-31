from flask import Flask, jsonify, request
from flask_sockets import Sockets

app = Flask(__name__)
sockets = Sockets(app)

@app.route('/')
def index():
    return "Serwer gry działa!"

@sockets.route('/game')
def game_socket(ws):
    while not ws.closed:
        message = ws.receive()
        if message:
            ws.send(f"Otrzymano: {message}")

if __name__ == '__main__':
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
    print("Serwer uruchomiony na http://127.0.0.1:5000")
    server.serve_forever()
