"""Parameterized tests for the tutorial game.

Each scenario feeds a scripted input sequence through game_loop and records
the final player state (hp, alive/victory flags, location and inventory).
"""
import contextlib
import io
import os
import sys
import unittest
from unittest import mock

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, 'adventuretutorial'))
os.chdir(REPO_ROOT)

import world
import game
from player import Player


def run_game(inputs):
    """Runs game_loop with scripted inputs; returns (player, captured_output)."""
    world.load_tiles()
    player = Player()
    feed = iter(inputs)
    buffer = io.StringIO()
    with mock.patch('builtins.input', side_effect=lambda prompt='': next(feed)), \
            contextlib.redirect_stdout(buffer):
        game.game_loop(player)
    return player, buffer.getvalue()


def snapshot(player):
    """Records the final state reached by an input sequence."""
    return {
        'hp': player.hp,
        'alive': player.is_alive(),
        'victory': player.victory,
        'location': (player.location_x, player.location_y),
        'inventory': [(type(item).__name__, getattr(item, 'amt', None))
                      for item in player.inventory],
    }


# (name, inputs, expected snapshot, substrings expected in output)
GAME_SCENARIOS = [
    # --- Minimal legal winning path: rock kills the spider guarding the exit ---
    ('minimal_victory_with_rock',
     ['n', 'n', 'n', 'e', 'a', 'a', 'n'],
     {'hp': 96, 'alive': True, 'victory': True, 'location': (3, 0),
      'inventory': [('Gold', 15), ('Rock', None)]},
     []),

    # --- Revisit the dagger room: the dagger is picked up only once ---
    ('dagger_room_revisited_picks_up_once',
     ['e', 'e', 'w', 'e', 'w', 'w', 'n', 'n', 'n', 'e', 'a', 'n'],
     {'hp': 98, 'alive': True, 'victory': True, 'location': (3, 0),
      'inventory': [('Gold', 15), ('Rock', None), ('Dagger', None)]},
     []),

    # --- Detour through the gold room: revisit the empty path safely ---
    ('gold_detour_then_victory',
     ['n', 'n', 'n', 'w', 'e', 'e', 'a', 'a', 'n'],
     {'hp': 96, 'alive': True, 'victory': True, 'location': (3, 0),
      'inventory': [('Gold', 15), ('Rock', None), ('Gold', 5)]},
     []),

    # --- Long legal path clearing both spider rooms ---
    ('clear_both_spiders_then_victory',
     ['w', 'w', 'a', 'a', 'e', 'e', 'n', 'n', 'n', 'e', 'a', 'a', 'n'],
     {'hp': 92, 'alive': True, 'victory': True, 'location': (3, 0),
      'inventory': [('Gold', 15), ('Rock', None)]},
     []),

    # --- Clear failure path: the snake pit kills the player ---
    ('snake_pit_death',
     ['s', 's', 's'],
     {'hp': 0, 'alive': False, 'victory': False, 'location': (2, 7),
      'inventory': [('Gold', 15), ('Rock', None), ('Gold', 5)]},
     ['You have died!']),

    # --- Failure path: illegal hotkeys while fighting the ogre do not exit ---
    # the game; the ogre keeps hitting and eventually kills the player.
    ('illegal_actions_keep_game_alive_ogre_death',
     ['s', 's', 'e'] + ['?'] * 7,
     {'hp': -5, 'alive': False, 'victory': False, 'location': (3, 6),
      'inventory': [('Gold', 15), ('Rock', None), ('Gold', 5)]},
     ['Invalid action.']),

    # --- Victory cannot be stolen by fleeing onto the exit tile while the
    # guarding spider is still alive; the player must come back and kill it. ---
    ('flee_onto_exit_does_not_grant_victory',
     ['n', 'n', 'n', 'e', 'f', 's', 'a', 'a', 'n'],
     {'hp': 94, 'alive': True, 'victory': True, 'location': (3, 0),
      'inventory': [('Gold', 15), ('Rock', None)]},
     []),

    # --- An invalid hotkey in a safe room prints an error and play continues ---
    ('invalid_hotkey_recovers_to_victory',
     ['z', 'n', 'n', 'n', 'e', 'a', 'a', 'n'],
     {'hp': 96, 'alive': True, 'victory': True, 'location': (3, 0),
      'inventory': [('Gold', 15), ('Rock', None)]},
     ['Invalid action.']),
]


class GameScenarioTests(unittest.TestCase):
    def test_scenarios(self):
        for name, inputs, expected, expected_text in GAME_SCENARIOS:
            with self.subTest(scenario=name):
                if name == 'flee_onto_exit_does_not_grant_victory':
                    with mock.patch('player.random.randint', return_value=2):
                        player, output = run_game(inputs)
                else:
                    player, output = run_game(inputs)
                self.assertEqual(snapshot(player), expected)
                for text in expected_text:
                    self.assertIn(text, output)


class MovementValidationTests(unittest.TestCase):
    def setUp(self):
        world.load_tiles()
        self.player = Player()

    def test_illegal_direction_is_rejected(self):
        # FindDaggerRoom (4, 4) has no tile to the east.
        self.player.location_x, self.player.location_y = 4, 4
        before = (self.player.location_x, self.player.location_y)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.player.move_east()
        self.assertEqual((self.player.location_x, self.player.location_y),
                         before)
        self.assertIn("You can't go that way!", buffer.getvalue())

    def test_legal_direction_is_accepted(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.player.move_north()
        self.assertEqual((self.player.location_x, self.player.location_y),
                         (2, 3))


class LootRoomTests(unittest.TestCase):
    def test_loot_is_added_only_once(self):
        world.load_tiles()
        player = Player()
        dagger_room = world.tile_exists(4, 4)
        dagger_room.modify_player(player)
        dagger_room.modify_player(player)
        self.assertEqual(sum(type(item).__name__ == 'Dagger'
                             for item in player.inventory), 1)
        self.assertTrue(dagger_room.looted)


class ExitGuardTests(unittest.TestCase):
    def test_exit_is_blocked_and_then_opens(self):
        world.load_tiles()
        player = Player()
        exit_room = world.tile_exists(3, 0)
        spider_room = world.tile_exists(3, 1)
        exit_room.modify_player(player)
        self.assertFalse(player.victory)
        spider_room.enemy.hp = 0
        exit_room.modify_player(player)
        self.assertTrue(player.victory)


if __name__ == '__main__':
    unittest.main()
