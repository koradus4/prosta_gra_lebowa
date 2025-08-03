class Game:
    def __init__(self):
        self.players = {}

    def set_player_choice(self, player_id, nation, turn_time, general, commanders):
        self.players[player_id] = {
            "nation": nation,
            "turn_time": turn_time,
            "general": general,
            "commanders": commanders
        }

    def get_player_choice(self, player_id):
        return self.players.get(player_id, None)

    def is_ready(self):
        return len(self.players) == 2
