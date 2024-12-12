from typing import List, Optional
import random
from enum import Enum
from server.py.game import Game, Player
class GamePhase(str, Enum):
    """
    Enum to represent the different phases of the Hangman game.
    """
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"


class GuessLetterAction:
    """
    Represents an action where a player guesses a letter in the Hangman game.
    """
    def __init__(self, letter: str) -> None:
        self.letter = letter.upper()


class HangmanGameState:
    """
    Represents the current state of the Hangman game, including the word to guess,
    the phase of the game, and the guesses made so far.
    """
    def __init__(self, word_to_guess: str, guesses: List[str], phase: GamePhase) -> None:
        """
        Args:
            word_to_guess (str): The word that the player is trying to guess.
            guesses (List[str]): List of guessed letters (both correct and incorrect).
            phase (GamePhase): The current phase of the game (RUNNING or FINISHED).
        """
        self.word_to_guess = word_to_guess.upper()  # Normalize to uppercase for consistency
        self.guesses = [guess.upper() for guess in guesses]
        self.phase = phase

    def incorrect_guesses(self) -> List[str]:
        """
        Get a list of incorrect guesses.

        Returns:
            List[str]: Letters guessed that are not in the word to guess.
        """
        return [guess for guess in self.guesses if guess not in self.word_to_guess]

    def is_word_guessed(self) -> bool:
        """
        Check if the entire word has been guessed.

        Returns:
            bool: True if all letters in the word have been guessed, False otherwise.
        """
        return all(
            char in self.guesses
            for char in self.word_to_guess
            if char.isalpha()
        )

    def get_masked_word(self) -> str:
        """
        Get the masked version of the word to guess.

        Returns:
            str: The word with unguessed letters replaced by underscores.
        """
        return "".join(
            char if char in self.guesses else "_"
            for char in self.word_to_guess
        )

    def __str__(self) -> str:
        """
        String representation of the game state for debugging or display.

        Returns:
            str: A formatted string showing the masked word, guesses, and phase.
        """
        return (
            f"Word to guess: {self.get_masked_word()}\n"
            f"Phase: {self.phase}\n"
            f"Guesses: {', '.join(self.guesses)}\n"
            f"Incorrect guesses: {', '.join(self.incorrect_guesses())}"
        )


class Hangman:
    """
    Manages the Hangman game, including game logic, state management, and actions.
    """
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