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
    # Define a single deck of 55 cards (will be doubled in reset())
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
    ]
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

    def reset(self) -> None:
        """Reset the game state."""
        # Create exactly 110 cards (2 decks of 55 cards each)
        all_cards = []
        for _ in range(2):  # Two decks
            for card in GameState.LIST_CARD:
                all_cards.append(copy.deepcopy(card))
        
        # Verify we have exactly 110 cards
        assert len(all_cards) == 110, f"Deck initialization error: got {len(all_cards)} cards instead of 110"
        random.shuffle(all_cards)
        
        # Always start with 6 cards per player in initial state
        cards_per_player = 6
        
        self._state = GameState(
            cnt_player=4,
            phase=GamePhase.RUNNING,
            cnt_round=1,              
            bool_game_finished=False,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=[
                PlayerState(
                    name=f"Player {i}",
                    list_card=all_cards[i * cards_per_player:(i + 1) * cards_per_player],
                    list_marble=[
                        Marble(pos=self.KENNEL_POSITIONS[i][j], is_save=False) 
                        for j in range(4)
                    ]
                )
                for i in range(4)
            ],
            list_card_draw=all_cards[24:],  
            list_card_discard=[],
            card_active=None,
            seven_steps_remaining=None,
            seven_backup_state=None,
            seven_player_idx=None
        )

        # Validate total card count
        total_cards = len(self._state.list_card_draw)
        for player in self._state.list_player:
            total_cards += len(player.list_card)
        
        assert total_cards == 110, f"Total card count error: {total_cards} cards instead of 110"


    def apply_action(self, action: Optional[Action]) -> None:
        state = self._state

        def validate_total_cards():
            """Ensure total cards remain at 110."""
            total_cards = len(state.list_card_draw) + len(state.list_card_discard)
            for p in state.list_player:
                total_cards += len(p.list_card)
            
            if total_cards != 110:
                logging.warning(f"Card count deviation: {total_cards} cards instead of 110")
                # Attempt to correct by removing excess from discard pile
                if total_cards > 110:
                    excess = total_cards - 110
                    state.list_card_discard = state.list_card_discard[:-excess]

        if action is None:
            if not state.bool_card_exchanged:
                active_player = state.list_player[state.idx_player_active]
                cards_needed = 6 - len(active_player.list_card)
                
                if cards_needed > 0:
                    # Reshuffle if draw pile is empty
                    if len(state.list_card_draw) == 0 and len(state.list_card_discard) > 0:
                        state.list_card_draw = state.list_card_discard[:]
                        state.list_card_discard = []
                        random.shuffle(state.list_card_draw)
                    
                    # Draw cards
                    while len(active_player.list_card) < 6 and len(state.list_card_draw) > 0:
                        active_player.list_card.append(state.list_card_draw.pop())
                    
                    # Validate card count after drawing
                    validate_total_cards()
                    if self.check_game_finished():
                        state.phase = GamePhase.FINISHED
                        state.bool_game_finished = True
                        return

                    # Move to next player
                    state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
                    
                    # Check if all players have their cards
                    all_players_have_cards = all(len(player.list_card) == 6 for player in state.list_player)
                    
                    if all_players_have_cards:
                        state.bool_card_exchanged = True
                        state.idx_player_active = state.idx_player_started
                    return

            # Handle SEVEN card passing
            if state.card_active and state.card_active.rank == '7':
                if state.seven_backup_state:
                    self._state = copy.deepcopy(state.seven_backup_state)
                    state = self._state
                state.card_active = None
                state.seven_steps_remaining = None
                state.seven_backup_state = None
                state.seven_player_idx = None
                state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
                return
                    
            # Handle regular fold
            player = state.list_player[state.idx_player_active]
            if len(player.list_card) > 0:
                state.list_card_discard.extend(player.list_card)
                player.list_card = []
                
            state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
            
            # Check if round is complete
            if state.idx_player_active == state.idx_player_started:
                all_cards_played = all(len(p.list_card) == 0 for p in state.list_player)
                if all_cards_played:
                    self._start_new_round()
            return

        # Handle card exchange at beginning of round
        if not state.bool_card_exchanged and action.pos_from is None and action.pos_to is None:
            self._handle_card_exchange(action.card)
            return

        # Handle Joker card transformation
        if action.card_swap is not None:
            state.card_active = action.card_swap
            player = state.list_player[state.idx_player_active]
            player.list_card.remove(action.card)
            return

        # Handle regular moves
        player = state.list_player[state.idx_player_active]
        
        # Move marble
        if action.pos_from is not None and action.pos_to is not None:
            if action.pos_from >= 64 and action.pos_from < 68:
                self._handle_marble_capture(action.pos_to)
                
                # Move marble out of kennel
                for marble in player.list_marble:
                    if marble.pos == action.pos_from:
                        marble.pos = action.pos_to
                        marble.is_save = True if action.pos_to % 16 == 0 else False
                        break
                        
                # Remove the used card
                if state.card_active is None:
                    state.card_active = action.card
                    player.list_card.remove(action.card)
                
                # Move to next player
                state.card_active = None
                state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
                return
                
            # Handle SEVEN card
            if action.card.rank == '7':
                if state.card_active is None:
                    # Starting new SEVEN sequence
                    state.card_active = action.card
                    state.seven_steps_remaining = 7
                    state.seven_backup_state = copy.deepcopy(state)
                    state.seven_player_idx = state.idx_player_active
                    player.list_card.remove(action.card)
                
                # Calculate steps used
                if self.is_finish_field(action.pos_to):
                    if self.is_finish_field(action.pos_from):
                        steps_used = action.pos_to - action.pos_from
                    else:
                        # Moving into finish area
                        finish_entry = state.idx_player_active * 16
                        steps_to_entry = (finish_entry - action.pos_from + 1) % 64
                        steps_used = 5  # Fixed cost for entering finish
                else:
                    steps_used = (action.pos_to - action.pos_from) % 64
                
                # Check if move is valid
                if steps_used <= state.seven_steps_remaining:
                    # Move the marble first
                    for marble in player.list_marble:
                        if marble.pos == action.pos_from:
                            # Handle captures before moving
                            if not self.is_finish_field(action.pos_from):
                                for pos in range(action.pos_from + 1, action.pos_to + 1):
                                    check_pos = pos % 64
                                    for p in state.list_player:
                                        for other_marble in p.list_marble:
                                            if other_marble.pos == check_pos and not other_marble.is_save:
                                                # Send marble back to kennel
                                                player_idx = state.list_player.index(p)
                                                kennel_base = 64 + (player_idx * 8)
                                                for kennel_pos in range(kennel_base, kennel_base + 4):
                                                    if all(m.pos != kennel_pos for m in p.list_marble):
                                                        other_marble.pos = kennel_pos
                                                        other_marble.is_save = False
                                                        break
                            
                            # Move the marble
                            marble.pos = action.pos_to
                            if self.is_finish_field(action.pos_to):
                                marble.is_save = True
                            else:
                                marble.is_save = True if action.pos_to % 16 == 0 else False
                            break
                    
                    # Update remaining steps
                    state.seven_steps_remaining -= steps_used
                    
                    # Keep card active between moves
                    if state.seven_steps_remaining > 0:
                        state.card_active = action.card
                    else:
                        # Complete SEVEN sequence
                        state.card_active = None
                        state.seven_steps_remaining = None
                        state.seven_backup_state = None
                        state.seven_player_idx = None
                        state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
                                               
            else:
                # Regular card move
                if state.card_active is None:
                    state.card_active = action.card
                    player.list_card.remove(action.card)
                
                # Handle Jack swaps
                if action.card.rank == 'J':
                    marble_from = None
                    marble_to = None
                    
                    for p in state.list_player:
                        for m in p.list_marble:
                            if m.pos == action.pos_from:
                                marble_from = m
                            elif m.pos == action.pos_to:
                                marble_to = m
                    
                    if marble_from and marble_to:
                        marble_from.pos, marble_to.pos = marble_to.pos, marble_from.pos
                else:
                    # Regular move
                    # First check for and handle captures at destination
                    for p in state.list_player:
                        if p != player:  # Don't capture own marbles
                            for marble in p.list_marble:
                                if marble.pos == action.pos_to and not marble.is_save:
                                    # Send marble back to kennel
                                    player_idx = state.list_player.index(p)
                                    kennel_base = 64 + (player_idx * 4)
                                    for kennel_pos in range(kennel_base, kennel_base + 4):
                                        if all(m.pos != kennel_pos for m in p.list_marble):
                                            marble.pos = kennel_pos
                                            marble.is_save = False
                                            break
                    
                    # Then move the active marble
                    for marble in player.list_marble:
                        if marble.pos == action.pos_from:
                            marble.pos = action.pos_to
                            marble.is_save = True if action.pos_to % 16 == 0 else False
                            break
                
                # Move to next player
                state.card_active = None
                state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player

    def _start_new_round(self) -> None:
        state = self._state
        state.cnt_round += 1
        state.bool_card_exchanged = False
        
        # Create a fresh deck of 110 cards
        all_cards = []
        for _ in range(2):  # Two decks
            for card in GameState.LIST_CARD:
                all_cards.append(copy.deepcopy(card))
        
        # Verify we have exactly 110 cards
        assert len(all_cards) == 110, f"Deck initialization error: got {len(all_cards)} cards instead of 110"
        random.shuffle(all_cards)
        
        # Clear all player hands
        for player in state.list_player:
            player.list_card = []
        
        # Reset draw and discard piles
        state.list_card_draw = all_cards
        state.list_card_discard = []
        
        # Deal new cards
        cards_per_player = self._get_cards_per_round(state.cnt_round)
        for i, player in enumerate(state.list_player):
            start_idx = i * cards_per_player
            end_idx = start_idx + cards_per_player
            player.list_card = state.list_card_draw[start_idx:end_idx]
        
        # Remove dealt cards from draw pile
        state.list_card_draw = state.list_card_draw[4 * cards_per_player:]
        
        # Reset round state
        state.card_active = None
        state.seven_steps_remaining = None
        state.seven_backup_state = None
        state.seven_player_idx = None
        
        # Update starting player
        state.idx_player_started = (state.idx_player_started + 1) % state.cnt_player
        state.idx_player_active = state.idx_player_started

        # Validate total card count
        total_cards = len(state.list_card_draw)
        for player in state.list_player:
            total_cards += len(player.list_card)
        
        assert total_cards == 110, f"Total card count error in round {state.cnt_round}: {total_cards} cards instead of 110"      

    def _handle_marble_capture(self, pos_to: int, pos_from: Optional[int] = None) -> None:
        """Send marbles at pos_to back to their kennels."""
        state = self._state
        active_player = state.list_player[state.idx_player_active]

        # For Seven card, check all positions in the path
        if state.card_active and state.card_active.rank == '7' and pos_from is not None:
            start_pos = min(pos_from, pos_to)
            end_pos = max(pos_from, pos_to)
            
            # Check each position in the path
            for pos in range(start_pos + 1, end_pos + 1):
                pos = pos % 64  # Wrap around board
                for player in state.list_player:
                    for marble in player.list_marble:
                        if marble.pos == pos and not marble.is_save:
                            # Send marble back to kennel
                            marble.pos = 64 + (8 * state.list_player.index(player))
        else:
            # Regular capture at destination
            for player in state.list_player:
                for marble in player.list_marble:
                    if marble.pos == pos_to and not marble.is_save:
                        marble.pos = 64 + (8 * state.list_player.index(player))

    def _copy_game_state(self) -> GameState:
        """Create a deep copy of the current game state."""
        state = self._state
        return GameState(
            cnt_player=state.cnt_player,
            phase=state.phase,
            cnt_round=state.cnt_round,
            bool_game_finished=state.bool_game_finished,
            bool_card_exchanged=state.bool_card_exchanged,
            idx_player_started=state.idx_player_started,
            idx_player_active=state.idx_player_active,
            list_player=[
                PlayerState(
                    name=p.name,
                    list_card=p.list_card.copy(),
                    list_marble=[
                        Marble(pos=m.pos, is_save=m.is_save)
                        for m in p.list_marble
                    ]
                )
                for p in state.list_player
            ],
            list_card_draw=state.list_card_draw.copy(),
            list_card_discard=state.list_card_discard.copy(),
            card_active=state.card_active,
            seven_steps_remaining=state.seven_steps_remaining,
            seven_backup_state=None,  # Don't copy backup state
            seven_player_idx=state.seven_player_idx
        )        
    
    def _handle_card_exchange(self, card: Card) -> None:
        """Handle card exchange between partners."""
        state = self._state
        active_player = state.list_player[state.idx_player_active]
        partner_idx = (state.idx_player_active + 2) % 4
        partner = state.list_player[partner_idx]
        
        # Exchange cards
        active_player.list_card.remove(card)
        partner.list_card.append(card)
        
        # Move to next player
        state.idx_player_active = (state.idx_player_active + 1) % 4
        
        # Check if exchange is complete
        if state.idx_player_active == state.idx_player_started:
            state.bool_card_exchanged = True

    def _get_cards_per_round(self, round_num: int) -> int:
        """Return number of cards to deal per player for given round."""
        if round_num in [1, 6]:
            return 6
        elif round_num in [2, 3, 4]:
            return 5
        else:
            return 2  

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

    def get_cards_per_round(self, round_num: int) -> int:
        """Return number of cards to deal per player for given round."""
        if round_num in [1, 6]:
            return 6
        elif round_num in [2, 3, 4]:
            return 5
        elif round_num == 5:
            return 2
        else:
            return 6  

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

    def start_game_state_at_round_2(self):
        """Set up game state for round 2 with differing 'idx_player_started' and 'idx_player_active'."""
        # Create players with their marbles in kennels
        players = [
            PlayerState(
                name="Player 1",
                colour="BLUE",
                list_card=[],  # Empty cards initially
                list_marble=[
                    Marble(pos=64 + i, is_save=False) for i in range(4)
                ]
            ),
            PlayerState(
                name="Player 2", 
                colour="GREEN",
                list_card=[],
                list_marble=[
                    Marble(pos=72 + i, is_save=False) for i in range(4)
                ]
            ),
            PlayerState(
                name="Player 3",
                colour="RED", 
                list_card=[],
                list_marble=[
                    Marble(pos=80 + i, is_save=False) for i in range(4)
                ]
            ),
            PlayerState(
                name="Player 4",
                colour="YELLOW",
                list_card=[],
                list_marble=[
                    Marble(pos=88 + i, is_save=False) for i in range(4)
                ]
            )
        ]

        # Set up minimal game state for round 2
        self._state = GameState(
            cnt_player=4,
            phase=GamePhase.RUNNING,
            cnt_round=2,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=1,  # Different from started player
            list_player=players,
            list_card_draw=[],  # Empty draw pile
            list_card_discard=[],
            card_active=None
        )
                
    def check_game_finished(self) -> bool:
        """Check if any team has finished the game."""
        # Check each team (players across from each other)
        for team_start in [0, 1]:
            team_finished = True
            # Check both players in the team
            for player_idx in [team_start, (team_start + 2) % 4]:
                player = self._state.list_player[player_idx]
                # Check if all marbles are in finish area
                for marble in player.list_marble:
                    if marble.pos < 72 or marble.pos >= 80:  # Not in finish area
                        team_finished = False
                        break
                if not team_finished:
                    break
            if team_finished:
                return True
        return False
    
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
            'JKR': []  
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

            if actions:  
                return actions

        # Special handling for seven card moves
        if state.card_active and state.card_active.rank == '7' and state.seven_steps_remaining is not None:
            for marble in player.list_marble:
                pos_from = marble.pos
                
                # Handle moves in finish area
                if self.is_finish_field(pos_from):
                    # Calculate available steps in finish area
                    remaining_positions = 79 - pos_from
                    max_steps = min(state.seven_steps_remaining, remaining_positions)
                    
                    # Generate possible moves within finish area
                    for steps in range(1, max_steps + 1):
                        pos_to = pos_from + steps
                        if pos_to <= 79:  
                            actions.append(Action(
                                card=state.card_active,
                                pos_from=pos_from,
                                pos_to=pos_to
                            ))
                else:
                    # Regular board moves
                    for steps in range(1, state.seven_steps_remaining + 1):
                        # Try regular move on board
                        pos_to = (pos_from + steps) % 64
                        if not is_path_blocked(pos_from, pos_to):
                            actions.append(Action(
                                card=state.card_active,
                                pos_from=pos_from,
                                pos_to=pos_to
                            ))
                        
                        # Try move to finish area
                        finish_entry = active_player_idx * 16
                        if pos_from <= finish_entry < (pos_from + steps):
                            # Calculate finish position based on remaining steps
                            steps_to_entry = (finish_entry - pos_from + 1)
                            remaining_steps = steps - steps_to_entry
                            finish_pos = 77  # First position in finish area
                            if self.can_move_to_finish(pos_from, finish_pos, active_player_idx):
                                actions.append(Action(
                                    card=state.card_active,
                                    pos_from=pos_from,
                                    pos_to=finish_pos
                                ))
            
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
                    if 0 <= marble.pos < 64:  # Marble on main board
                        for step in steps_list:
                            # Calculate positions
                            pos_finish = self.CNT_STEPS + active_player_idx * self.CNT_BALLS * 2 + self.CNT_BALLS
                            pos_start = active_player_idx * int(self.CNT_STEPS / self.CNT_PLAYERS)
                            
                            # Try regular board moves
                            new_pos = (marble.pos + step) % 64
                            if not is_path_blocked(marble.pos, new_pos):
                                actions.append(Action(card=card, pos_from=marble.pos, pos_to=new_pos))
                            
                            # Try finish moves for each possible finish position
                            for i in range(4):
                                pos_to = pos_finish + i
                                
                                # Calculate required starting position using test logic
                                if pos_to - step < pos_finish:
                                    pos_from = (pos_start - step + (pos_to - pos_finish + 1) + self.CNT_STEPS) % self.CNT_STEPS
                                else:
                                    pos_from = pos_to - step
                                    
                                # If marble is in the calculated starting position, add finish move
                                if marble.pos == pos_from:
                                    # Check if finish position is empty
                                    if all(not any(m.pos == pos_to for m in p.list_marble) 
                                        for p in state.list_player):
                                        actions.append(Action(card=card, pos_from=pos_from, pos_to=pos_to))
                                
        # Joker transformations
        jokers = [c for c in player.list_card if c.rank == 'JKR']
        if jokers:
            joker_card = jokers[0]
            suits = ['♠', '♥', '♦', '♣']
            
            if state.card_active is None:
                # Check if we have any marbles in kennel
                if has_marble_at_64:
                    actions.append(Action(card=joker_card, pos_from=64, pos_to=0))
                
                # If marble in kennel, only allow A and K transformations
                if has_marble_at_64:
                    for suit in suits:
                        for rank in ['A', 'K']:
                            actions.append(Action(
                                card=joker_card,
                                pos_from=None,
                                pos_to=None,
                                card_swap=Card(suit=suit, rank=rank)
                            ))
                else:
                    # In later game, allow transformation to any card
                    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
                    for suit in suits:
                        for rank in ranks:
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
                our_marbles = []
                opponent_marbles = []
                
                # Collect marble positions
                for p_idx, p in enumerate(state.list_player):
                    for marble in p.list_marble:
                        if 0 <= marble.pos < 64: 
                            if p_idx == active_player_idx:
                                our_marbles.append(marble.pos)  
                            elif not marble.is_save:  
                                opponent_marbles.append(marble.pos)

                # If there are opponent marbles available, generate swaps with them
                if opponent_marbles:
                    # Generate swaps between our marbles and opponent marbles
                    for our_pos in our_marbles:
                        for opp_pos in opponent_marbles:
                            actions.append(Action(card=card, pos_from=our_pos, pos_to=opp_pos))
                            actions.append(Action(card=card, pos_from=opp_pos, pos_to=our_pos))
                else:
                    # If no opponent swaps available, allow swaps between our own marbles
                    if len(our_marbles) >= 2:
                        for i, pos1 in enumerate(our_marbles):
                            for pos2 in our_marbles[i+1:]:
                                actions.append(Action(card=card, pos_from=pos1, pos_to=pos2))
                                actions.append(Action(card=card, pos_from=pos2, pos_to=pos1))
                                                      
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
                
    def _calculate_new_position(self, pos_from: int, steps: int, player_idx: int) -> int:
        """Calculate new position after moving steps, considering finish area."""
        if pos_from >= 64:  # In kennel
            return -1
            
        # Calculate finish entry point
        finish_entry = player_idx * 16
        finish_start = 64 + player_idx * 8
        
        # If already in finish area
        if self.is_finish_field(pos_from):
            new_pos = pos_from + steps
            if finish_start <= new_pos < finish_start + 4:  
                return new_pos
            return -1
        
        # Calculate new position on main board
        new_pos = (pos_from + steps) % 64
        
        # Check if we should enter finish area
        if pos_from <= finish_entry < new_pos:
            remaining_steps = steps - (finish_entry - pos_from + 1)
            if 0 <= remaining_steps < 4:  
                return finish_start + remaining_steps
                
        return new_pos

    def can_move_to_finish(self, pos_from: int, pos_to: int, player_idx: int) -> bool:
        """Check if a move to finish area is valid."""
        if not self.is_finish_field(pos_to):
            return True
            
        finish_start = 64 + player_idx * 8
        finish_end = finish_start + 4
        
        # Check if target position is in player's finish area
        if not (finish_start <= pos_to < finish_end):
            return False
            
        # If already in finish area
        if self.is_finish_field(pos_from):
            return pos_from < pos_to and all(
                self.get_player_who_occupies_pos(pos) is None
                for pos in range(pos_from + 1, pos_to)
            )
        
        # Coming from main board
        finish_entry = player_idx * 16
        
        # Check if path to finish entry is clear
        for pos in range(pos_from + 1, finish_entry + 1):
            pos_check = pos % 64
            if self.get_player_who_occupies_pos(pos_check) is not None:
                return False
                
        # Check if finish area path is clear
        for pos in range(finish_start, pos_to):
            if self.get_player_who_occupies_pos(pos) is not None:
                return False
                
        return True

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
                if finish_pos < 80:  
                    return finish_pos
                return None
        elif self.is_finish_field(pos_from):  
            new_pos = pos_from + steps
            if new_pos < 80:  
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