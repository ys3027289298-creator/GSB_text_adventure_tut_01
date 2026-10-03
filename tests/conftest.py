"""Shared test setup: the game uses flat imports, so the package dir goes on sys.path."""
import contextlib
import io
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_DIR = os.path.join(REPO_ROOT, 'adventuretutorial')
sys.path.insert(0, GAME_DIR)

MAIN_MAP = os.path.join(REPO_ROOT, 'resources', 'map.txt')
MAPS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'maps')

import game  # noqa: E402
import items  # noqa: E402
import world  # noqa: E402
from player import Player  # noqa: E402


def run_game(inputs, map_path=MAIN_MAP):
    """Plays through one scripted game and returns (final player, recorded output)."""
    world.load_tiles(map_path)
    player = Player()
    script = iter(inputs)

    def fake_input(prompt=''):
        try:
            return next(script)
        except StopIteration:
            raise EOFError

    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        game.game_loop(player, input_func=fake_input)
    return player, stream.getvalue()


def final_state(player):
    """Records the final state of the player after an input sequence."""
    return {
        'location': (player.location_x, player.location_y),
        'hp': player.hp,
        'alive': player.is_alive(),
        'victory': player.victory,
        'gold': sum(item.amt for item in player.inventory
                    if isinstance(item, items.Gold)),
        'weapons': sorted(item.name for item in player.inventory
                          if isinstance(item, items.Weapon)),
    }
