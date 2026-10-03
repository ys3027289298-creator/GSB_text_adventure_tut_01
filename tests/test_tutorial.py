"""Parametrized tests that record the final state of scripted input sequences.

Each case pairs an input hotkey sequence with the exact final player state
expected after the sequence is consumed. The cases cover the minimal legal
victory path, the failure path, repeated visits, illegal actions and item
pickup rules for every room type used by the tutorial.
"""
import os

import pytest

from conftest import MAIN_MAP, MAPS_DIR, final_state, run_game
import world
from player import Player


def level_map(name):
    return os.path.join(MAPS_DIR, name)


# (case id, map file, input sequence, expected final state, expected output snippets)
CASES = [
    (
        'main_minimal_victory_path',
        MAIN_MAP,
        ['n', 'n', 'n', 'e', 'a', 'a', 'n'],
        {'location': (3, 0), 'hp': 96, 'alive': True, 'victory': True,
         'gold': 15, 'weapons': ['Rock']},
        ['You made it out of the cave alive. You win!'],
    ),
    (
        'main_failure_path_snake_pit',
        MAIN_MAP,
        ['s', 's', 's'],
        {'location': (2, 7), 'hp': 0, 'alive': False, 'victory': False,
         'gold': 20, 'weapons': ['Rock']},
        ['You have died. Game over.'],
    ),
    (
        'main_unknown_hotkey_does_not_exit',
        MAIN_MAP,
        ['q', 'n', 's'],
        {'location': (2, 4), 'hp': 100, 'alive': True, 'victory': False,
         'gold': 15, 'weapons': ['Rock']},
        ['Invalid action. Please choose one of the listed actions.',
         'No more input. Ending game.'],
    ),
    (
        'main_illegal_direction_is_rejected',
        MAIN_MAP,
        ['n', 'e', 's'],
        {'location': (2, 4), 'hp': 100, 'alive': True, 'victory': False,
         'gold': 15, 'weapons': ['Rock']},
        ['Invalid action. Please choose one of the listed actions.'],
    ),
    (
        'main_invalid_input_then_victory_still_works',
        MAIN_MAP,
        ['junk', 'n', 'n', 'n', 'e', 'a', 'a', 'n'],
        {'location': (3, 0), 'hp': 96, 'alive': True, 'victory': True,
         'gold': 15, 'weapons': ['Rock']},
        ['Invalid action. Please choose one of the listed actions.'],
    ),
    (
        'main_gold_taken_only_once_on_revisit',
        MAIN_MAP,
        ['s', 'n', 's'],
        {'location': (2, 5), 'hp': 100, 'alive': True, 'victory': False,
         'gold': 20, 'weapons': ['Rock']},
        [],
    ),
    (
        'main_dagger_taken_only_once_on_revisit',
        MAIN_MAP,
        ['e', 'e', 'w', 'e'],
        {'location': (4, 4), 'hp': 100, 'alive': True, 'victory': False,
         'gold': 15, 'weapons': ['Dagger', 'Rock']},
        [],
    ),
    (
        'main_ogre_fight_with_dagger_then_loot',
        MAIN_MAP,
        ['e', 'e', 'w', 'w', 's', 's', 'e', 'a', 'a', 'a', 'e'],
        {'location': (4, 6), 'hp': 55, 'alive': True, 'victory': False,
         'gold': 25, 'weapons': ['Dagger', 'Rock']},
        ['You killed Ogre!'],
    ),
    (
        'main_spider_corpse_revisit_does_not_damage',
        MAIN_MAP,
        ['n', 'n', 'n', 'e', 'a', 'a', 'w', 'e'],
        {'location': (3, 1), 'hp': 96, 'alive': True, 'victory': False,
         'gold': 15, 'weapons': ['Rock']},
        ['The corpse of a dead spider rots on the ground.'],
    ),
    (
        'leave_level_minimal_victory',
        level_map('leave_level.txt'),
        ['e'],
        {'location': (1, 0), 'hp': 100, 'alive': True, 'victory': True,
         'gold': 15, 'weapons': ['Rock']},
        ['You made it out of the cave alive. You win!'],
    ),
    (
        'snake_level_failure_path',
        level_map('snake_level.txt'),
        ['e'],
        {'location': (1, 0), 'hp': 0, 'alive': False, 'victory': False,
         'gold': 15, 'weapons': ['Rock']},
        ['You have died. Game over.'],
    ),
    (
        'loot_level_victory_with_loot',
        level_map('loot_level.txt'),
        ['e', 'e'],
        {'location': (2, 0), 'hp': 100, 'alive': True, 'victory': True,
         'gold': 20, 'weapons': ['Rock']},
        [],
    ),
    (
        'loot_level_revisit_takes_gold_once',
        level_map('loot_level.txt'),
        ['e', 'w', 'e', 'e'],
        {'location': (2, 0), 'hp': 100, 'alive': True, 'victory': True,
         'gold': 20, 'weapons': ['Rock']},
        [],
    ),
    (
        'enemy_level_kill_spider_then_victory',
        level_map('enemy_level.txt'),
        ['e', 'a', 'a', 'e'],
        {'location': (2, 0), 'hp': 96, 'alive': True, 'victory': True,
         'gold': 15, 'weapons': ['Rock']},
        ['You killed Giant Spider!'],
    ),
]

CASE_IDS = [case[0] for case in CASES]


@pytest.mark.parametrize('map_path,inputs,expected,output_snippets',
                         [case[1:] for case in CASES],
                         ids=CASE_IDS)
def test_input_sequence_final_state(map_path, inputs, expected, output_snippets):
    player, output = run_game(inputs, map_path)
    state = final_state(player)
    assert state == expected
    for snippet in output_snippets:
        assert snippet in output


@pytest.mark.parametrize('map_path,inputs,expected',
                         [(case[1], case[2], case[3]) for case in CASES
                          if case[0].endswith('_revisit_takes_gold_once')
                          or case[0] == 'main_gold_taken_only_once_on_revisit'],
                         ids=['loot_level_revisit', 'main_gold_room_revisit'])
def test_loot_intro_shown_once(map_path, inputs, expected):
    player, output = run_game(inputs, map_path)
    assert final_state(player) == expected
    assert output.count('You pick it up.') == 1


def test_move_into_nonexistent_tile_is_blocked(capsys):
    world.load_tiles(MAIN_MAP)
    player = Player()
    player.move(dx=1, dy=0)
    player.move(dx=1, dy=0)
    player.move(dx=1, dy=0)
    assert (player.location_x, player.location_y) == (4, 4)
    assert "You can't go that way." in capsys.readouterr().out


def test_main_map_has_distinct_victory_and_failure_paths():
    winner, win_output = run_game(
        ['n', 'n', 'n', 'e', 'a', 'a', 'n'], MAIN_MAP)
    loser, lose_output = run_game(['s', 's', 's'], MAIN_MAP)
    assert winner.victory and winner.is_alive()
    assert 'You win!' in win_output
    assert not loser.victory and not loser.is_alive()
    assert 'Game over.' in lose_output
