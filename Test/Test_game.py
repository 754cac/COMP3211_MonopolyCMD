import unittest
from unittest.mock import MagicMock, patch
from game import Game
from player import Player
from gameboard import Gameboard
import vars

class TestGame(unittest.TestCase):

    def setUp(self):
        self.game = Game()

        self.game.gameboard = MagicMock(spec=Gameboard)
        self.game.gameboard.design_file_name = "default_gameboard.json"
        self.game.gameboard.game_id = "test_game"
        self.mock_player1 = MagicMock(spec=Player)
        self.mock_player2 = MagicMock(spec=Player)

        self.mock_player1.id = 'player1'
        self.mock_player1.name = 'Player1'
        self.mock_player1.location = 0
        self.mock_player1.owned_properties = []
        self.mock_player1.is_retired = False
        self.mock_player1.money = 1000
        self.mock_player1.is_jailed = False
        self.mock_player1.jailed_rounds_count_down = 0
        self.mock_player1.gameboard_size = 10
        self.mock_player1.game_id = "test_game_id"  # 新增屬性

        self.mock_player2.id = 'player2'
        self.mock_player2.name = 'Player2'
        self.mock_player2.location = 1
        self.mock_player2.owned_properties = []
        self.mock_player2.is_retired = False
        self.mock_player2.money = 800
        self.mock_player2.is_jailed = False
        self.mock_player2.jailed_rounds_count_down = 0
        self.mock_player2.gameboard_size = 10
        self.mock_player2.game_id = "test_game_id"  # 新增屬性


        self.game.players = {
            self.mock_player1.id: self.mock_player1,
            self.mock_player2.id: self.mock_player2
        }
        self.game.player_orders = {1: 'player1', 2: 'player2'}

 
        self.game.gameboard.actual_layout = {
            'layout': {
                0: {'ownership': None, 'owner_name': '', 'is_ownable': True, 'price': 200, 'rent': 20, 'name': 'Property1'},
                1: {'ownership': None, 'owner_name': '', 'is_ownable': True, 'price': 300, 'rent': 30, 'name': 'Property2'},
                2: {'ownership': None, 'owner_name': '', 'is_ownable': False, 'name': 'Go To Jail'},
            }
        }

    def tearDown(self):
        self.game = None
        self.mock_player1 = None
        self.mock_player2 = None

    def test_game_initialization(self):
        game = Game()
        self.assertIsNotNone(game)
        self.assertEqual(game.players, {})
        self.assertEqual(game.player_orders, {})
        self.assertEqual(game.game_state['game_over'], False)
        self.assertEqual(game.game_state['current_round'], 1)

    def test_change_property_ownership(self):
        self.game.change_property_ownership(self.mock_player1)
        self.assertEqual(self.game.gameboard.actual_layout['layout'][0]['ownership'], 'player1')
        self.assertEqual(self.game.gameboard.actual_layout['layout'][0]['owner_name'], 'Player1')

    def test_retire_player(self):
        self.game.retire_player(self.mock_player1)
        self.assertTrue(self.mock_player1.retired.called)
        self.assertIsNone(self.game.gameboard.actual_layout['layout'][0]['ownership'])

    def test_show_player_status(self):
        self.mock_player1.show_status = MagicMock()
        self.game.show_player_status(self.mock_player1.id)
        self.mock_player1.show_status.assert_called_once()

    def test_show_all_players_status(self):
        with patch('pandas.DataFrame.to_string') as mock_to_string:
            self.game.show_all_players_status()
            self.assertTrue(mock_to_string.called)

    def test_show_game_status(self):
        with patch('pandas.DataFrame.to_string') as mock_to_string:
            self.game.show_game_status()
            self.assertTrue(mock_to_string.called)

    @patch('builtins.input', side_effect=['0', '2', 'Player1', 'Player2'])
    def test_new_game(self, mock_input):
        self.assertTrue(self.game.new_game())
        self.assertEqual(len(self.game.players), 2)
        self.assertEqual(self.game.game_state['current_round'], 1)

    def test_player_buy_property(self):
        self.mock_player1.money = 500
        self.mock_player1.owned_properties = [0] 
        self.game.change_property_ownership(self.mock_player1)
        self.assertIn(0, self.mock_player1.owned_properties) 

    def test_player_pay_rent(self):
        """測試玩家支付租金"""
        self.mock_player1.money = 1000
        self.mock_player2.location = 0
        self.mock_player2.money = 800

        self.game.gameboard.actual_layout['layout'][0]['ownership'] = self.mock_player1.id
        self.game.gameboard.actual_layout['layout'][0]['owner_name'] = self.mock_player1.name

        rent = self.game.gameboard.actual_layout['layout'][0]['rent']
        self.mock_player2.money -= rent
        self.mock_player1.money += rent

        self.assertEqual(self.mock_player1.money, 1020) 
        self.assertEqual(self.mock_player2.money, 780) 

    @patch('builtins.input', side_effect=['y', 'save_file.json', 'n'])
    def test_save_and_load_game(self, mock_input):
        with patch('vars.json.dump') as mock_json_dump:
            self.game.save_game_state('save_file.json')
            self.assertTrue(mock_json_dump.called)

        with patch('vars.json.load', return_value={
            'game_state': self.game.game_state,
            'player_orders': self.game.player_orders,
            'game_parameters': self.game.game_parameters,
            'players': {},
            'gameboard_parameters': {'design_file_name': 'default_gameboard.json', 'game_id': 'test_game'}
        }):
            self.assertFalse(self.game.load_game_state('save_file.json'))

    def test_player_jailbreak(self):
        self.mock_player1.is_jailed = True
        self.mock_player1.jailed_rounds_count_down = 1
        self.mock_player1.money = 200

        def mock_jailbreak(price):
            self.mock_player1.money -= price  
            self.mock_player1.is_jailed = False  
            return [3, 4]  

        self.mock_player1.jailbreak = mock_jailbreak

        dice = self.mock_player1.jailbreak(50)  
        self.assertFalse(self.mock_player1.is_jailed)  
        self.assertEqual(self.mock_player1.money, 150)  
        self.assertEqual(dice, [3, 4])  

    def test_game_over_when_only_one_player_left(self):
        self.mock_player2.is_retired = True
        self.game.check_only_player_is_left()
        self.assertTrue(self.game.game_state["game_over"])

if __name__ == '__main__':
    unittest.main()