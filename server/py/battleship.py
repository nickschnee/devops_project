from typing import List, Optional
from enum import Enum
import random
from server.py.game import Game, Player


from typing import List, Optional
from enum import Enum
import random

# Enums and Constants
class ActionType(str, Enum):
    SET_SHIP = 'set_ship'
    SHOOT = 'shoot'

class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'

# Data Models
class BattleshipAction:
    def __init__(self, action_type: ActionType, ship_name: Optional[str], location: List[str]) -> None:
        self.action_type = action_type
        self.ship_name = ship_name
        self.location = location

class Ship:
    def __init__(self, name: str, length: int) -> None:
        self.name = name
        self.length = length
        self.location = []  # List of grid coordinates occupied by the ship
        self.hits = 0       # Count of hits on the ship

    def is_sunk(self) -> bool:
        return self.hits >= self.length

class PlayerState:
    def __init__(self, name: str, ships: List[Ship]) -> None:
        self.name = name
        self.ships = ships
        self.shots = []  # All attempted shots
        self.successful_shots = []  # Successful hits

    def all_ships_sunk(self) -> bool:
        return all(ship.is_sunk() for ship in self.ships)

class BattleshipGameState:
    def __init__(self, idx_player_active: int, phase: GamePhase, winner: Optional[int], players: List[PlayerState]) -> None:
        self.idx_player_active = idx_player_active
        self.phase = phase
        self.winner = winner
        self.players = players

# Main Game Class
class Battleship:
    def __init__(self):
        """ Initialize the game """
        self.state = BattleshipGameState(
            idx_player_active=0,
            phase=GamePhase.SETUP,
            winner=None,
            players=[
                PlayerState("Player 1", self.create_ships()),
                PlayerState("Player 2", self.create_ships())
            ]
        )

    def create_ships(self) -> List[Ship]:
        """ Create the default set of ships """
        return [
            Ship("Carrier", 5),
            Ship("Battleship", 4),
            Ship("Cruiser", 3),
            Ship("Submarine", 3),
            Ship("Destroyer", 2)
        ]

    def print_state(self) -> None:
        """ Print the current state for debugging """
        print(f"Phase: {self.state.phase}")
        print(f"Active Player: {self.state.players[self.state.idx_player_active].name}")
        for idx, player in enumerate(self.state.players):
            print(f"Player {idx + 1} ({player.name}):")
            for ship in player.ships:
                print(f"  Ship: {ship.name}, Location: {ship.location}, Hits: {ship.hits}")
            print(f"  Shots: {player.shots}")
            print(f"  Successful Shots: {player.successful_shots}")

    def get_state(self) -> BattleshipGameState:
        return self.state

    def set_state(self, state: BattleshipGameState) -> None:
        self.state = state

    def get_list_action(self) -> List[BattleshipAction]:
        """ Return possible actions for the active player """
        actions = []
        active_player = self.state.players[self.state.idx_player_active]

        if self.state.phase == GamePhase.SETUP:
            for ship in active_player.ships:
                if not ship.location:
                    actions.append(BattleshipAction(ActionType.SET_SHIP, ship.name, []))
        elif self.state.phase == GamePhase.RUNNING:
            all_shots = active_player.shots
            for x in range(1, 11):
                for y in range(1, 11):
                    location = f"{chr(64 + x)}{y}"
                    if location not in all_shots:
                        actions.append(BattleshipAction(ActionType.SHOOT, None, [location]))

        return actions

    def apply_action(self, action: BattleshipAction) -> None:
        """ Apply the given action to the game """
        active_player = self.state.players[self.state.idx_player_active]
        opponent = self.state.players[1 - self.state.idx_player_active]

        if action.action_type == ActionType.SET_SHIP:
            for ship in active_player.ships:
                if ship.name == action.ship_name:
                    ship.location = action.location
                    break

            # Check if all ships are set
            if all(ship.location for ship in active_player.ships):
                if self.state.idx_player_active == 0:
                    self.state.idx_player_active = 1
                else:
                    self.state.phase = GamePhase.RUNNING
                    self.state.idx_player_active = 0

        elif action.action_type == ActionType.SHOOT:
            location = action.location[0]
            active_player.shots.append(location)

            hit = False
            for ship in opponent.ships:
                if location in ship.location:
                    ship.hits += 1
                    active_player.successful_shots.append(location)
                    hit = True
                    break

            if not hit:
                print(f"{location} was a miss!")

            # Check if the game is over
            if opponent.all_ships_sunk():
                self.state.phase = GamePhase.FINISHED
                self.state.winner = self.state.idx_player_active

            # Switch turns
            self.state.idx_player_active = 1 - self.state.idx_player_active

    def get_player_view(self, idx_player: int) -> BattleshipGameState:
        """ Get the masked state for the active player """
        masked_state = BattleshipGameState(
            idx_player_active=self.state.idx_player_active,
            phase=self.state.phase,
            winner=self.state.winner,
            players=[]
        )

        for idx, player in enumerate(self.state.players):
            if idx == idx_player:
                masked_state.players.append(player)
            else:
                # Mask opponent's ship locations
                masked_ships = [Ship(ship.name, ship.length) for ship in player.ships]
                masked_state.players.append(
                    PlayerState(player.name, masked_ships)
                )

        return masked_state

# Random Player Implementation
class RandomPlayer(PlayerState):
    def __init__(self, name: str):
        super().__init__(name, ships=[])

    def select_action(self, state: BattleshipGameState, actions: List[BattleshipAction]) -> Optional[BattleshipAction]:
        if actions:
            return random.choice(actions)
        return None

if __name__ == "__main__":
    game = Battleship()
    player1 = RandomPlayer("Player 1")
    player2 = RandomPlayer("Player 2")

    while game.get_state().phase != GamePhase.FINISHED:
        state = game.get_state()
        actions = game.get_list_action()

        if state.idx_player_active == 0:
            action = player1.select_action(state, actions)
        else:
            action = player2.select_action(state, actions)

        if action:
            game.apply_action(action)

    game.print_state()
    print(f"Winner: {game.get_state().players[game.get_state().winner].name}")
