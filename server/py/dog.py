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
        if state.cnt_round == 0 and not state.bool_card_exchanged:
            return []

        actions = []
        active_player_idx = state.idx_player_active
        player = state.list_player[active_player_idx]

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

        # J (Jack) card swap actions
        # For each J card, we can swap one of our marbles with another marble on the board.
        # Conditions:
        # - pos_from must be one of our marbles on the board (pos<64).
        # - pos_to can be any other marble on the board (pos<64).
        # - If pos_to belongs to opponent and is_save=True, skip.
        # - Otherwise, add the swap action.
        # J (Jack) card swap actions
        for card in player.list_card:
            if card.rank == 'J':
                # Get all marbles on the board
                all_marbles_positions = []
                for p_idx, p in enumerate(state.list_player):
                    for m in p.list_marble:
                        if 0 <= m.pos < 64:
                            all_marbles_positions.append((p_idx, m.pos, m.is_save))

                # Our marbles on the board
                our_marbles = [(p_idx, pos, is_save) 
                            for (p_idx, pos, is_save) in all_marbles_positions 
                            if p_idx == active_player_idx]

                # First determine if there are any opponent swaps available (opponent marbles that are not save)
                opponent_swaps_available = False
                for (_, pos_from, _) in our_marbles:
                    for (p_idx_to, pos_to, save_to) in all_marbles_positions:
                        if pos_from != pos_to:
                            # Opponent and non-save
                            if p_idx_to != active_player_idx and not save_to:
                                opponent_swaps_available = True
                                break
                    if opponent_swaps_available:
                        break

                # Now add actions based on whether opponent swaps are available
                for (p_idx_from, pos_from, save_from) in our_marbles:
                    for (p_idx_to, pos_to, save_to) in all_marbles_positions:
                        if pos_from != pos_to:
                            if opponent_swaps_available:
                                # Only add opponent non-save swaps
                                if p_idx_to != active_player_idx and not save_to:
                                    actions.append(Action(card=card, pos_from=pos_from, pos_to=pos_to))
                            else:
                                # No opponent swaps available, add self-swaps and non-save opponent swaps
                                if p_idx_to == active_player_idx or not save_to:
                                    actions.append(Action(card=card, pos_from=pos_from, pos_to=pos_to))

        return actions

    def apply_action(self, action: Action) -> None:
        if action is None:
            return

        state = self._state
        active_player_idx = state.idx_player_active
        player = state.list_player[active_player_idx]

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
            # Find the two marbles involved
            from_marble = None
            to_marble = None
            from_owner = None
            to_owner = None

            # Find marbles at pos_from and pos_to
            for p_idx, p in enumerate(state.list_player):
                for m_idx, m in enumerate(p.list_marble):
                    if m.pos == action.pos_from:
                        from_marble = m
                        from_owner = p
                    if m.pos == action.pos_to:
                        to_marble = m
                        to_owner = p

            # Swap their positions if both found
            if from_marble and to_marble:
                old_from_pos = from_marble.pos
                old_to_pos = to_marble.pos
                from_marble.pos = old_to_pos
                to_marble.pos = old_from_pos
                # Card used up
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

class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        if actions:
            return random.choice(actions)
        return None
