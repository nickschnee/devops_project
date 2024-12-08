# to run the test: pytest -v test/test_dog.py 

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.py.dog import Card, Marble, PlayerState, Action, GameState, GamePhase, Dog
import pytest

class TestDogBenchmark:
    CNT_PLAYERS = 4
    CNT_STEPS = 64
    CNT_BALLS = 4

    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.game_server = Dog()

    def start_game_state_at_round_2(self):
        """Helper method to set up game state at round 2"""
        self.game_server.reset()
        # Simulate playing through round 1
        self.game_server._state.cnt_round = 2
        self.game_server._state.idx_player_started = 0
        self.game_server._state.idx_player_active = 1  # Different from started player
        self.game_server._state.list_card_draw = self.game_server._state.list_card_draw[:85]

    def get_sorted_list_action(self, list_action):
        """Helper method to sort list of actions for comparison"""
        return sorted([str(action) for action in list_action])

    def get_list_action_as_str(self, list_action):
        """Helper method to convert list of actions to string representation"""
        return '\n'.join([str(action) for action in sorted([str(action) for action in list_action])])

    def test_initial_game_state_values(self):
        """Test 001: Validate values of initial game state (cnt_round=1) [5 points]"""
        # TODO: Must be valid for 2 players too!
        self.game_server.reset()
        state = self.game_server.get_state()

        # Game state assertions
        assert state.phase == GamePhase.RUNNING, f'{state}Error: "bool_game_finished" must be False initially'
        assert state.cnt_round == 1, f'{state}Error: "cnt_round" must be 1 initially'
        assert len(state.list_card_discard) == 0, f'{state}Error: len("list_card_discard") must be 0 initially'
        assert len(state.list_card_draw) == 86, f'{state}Error: len("list_card_draw") must be 86 initially'
        assert len(state.list_player) == 4, f'{state}Error: len("list_player") must be 4'
        assert state.idx_player_active >= 0, f'{state}Error: "idx_player_active" must >= 0'
        assert state.idx_player_active < 4, f'{state}Error: "idx_player_active" must < 4'
        assert state.idx_player_started == state.idx_player_active, f'{state}Error: "idx_player_active" must be == "idx_player_started"'
        assert state.card_active is None, f'{state}Error: "card_active" must be None'
        assert not state.bool_card_exchanged, f'{state}Error: bool_card_exchangedmust be False'

        # Player state assertions
        for player in state.list_player:
            assert len(player.list_card) == 6, f'{state}Error: len("list_player.list_card") must be 6 initially'
            assert len(player.list_marble) == 4, f'{state}Error: len("list_player.list_marble") must be 4 initially'

    def test_later_game_state_values(self):
        """Test 002: Validate values of later game state (cnt_round=2) [5 points]"""
        # TODO: Must be valid for 2 players too!
        self.start_game_state_at_round_2()

        state = self.game_server.get_state()

        assert state.cnt_round > 0, f'{state}Error: "cnt_round" must be > 0'
        assert len(state.list_card_draw) < 86, f'{state}Error: len("list_card_draw") must be < 86'
        assert len(state.list_player) == 4, f'{state}Error: len("list_player") must be 4'
        assert state.idx_player_active >= 0, f'{state}Error: "idx_player_active" must >= 0'
        assert state.idx_player_active < 4, f'{state}Error: "idx_player_active" must < 4'
        assert state.idx_player_started != state.idx_player_active, f'{state}Error: "idx_player_active" must be != "idx_player_started"'

        for player in state.list_player:
            assert len(player.list_marble) == 4, f'{state}Error: len("list_player.list_marble") must be 4 initially'

    def test_get_list_action_without_start_cards(self):
        """Test 003: Test get_list_action without start-cards [1 point]"""
        self.game_server.reset()
        state = self.game_server.get_state()

        idx_player_active = 0
        state.cnt_round = 0
        state.idx_player_started = idx_player_active
        state.idx_player_active = idx_player_active
        state.bool_card_exchanged = True
        player = state.list_player[idx_player_active]
        player.list_card = [Card(suit='♣', rank='3'), Card(suit='♦', rank='9'), Card(suit='♣', rank='10'), 
                           Card(suit='♥', rank='Q'), Card(suit='♠', rank='7'), Card(suit='♣', rank='J')]
        self.game_server.set_state(state)
        str_state = str(state)

        list_action_found = self.game_server.get_list_action()
        list_action_expected = []

        hint = str_state
        hint += 'Error: "get_list_action" result is wrong'
        hint += f'\nExpected:'
        hint += f'\n{self.get_list_action_as_str(list_action_expected)}'
        hint += f'\nFound:'
        hint += f'\n{self.get_list_action_as_str(list_action_found)}'
        assert self.get_sorted_list_action(list_action_found) == self.get_sorted_list_action(list_action_expected), hint
    
    def test_get_list_action_with_one_start_card(self):
        """Test 004: Test get_list_action with one start-card [1 point]"""

        list_card = [Card(suit='♦', rank='A'), Card(suit='♥', rank='K'), Card(suit='', rank='JKR')]

        for card in list_card:
            self.game_server.reset()
            state = self.game_server.get_state()

            idx_player_active = 0
            state.cnt_round = 0
            state.idx_player_started = idx_player_active
            state.idx_player_active = idx_player_active
            state.bool_card_exchanged = True
            player = state.list_player[idx_player_active]
            player.list_card = [Card(suit='♣', rank='10'), Card(suit='♥', rank='Q'), Card(suit='♠', rank='7'), Card(suit='♣', rank='J'), card]
            self.game_server.set_state(state)
            str_state = str(state)

            list_action_found = self.game_server.get_list_action()
            action = Action(card=card, pos_from=64, pos_to=0)

            hint = str_state
            hint += f'Error: "get_list_action" must return an action to get out of kennel for {card}'
            hint += f'\nFound:'
            hint += f'\n{self.get_list_action_as_str(list_action_found)}'
            assert action in list_action_found, hint

    def test_get_list_action_with_three_start_cards(self):
        """Test 005: Test get_list_action with three start-cards [1 point]"""

        self.game_server.reset()
        state = self.game_server.get_state()

        idx_player_active = 0
        state.cnt_round = 0
        state.idx_player_started = idx_player_active
        state.idx_player_active = idx_player_active
        state.bool_card_exchanged = True
        player = state.list_player[idx_player_active]
        player.list_card = [Card(suit='♣', rank='10'), Card(suit='♦', rank='A'), Card(suit='♠', rank='2'), Card(suit='♥', rank='K'), Card(suit='♠', rank='7'), Card(suit='♥', rank='A')]
        self.game_server.set_state(state)
        str_state = str(state)

        list_action = self.game_server.get_list_action()
        list_action_found = self.get_sorted_list_action(list_action)
        list_action_expected = self.get_sorted_list_action([
            Action(card=Card(suit='♦', rank='A'), pos_from=64, pos_to=0),
            Action(card=Card(suit='♥', rank='K'), pos_from=64, pos_to=0),
            Action(card=Card(suit='♥', rank='A'), pos_from=64, pos_to=0)
        ])

        hint = str_state
        hint += f'Error 1: "get_list_action" must return {len(list_action_expected)} not {len(list_action_found)} actions'
        assert len(list_action_found) == len(list_action_expected), hint

        hint = str_state
        hint += 'Error 2: "get_list_action" list is wrong'
        hint += f'\nExpected:'
        hint += f'\n{self.get_list_action_as_str(list_action_expected)}'
        hint += f'\nFound:'
        hint += f'\n{self.get_list_action_as_str(list_action_found)}'
        assert self.get_sorted_list_action(list_action_found) == self.get_sorted_list_action(list_action_expected), hint

    def test_move_out_of_kennel_1(self):
        """Test 006: Test move out of kennel without marble on start [1 point]"""

        self.game_server.reset()
        state = self.game_server.get_state()

        idx_player_active = 0
        state.cnt_round = 0
        state.idx_player_started = idx_player_active
        state.idx_player_active = idx_player_active
        state.bool_card_exchanged = True
        player = state.list_player[idx_player_active]
        player.list_card = [Card(suit='♦', rank='A'), Card(suit='♣', rank='10')]
        self.game_server.set_state(state)
        str_state_1 = str(state)

        action = Action(card=Card(suit='♦', rank='A'), pos_from=64, pos_to=0)
        self.game_server.apply_action(action)
        str_action = f'Action: {action}\n'

        state = self.game_server.get_state()
        str_state_2 = str(state)

        marble_found = False
        marble_save = False
        player = state.list_player[idx_player_active]

        idx_marble = self.get_idx_marble(player=player, pos=0)
        if idx_marble != -1:
            marble_found = True
            marble_save = player.list_marble[idx_marble].is_save

        hint = str_state_1 + str_action + str_state_2
        hint += 'Error: Player 1 must end with a marble at pos=0'
        assert marble_found, hint
        hint = str_state_1 + str_action + str_state_2
        hint += 'Error: Status of marble at pos=0 must be "is_save"=True'
        assert marble_save, hint

    def test_move_out_of_kennel_2(self):
        """Test 007: Test move out of kennel with self-blocking on start [1 point]"""

        self.game_server.reset()
        state = self.game_server.get_state()

        idx_player_active = 0
        state.cnt_round = 0
        state.idx_player_started = idx_player_active
        state.idx_player_active = idx_player_active
        state.bool_card_exchanged = True
        player = state.list_player[idx_player_active]
        player.list_card = [Card(suit='♦', rank='A')]
        player.list_marble[0].pos = 0
        player.list_marble[0].is_save = True
        self.game_server.set_state(state)
        str_state = str(state)

        list_action = self.game_server.get_list_action()
        list_action_found = [action for action in list_action if action.pos_from >= 64 and action.pos_from < 68]
        list_action_expected = []

        hint = str_state
        hint += f'Error: "get_list_action" must return {len(list_action_expected)} not {len(list_action_found)} actions'
        hint += '\nHint: Player 1\'s marbel on start is blocking.'
        assert len(list_action_found) == len(list_action_expected), hint

    def test_move_out_of_kennel_3(self):
        """Test 008: Test move out of kennel with oponent on start [1 point]"""

        self.game_server.reset()
        state = self.game_server.get_state()

        idx_player_active = 0
        state.cnt_round = 0
        state.idx_player_started = idx_player_active
        state.idx_player_active = idx_player_active
        state.bool_card_exchanged = True
        player = state.list_player[idx_player_active]
        player.list_card = [Card(suit='♦', rank='A')]
        player2 = state.list_player[idx_player_active + 1]
        player2.list_marble[0].pos = 0
        player2.list_marble[0].is_save = True
        self.game_server.set_state(state)
        str_state_1 = str(state)

        list_action_found = self.game_server.get_list_action()
        action = Action(card=Card(suit='♦', rank='A'), pos_from=64, pos_to=0)
        list_action_expected = [action]

        hint = str_state_1
        hint += f'Error: "get_list_action" must return {len(list_action_expected)} not {len(list_action_found)} actions'
        assert len(list_action_found) == len(list_action_expected), hint

        self.game_server.apply_action(action)
        str_action = f'Action: {action}\n'

        state = self.game_server.get_state()
        str_state_2 = str(state)

        player = state.list_player[idx_player_active]
        found = self.get_idx_marble(player=player, pos=0) != -1
        hint = str_state_1 + str_action + str_state_2
        hint += 'Error: Player 1\'s marble must be on start (pos=0)'
        assert found, hint

        player2 = state.list_player[idx_player_active + 1]
        found = self.get_idx_marble(player=player2, pos=72) != -1
        hint = str_state_1 + str_action + str_state_2
        hint += 'Error: Player 2\'s marble must be back in kennel (pos=72)'
        assert found, hint

if __name__ == '__main__':
    pytest.main(['-v', __file__])