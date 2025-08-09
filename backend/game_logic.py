import json
import os
import uuid
from typing import Dict, List, Tuple, Any


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DEFAULT_MAP_PATH = os.path.join(DATA_DIR, 'map.json')
DEFAULT_TOKENS_PATH = os.path.join(DATA_DIR, 'tokens.json')
DEFAULT_PLACEMENTS_PATH = os.path.join(DATA_DIR, 'placements.json')


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def read_json(path: str, default):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def write_json(path: str, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class GameManager:
    """Prosty menedżer gry turowej 2 graczy z heksową lub kwadratową mapą.
    API: map, tokens, placements, join, state, move, reset.
    """

    def __init__(self):
        ensure_data_dir()
        self._maps: Dict[str, Dict[str, Any]] = {}  # room -> map
        self._token_types: Dict[str, List[Dict[str, Any]]] = {}  # room/global -> token defs
        self._placements: Dict[str, List[Dict[str, Any]]] = {}  # room -> placed tokens
        self._rooms: Dict[str, Dict[str, Any]] = {}  # room -> {players: [id...], turn: 0/1, started: bool}

    # ---- map & tokens ----
    def get_map(self, room: str = 'default') -> Dict[str, Any]:
        return self._maps.get(room) or read_json(DEFAULT_MAP_PATH, {
            "grid": "square",  # square|hex
            "width": 8,
            "height": 8,
            "terrain": []  # list of {x,y,type}
        })

    def set_map(self, data: Dict[str, Any], room: str = 'default'):
        self._maps[room] = data
        if room == 'default':
            write_json(DEFAULT_MAP_PATH, data)

    def get_token_types(self, room: str = 'default') -> List[Dict[str, Any]]:
        return self._token_types.get(room) or read_json(DEFAULT_TOKENS_PATH, [
            {"type": "infantry", "hp": 3, "move": 2, "attack": 1, "range": 1},
            {"type": "tank", "hp": 5, "move": 3, "attack": 2, "range": 1},
            {"type": "artillery", "hp": 2, "move": 1, "attack": 2, "range": 3}
        ])

    def set_token_types(self, data: List[Dict[str, Any]], room: str = 'default'):
        self._token_types[room] = data
        if room == 'default':
            write_json(DEFAULT_TOKENS_PATH, data)

    # ---- placements ----
    def get_placements(self, room: str) -> List[Dict[str, Any]]:
        if room in self._placements:
            return self._placements[room]
        if room == 'default':
            data = read_json(DEFAULT_PLACEMENTS_PATH, [])
            # ensure normalization
            for p in data:
                p.setdefault('id', str(uuid.uuid4()))
                p.setdefault('owner', 0)
                p.setdefault('hp', self._hp_for_type(room, p.get('type')))
                p['x'] = int(p['x']); p['y'] = int(p['y'])
            self._placements[room] = data
            return data
        return []

    def set_placements(self, room: str, data: List[Dict[str, Any]]):
        # normalize id
        for p in data:
            if 'id' not in p:
                p['id'] = str(uuid.uuid4())
            p.setdefault('owner', 0)
            p.setdefault('hp', self._hp_for_type(room, p.get('type')))
        self._placements[room] = data
        if room == 'default':
            # write without ids to keep file clean of UUID churn
            persist = [
                {"type": p['type'], "owner": p['owner'], "x": int(p['x']), "y": int(p['y'])}
                for p in data
            ]
            write_json(DEFAULT_PLACEMENTS_PATH, persist)

    # ---- sessions ----
    def join_room(self, room: str) -> int:
        r = self._rooms.setdefault(room, {"players": [], "turn": 0, "started": False})
        if len(r["players"]) >= 2:
            # allow spectators: return -1
            return -1
        pid = len(r["players"])  # 0 or 1
        r["players"].append(pid)
        # Start when both joined and placements exist
        if len(r["players"]) == 2:
            r["started"] = True
        return pid

    def reset_game(self, room: str):
        self._rooms[room] = {"players": [], "turn": 0, "started": False}

    def get_state(self, room: str) -> Dict[str, Any]:
        r = self._rooms.get(room, {"players": [], "turn": 0, "started": False})
        return {
            "room": room,
            "players": len(r.get("players", [])),
            "turn": r.get("turn", 0),
            "started": r.get("started", False),
            "map": self.get_map(room),
            "tokens": self.get_token_types(room),
            "placements": self.get_placements(room)
        }

    # ---- gameplay ----
    def apply_move(self, room: str, move: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Move: {player:int, action:'move|attack', id:str, to:{x,y}} or attack:{targetId}
        Rules: turn-based, orthogonal move on square, range check, simple damage & death.
        """
        r = self._rooms.setdefault(room, {"players": [], "turn": 0, "started": False})
        if not r["started"]:
            return False, {"error": "game_not_started"}

        player = move.get('player')
        if player != r["turn"]:
            return False, {"error": "not_your_turn"}

        units = self._placements.get(room, [])
        unit = next((u for u in units if u.get('id') == move.get('id')), None)
        if not unit:
            return False, {"error": "unit_not_found"}
        if unit.get('owner') != player:
            return False, {"error": "not_your_unit"}

        # Move
        if move.get('action') == 'move':
            dest = move.get('to') or {}
            dx = abs(int(dest.get('x', unit['x'])) - int(unit['x']))
            dy = abs(int(dest.get('y', unit['y'])) - int(unit['y']))
            speed = self._stat_for_type(room, unit['type'], 'move', default=1)
            if dx + dy > speed:
                return False, {"error": "too_far"}
            if self._blocked(units, dest['x'], dest['y']):
                return False, {"error": "blocked"}
            unit['x'], unit['y'] = int(dest['x']), int(dest['y'])
            r['turn'] = 1 - r['turn']
            return True, {"ok": True, "state": self.get_state(room)}

        # Attack
        if move.get('action') == 'attack':
            target_id = (move.get('targetId') or move.get('target_id'))
            target = next((u for u in units if u.get('id') == target_id), None)
            if not target:
                return False, {"error": "target_not_found"}
            rng = self._stat_for_type(room, unit['type'], 'range', default=1)
            atk = self._stat_for_type(room, unit['type'], 'attack', default=1)
            dist = abs(unit['x'] - target['x']) + abs(unit['y'] - target['y'])
            if dist > rng:
                return False, {"error": "out_of_range"}
            target['hp'] = int(target.get('hp', 1)) - atk
            if target['hp'] <= 0:
                # remove
                self._placements[room] = [u for u in units if u.get('id') != target_id]
            r['turn'] = 1 - r['turn']
            return True, {"ok": True, "state": self.get_state(room)}

        return False, {"error": "unknown_action"}

    # ---- helpers ----
    def _hp_for_type(self, room: str, t: str) -> int:
        return self._stat_for_type(room, t, 'hp', default=1)

    def _stat_for_type(self, room: str, t: str, key: str, default=0) -> int:
        for d in self.get_token_types(room):
            if d.get('type') == t:
                return int(d.get(key, default))
        return int(default)

    @staticmethod
    def _blocked(units: List[Dict[str, Any]], x: int, y: int) -> bool:
        return any(u['x'] == int(x) and u['y'] == int(y) for u in units)


game_manager = GameManager()


def load_persisted_defaults():
    # Touch defaults so they are created on disk if missing
    game_manager.set_map(game_manager.get_map('default'))
    game_manager.set_token_types(game_manager.get_token_types('default'))
    # Load placements into memory (and create file if missing)
    pls = game_manager.get_placements('default')
    game_manager.set_placements('default', pls)

# Optional global health marker if needed later
HEALTH = {"bootstrap": "ok"}
