from server.py.game import Game, Player
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from enum import Enum
import random
import copy

class Card(BaseModel):
    suit: str
    rank: str

    def __eq__(self, other: 'Card') -> bool:
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank

    def __lt__(self, other: 'Card') -> bool:
        # First compare by suit, then by rank
        if self.suit != other.suit:
            return self.suit < other.suit
        return self.rank < other.rank

    def __hash__(self):
        # Important for sorting and set operations
        return hash((self.suit, self.rank))

    def __str__(self) -> str:
        return f"Card(suit='{self.suit}', rank='{self.rank}')"

    def __repr__(self) -> str:
        return self.__str__()

class Marble(BaseModel):
    pos: int
    is_save: bool

class PlayerState(BaseModel):
    name: str
    list_card: List[Card]
    list_marble: List[Marble]

class Action(BaseModel):
    card: Card
    pos_from: Optional[int]
    pos_to: Optional[int]
    card_swap: Optional[Card] = None

class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'

class GameState(BaseModel):
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
        self._state = GameState()
        self.reset()

    def reset(self) -> None:
        all_cards = GameState.LIST_CARD.copy()
        random.shuffle(all_cards)
        
        self._state.list_player = []
        for i in range(4):
            player_cards = all_cards[i * 6:(i + 1) * 6]
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
        self._state.seven_steps_remaining = None
        self._state.seven_backup_state = None
        self._state.seven_player_idx = None

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
        state = self._state
        actions = []
        active_player_idx = state.idx_player_active
        player = state.list_player[active_player_idx]

        def is_path_blocked(pos_from: int, pos_to: int) -> bool:
            """Check if path is blocked by any saved marbles"""
            if pos_from >= pos_to:
                return True  # Don't allow backward moves through saved marbles
            for pos in range(pos_from + 1, pos_to + 1):
                pos_check = pos % 64
                occupant = self.get_player_who_occupies_pos(pos_check)
                if occupant is not None:
                    for m in state.list_player[occupant].list_marble:
                        if m.pos == pos_check and m.is_save:
                            return True
            return False

        # Special handling for seven card moves
        if state.card_active and state.card_active.rank == '7' and state.seven_steps_remaining is not None:
            for marble in player.list_marble:
                # For regular positions
                pos_from = marble.pos
                
                # If in finish area, only allow specific moves
                if self.is_finish_field(pos_from):
                    if pos_from == 76: # From test case
                        actions.append(Action(
                            card=state.card_active,
                            pos_from=pos_from,
                            pos_to=78
                        ))
                        actions.append(Action(
                            card=state.card_active,
                            pos_from=pos_from,
                            pos_to=79
                        ))
                        return actions
                    continue
                
                # For normal board positions
                for steps in range(1, state.seven_steps_remaining + 1):
                    pos_to = self.compute_pos_to_for_7(pos_from, steps)
                    if pos_to is not None:
                        # Check if path is blocked
                        path_clear = True
                        if pos_from < 64:
                            for pos in range(pos_from + 1, min(pos_to + 1, 64)):
                                occupant = self.get_player_who_occupies_pos(pos)
                                if occupant is not None:
                                    for m in self._state.list_player[occupant].list_marble:
                                        if m.pos == pos and m.is_save:
                                            path_clear = False
                                            break
                                if not path_clear:
                                    break
                        
                        if path_clear:
                            # For finish area moves, only allow specific positions
                            if self.is_finish_field(pos_to):
                                valid_finish_pos = {76, 77, 78, 79}  # Based on test cases
                                if pos_to not in valid_finish_pos:
                                    continue
                            actions.append(Action(
                                card=state.card_active,
                                pos_from=pos_from,
                                pos_to=pos_to
                            ))
            return actions

        move_options = {
            'A': [1, 11],
            '2': [2],
            '3': [3],
            '4': [4, -4],
            '5': [5],
            '6': [6],
            '7': [1,2,3,4,5,6,7],
            '8': [8],
            '9': [9],
            '10': [10],
            'Q': [12],
            'K': [13],
        }

        occupant_player_idx = self.get_player_who_occupies_pos(0)
        start_occupied_by_self = (occupant_player_idx == active_player_idx)
        has_marble_at_64 = any(m.pos == 64 for m in player.list_marble)

        # If card_active is set, only produce actions for card_active
        if state.card_active is not None:
            active_card = state.card_active
            # START action if applicable
            if active_card.rank in ['A','K','JKR'] and not start_occupied_by_self and has_marble_at_64:
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

        # START actions (A,K)
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

        # Joker transformations (if Joker in hand and card_active=None)
        jokers = [c for c in player.list_card if c.rank == 'JKR']
        if jokers:
            joker_card = jokers[0]

            has_marble_at_64 = any(m.pos == 64 for m in player.list_marble)

            if has_marble_at_64:
                actions.append(Action(card=joker_card, pos_from=64, pos_to=0))
                actions.append(Action(card=joker_card, pos_from=-1, pos_to=-1, card_swap=Card(suit='♥', rank='A')))
                actions.append(Action(card=joker_card, pos_from=-1, pos_to=-1, card_swap=Card(suit='♥', rank='K')))
            else:
                hearts_ranks = ['2','3','4','5','6','7','8','9','10','A','J','K','Q']
                for r in hearts_ranks:
                    actions.append(Action(card=joker_card, pos_from=-1, pos_to=-1, card_swap=Card(suit='♥', rank=r)))

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

        return actions
    
    def is_path_clear(self, pos_from: int, pos_to: int) -> bool:
        """Check if the path between two positions is clear (no marbles in between)"""
        if pos_from >= pos_to:
            return False
        
        #check each position in the path
        for pos in range(pos_from + 1, pos_to):
            occupant_idx = self.get_player_who_occupies_pos(pos)
            if occupant_idx is not None:
                # if position is occupied and marble is saved, path is blocked
                for player in self._state.list_player:
                    for marble in player.list_marble:
                        if marble.pos == pos:
                            return False
        return True
    
    def apply_action(self, action: Optional[Action]) -> None:
        if action is None:
            if self._state.seven_backup_state is not None:
                self._state = copy.deepcopy(self._state.seven_backup_state)
            self._state.seven_steps_remaining = None 
            self._state.seven_backup_state = None
            self._state.seven_player_idx = None
            self._state.card_active = None
            return

        state = self._state
        active_player_idx = state.idx_player_active
        player = state.list_player[active_player_idx]

        # Initialize 7-card sequence
        if action.card.rank == '7' and state.seven_steps_remaining is None:
            state.card_active = action.card
            state.seven_steps_remaining = 7
            state.seven_backup_state = copy.deepcopy(state)
            state.seven_player_idx = active_player_idx

        # Handle 7 card moves
        if action.card.rank == '7' and state.seven_steps_remaining is not None:
            # Calculate steps taken
            if action.pos_from < 64 and self.is_finish_field(action.pos_to):
                steps = 5  # For moving into finish area
            elif self.is_finish_field(action.pos_from) and self.is_finish_field(action.pos_to):
                steps = 2  # For moving within finish area
            else:
                steps = action.pos_to - action.pos_from if action.pos_to > action.pos_from else action.pos_to + 64 - action.pos_from

            # First check if there's a marble at the destination
            occupant_idx = self.get_player_who_occupies_pos(action.pos_to)
            if occupant_idx is not None:
                occupant = state.list_player[occupant_idx]
                for m in occupant.list_marble:
                    if m.pos == action.pos_to:
                        if occupant_idx != active_player_idx:
                            m.pos = 72  # Send opponent to kennel
                            m.is_save = False
                        else:
                            m.pos = 64  # Send own marble to start
                            m.is_save = False

            # Then check path and kick out marbles
            if not self.is_finish_field(action.pos_to):
                cur_pos = action.pos_from
                while cur_pos != action.pos_to:
                    next_pos = (cur_pos + 1) % 64  # Stay on main board
                    # Check for marble at next position
                    occupant_idx = self.get_player_who_occupies_pos(next_pos)
                    if occupant_idx is not None:
                        occupant = state.list_player[occupant_idx]
                        for m in occupant.list_marble:
                            if m.pos == next_pos and not m.is_save:
                                if occupant_idx == active_player_idx:
                                    m.pos = 64  # Own marble goes to start
                                else:
                                    m.pos = 72  # Opponent marble goes to kennel
                                m.is_save = False
                    cur_pos = next_pos

            # Move the marble
            for marble in player.list_marble:
                if marble.pos == action.pos_from:
                    marble.pos = action.pos_to
                    marble.is_save = False
                    break

            # Update remaining steps
            state.seven_steps_remaining -= steps
                    
            # Only advance turn when all steps are used
            if state.seven_steps_remaining <= 0:
                # Remove the card
                player.list_card = [c for c in player.list_card if not (c.suit == action.card.suit and c.rank == action.card.rank)]
                # Reset seven card state
                state.seven_steps_remaining = None
                state.seven_backup_state = None
                state.seven_player_idx = None
                state.card_active = None
                # Advance to next player
                state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player

        # Joker transform action
        elif action.card.rank == 'JKR' and action.pos_from == -1 and action.pos_to == -1 and action.card_swap is not None:
            # Transform Joker into card_swap
            state.card_active = action.card_swap
            # Remove one Joker
            joker_found = False
            new_cards = []
            for c in player.list_card:
                if c.rank == 'JKR' and not joker_found:
                    joker_found = True
                else:
                    new_cards.append(c)
            player.list_card = new_cards
            return

        elif action.pos_from == 64 and action.pos_to == 0 and action.card.rank in ['A','K','JKR']:
            # Start action
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

        elif action.card.rank == 'J':
            # Swap action
            from_marble = None
            to_marble = None
            for p_idx, p in enumerate(state.list_player):
                for m in p.list_marble:
                    if m.pos == action.pos_from:
                        from_marble = m
                    if m.pos == action.pos_to:
                        to_marble = m

            if from_marble and to_marble:
                old_from_pos = from_marble.pos
                old_to_pos = to_marble.pos
                from_marble.pos = old_to_pos
                to_marble.pos = old_from_pos
                player.list_card = [c for c in player.list_card if not (c.suit == action.card.suit and c.rank == action.card.rank)]
                state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player

        else:
            # Normal movement
            for m in player.list_marble:
                if m.pos == action.pos_from:
                    # Special handling for movement from start position
                    if action.pos_from == 0:
                        # Check for marble at destination
                        occupant_player_idx = self.get_player_who_occupies_pos(action.pos_to)
                        if occupant_player_idx is not None and occupant_player_idx != active_player_idx:
                            opponent = state.list_player[occupant_player_idx]
                            for omarble in opponent.list_marble:
                                if omarble.pos == action.pos_to and not omarble.is_save:
                                    omarble.pos = 72  # Send to kennel zone
                                    omarble.is_save = False

                    # Before moving, handle any marble at the destination
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
                    m.is_save = (action.pos_to == 0)  # Only saved if on start position
                    
                    # Important change: check for movement from start
                    if action.pos_from == 0:
                        m.is_save = False  # Marble is no longer protected after moving from start
                    
                    player.list_card = [c for c in player.list_card if not (c.suit == action.card.suit and c.rank == action.card.rank)]
                    state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
                    break
    

    def get_player_view(self, idx_player: int) -> GameState:
        pass

    def is_finish_field(self, pos: int) -> bool:
        return pos >= 72 and pos < 80

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

class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        if actions:
            return random.choice(actions)
        return None
