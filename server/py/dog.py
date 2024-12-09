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

    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']  # 4 suits
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',
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
        # 7: Move 7 single steps forward (not implemented yet, but in deck)
        Card(suit='♠', rank='7'), Card(suit='♥', rank='7'), Card(suit='♦', rank='7'), Card(suit='♣', rank='7'),
        # 8: Move 8 spots forward
        Card(suit='♠', rank='8'), Card(suit='♥', rank='8'), Card(suit='♦', rank='8'), Card(suit='♣', rank='8'),
        # 9: Move 9 spots forward
        Card(suit='♠', rank='9'), Card(suit='♥', rank='9'), Card(suit='♦', rank='9'), Card(suit='♣', rank='9'),
        # 10: Move 10 spots forward
        Card(suit='♠', rank='10'), Card(suit='♥', rank='10'), Card(suit='♦', rank='10'), Card(suit='♣', rank='10'),
        # J (Jack): exchange marbles (not implemented yet)
        Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(suit='♦', rank='J'), Card(suit='♣', rank='J'),
        # Q (Queen): Move 12 spots forward
        Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(suit='♦', rank='Q'), Card(suit='♣', rank='Q'),
        # K (King): Start or move 13 spots forward
        Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(suit='♦', rank='K'), Card(suit='♣', rank='K'),
        # A (Ace): Start or move 1 or 11 spots forward
        Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(suit='♦', rank='A'), Card(suit='♣', rank='A'),
        # Joker: Use as any card
        Card(suit='', rank='JKR'), Card(suit='', rank='JKR'), Card(suit='', rank='JKR')
    ] * 2

    cnt_player: int = 4
    phase: GamePhase = GamePhase.RUNNING
    cnt_round: int = 1
    bool_game_finished: bool = False
    bool_card_exchanged: bool = False
    idx_player_started: int = 0
    idx_player_active: int = 0
    list_player: List[PlayerState] = []
    list_card_draw: List[Card] = []
    list_card_discard: List[Card] = []
    card_active: Optional[Card] = None


class Dog(Game):
    def __init__(self) -> None:
        """Game initialization"""
        self._state = GameState()
        self.reset()

    def reset(self) -> None:
        """Reset the game to initial state"""
        all_cards = GameState.LIST_CARD.copy()
        random.shuffle(all_cards)
        
        # Initialize players
        self._state.list_player = []
        for i in range(4):
            player_cards = all_cards[i * 6:(i + 1) * 6]
            
            # 4 marbles in kennel positions 64,65,66,67
            player_marbles = [Marble(pos=64 + j, is_save=False) for j in range(4)]
            
            player = PlayerState(
                name=f"Player {i}",
                list_card=player_cards,
                list_marble=player_marbles
            )
            self._state.list_player.append(player)
        
        self._state.list_card_draw = all_cards[24:]
        self._state.list_card_discard = []
        
        self._state.cnt_round = 1
        self._state.bool_game_finished = False
        self._state.bool_card_exchanged = False
        self._state.idx_player_started = 0
        self._state.idx_player_active = 0
        self._state.card_active = None

    def get_state(self) -> GameState:
        return self._state

    def set_state(self, state: GameState) -> None:
        self._state = state

    def print_state(self) -> None:
        pass

    def get_player_who_occupies_pos(self, position: int) -> Optional[int]:
        for i, p in enumerate(self._state.list_player):
            for m in p.list_marble:
                if m.pos == position:
                    return i
        return None

    def get_list_action(self) -> List[Action]:
        """Get a list of possible actions for the active player."""
        state = self._state
        if state.cnt_round == 0 and not state.bool_card_exchanged:
            # No actions if round=0 and no card exchange done
            return []

        actions = []
        active_player_idx = state.idx_player_active
        player = state.list_player[active_player_idx]

        # Define move options for numeric cards
        move_options = {
            'A': [1, 11],
            '2': [2],
            '3': [3],
            '4': [4, -4],
            '5': [5],
            '6': [6],
        }

        # Check if start is blocked by self
        occupant_player_idx = self.get_player_who_occupies_pos(0)
        start_occupied_by_self = (occupant_player_idx == active_player_idx)

        # Check if there's a marble in the first kennel position (pos=64)
        # for a start action
        has_marble_at_64 = any(m.pos == 64 for m in player.list_marble)

        # START actions (A,K,JKR) only if not self-blocked and a marble at pos=64
        for card in player.list_card:
            if card.rank in ['A', 'K', 'JKR'] and not start_occupied_by_self and has_marble_at_64:
                # Add exactly one start action per start card
                # from pos=64 to pos=0
                actions.append(Action(
                    card=card,
                    pos_from=64,
                    pos_to=0,
                    card_swap=None
                ))

        # NORMAL MOVE actions:
        # Produce moves only for marbles on the board (pos<64)
        # Do not produce moves for marbles in kennel (pos>=64)
        for card in player.list_card:
            if card.rank in move_options:
                steps_list = move_options[card.rank]
                for marble in player.list_marble:
                    # Only consider marbles on the board (pos<64)
                    if 0 <= marble.pos < 64:
                        for step in steps_list:
                            new_pos = (marble.pos + step) % 96
                            actions.append(Action(
                                card=card,
                                pos_from=marble.pos,
                                pos_to=new_pos,
                                card_swap=None
                            ))

        return actions

    def apply_action(self, action: Action) -> None:
        if action is None:
            return

        state = self._state
        active_player_idx = state.idx_player_active
        player = state.list_player[active_player_idx]

        # Move out of kennel to start
        if action.pos_from == 64 and action.pos_to == 0:
            occupant_player_idx = self.get_player_who_occupies_pos(0)
            if occupant_player_idx is not None and occupant_player_idx != active_player_idx:
                # Kick out opponent's marble to pos=72
                opponent = state.list_player[occupant_player_idx]
                for m in opponent.list_marble:
                    if m.pos == 0:
                        m.pos = 72
                        m.is_save = False
                        break

            # Move our marble from kennel (pos=64) to start (pos=0)
            for m in player.list_marble:
                if m.pos == 64:
                    m.pos = 0
                    m.is_save = True
                    # Remove used card
                    player.list_card = [c for c in player.list_card if not (c.suit == action.card.suit and c.rank == action.card.rank)]
                    break
        else:
            # Normal movement on the board
            for m in player.list_marble:
                if m.pos == action.pos_from:
                    # If opponent occupies pos_to, kick them out
                    occupant_player_idx = self.get_player_who_occupies_pos(action.pos_to)
                    if occupant_player_idx is not None and occupant_player_idx != active_player_idx:
                        opponent = state.list_player[occupant_player_idx]
                        for omarble in opponent.list_marble:
                            if omarble.pos == action.pos_to:
                                omarble.pos = 72
                                omarble.is_save = False
                                break

                    m.pos = action.pos_to
                    # Once moved from start using a step card, it's no longer "save"
                    m.is_save = False
                    # Remove used card
                    player.list_card = [c for c in player.list_card if not (c.suit == action.card.suit and c.rank == action.card.rank)]
                    break

    def get_player_view(self, idx_player: int) -> GameState:
        # Masking not required for current tests
        pass


class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        if actions:
            return random.choice(actions)
        return None
