"""
A simple text adventure designed as a learning experience for new programmers.
"""
__author__ = 'Phillip Johnson'
import world
from player import Player
from pathlib import Path
import pickle


def play(saved_world=None, saved_player=None):
    if saved_world is not None and saved_player is not None:
        world._world = saved_world
        player = saved_player
    else:
        world.load_tiles()
        player = Player()
    return game_loop(player)

def game_loop(player, input_func=input):
    room = world.tile_exists(player.location_x, player.location_y)
    print(room.intro_text())
    while player.is_alive() and not player.victory:
        room = world.tile_exists(player.location_x, player.location_y)
        room.modify_player(player)
        # Check again since the room could have changed the player's state
        if not player.is_alive() or player.victory:
            break
        print("Choose an action:\n")
        available_actions = room.available_actions()
        for action in available_actions:
            print(action)
        action = choose_action(available_actions, input_func)
        if action is None:
            # Input stream ended (e.g. EOF); stop the game without crashing.
            print("No more input. Ending game.")
            break
        player.do_action(action, **action.kwargs)
    print_outcome(player)
    return player

def choose_action(available_actions, input_func):
    """Prompts until the player picks a listed action. Returns None on EOF."""
    while True:
        try:
            action_input = input_func('Action: ')
        except EOFError:
            return None
        for action in available_actions:
            if action_input == action.hotkey:
                return action
        print("Invalid action. Please choose one of the listed actions.")

def print_outcome(player):
    """Reports the final result so victory is never confused with death."""
    if player.victory:
        print("You made it out of the cave alive. You win!")
    elif not player.is_alive():
        print("You have died. Game over.")

def check_for_save():
    if Path("saved_player.p").is_file() and Path("saved_world.p").is_file():
        saved_world = pickle.load(open("saved_world.p", "rb"))
        saved_player = pickle.load(open("saved_player.p", "rb"))
        save_exists = True
    else:
        save_exists = False

    if save_exists:
        valid_input = False
        while not valid_input:
            load = input("Saved game found! Do you want to load the game? Y/N ")
            if load in ['Y','y']:
                play(saved_world, saved_player)
                valid_input = True
            elif load in ['N','n']:
                play()
                valid_input = True
            else:
                print("Invalid choice.")
    else:
        play()

if __name__ == "__main__":
    check_for_save()
