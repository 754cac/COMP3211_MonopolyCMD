import unittest
from unittest.mock import Mock
import random
from functions import go, income_tax, chance, free_parking, just_visiting_or_in_jail, go_to_jail, retire

class TestGameFunctions(unittest.TestCase):

    def setUp(self):
        self.player = Mock()
        self.player.name = "TestPlayer"
        self.player.money = 1000
        self.player.is_jailed = False
        self.player.is_retired = False

        self.game_parameters = {
            "go_money": 200,
            "tax_amount_rate": 0.1,
            "chance_multiplier": 10,
            "jailbreak_price": 50
        }

    def tearDown(self):
        self.player = None
        self.game_parameters = None
        
    def test_go(self):
        go(self.player, self.game_parameters)
        self.assertEqual(self.player.money, 1200)

    def test_income_tax(self):
        income_tax(self.player, self.game_parameters)
        tax_amount = int((self.player.money * self.game_parameters["tax_amount_rate"]) // 10 * 10)
        self.assertEqual(self.player.money, 900)

    def test_chance_gain(self):
        random.choice = Mock(side_effect=[True, 5])
        chance(self.player, self.game_parameters)
        gain_money = self.game_parameters['chance_multiplier'] * 5
        self.assertEqual(self.player.money, 1050)

    def test_chance_loss(self):
        random.choice = Mock(side_effect=[False, 3])
        chance(self.player, self.game_parameters)
        loss_money = self.game_parameters['chance_multiplier'] * 3
        self.assertEqual(self.player.money, 970)

    def test_free_parking(self):
        free_parking(self.player, self.game_parameters)

    def test_just_visiting(self):
        just_visiting_or_in_jail(self.player, self.game_parameters)
        self.assertFalse(self.player.is_jailed)

    def test_in_jail(self):
        self.player.is_jailed = True
        just_visiting_or_in_jail(self.player, self.game_parameters)
        self.player.jailbreak.assert_called_with(self.game_parameters['jailbreak_price'])

    def test_go_to_jail(self):
        go_to_jail(self.player, 10)
        self.player.jailed.assert_called_with(10)

    def test_retire(self):
        retire(self.player)
        self.player.retired.assert_called_once()

if __name__ == '__main__':
    unittest.main()