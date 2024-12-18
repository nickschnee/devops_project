import copy
import logging
import random
from enum import Enum
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from server.py.game import Game, Player

from typing import Any, Callable

def log_method_call(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to log method calls."""
    def wrapper(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
        logging.info(f"Calling method {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logging.info(f"Method {func.__name__} returned: {result}")
        return result
    return wrapper

class Card(BaseModel):
    """Represents a playing card with a suit and rank."""
    suit: str
    rank: str

    def __eq__(self, other: object) -> bool:
        """Check if two cards are equal based on suit and rank."""
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank

    def __lt__(self, other: 'Card') -> bool:
        """Compare two cards based on suit and rank."""
        if self.suit != other.suit:
            return self.suit < other.suit
        return self.rank < other.rank

    def __hash__(self) -> int:
        """Generate a hash value for the card."""
        return hash((self.suit, self.rank))

    def __str__(self) -> str:
        """Return a string representation of the card."""
        return f"Card(suit='{self.suit}', rank='{self.rank}')"

    def __repr__(self) -> str:
        """Return a string representation of the card."""
        return self.__str__()

class Marble(BaseModel):
    """Represents a marble with a position and save status."""
    pos: int
    is_save: bool

class PlayerState(BaseModel):
    """Represents the state of a player, including name, cards, and marbles."""
    name: str
    list_card: List[Card]
    list_marble: List[Marble]

class Action(BaseModel):
    """Represents an action in the game, including card, positions, and optional card swap."""
    card: Card
    pos_from: Optional[int]
    pos_to: Optional[int]
    card_swap: Optional[Card] = None

class GamePhase(str, Enum):
    """Enumeration of game phases."""
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'

class GameState(BaseModel):
    """Represents the state of the game, including players, cards, and game phase."""
    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
        Card(suit='♠', rank='2'), Card(suit='♥', rank='2'), Card(suit='♦', rank='2'), Card(suit='♣', rank='2'),
        Card(suit='♠', rank='3'), Card(suit='♥', rank='3'), Card(suit='♦', rank='3'), Card(suit='♣', rank='3'),
        Card(suit='♠', rank='4'), Card(suit='♥', rank='4'), Card(suit='♦', rank='4'), Card(suit='♣', rank='4'),
        Card(suit='♠', rank='5'), Card(suit='♥', rank='5'), Card(suit='♦', rank='5'), Card(suit='♣', rank='5'),
        Card(suit='♠', rank='6'), Card(suit='♥', rank='6'), Card(suit='♦', rank='6'), Card(suit='♣', rank='6'),
        Card(suit='♠', rank='7'), Card(suit='♥', rank='7'), Card(suit='♦', rank='7'), Card(suit='♣', rank='7'),
        Card(suit='♠', rank='8'), Card(suit='♥', rank='8'), Card(suit='♦', rank='8'), Card(suit='♣', rank='8'),
        Card(suit='♠', rank='9'), Card(suit='♥', rank='9'), Card(suit='♦', rank='9'), Card(suit='♣', rank='9'),
        Card(suit='♠', rank='10'), Card(suit='♥', rank='10'), Card(suit='♦', rank='10'), Card(suit='♣', rank='10'),
        Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(suit='♦', rank='J'), Card(suit='♣', rank='J'),
        Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(suit='♦', rank='Q'), Card(suit='♣', rank='Q'),
        Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(suit='♦', rank='K'), Card(suit='♣', rank='K'),
        Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(suit='♦', rank='A'), Card(suit='♣', rank='A'),
        Card(suit='', rank='JKR'), Card(suit='', rank='JKR'), Card(suit='', rank='JKR')
    ] * 2


    cnt_player: int = 4
    phase: GamePhase = GamePhase.RUNNING# Changed default from SETUP to RUNNING
    cnt_round: int = 1 # Changed default from 0 to 1
    bool_game_finished: bool = False
    bool_card_exchanged: bool = False
    idx_player_started: int = 0
    idx_player_active: int = 0
    list_player: List[PlayerState] = []
    list_card_draw: List[Card] = []
    list_card_discard: List[Card] = []
    card_active: Optional[Card] = None
    seven_steps_remaining: Optional[int] = None
    seven_backup_state: Optional['GameState'] = None
    seven_player_idx: Optional[int] = None

class Dog(Game):
    def __init__(self) -> None:
        """Game initialization"""
        super().__init__()
        self.CNT_PLAYERS = 4
        self.CNT_STEPS = 64
        self.CNT_BALLS = 4
        
        # Define constants
        self.KENNEL_POSITIONS = {
            0: [64, 65, 66, 67],
            1: [68, 69, 70, 71],
            2: [72, 73, 74, 75],
            3: [76, 77, 78, 79]
        }
        
        self.START_POSITION = {
            0: 0,
            1: 16,
            2: 32,
            3: 48
        }
        
        self._state = None
        self.reset()

    # State Management Methods
    def reset(self) -> None:
        """Reset the game state."""
        # Initialize cards
        all_cards = list(GameState.LIST_CARD)
        random.shuffle(all_cards)
        
        # Always start with 6 cards per player in initial state
        cards_per_player = 6
        
        self._state = GameState(
            cnt_player=4,
            phase=GamePhase.RUNNING,  # Start in RUNNING phase
            cnt_round=1,              # Start at round 1
            bool_game_finished=False,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=[
                PlayerState(
                    name=f"Player {i}",
                    list_card=all_cards[i * cards_per_player:(i + 1) * cards_per_player],
                    list_marble=[
                        Marble(pos=64 + i * 4 + j, is_save=False) 
                        for j in range(4)
                    ]
                )
                for i in range(4)
            ],
            list_card_draw=all_cards[24:],  # 4 players * 6 cards = 24 cards dealt
            list_card_discard=[],
            card_active=None,
            seven_steps_remaining=None,
            seven_backup_state=None,
            seven_player_idx=None
        )

    def apply_action(self, action: Optional[Action]) -> None:
        """Apply a given action to the game state."""
        state = self._state
        active_player_idx = state.idx_player_active
        player = state.list_player[active_player_idx]
        
        # Handle round transitions when action is None
        if action is None:
            # SEVEN card handling comes first
            if state.card_active and state.card_active.rank == '7':
                state.card_active = None
                state.seven_steps_remaining = None
                state.seven_backup_state = None
                state.seven_player_idx = None
                state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
                return

            # Check if player needs to fold cards
            if not self.get_list_action():
                player.list_card = []
                
            # Handle round transitions
            if state.idx_player_active == 0:
                # Handle card exchange at beginning of round 1
                if state.cnt_round == 1 and not state.bool_card_exchanged:
                    state.bool_card_exchanged = True
                    state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
                    return
                    
                # Check if all players have played their cards
                all_cards_played = all(len(p.list_card) == 0 for p in state.list_player)
                
                if all_cards_played:
                    # Special handling for round 1 to 2 transition
                    if state.cnt_round == 1:
                        if state.bool_card_exchanged:
                            state.cnt_round = 2
                    else:
                        state.cnt_round += 1
                    
                    # Get cards for new round
                    cards_per_player = self.get_cards_per_round(state.cnt_round)
                    
                # Rest of the card dealing logic remains the same...
                    
                    # Clear and deal new cards
                    for p in state.list_player:
                        state.list_card_discard.extend(p.list_card)
                        p.list_card = []
                            
                    # Reshuffle if needed
                    if len(state.list_card_draw) < cards_per_player * 4:
                        state.list_card_draw.extend(state.list_card_discard)
                        state.list_card_discard = []
                        random.shuffle(state.list_card_draw)
                            
                    # Deal new cards
                    for p in state.list_player:
                        for _ in range(cards_per_player):
                            if state.list_card_draw:
                                card = state.list_card_draw.pop(0)
                                p.list_card.append(card)
            
            # Move to next player
            state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
            return


    
    
        # Initialize 7-card sequence
        if action.card.rank == '7' and state.seven_steps_remaining is None:
            state.card_active = action.card
            state.seven_steps_remaining = 7
            state.seven_backup_state = copy.deepcopy(state)
            state.seven_player_idx = active_player_idx
            
            # If there's an immediate move, process it
            if action.pos_from is not None and action.pos_to is not None:
                steps = self.calculate_steps(action.pos_from, action.pos_to)
                if steps <= state.seven_steps_remaining:
                    self.move_marble(action.pos_from, action.pos_to, active_player_idx)
                    state.seven_steps_remaining -= steps
                    
                    if state.seven_steps_remaining <= 0:
                        # Remove card and reset seven state
                        player.list_card = [c for c in player.list_card if not (c.suit == action.card.suit and c.rank == action.card.rank)]
                        state.seven_steps_remaining = None
                        state.seven_backup_state = None
                        state.seven_player_idx = None
                        state.card_active = None
                        state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
            return

        # Handle subsequent 7 card moves
        if state.card_active and state.card_active.rank == '7' and state.seven_steps_remaining is not None:
            if action.pos_from is not None and action.pos_to is not None:
                steps = self.calculate_steps(action.pos_from, action.pos_to)
                if steps <= state.seven_steps_remaining:
                    self.move_marble(action.pos_from, action.pos_to, active_player_idx)
                    state.seven_steps_remaining -= steps
                    
                    if state.seven_steps_remaining <= 0:
                        # Remove card and reset seven state
                        player.list_card = [c for c in player.list_card if not (c.suit == state.card_active.suit and c.rank == state.card_active.rank)]
                        state.seven_steps_remaining = None
                        state.seven_backup_state = None
                        state.seven_player_idx = None
                        state.card_active = None
                        state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
            return

        # Joker transform action
        elif action.card.rank == 'JKR':
            if action.pos_from == 64 and action.pos_to == 0:
                # Handle moving from start to position 0
                for m in player.list_marble:
                    if m.pos == 64:
                        # Check if position 0 is occupied
                        occupant_idx = self.get_player_who_occupies_pos(0)
                        if occupant_idx is not None and occupant_idx != active_player_idx:
                            # Send opponent marble to kennel
                            opponent = state.list_player[occupant_idx]
                            for om in opponent.list_marble:
                                if om.pos == 0:
                                    om.pos = 72
                                    om.is_save = False
                        
                        m.pos = 0
                        m.is_save = True
                        break
                # Remove only one Joker
                for i, card in enumerate(player.list_card):
                    if card.rank == 'JKR':
                        player.list_card.pop(i)
                        break
                state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
                
            elif action.pos_from == -1 and action.pos_to == -1 and action.card_swap is not None:
                # Transform only one Joker into another card
                for i, card in enumerate(player.list_card):
                    if card.rank == 'JKR':
                        player.list_card[i] = copy.deepcopy(action.card_swap)
                        state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
                        break
            return

        elif action.pos_from == 64 and action.pos_to == 0 and action.card.rank in ['A', 'K']:
            """Start action."""
            occupant_player_idx = self.get_player_who_occupies_pos(0)
            if occupant_player_idx is not None and occupant_player_idx != active_player_idx:
                opponent = state.list_player[occupant_player_idx]
                for m in opponent.list_marble:
                    if m.pos == 0:
                        m.pos = 72
                        m.is_save = False
                        break
            for m in player.list_marble:
                if m.pos == 64:
                    m.pos = 0
                    m.is_save = True
                    player.list_card = [c for c in player.list_card if not (c.suit == action.card.suit and c.rank == action.card.rank)]
                    state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
                    break
            return

        elif action.card.rank == 'J':
            """Swap action."""
            # Find marbles to swap
            from_marble = None
            to_marble = None
            
            # Find the marbles to swap
            for p in state.list_player:
                for m in p.list_marble:
                    if m.pos == action.pos_from:
                        from_marble = m
                    elif m.pos == action.pos_to:
                        to_marble = m

            # Only swap if both marbles exist and neither is in finish
            if from_marble and to_marble and \
            not self.is_finish_field(from_marble.pos) and \
            not self.is_finish_field(to_marble.pos):
                # Perform the swap
                from_marble.pos, to_marble.pos = to_marble.pos, from_marble.pos
                # Update save status
                from_marble.is_save = (from_marble.pos == 0)
                to_marble.is_save = (to_marble.pos == 0)
                # Remove the card and advance turn
                for i, card in enumerate(player.list_card):
                    if card.rank == 'J' and card.suit == action.card.suit:
                        player.list_card.pop(i)
                        break
                state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
            return

        else:
            """Normal movement."""
            for m in player.list_marble:
                if m.pos == action.pos_from:
                    if action.pos_to is not None:
                        # Check if moving to finish area
                        if self.is_finish_position(action.pos_to, active_player_idx):
                            # Check if path to finish is clear
                            for other_marble in player.list_marble:
                                if other_marble.pos < action.pos_to and \
                                other_marble != m and \
                                self.is_finish_position(other_marble.pos, active_player_idx):
                                    # Can't overtake in finish area
                                    return

                        # Handle marble at destination
                        occupant_player_idx = self.get_player_who_occupies_pos(action.pos_to)
                        if occupant_player_idx is not None:
                            if occupant_player_idx != active_player_idx:
                                # Handle opponent's marble
                                opponent = state.list_player[occupant_player_idx]
                                for omarble in opponent.list_marble:
                                    if omarble.pos == action.pos_to and not omarble.is_save:
                                        omarble.pos = 72  # Send to kennel zone
                                        omarble.is_save = False
                            else:
                                # Handle own marble
                                for own_marble in player.list_marble:
                                    if own_marble.pos == action.pos_to:
                                        own_marble.pos = 64  # Send to start
                                        own_marble.is_save = False

                        # Move the marble
                        m.pos = action.pos_to
                        m.is_save = (action.pos_to == 0)

                        if action.pos_from == 0:
                            m.is_save = False

                        # Remove the used card
                        player.list_card = [c for c in player.list_card if not (c.suit == action.card.suit and c.rank == action.card.rank)]
                        state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
                        break
                     
        
        
        
        
        

    def get_state(self) -> GameState:
        """Return the current game state."""
        return self._state

    def set_state(self, state: GameState) -> None:
        """Set the game state to a new state."""
        self._state = state

    def print_state(self) -> None:
        """Print the current game state."""
        logging.info(self._state)

    # Round Management Methods
    def next_round(self) -> None:
        """Handle transition to next round."""
        self._state.cnt_round += 1
        self._state.bool_card_exchanged = False
        
        # Clear all player hands
        for player in self._state.list_player:
            player.list_card = []
        
        cards_per_player = self.get_cards_per_round(self._state.cnt_round)
        all_cards = GameState.LIST_CARD.copy()
        random.shuffle(all_cards)
        
        for i in range(4):
            start_idx = i * cards_per_player
            end_idx = start_idx + cards_per_player
            self._state.list_player[i].list_card = all_cards[start_idx:end_idx]
        
        self._state.list_card_draw = all_cards[4 * cards_per_player:]
        self._state.list_card_discard = []

    def get_cards_per_round(self, round_number: int) -> int:
        """Return the number of cards to deal per player for a given round."""
        cards_per_round = {
            0: 6,
            1: 6,
            2: 5,
            3: 4,
            4: 3,
            5: 2,
            6: 6
        }
        return cards_per_round.get(round_number, 6)

    # Card Management Methods
    def reshuffle_cards(self, state):
        """Reshuffle discard pile into draw pile"""
        if not state.list_card_draw and state.list_card_discard:
            state.list_card_draw.extend(state.list_card_discard)
            state.list_card_discard = []
            random.shuffle(state.list_card_draw)

    def deal_cards(self):
        """Deal cards to players based on round number"""
        num_cards = self.get_cards_per_round(self._state.cnt_round)
        
        for player in self._state.list_player:
            player.list_card = []
            for _ in range(num_cards):
                if self._state.list_card_draw:
                    player.list_card.append(self._state.list_card_draw.pop(0))

    # Position and Movement Methods
    def get_player_who_occupies_pos(self, position: int) -> Optional[int]:
        """Return the index of the player who occupies a given position."""
        for i, p in enumerate(self._state.list_player):
            for m in p.list_marble:
                if m.pos == position:
                    return i
        return None

    def is_finish_field(self, pos: int) -> bool:
        """Check if a given position is in the finish area."""
        return 72 <= pos < 80

    def is_path_clear(self, pos_from: int, pos_to: int) -> bool:
        """Check if the path between positions is clear."""
        if pos_from >= pos_to:
            return False

        for pos in range(pos_from + 1, pos_to):
            occupant_idx = self.get_player_who_occupies_pos(pos)
            if occupant_idx is not None:
                for player in self._state.list_player:
                    for marble in player.list_marble:
                        if marble.pos == pos:
                            return False
        return True

    def is_path_to_finish_clear(self, pos_from: int, pos_to: int) -> bool:
        """Check if the path to finish is clear."""
        if pos_from < 64:
            for pos in range(pos_from + 1, 64):
                if self.get_player_who_occupies_pos(pos) is not None:
                    return False
        
        if self.is_finish_field(pos_to):
            for pos in range(72, pos_to):
                if self.get_player_who_occupies_pos(pos) is not None:
                    return False
        
        return True

    def can_move_to_finish(self, pos_from: int, pos_to: int, active_player_idx: int) -> bool:
        """Check if a marble can move to a finish position."""
        if not self.is_finish_field(pos_to):
            return False
            
        if not self.is_path_to_finish_clear(pos_from, pos_to):
            return False
            
        occupant = self.get_player_who_occupies_pos(pos_to)
        if occupant is not None and occupant == active_player_idx:
            return False
            
        return True

    def is_finish_position(self, pos: int, player_idx: int) -> bool:
        """Check if position is in finish area for given player"""
        finish_start = self.CNT_STEPS + player_idx * self.CNT_BALLS * 2
        finish_end = finish_start + self.CNT_BALLS
        return finish_start <= pos < finish_end

    def is_marble_in_finish(self, marble: Marble, player_idx: int) -> bool:
        """Check if a marble is in the finish area for a given player."""
        finish_start = self.CNT_STEPS + player_idx * self.CNT_BALLS * 2
        finish_end = finish_start + self.CNT_BALLS
        return finish_start <= marble.pos < finish_end

    # Special Game State Methods
    def start_game_state_at_round_2(self):
        """Set up game state for round 2."""
        all_cards = GameState.LIST_CARD.copy()
        random.shuffle(all_cards)
        
        self._state = GameState(
            cnt_player=4,
            phase=GamePhase.RUNNING,
            cnt_round=2,
            bool_game_finished=False,
            bool_card_exchanged=True,
            idx_player_started=0,
            idx_player_active=1,
            list_player=[],
            list_card_draw=[],
            list_card_discard=[],
            card_active=None,
            seven_steps_remaining=None,
            seven_backup_state=None,
            seven_player_idx=None
        )
        
        for i in range(4):
            start_idx = i * 5
            end_idx = start_idx + 5
            player_cards = all_cards[start_idx:end_idx]
            player_marbles = [Marble(pos=64 + j, is_save=False) for j in range(4)]
            
            player = PlayerState(
                name=f"Player {i}",
                list_card=player_cards,
                list_marble=player_marbles
            )
            self._state.list_player.append(player)
        
        self._state.list_card_draw = all_cards[20:]

    def get_list_action(self) -> List[Action]:
        """Return a list of possible actions for the active player."""
        state = self._state
        actions = []
        active_player_idx = state.idx_player_active
        player = state.list_player[active_player_idx]

        # Define move options
        move_options = {
            'A': [1, 11],
            '2': [2],
            '3': [3],
            '4': [4, -4],
            '5': [5],
            '6': [6],
            '7': [1, 2, 3, 4, 5, 6, 7],
            '8': [8],
            '9': [9],
            '10': [10],
            'Q': [12],
            'K': [13],
            'JKR': []  # Special handling for Joker
        }

        def is_path_blocked(pos_from: int, pos_to: int) -> bool:
            """Check if path is blocked by any saved marbles."""
            if pos_from >= pos_to:
                return True
            for pos in range(pos_from + 1, pos_to + 1):
                pos_check = pos % 64
                occupant = self.get_player_who_occupies_pos(pos_check)
                if occupant is not None:
                    for m in state.list_player[occupant].list_marble:
                        if m.pos == pos_check and m.is_save:
                            return True
            return False

        # Card exchange at beginning of round
        if not state.bool_card_exchanged:
            for card in player.list_card:
                action = Action(card=card, pos_from=None, pos_to=None)
                if action not in actions:
                    actions.append(action)
            return actions

        # Check if all marbles are in finish
        all_marbles_in_finish = True
        for marble in player.list_marble:
            if not self.is_finish_field(marble.pos):
                all_marbles_in_finish = False
                break

        # If all marbles are in finish, allow moving partner's marbles
        if all_marbles_in_finish:
            partner_idx = (active_player_idx + 2) % 4
            partner = state.list_player[partner_idx]
            
            for card in player.list_card:
                if card.rank in move_options:
                    steps_list = move_options[card.rank]
                    for marble in partner.list_marble:
                        if 0 <= marble.pos < 64 and not marble.is_save:
                            for step in steps_list:
                                new_pos = (marble.pos + step) % 64
                                if not is_path_blocked(marble.pos, new_pos):
                                    actions.append(Action(card=card, pos_from=marble.pos, pos_to=new_pos))
            
            # Handle Joker cards for partner support
            for card in player.list_card:
                if card.rank == 'JKR':
                    for marble in partner.list_marble:
                        if marble.pos >= 64:  # Marble in kennel
                            actions.append(Action(card=card, pos_from=marble.pos, pos_to=0))
                        elif 0 <= marble.pos < 64:  # Marble on board
                            for suit in ['♠', '♥', '♦', '♣']:
                                actions.append(Action(card=card, pos_from=None, pos_to=None, card_swap=Card(suit=suit, rank='A')))
                                actions.append(Action(card=card, pos_from=None, pos_to=None, card_swap=Card(suit=suit, rank='K')))

            if actions:  # If we found partner actions, return them
                return actions

        # Special handling for seven card moves
        
        if state.card_active and state.card_active.rank == '7' and state.seven_steps_remaining is not None:
            for marble in player.list_marble:
                if not self.is_finish_field(marble.pos):  # Allow moves for marbles not in finish
                    for steps in range(1, state.seven_steps_remaining + 1):
                        new_pos = self._calculate_new_position(marble.pos, steps, active_player_idx)
                        if new_pos != -1:  # Valid position
                            # Check if path is clear
                            if marble.pos < 64 and new_pos < 64:  # Both positions on main board
                                if not is_path_blocked(marble.pos, new_pos):
                                    actions.append(Action(card=state.card_active, pos_from=marble.pos, pos_to=new_pos))
                            elif self.is_finish_field(new_pos):  # Moving to finish
                                if self.can_move_to_finish(marble.pos, new_pos, active_player_idx):
                                    actions.append(Action(card=state.card_active, pos_from=marble.pos, pos_to=new_pos))
            return actions

        occupant_player_idx = self.get_player_who_occupies_pos(0)
        start_occupied_by_self = (occupant_player_idx == active_player_idx)
        has_marble_at_64 = any(m.pos == 64 for m in player.list_marble)

        # If card_active is set, only produce actions for card_active
        if state.card_active is not None:
            active_card = state.card_active
            # START action if applicable
            if active_card.rank in ['A', 'K', 'JKR'] and not start_occupied_by_self and has_marble_at_64:
                actions.append(Action(card=active_card, pos_from=64, pos_to=0))
            # Normal moves if in move_options
            if active_card.rank in move_options:
                steps_list = move_options[active_card.rank]
                for marble in player.list_marble:
                    if 0 <= marble.pos < 64:
                        for step in steps_list:
                            new_pos = (marble.pos + step) % 64
                            if not is_path_blocked(marble.pos, new_pos):
                                actions.append(Action(card=active_card, pos_from=marble.pos, pos_to=new_pos))
            return actions

        # START actions (A, K)
        for card in player.list_card:
            if card.rank in ['A', 'K'] and not start_occupied_by_self and has_marble_at_64:
                # Check for opponents on the start position
                opponent_on_start = False
                for p_idx, p in enumerate(state.list_player):
                    if p_idx != active_player_idx:
                        for marble in p.list_marble:
                            if marble.pos == 0 and not marble.is_save:
                                opponent_on_start = True
                                break
                        if opponent_on_start:
                            break

                # Add start action with or without opponent consideration
                actions.append(Action(card=card, pos_from=64, pos_to=0))

        # NORMAL MOVE actions for numeric cards
        for card in player.list_card:
            if card.rank in move_options:
                steps_list = move_options[card.rank]
                for marble in player.list_marble:
                    if 0 <= marble.pos < 64:
                        for step in steps_list:
                            new_pos = (marble.pos + step) % 64
                            if not is_path_blocked(marble.pos, new_pos):
                                actions.append(Action(card=card, pos_from=marble.pos, pos_to=new_pos))

        # Joker transformations
        jokers = [c for c in player.list_card if c.rank == 'JKR']
        if jokers:
            joker_card = jokers[0]
            
            if state.card_active is None:
                if has_marble_at_64:
                    actions.append(Action(card=joker_card, pos_from=64, pos_to=0))
                
                # Allow transforming into all suits
                for suit in ['♠', '♥', '♦', '♣']:
                    for rank in ['A', 'K']:
                        actions.append(Action(
                            card=joker_card,
                            pos_from=None,
                            pos_to=None,
                            card_swap=Card(suit=suit, rank=rank)
                        ))
            elif state.card_active.rank == 'JKR':
                if has_marble_at_64:
                    actions.append(Action(card=joker_card, pos_from=64, pos_to=0))

        # J (Jack) card swap actions
        for card in player.list_card:
            if card.rank == 'J':
                # Gather all marbles on board
                all_marbles_positions = []
                for p_idx, p in enumerate(state.list_player):
                    for m in p.list_marble:
                        if 0 <= m.pos < 64:
                            all_marbles_positions.append((p_idx, m.pos, m.is_save))

                our_marbles = [(p_idx, pos, is_save)
                            for (p_idx, pos, is_save) in all_marbles_positions
                            if p_idx == active_player_idx]

                # Check if any opponent non-save marbles exist
                opponent_swaps_available = False
                for (_, pos_from, _) in our_marbles:
                    for (p_idx_to, pos_to, save_to) in all_marbles_positions:
                        if pos_from != pos_to and p_idx_to != active_player_idx and not save_to:
                            opponent_swaps_available = True
                            break
                    if opponent_swaps_available:
                        break

                # Add actions
                for (_, pos_from, _) in our_marbles:
                    for (p_idx_to, pos_to, save_to) in all_marbles_positions:
                        if pos_from != pos_to:
                            if opponent_swaps_available:
                                # Only opponent non-save swaps
                                if p_idx_to != active_player_idx and not save_to:
                                    actions.append(Action(card=card, pos_from=pos_from, pos_to=pos_to))
                            else:
                                # No opponent swaps available -> self-swaps & non-save opp
                                if p_idx_to == active_player_idx or not save_to:
                                    actions.append(Action(card=card, pos_from=pos_from, pos_to=pos_to))

        # Remove duplicates
        unique_actions = []
        seen = set()
        for action in actions:
            action_tuple = (
                str(action.card),
                action.pos_from,
                action.pos_to,
                str(action.card_swap) if action.card_swap else None
            )
            if action_tuple not in seen:
                seen.add(action_tuple)
                unique_actions.append(action)

        return unique_actions




       
                                            
    def calculate_steps(self, pos_from: int, pos_to: int) -> int:
        """Calculate number of steps between positions"""
        if pos_from < 64 and pos_to > 71:  # Moving to finish
            return 5
        elif self.is_finish_field(pos_from) and self.is_finish_field(pos_to):
            return abs(pos_to - pos_from)
        else:
            return (pos_to - pos_from) if pos_to > pos_from else (pos_to + 64 - pos_from)

    def move_marble(self, pos_from: int, pos_to: int, player_idx: int) -> None:
        """Move a marble and handle collisions"""
        state = self._state
        player = state.list_player[player_idx]
        
        # Handle marble at destination
        occupant_idx = self.get_player_who_occupies_pos(pos_to)
        if occupant_idx is not None:
            occupant = state.list_player[occupant_idx]
            for m in occupant.list_marble:
                if m.pos == pos_to:
                    if occupant_idx != player_idx:
                        m.pos = 72  # Send to kennel
                    else:
                        m.pos = 64  # Send to start
                    m.is_save = False
        
        # Move the marble
        for m in player.list_marble:
            if m.pos == pos_from:
                m.pos = pos_to
                m.is_save = (pos_to == 0)
                if pos_from == 0:
                    m.is_save = False
                break
                
    def _calculate_new_position(self, current_pos: int, steps: int, player_idx: int) -> int:
        """Calculate new position after moving steps forward."""
        if current_pos >= 64:  # In finish area
            new_pos = current_pos + steps
            if new_pos < 80:  # Check within finish area
                # Check if position is blocked by own marble
                if self.get_player_who_occupies_pos(new_pos) == player_idx:
                    return -1
                return new_pos
            return -1

        # On main board
        new_pos = (current_pos + steps) % 64
        
        # Check if crossing finish line
        start_pos = self.START_POSITION[player_idx]
        if current_pos <= start_pos and new_pos > start_pos:
            # Calculate finish position
            steps_past_start = new_pos - start_pos
            finish_pos = 72 + (player_idx * 4) + steps_past_start - 1
            if finish_pos < 72 + (player_idx + 1) * 4:  # Within player's finish area
                return finish_pos
            return -1
            
        return new_pos

    def get_player_view(self, idx_player: int) -> GameState:
        """Return the game state from the perspective of a specific player."""
        return copy.deepcopy(self._state)



    def compute_pos_to_for_7(self, pos_from: int, steps: int) -> Optional[int]:
        """
        Compute the target position for a 7-card move, considering finish area.
        Returns None if the move would be invalid.
        """
        if pos_from < 64:  # If on main board
            if pos_from + steps <= 63:  # Stay on board
                return pos_from + steps
            else:  # Enter finish area
                remaining = steps - (63 - pos_from)
                finish_pos = 72 + remaining - 1
                if finish_pos < 80:  # Check within finish area
                    return finish_pos
                return None
        elif self.is_finish_field(pos_from):  # If in finish area
            new_pos = pos_from + steps
            if new_pos < 80:  # Check within finish area
                return new_pos
            return None
        return None

    def is_move_7_valid(self, marble_idx: int, pos_from: int, pos_to: int) -> bool:
        """Check if a 7-card move is valid."""
        if pos_to is None:
            return False

        # Check if path is clear (no blocked positions)
        if pos_from < 64 and pos_to < 64:
            # Check normal track path
            for pos in range(pos_from + 1, pos_to):
                if self.get_player_who_occupies_pos(pos) is not None:
                    return False
        elif pos_from < 64 and self.is_finish_field(pos_to):
            # Check path to finish
            for pos in range(pos_from + 1, 64):
                if self.get_player_who_occupies_pos(pos) is not None:
                    return False
            # Check finish path
            for pos in range(72, pos_to):
                if self.get_player_who_occupies_pos(pos) is not None:
                    return False
        elif self.is_finish_field(pos_from):
            # Check finish path
            for pos in range(pos_from + 1, pos_to):
                if self.get_player_who_occupies_pos(pos) is not None:
                    return False

        return True

    def get_joker_actions(self, player: PlayerState) -> List[Action]:
        """Generate actions for JOKER card."""
        actions = []
        for suit in ['♠', '♥', '♦', '♣']:
            actions.append(Action(card=Card(suit='', rank='JKR'), pos_from=64, pos_to=0))  # Move out of kennel
            actions.append(Action(card=Card(suit='', rank='JKR'), pos_from=None, pos_to=None, card_swap=Card(suit=suit, rank='A')))
            actions.append(Action(card=Card(suit='', rank='JKR'), pos_from=None, pos_to=None, card_swap=Card(suit=suit, rank='K')))
        return actions

class RandomPlayer(Player):
    """Represents a random player who selects actions randomly."""
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """Select a random action from the list of possible actions."""
        if actions:
            return random.choice(actions)
        return None