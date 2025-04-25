import unittest
from unittest.mock import patch, MagicMock
from player import Player
import vars

class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.player = Player("TestPlayer", 10, "game_1")

    def tearDown(self):
        self.player = None

    def test_initialization(self):
        self.assertEqual(self.player.name, "TestPlayer")
        self.assertEqual(self.player.gameboard_size, 10)
        self.assertEqual(self.player.game_id, "game_1")
        self.assertEqual(self.player.location, vars.PLAYER_DEFAULT_PROPERTIES['location'])
        self.assertEqual(self.player.money, vars.PLAYER_DEFAULT_PROPERTIES['money'])
        self.assertEqual(self.player.owned_properties, vars.PLAYER_DEFAULT_PROPERTIES['owned_properties'])
        self.assertFalse(self.player.is_jailed)
        self.assertFalse(self.player.is_retired)

    @patch('vars.secure_random_string', return_value="secure_id")
    def test_id_generation(self, mock_secure_random_string):
        player = Player("TestPlayer", 10, "game_1")
        self.assertEqual(player.id, "secure_id")
        mock_secure_random_string.assert_called_once_with(9)

    @patch('player.randint', return_value=3)
    def test_roll_dice(self, mock_randint):
        dice = self.player.roll_dice()
        self.assertEqual(dice, [3, 3])

    def test_move(self):
        self.player.move(5)
        self.assertEqual(self.player.location, vars.PLAYER_DEFAULT_PROPERTIES['location'] + 5)

    def test_adjust_location(self):
        self.player.location = 12
        self.player.adjust_location()
        self.assertEqual(self.player.location, 2)

    def test_buy_property(self):
        self.player.buy_property(2, 100)
        self.assertIn(2, self.player.owned_properties)
        self.assertEqual(self.player.money, vars.PLAYER_DEFAULT_PROPERTIES['money'] - 100)

    def test_jailed(self):
        self.player.jailed(5)
        self.assertTrue(self.player.is_jailed)
        self.assertEqual(self.player.location, 5)

    @patch('vars.handle_question_with_options', return_value='y')
    @patch('player.Player.roll_dice', return_value=[2, 2])
    def test_jailbreak_success_by_payment(self, mock_roll_dice, mock_handle_question_with_options):
        self.player.is_jailed = True
        self.player.jailed_rounds_count_down = 3
        self.player.money = 200

        dice = self.player.jailbreak(50)

        self.assertFalse(self.player.is_jailed)
        self.assertEqual(self.player.money, 150) 
        self.assertEqual(dice, [2, 2])
        mock_handle_question_with_options.assert_called_once()
        mock_roll_dice.assert_called_once()

    @patch('player.Player.roll_dice', return_value=[3, 3])
    def test_jailbreak_success_by_double(self, mock_roll_dice):
        self.player.is_jailed = True
        self.player.jailed_rounds_count_down = 2

        dice = self.player.jailbreak(50)

        self.assertFalse(self.player.is_jailed)
        self.assertEqual(self.player.jailed_rounds_count_down, 3)  # 重置倒計時
        self.assertEqual(dice, [3, 3])
        mock_roll_dice.assert_called_once()

    @patch('player.Player.roll_dice', return_value=[1, 2])
    def test_jailbreak_failed_no_double(self, mock_roll_dice):
        self.player.is_jailed = True
        self.player.jailed_rounds_count_down = 2

        dice = self.player.jailbreak(50)

        self.assertTrue(self.player.is_jailed)
        self.assertEqual(self.player.jailed_rounds_count_down, 1)  
        self.assertEqual(dice, [None, None])
        mock_roll_dice.assert_called_once()

    @patch('vars.handle_question_with_options', return_value='y')
    @patch('player.Player.roll_dice', return_value=[1, 2])
    def test_jailbreak_failed_no_money(self, mock_handle_question_with_options, mock_roll_dice):
        self.player.is_jailed = True
        self.player.jailed_rounds_count_down = 3
        self.player.money = 30  # 不足以支付

        dice = self.player.jailbreak(50)

        self.assertTrue(self.player.is_jailed)
        self.assertEqual(self.player.money, 30)  # 金額不變
        self.assertEqual(dice, [1, 2])
        mock_handle_question_with_options.assert_called_once()
        mock_roll_dice.assert_called_once()

    def test_retired(self):
        self.player.retired()
        self.assertTrue(self.player.is_retired)
        self.assertEqual(self.player.money, 0)
        self.assertEqual(self.player.owned_properties, [])

    @patch('builtins.print')
    def test_show_status(self, mock_print):
        self.player.show_status()
        mock_print.assert_called()

    @patch('builtins.print')
    def test_show_status_retired(self, mock_print):
        self.player.retired()
        self.player.show_status()
        mock_print.assert_called_with(
            f'\nPlayer ID: {self.player.id}\nPlayer Name: {self.player.name}\nPlayer is retired: {self.player.is_retired}'
        )

    @patch('builtins.print')
    def test_show_status_jailed(self, mock_print):
        self.player.is_jailed = True
        self.player.jailed_rounds_count_down = 2
        self.player.show_status()
        mock_print.assert_called_with(
            f'\nPlayer ID: {self.player.id}\nPlayer Name: {self.player.name}\nPlayer Location: {self.player.location}\nPlayer Money: {self.player.money}\nPlayer Owned Properties: {self.player.owned_properties}\nPlayer is jailed: {self.player.is_jailed}\nRounds to stay in Jail: {self.player.jailed_rounds_count_down}\n'
        )

if __name__ == '__main__':
    unittest.main()