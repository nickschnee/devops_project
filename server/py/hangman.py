from typing import List, Optional
import random
from enum import Enum
from server.py.game import Game, Player

class GamePhase(str, Enum):
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"


class GuessLetterAction:
    def __init__(self, letter: str) -> None:
        self.letter = letter.upper()


class HangmanGameState:
    def __init__(self, word_to_guess: str, guesses: List[str], phase: GamePhase) -> None:
        self.word_to_guess = word_to_guess.upper()
        self.guesses = [guess.upper() for guess in guesses]
        self.phase = phase


class Hangman:
    def __init__(self) -> None:
        """Initialize the Hangman game."""
        self.state: Optional[HangmanGameState] = None

    def reset(self) -> None:
        """Reset the game state."""
        self.state = None

    def set_state(self, state: HangmanGameState) -> None:
        """Set the game state."""
        self.state = state

    def get_state(self) -> HangmanGameState:
        """Get the current game state."""
        if not self.state:
            raise ValueError("Game state has not been set.")
        return self.state

    def get_list_action(self) -> List[GuessLetterAction]:
        """Get a list of possible letter actions (unused letters)."""
        if not self.state:
            raise ValueError("Game state has not been set.")

        all_letters = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        used_letters = set(self.state.guesses)
        available_letters = all_letters - used_letters
        return [GuessLetterAction(letter) for letter in sorted(available_letters)]

    def apply_action(self, action: GuessLetterAction) -> None:
        """Apply a letter-guess action to the game."""
        if not self.state:
            raise ValueError("Game state has not been set.")

        letter = action.letter.upper()
        if letter in self.state.guesses:
            return  # Letter already guessed, no change

        self.state.guesses.append(letter)

        if letter not in self.state.word_to_guess:
            # Count incorrect guesses
            incorrect_guesses = len(
                [g for g in self.state.guesses if g not in self.state.word_to_guess]
            )
            if incorrect_guesses >= 8:
                self.state.phase = GamePhase.FINISHED
        else:
            # Check if the word is fully guessed
            word_set = set(self.state.word_to_guess)
            if all(char in self.state.guesses for char in word_set):
                self.state.phase = GamePhase.FINISHED