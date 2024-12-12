"""
Hangman Game Implementation

This module provides the classes and logic for a Hangman game. It includes classes for managing
player actions, the game state, and automated/random players for testing or simulations.
"""
from typing import List, Optional
import random
from enum import Enum

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
        if len(letter) != 1 or not letter.isalpha():
            raise ValueError("Guess must be a single alphabetic character.")
        self.letter = letter.upper()

    def __str__(self) -> str:
        """
        String representation of the guessed letter.

        Returns:
            str: The guessed letter in uppercase.
        """
        return self.letter

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
        self.word_to_guess = word_to_guess.upper()
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
        return all(char in self.guesses for char in self.word_to_guess if char.isalpha())

    def get_masked_word(self) -> str:
        """
        Get the masked version of the word to guess.

        Returns:
            str: The word with unguessed letters replaced by underscores.
        """
        return "".join(char if char in self.guesses else "_" for char in self.word_to_guess)

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
    MAX_INCORRECT_GUESSES = 8

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

    def apply_action(self, guess_action: GuessLetterAction) -> None:
        """Apply a letter-guess action to the game."""
        if not self.state:
            raise ValueError("Game state has not been set.")

        letter = guess_action.letter
        if letter in self.state.guesses:
            print(f"Letter '{letter}' has already been guessed.")
            return  # Letter already guessed, no change

        self.state.guesses.append(letter)

        if letter not in self.state.word_to_guess:
            if len(self.state.incorrect_guesses()) >= self.MAX_INCORRECT_GUESSES:
                self.state.phase = GamePhase.FINISHED
        else:
            if self.state.is_word_guessed():
                self.state.phase = GamePhase.FINISHED

        # Normalize state to ensure consistent handling of mixed cases
        self.state.word_to_guess = self.state.word_to_guess.upper()
        self.state.guesses = [guess.upper() for guess in self.state.guesses]

class RandomPlayer:
    """
    A player that makes random guesses in the Hangman game.
    """
    def make_guess(self, available_moves: List[GuessLetterAction]) -> GuessLetterAction:
        """
        Make a random guess from the available actions.

        Args:
            available_moves (List[GuessLetterAction]): List of possible actions.

        Returns:
            GuessLetterAction: The randomly chosen action.
        """
        if not available_moves:
            raise ValueError("No available actions to guess.")
        return random.choice(available_moves)

if __name__ == "__main__":
    game = Hangman()
    game_state = HangmanGameState(
        word_to_guess="Python",
        guesses=[],
        phase=GamePhase.RUNNING
    )
    game.set_state(game_state)

    while game.get_state().phase == GamePhase.RUNNING:
        print(game.get_state())
        try:
            user_input = input("Enter your guess (a single letter): ").strip()
            user_guess = GuessLetterAction(user_input)
            game.apply_action(user_guess)
        except ValueError as err:
            print(err)

    if game.get_state().is_word_guessed():
        print("Congratulations! You've guessed the word.")
    else:
        print("Game over! Better luck next time.")
