from server.py.game import Game, Player
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from enum import Enum
import random
import copy

class Card(BaseModel):
    suit: str
    rank: str

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

        # If we're in the middle of a 7-card move
        if state.card_active and state.card_active.rank == '7' and state.seven_steps_remaining is not None:
            for marble in player.list_marble:
                if marble.pos < 64 or self.is_finish_field(marble.pos):  # On board or in finish area
                    for steps in range(1, state.seven_steps_remaining + 1):
                        pos_to = self.compute_pos_to_for_7(marble.pos, steps)
                        if pos_to is not None and self.is_move_7_valid(0, marble.pos, pos_to):
                            actions.append(Action(
                                card=state.card_active,
                                pos_from=marble.pos,
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
                            new_pos = (marble.pos + step) % 96
                            actions.append(Action(card=active_card, pos_from=marble.pos, pos_to=new_pos))
            return actions

        # If card_active is None, proceed with normal logic

        # START actions (A,K,JKR)
        for card in player.list_card:
            if card.rank in ['A', 'K', 'JKR'] and not start_occupied_by_self and has_marble_at_64:
                actions.append(Action(card=card, pos_from=64, pos_to=0))

        # NORMAL MOVE actions for numeric cards
        for card in player.list_card:
            if card.rank in move_options:
                steps_list = move_options[card.rank]
                for marble in player.list_marble:
                    if 0 <= marble.pos < 64:
                        for step in steps_list:
                            new_pos = (marble.pos + step) % 96
                            actions.append(Action(card=card, pos_from=marble.pos, pos_to=new_pos))

        # Joker transformations (if Joker in hand and card_active=None)
        jokers = [c for c in player.list_card if c.rank == 'JKR']
        if jokers:
            joker_card = jokers[0]
            # If start possible with Joker (like A/K), show ♥A and ♥K
            if not start_occupied_by_self and has_marble_at_64:
                actions.append(Action(card=joker_card, pos_from=-1, pos_to=-1, card_swap=Card(suit='♥', rank='A')))
                actions.append(Action(card=joker_card, pos_from=-1, pos_to=-1, card_swap=Card(suit='♥', rank='K')))
            else:
                # Show all hearts transformations
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

    def apply_action(self, action: Optional[Action]) -> None:
        if action is None:
            # Handle reverting 7-card state
            if self._state.seven_steps_remaining is not None:
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

        # Handle 7-card moves
        if action.card.rank == '7' and state.seven_steps_remaining is not None:
            steps = (action.pos_to - action.pos_from) % 96
            
            # Check and kick out any marbles in the path
            for pos in range(action.pos_from + 1, action.pos_to + 1):
                pos = pos % 96
                occupant_idx = self.get_player_who_occupies_pos(pos)
                if occupant_idx is not None:
                    opp = state.list_player[occupant_idx]
                    for m in opp.list_marble:
                        if m.pos == pos:
                            m.pos = 72
                            m.is_save = False

            # Move the marble
            for m in player.list_marble:
                if m.pos == action.pos_from:
                    m.pos = action.pos_to
                    m.is_save = False
                    break

            state.seven_steps_remaining -= steps
            
            # Check if 7-card sequence is complete
            if state.seven_steps_remaining == 0:
                player.list_card = [c for c in player.list_card if not (c.suit == action.card.suit and c.rank == action.card.rank)]
                state.seven_steps_remaining = None
                state.seven_backup_state = None
                state.seven_player_idx = None
                state.card_active = None
                state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
            return

        # Joker transform action
        if action.card.rank == 'JKR' and action.pos_from == -1 and action.pos_to == -1 and action.card_swap is not None:
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

        if action.pos_from == 64 and action.pos_to == 0 and action.card.rank in ['A','K','JKR']:
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
        else:
            # Normal movement
            for m in player.list_marble:
                if m.pos == action.pos_from:
                    occupant_player_idx = self.get_player_who_occupies_pos(action.pos_to)
                    if occupant_player_idx is not None and occupant_player_idx != active_player_idx:
                        opponent = state.list_player[occupant_player_idx]
                        for omarble in opponent.list_marble:
                            if omarble.pos == action.pos_to:
                                omarble.pos = 72
                                omarble.is_save = False
                                break
                    m.pos = action.pos_to
                    m.is_save = False
                    player.list_card = [c for c in player.list_card if not (c.suit == action.card.suit and c.rank == action.card.rank)]
                    break

    def get_player_view(self, idx_player: int) -> GameState:
        pass

    def is_finish_field(self, pos: int) -> bool:
        return pos >= 72 and pos < 80

    def compute_pos_to_for_7(self, pos_from: int, steps: int) -> Optional[int]:
        # If starting from normal track
        if pos_from < 64:
            steps_to_end = 63 - pos_from
            if steps <= steps_to_end:
                return pos_from + steps
            else:
                # Need to enter finish area
                remaining_steps = steps - steps_to_end - 1  # -1 because first finish field is one step after 63
                finish_pos = 72 + remaining_steps
                if finish_pos < 80:  # Valid finish position
                    return finish_pos
                return None  # Invalid - would go beyond finish area
        
        # If already in finish area
        elif self.is_finish_field(pos_from):
            new_pos = pos_from + steps
            if new_pos < 80:  # Valid finish position
                return new_pos
            return None  # Invalid - would go beyond finish area
        
        return None  # Invalid starting position

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
