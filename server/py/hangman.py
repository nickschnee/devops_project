from typing import List, Optional
import random
from enum import Enum
from server.py.game import Game, Player


class GuessLetterAction:

    def __init__(self, letter: str) -> None:
        self.letter = letter


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class HangmanGameState:

    def __init__(self, word_to_guess: str, phase: GamePhase, guesses: List[str], incorrect_guesses: List[str]) -> None:
        self.word_to_guess = word_to_guess
        self.phase = phase
        self.guesses = guesses
        self.incorrect_guesses = incorrect_guesses


class Hangman(Game):
    def __init__(self) -> None:
        """Game initialization also requires a set_state call to set the 'word_to_guess'."""
        self.state: Optional[HangmanGameState] = None

    def get_state(self) -> HangmanGameState:
        """Get the complete, unmasked game state."""
        if not self.state:
            raise ValueError("Game state has not been set.")
        return self.state

    def set_state(self, state: HangmanGameState) -> None:
        """Set the game state."""
        self.state = state

    def print_state(self) -> None:
        """Print the current game state."""
        if not self.state:
            print("Game state has not been set.")
            return
        print(f"Word to guess: {self.state.word_to_guess}")
        print(f"Phase: {self.state.phase}")
        print(f"Guesses: {', '.join(self.state.guesses)}")
        print(f"Incorrect guesses: {', '.join(self.state.incorrect_guesses)}")

    def get_list_action(self) -> List[GuessLetterAction]:
    """Get a list of possible actions for the active player.
    Only returns letters that haven't been guessed yet in the Hangman game.
    
    Returns:
        List[GuessLetterAction]: List of available letter actions
        
    Raises:
        ValueError: If game state hasn't been set
    """
    if not self.state:
        raise ValueError("Game state has not been set.")
    
    # Track all used letters
    used_letters = set(self.state.guesses + self.state.incorrect_guesses)
    return [GuessLetterAction(chr(i)) for i in range(97, 123)]  

    def apply_action(self, action: GuessLetterAction) -> None:
        """Apply the given action to the game."""
        if not self.state:
            raise ValueError("Game state has not been set.")
        letter = action.letter.lower()
        if letter in self.state.guesses or letter in self.state.incorrect_guesses:
            print(f"The letter '{letter}' has already been guessed.")
            return

        if letter in self.state.word_to_guess.lower():
            self.state.guesses.append(letter)
        else:
            self.state.incorrect_guesses.append(letter)

        if all(char.lower() in self.state.guesses for char in self.state.word_to_guess if char.isalpha()):
            self.state.phase = GamePhase.FINISHED

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """Get the masked state for the active player."""
        if not self.state:
            raise ValueError("Game state has not been set.")

        masked_word = ''.join(
            char if char.lower() in self.state.guesses else '_'
            for char in self.state.word_to_guess
        )
        return HangmanGameState(
            word_to_guess=masked_word,
            phase=self.state.phase,
            guesses=self.state.guesses,
            incorrect_guesses=self.state.incorrect_guesses
        )



class RandomPlayer(Player):  

    def select_action(self, state: HangmanGameState, actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == "__main__":
    # Example usage
    game = Hangman()
    game_state = HangmanGameState(word_to_guess='DevOps', phase=GamePhase.SETUP, guesses=[], incorrect_guesses=[])
    game.set_state(game_state)

    # Simulate player view
    print("Full game state:")
    game.print_state()

    print("\nMasked player view:")
    player_view = game.get_player_view(idx_player=0)
    print(f"Word to guess (masked): {player_view.word_to_guess}")
    print(f"Phase: {player_view.phase}")
    print(f"Guesses: {', '.join(player_view.guesses)}")
    print(f"Incorrect guesses: {', '.join(player_view.incorrect_guesses)}")