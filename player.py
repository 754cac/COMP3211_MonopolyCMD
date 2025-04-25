from random import randint
import vars


class Player:

    def __init__(self, name, gameboard_size, game_id):
        self.name = name
        self.id = vars.secure_random_string(9)
        self.location = vars.PLAYER_DEFAULT_PROPERTIES['location']
        self.money = vars.PLAYER_DEFAULT_PROPERTIES['money']
        self.owned_properties = [i for i in vars.PLAYER_DEFAULT_PROPERTIES['owned_properties']] # Directly assign will lead to pass by reference
        self.is_jailed = vars.PLAYER_DEFAULT_PROPERTIES['is_jailed']
        self.jailed_rounds_count_down = vars.PLAYER_DEFAULT_PROPERTIES['jailed_rounds_count_down']
        self.is_retired = vars.PLAYER_DEFAULT_PROPERTIES['is_retired']
        self.gameboard_size = gameboard_size
        self.game_id = game_id

    @staticmethod
    def roll_dice():
        return [randint(1, 4), randint(1, 4)]

    def move(self, steps):
        self.location += steps

    def buy_property(self, location, amount):
        self.money -= amount
        self.owned_properties.append(location)

    def adjust_location(self):
        if self.location >= (self.gameboard_size + 1):
            self.location = self.location % (self.gameboard_size + 1) + 1

    def jailed(self, jail_location):
        self.is_jailed = True
        self.location = jail_location

    def jailbreak(self, jailbreak_price):
        if self.is_jailed:
            # If the player is in the 1st round of jail (countdown is 3)
            if self.jailed_rounds_count_down == 3:
                print(f'{self.name} is jailed for the 1st round.')
                # Player can choose to pay the fine or roll the dice
                selection = vars.handle_question_with_options(f'Pay ${jailbreak_price} to jailbreak immediately [Y / n]? ', ['y', 'n', ''])
                if selection.lower() == 'y' or selection.lower() == '':
                    if self.money >= jailbreak_price:
                        self.money -= jailbreak_price
                        print(f'{self.name} jailbreak success by paying ${jailbreak_price}!')
                        self.is_jailed = False
                        self.jailed_rounds_count_down = 3  # Reset the countdown
                        return self.roll_dice()
                    else:
                        print(f'{self.name} does not have enough money to pay the fine!')
                        first_roll, second_roll = self.roll_dice()
                        print(f'{self.name} rolled 2 dice: [{first_roll}, {second_roll}]')
                        if first_roll == second_roll:
                            print(f'{self.name} jailbreak success by luck!')
                            self.is_jailed = False
                            self.jailed_rounds_count_down = 3  # Reset the countdown
                        return [first_roll, second_roll]
                else:
                    print(f'{self.name} chooses to roll double!')
                    first_roll, second_roll = self.roll_dice()
                    print(f'{self.name} rolled 2 dice: [{first_roll}, {second_roll}]')
                    if first_roll == second_roll:
                        print(f'{self.name} jailbreak success by luck!')
                        self.is_jailed = False
                        self.jailed_rounds_count_down = 3  # Reset the countdown
                        return [first_roll, second_roll]
                    else:
                        print(f'{self.name} failed to roll doubles. Must roll again next turn.')
                        self.jailed_rounds_count_down -= 1  # Decrement countdown

        # If the player is in the 3rd round of jail (countdown is 1)
            # If the player is in the 2nd round of jail (countdown is 2)
            elif self.jailed_rounds_count_down == 2:
                print(f'{self.name} is jailed for the 2nd round.')
                # Player can only roll the dice
                first_roll, second_roll = self.roll_dice()
                print(f'{self.name} rolled 2 dice: [{first_roll}, {second_roll}]')
                if first_roll == second_roll:
                    print(f'{self.name} jailbreak success by luck!')
                    self.is_jailed = False
                    self.jailed_rounds_count_down = 3  # Reset the countdown
                    return [first_roll, second_roll]
                else:
                    print(f'{self.name} failed to roll doubles. Must roll again next turn.')
                    self.jailed_rounds_count_down -= 1  # Decrement countdown

            # If the player is in the 3rd round of jail (countdown is 1)
            elif self.jailed_rounds_count_down == 1:
                print(f'{self.name} is jailed for the 3rd round.')
                first_roll, second_roll = self.roll_dice()
                print(f'{self.name} rolled 2 dice: [{first_roll}, {second_roll}]')
                if first_roll == second_roll:
                    print(f'{self.name} jailbreak success by luck!')
                    self.is_jailed = False
                    self.jailed_rounds_count_down = 3  # Reset the countdown
                    return [first_roll, second_roll]
                else:
                    print(f'{self.name} failed to roll doubles and must pay ${jailbreak_price} to get out of jail.')
                    self.money -= jailbreak_price
                    self.is_jailed = False
                    self.jailed_rounds_count_down = 3  # Reset the countdown
                    return [first_roll, second_roll]

            return [None, None]  # No action can be taken if still jailed
        else:
            return self.roll_dice()  # If not jailed, roll the dice normally

    def retired(self):
        self.is_retired = True
        self.money = 0
        self.owned_properties = []

    def show_status(self):
        if self.is_retired:
            print(f'\nPlayer ID: {self.id}\nPlayer Name: {self.name}\nPlayer is retired: {self.is_retired}')
        elif not self.is_jailed:
            print(f'\nPlayer ID: {self.id}\nPlayer Name: {self.name}\nPlayer Location: {self.location}\nPlayer Money: {self.money}\nPlayer Owned Properties: {self.owned_properties}\nPlayer is jailed: {self.is_jailed}\n')
        else:
            print(f'\nPlayer ID: {self.id}\nPlayer Name: {self.name}\nPlayer Location: {self.location}\nPlayer Money: {self.money}\nPlayer Owned Properties: {self.owned_properties}\nPlayer is jailed: {self.is_jailed}\nRounds to stay in Jail: {self.jailed_rounds_count_down}\n')
