import os
from flask import Flask, jsonify, request, send_from_directory
from .game_logic import game_manager, load_persisted_defaults


app = Flask(__name__, static_folder=None)


# ---------- Static frontend ----------
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))


@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/<path:path>')
def static_proxy(path):
    # Nie przechwytuj API
    if path.startswith('api/'):
        return jsonify({"error": "not_found"}), 404
    full = os.path.join(FRONTEND_DIR, path)
    if os.path.isfile(full):
        return send_from_directory(FRONTEND_DIR, path)
    return jsonify({"error": "not_found"}), 404


# ---------- Health ----------
@app.get('/healthz')
def healthz():
    return jsonify({"status": "ok"})


# ---------- API edytorów ----------
@app.get('/api/map')
def api_get_map():
    return jsonify(game_manager.get_map())


@app.post('/api/map')
def api_set_map():
    payload = request.get_json(force=True)
    game_manager.set_map(payload)
    return jsonify({"status": "ok"})


@app.get('/api/tokens')
def api_get_tokens():
    return jsonify(game_manager.get_token_types())


@app.post('/api/tokens')
def api_set_tokens():
    payload = request.get_json(force=True)
    game_manager.set_token_types(payload)
    return jsonify({"status": "ok"})


@app.get('/api/placements')
def api_get_placements():
    room = request.args.get('room', 'default')
    return jsonify(game_manager.get_placements(room))


@app.post('/api/placements')
def api_set_placements():
    room = request.args.get('room', 'default')
    payload = request.get_json(force=True)
    game_manager.set_placements(room, payload)
    return jsonify({"status": "ok"})


# ---------- API gry ----------
@app.post('/api/session/join')
def api_join():
    room = (request.args.get('room') or request.json.get('room') or 'default')
    player_id = game_manager.join_room(room)
    return jsonify({"room": room, "player": player_id})


@app.post('/api/game/reset')
def api_reset():
    room = (request.args.get('room') or request.json.get('room') or 'default')
    game_manager.reset_game(room)
    return jsonify({"status": "ok"})


@app.get('/api/game/state')
def api_state():
    room = request.args.get('room', 'default')
    return jsonify(game_manager.get_state(room))


@app.post('/api/game/move')
def api_move():
    room = (request.args.get('room') or request.json.get('room') or 'default')
    payload = request.get_json(force=True)
    ok, result = game_manager.apply_move(room, payload)
    status = 200 if ok else 400
    return jsonify(result), status


def create_app():
    # Bootstrap danych (bez efektów ubocznych przy imporcie modułu)
    try:
        load_persisted_defaults()
    except Exception as e:
        # Nie wywalaj serwera – pokaż błąd w /healthz i logach
        app.logger.exception("Bootstrap danych nie powiódł się: %s", e)
    return app


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    print(f"Serwer uruchomiony na http://{host}:{port}")
    app.run(host=host, port=port, debug=False)
