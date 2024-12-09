# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py
from server.py.game import Game, Player
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from enum import Enum
import random


class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank


class Marble(BaseModel):
    pos: int       # position on board (0 to 95)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel):
    name: str                  # name of player
    list_card: List[Card]      # list of cards
    list_marble: List[Marble]  # list of marbles


class Action(BaseModel):
    card: Card                 # card to play
    pos_from: Optional[int]    # position to move the marble from
    pos_to: Optional[int]      # position to move the marble to
    card_swap: Optional[Card] = None  # optional card to swap ()


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class GameState(BaseModel):

    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']  # 4 suits (colors)
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',      # 13 ranks + Joker
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
        # 2: Move 2 spots forward
        Card(suit='♠', rank='2'), Card(suit='♥', rank='2'), Card(suit='♦', rank='2'), Card(suit='♣', rank='2'),
        # 3: Move 3 spots forward
        Card(suit='♠', rank='3'), Card(suit='♥', rank='3'), Card(suit='♦', rank='3'), Card(suit='♣', rank='3'),
        # 4: Move 4 spots forward or back
        Card(suit='♠', rank='4'), Card(suit='♥', rank='4'), Card(suit='♦', rank='4'), Card(suit='♣', rank='4'),
        # 5: Move 5 spots forward
        Card(suit='♠', rank='5'), Card(suit='♥', rank='5'), Card(suit='♦', rank='5'), Card(suit='♣', rank='5'),
        # 6: Move 6 spots forward
        Card(suit='♠', rank='6'), Card(suit='♥', rank='6'), Card(suit='♦', rank='6'), Card(suit='♣', rank='6'),
        # 7: Move 7 single steps forward
        Card(suit='♠', rank='7'), Card(suit='♥', rank='7'), Card(suit='♦', rank='7'), Card(suit='♣', rank='7'),
        # 8: Move 8 spots forward
        Card(suit='♠', rank='8'), Card(suit='♥', rank='8'), Card(suit='♦', rank='8'), Card(suit='♣', rank='8'),
        # 9: Move 9 spots forward
        Card(suit='♠', rank='9'), Card(suit='♥', rank='9'), Card(suit='♦', rank='9'), Card(suit='♣', rank='9'),
        # 10: Move 10 spots forward
        Card(suit='♠', rank='10'), Card(suit='♥', rank='10'), Card(suit='♦', rank='10'), Card(suit='♣', rank='10'),
        # Jake: A marble must be exchanged
        Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(suit='♦', rank='J'), Card(suit='♣', rank='J'),
        # Queen: Move 12 spots forward
        Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(suit='♦', rank='Q'), Card(suit='♣', rank='Q'),
        # King: Start or move 13 spots forward
        Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(suit='♦', rank='K'), Card(suit='♣', rank='K'),
        # Ass: Start or move 1 or 11 spots forward
        Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(suit='♦', rank='A'), Card(suit='♣', rank='A'),
        # Joker: Use as any other card you want
        Card(suit='', rank='JKR'), Card(suit='', rank='JKR'), Card(suit='', rank='JKR')
    ] * 2

    cnt_player: int = 4                # number of players (must be 4)
    phase: GamePhase                   # current phase of the game
    cnt_round: int                     # current round
    bool_game_finished: bool           # true if game has finished
    bool_card_exchanged: bool          # true if cards was exchanged in round
    idx_player_started: int            # index of player that started the round
    idx_player_active: int             # index of active player in round
    list_player: List[PlayerState]     # list of players
    list_card_draw: List[Card]         # list of cards to draw
    list_card_discard: List[Card]      # list of cards discarded
    card_active: Optional[Card]        # active card (for 7 and JKR with sequence of actions)

class Dog(Game):
    def __init__(self) -> None:
        """Game initialization"""
        self._state = GameState(
            cnt_player=4,
            phase=GamePhase.RUNNING,
            cnt_round=1,
            bool_game_finished=False,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=[],
            list_card_draw=[],
            list_card_discard=[],
            card_active=None
        )
        self.reset()

    def reset(self) -> None:
        """Reset the game to initial state"""
        # Create a fresh deck and shuffle it
        all_cards = GameState.LIST_CARD.copy()
        random.shuffle(all_cards)
        
        # Initialize players
        self._state.list_player = []
        for i in range(4):
            # Deal 6 cards to each player
            player_cards = all_cards[i * 6:(i + 1) * 6]
            
            # Create 4 marbles for each player, starting in kennel (pos 64-67)
            player_marbles = [
                Marble(pos=64 + j, is_save=False) 
                for j in range(4)
            ]
            
            # Create player state
            player = PlayerState(
                name=f"Player {i}",
                list_card=player_cards,
                list_marble=player_marbles
            )
            self._state.list_player.append(player)
        
        # Remaining cards go to draw pile
        self._state.list_card_draw = all_cards[24:]
        self._state.list_card_discard = []
        
        # Reset game state
        self._state.cnt_round = 1
        self._state.bool_game_finished = False
        self._state.bool_card_exchanged = False
        self._state.idx_player_started = 0
        self._state.idx_player_active = 0
        self._state.card_active = None

    def get_state(self) -> GameState:
        """Get the complete, unmasked game state"""
        return self._state

    def set_state(self, state: GameState) -> None:
        """Set the game to a given state"""
        self._state = state

    def print_state(self) -> None:
        """ Print the current game state """
        pass

    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        if self._state.cnt_round == 0 and not self._state.bool_card_exchanged:
            return []

        actions = []
        active_player_idx = self._state.idx_player_active
        player = self._state.list_player[active_player_idx]

        # Check if start position is occupied by the player's own marble
        occupant_player_idx = self.get_player_who_occupies_pos(0)
        start_occupied_by_self = (occupant_player_idx == active_player_idx)

        # START actions (Kennel -> Start)
        for card in player.list_card:
            # A, K, JKR can start a marble if not blocked by self
            if card.rank in ['A', 'K', 'JKR'] and not start_occupied_by_self:
                actions.append(Action(
                    card=card,
                    pos_from=64,
                    pos_to=0,
                    card_swap=None
                ))

        # REGULAR MOVE actions with ACE:
        # An Ace can also move a marble already on the board by 1 or 11 steps.
        for card in player.list_card:
            if card.rank == 'A':
                steps = [1, 11]
                for marble in player.list_marble:
                    # Marble must be on the board (0 to 63 for main track, as an assumption)
                    # We know pos=0 is start - so let's allow from there.
                    if 0 <= marble.pos < 64:
                        for step in steps:
                            new_pos = (marble.pos + step) % 96
                            # In a real game, you'd check for blocking rules, 
                            # but for now let's just add these possible moves.
                            actions.append(Action(
                                card=card,
                                pos_from=marble.pos,
                                pos_to=new_pos
                            ))
        return actions


    def apply_action(self, action: Action) -> None:
        """Apply the given action to the game state"""
        if action is None:
            return

        active_player_idx = self._state.idx_player_active
        player = self._state.list_player[active_player_idx]

        # Moving out of kennel to start
        if action.pos_from == 64 and action.pos_to == 0:
            occupant_player_idx = self.get_player_who_occupies_pos(0)
            if occupant_player_idx is not None and occupant_player_idx != active_player_idx:
                # Kick out opponent's marble
                opponent = self._state.list_player[occupant_player_idx]
                for marble in opponent.list_marble:
                    if marble.pos == 0:
                        # Move opponent's marble back to its kennel start
                        marble.pos = 72
                        marble.is_save = False
                        break

            # Move our marble from kennel to start
            for marble in player.list_marble:
                if marble.pos >= 64:
                    marble.pos = 0
                    marble.is_save = True
                    # Remove used card
                    player.list_card = [c for c in player.list_card if not (c.suit == action.card.suit and c.rank == action.card.rank)]
                    break

        # Moving a marble on the board using an ACE (1 or 11 steps)
        elif action.card.rank == 'A' and 0 <= action.pos_from < 64:
            # Find the marble at pos_from
            for marble in player.list_marble:
                if marble.pos == action.pos_from:
                    # Move it
                    # If there's an opponent marble at pos_to, kick it out (optional if needed)
                    occupant_player_idx = self.get_player_who_occupies_pos(action.pos_to)
                    if occupant_player_idx is not None and occupant_player_idx != active_player_idx:
                        opponent = self._state.list_player[occupant_player_idx]
                        for omarble in opponent.list_marble:
                            if omarble.pos == action.pos_to:
                                omarble.pos = 72
                                omarble.is_save = False
                                break

                    marble.pos = action.pos_to
                    marble.is_save = False  # once moved, it's not in the initial "is_save" state
                    # Remove used card
                    player.list_card = [c for c in player.list_card if not (c.suit == action.card.suit and c.rank == action.card.rank)]
                    break
            
    def get_player_who_occupies_pos(self, position: int) -> Optional[int]:
        """Return the index of the player who occupies the given position, or None if empty."""
        for i, p in enumerate(self._state.list_player):
            for m in p.list_marble:
                if m.pos == position:
                    return i
        return None

    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        pass


class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None