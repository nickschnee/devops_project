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

if __name__ == '__main__':
    pytest.main(['-v', __file__])