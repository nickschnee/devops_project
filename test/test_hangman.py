import random
import pickle
import os


class Hangman:
    def __init__(self):
        self.words = [
            "apple", "beach", "chair", "dance", "eagle", "friend", "garden", "house", "island", "jacket",
            "bicycle", "captain", "dolphin", "energy", "farmer", "galaxy", "harmony", "insect", "journey", "kingdom",
            "labyrinth", "marathon", "nebula", "oxygen", "pyramid", "quantum", "reservoir", "symphony", "tranquil",
            "umbrella", "algorithm", "blockchain", "cryptocurrency", "debugging", "ecosystem", "framework",
            "hypothesis", "kaleidoscope", "longitude", "wilderness"
        ]

        self.word_to_guess = random.choice(self.words)
        self.correct_guesses = set()
        self.incorrect_guesses = set()
        self.attempts_left = 6
        self.score = 0 
        self.hangman_images = [
            """
               -----
               |   |
                   |
                   |
                   |
                   |
            =========
            """,
            """
               -----
               |   |
               O   |
                   |
                   |
                   |
            =========
            """,
            """
               -----
               |   |
               O   |
               |   |
                   |
                   |
            =========
            """,
            """
               -----
               |   |
               O   |
              /|   |
                   |
                   |
            =========
            """,
            """
               -----
               |   |
               O   |
              /|\\  |
                   |
                   |
            =========
            """,
            """
               -----
               |   |
               O   |
              /|\\  |
              /    |
                   |
            =========
            """,
            """
               -----
               |   |
               O   |
              /|\\  |
              / \\  |
                   |
            =========
            """
        ]

    def save_state(self):
        with open("game_state.pkl", "wb") as file:
            pickle.dump(self, file)

    @staticmethod
    def load_state():
        try:
            with open("game_state.pkl", "rb") as file:
                return pickle.load(file)
        except FileNotFoundError:
            return None

    @staticmethod
    def delete_state():
        if os.path.exists("game_state.pkl"):
            os.remove("game_state.pkl")

    def display_progress(self):
        progress = " ".join([letter if letter in self.correct_guesses else "_" for letter in self.word_to_guess])
        print(f"Word progress: {progress}")
        return progress

    def play_turn(self):
        print(self.hangman_images[6 - self.attempts_left])  
        while True:
            guess = input("Enter your guess (single letter): ").lower().strip()
            if len(guess) == 1 and guess.isalpha():
                break
            print("Invalid input, Please enter a single alphabetic character.")
        
        if guess in self.word_to_guess:
            if guess in self.correct_guesses:
                print(f"You have already guessed '{guess}'.")
            else:
                print(f"Good guess! '{guess}' is in the word.")
                self.correct_guesses.add(guess)
                self.score += 10 
        else:
            if guess in self.incorrect_guesses:
                print(f"You have already guessed '{guess}' and it was incorrect.")
            else:
                print(f"Sorry, Wrong guess. '{guess}' is not in the word.")
                self.incorrect_guesses.add(guess)
                self.attempts_left -= 1
                self.score -= 5  

        print(f"Score: {self.score}")
        self.save_state()

    def play_game(self):
        print("Welcome to Hangman")
        while self.attempts_left > 0:
            progress = self.display_progress()
            if "_" not in progress:
                print(f"Congratulations! You have guessed the word: {self.word_to_guess}.")
                print(f"Final Score: {self.score}")
                break
            self.play_turn()
        else:
            print(f"Game over! The correct word was: {self.word_to_guess}.")
            print(f"Final Score : {self.score}")
        self.delete_state()
        self.ask_for_restart()

    def ask_for_restart(self):
        restart = input("Would you like to play again? (yes/no): ").strip().lower()
        if restart == "yes":
            self.__init__()  
            self.play_game()
        else:
            print("Thank you for playing Goodbye...")


game = Hangman.load_state()
if game is None:
    print("No saved game found!!!")
    game = Hangman()
game.play_game()
