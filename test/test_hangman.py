import pytest
from server.py.hangman import Hangman, HangmanGameState, GamePhase, GuessLetterAction
import string

@pytest.fixture
def game_server():
    """Create a new Hangman game instance for testing."""
    return Hangman()

def test_set_get_state(game_server):
    """Test 001: Set/get methods work properly [1 point]"""
    state = HangmanGameState(word_to_guess='devops', guesses=[], phase=GamePhase.RUNNING)
    game_server.set_state(state)
    game_state = game_server.get_state()
    hint = "Applying 'set_state' and then 'get_state' returns a different state"
    assert state.word_to_guess == game_state.word_to_guess, hint
    assert state.guesses == game_state.guesses, hint
    assert state.phase == game_state.phase, hint

def test_action_list(game_server):
    """Test 002: Action list contains only 'unused' capital letters [1 point]"""
    state = HangmanGameState(word_to_guess='devops', guesses=[], phase=GamePhase.RUNNING)
    game_server.set_state(state)

    # Initial actions
    actions = game_server.get_list_action()
    hint = "Initial actions list should contain all existing capital letters"
    assert {action.letter for action in actions} == set(string.ascii_uppercase), hint

    # Testcase 1
    test_state1 = HangmanGameState(word_to_guess="", guesses=['A', 'B', 'C'], phase=GamePhase.RUNNING)
    game_server.set_state(test_state1)
    actions1 = game_server.get_list_action()
    hint = "Some 'guessed' letters are still in the action list"
    assert {action.letter for action in actions1} == set(string.ascii_uppercase[3:]), hint

    # Testcase 2
    test_state2 = HangmanGameState(word_to_guess="", guesses=[*string.ascii_uppercase], phase=GamePhase.RUNNING)
    game_server.set_state(test_state2)
    actions2 = game_server.get_list_action()
    assert len(actions2) == 0, "Having guessed all letters, the action list should be empty"

def test_apply_action_general(game_server):
    """Test 003: Apply action method adds new guess to gamestate [1 point]"""
    state = HangmanGameState(word_to_guess='devops', guesses=[], phase=GamePhase.RUNNING)
    game_server.set_state(state)
    game_server.apply_action(GuessLetterAction(letter='D'))
    updated_state = game_server.get_state()
    hint = "After applying a 'GuessLetterAction', the letter is not in the list of 'guesses'"
    assert updated_state.guesses == ['D'], hint

def test_apply_action_lowercase(game_server):
    """Test 004: Apply action also works for lowercase letters [1 point]"""
    state = HangmanGameState(word_to_guess='devops', guesses=[], phase=GamePhase.RUNNING)
    game_server.set_state(state)
    game_server.apply_action(GuessLetterAction(letter='x'))
    updated_state = game_server.get_state()
    assert updated_state.guesses == ['X'], "Guessing a lower case letter doesn't work"

def test_game_ending(game_server):
    """Test 005: Game ends with 8 wrong guesses or when secret word is revealed [1 point]"""
    # Test 8 wrong guesses
    state1 = HangmanGameState(word_to_guess="XY", guesses=[*'ABCDEFG'], phase=GamePhase.RUNNING)
    game_server.set_state(state1)
    game_server.apply_action(GuessLetterAction(letter='H'))
    assert game_server.get_state().phase == GamePhase.FINISHED, "Gamephase should be 'FINISHED' after 8 wrong guesses"

    # Test secret word revealed
    state2 = HangmanGameState(word_to_guess="XY", guesses=[*'AX'], phase=GamePhase.RUNNING)
    game_server.set_state(state2)
    game_server.apply_action(GuessLetterAction(letter='Y'))
    assert game_server.get_state().phase == GamePhase.FINISHED, "Gamephase should be 'FINISHED' after revealing the secret word"

def test_secret_word_lowercase_letters(game_server):
    """Test 006: Game also works when secret words contain lowercase letters [1 point]"""
    state = HangmanGameState(word_to_guess="Xy", guesses=[*'AY'], phase=GamePhase.RUNNING)
    game_server.set_state(state)
    game_server.apply_action(GuessLetterAction(letter='x'))
    assert game_server.get_state().phase == GamePhase.FINISHED, "Game did not finish correctly with a lowercase letter in the word"

def test_no_action_on_finished_game(game_server):
    """Test 007: No actions are allowed on a finished game [1 point]"""
    state = HangmanGameState(word_to_guess="HELLO", guesses=[*'AEIOUBCDF'], phase=GamePhase.FINISHED)
    game_server.set_state(state)
    with pytest.raises(RuntimeError):
        game_server.apply_action(GuessLetterAction(letter='G'))

def test_repeated_guess(game_server):
    """Test 008: Repeated guesses should not alter the game state [1 point]"""
    state = HangmanGameState(word_to_guess="HELLO", guesses=['H'], phase=GamePhase.RUNNING)
    game_server.set_state(state)
    game_server.apply_action(GuessLetterAction(letter='H'))
    updated_state = game_server.get_state()
    assert updated_state.guesses == ['H'], "Repeated guess changed the guesses list"

def test_case_insensitivity_in_word(game_server):
    """Test 009: Word with mixed-case letters is treated correctly [1 point]"""
    state = HangmanGameState(word_to_guess="HeLLo", guesses=['H', 'E', 'L'], phase=GamePhase.RUNNING)
    game_server.set_state(state)
    game_server.apply_action(GuessLetterAction(letter='o'))
    assert game_server.get_state().phase == GamePhase.FINISHED, "Mixed-case word not handled correctly"

def test_word_with_special_characters(game_server):
    """Test 010: Words with special characters are handled properly [1 point]"""
    state = HangmanGameState(word_to_guess="C#D3", guesses=['C', '#', 'D'], phase=GamePhase.RUNNING)
    game_server.set_state(state)
    game_server.apply_action(GuessLetterAction(letter='3'))
    assert game_server.get_state().phase == GamePhase.FINISHED, "Word with special characters not handled correctly"
