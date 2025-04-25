import json
import vars
from gameboard import Gameboard, check_design
from player import Player
import pathlib as pl
import random
import pandas as pd


class Game:

    def __init__(self):

        self.gameboard = None
        self.players = {}
        self.player_orders = {}
        self.game_state = {
            "game_id": None,
            "game_over": False,
            "current_round": 1,
            "current_player_id": '',
        }
        self.game_parameters = {
            "random_player_orders": False,
            "chance_multiplier": 0,
            "jailbreak_price": 0,
            "tax_amount_rate": 0,
            "go_money": 0,
            "maximum_rounds": 0,
            "minimum_player": 0,
            "maximum_player": 0
        }

    def change_property_ownership(self, player, active_retire_player=False):
        if active_retire_player:
            for i in player.owned_properties:
                self.gameboard.actual_layout['layout'][i]['ownership'] = None
                self.gameboard.actual_layout['layout'][i]['owner_name'] = ''

        elif self.gameboard.actual_layout['layout'][player.location]['is_ownable'] and not self.gameboard.actual_layout['layout'][player.location]['ownership']:
            self.gameboard.actual_layout['layout'][player.location]['ownership'] = player.id
            self.gameboard.actual_layout['layout'][player.location]['owner_name'] = player.name

        elif not self.gameboard.actual_layout['layout'][player.location]['is_ownable']:
            print('Not ownable.')

        else:
            print('Ownership update failed.')

    def retire_player(self, player):
        if not player.is_retired:
            self.change_property_ownership(player, True)
            player.retired()

            retired_player_id = player.id
            player_orders_keys = list(self.player_orders.keys())
            player_orders_keys.sort()
            if max(player_orders_keys) <= self.game_parameters["maximum_player"]:
                next_retired_player_order = self.game_parameters["maximum_player"] + 1
            else:
                next_retired_player_order = max(player_orders_keys) + 1

            new_player_orders = {}
            new_player_order = 1
            player_orders_keys_still_playing = [i for i in player_orders_keys if i <= self.game_parameters["maximum_player"]]
            player_orders_keys_retired = [i for i in player_orders_keys if i > self.game_parameters["maximum_player"]]

            for player_order_key in player_orders_keys_still_playing:
                if self.player_orders[player_order_key] != retired_player_id:
                    new_player_orders[new_player_order] = self.player_orders[player_order_key]
                    new_player_order += 1
                else:
                    new_player_orders[next_retired_player_order] = self.player_orders[player_order_key]

            for player_order_key in player_orders_keys_retired:
                new_player_orders[player_order_key] = self.player_orders[player_order_key]

            self.player_orders = new_player_orders
            print(f'{player.name} is retired!')

    def show_player_status(self, player_id):
        player = self.players[player_id]
        player.show_status()

    def show_all_players_status(self):
        player_orders_keys = list(self.player_orders.keys())
        player_orders_keys.sort()
        player_details = []
        for player_order in player_orders_keys:
            player_detail = {
                "IsRetired": '-',
                "ID": '-',
                "Name": '-',
                "Order": '-',
                "Location": '-',
                "Money": '-',
                "OwnedProperties": '-',
                "IsJailed": '-',
                "RoundsToStayInJail": '-',
            }
            player = self.players[self.player_orders[player_order]]
            if player.is_retired:
                player_detail.update({
                    "IsRetired": True,
                    "ID": player.id,
                    "Name": player.name
                })
            elif player.is_jailed:
                player_detail.update({
                    "ID": player.id,
                    "Name": player.name,
                    "Order": player_order if not self.game_parameters["random_player_orders"] else '?',
                    "Location": player.location,
                    "Money": player.money,
                    "OwnedProperties": player.owned_properties,
                    "IsJailed": player.is_jailed,
                    "RoundsToStayInJail": player.jailed_rounds_count_down
                })
            else:
                player_detail.update({
                    "ID": player.id,
                    "Name": player.name,
                    "Order": player_order if not self.game_parameters["random_player_orders"] else '?',
                    "Location": player.location,
                    "Money": player.money,
                    "OwnedProperties": player.owned_properties,
                })
            player_details.append(player_detail)
        player_status_df = pd.DataFrame(player_details, index=player_orders_keys)
        pd.set_option('display.max_rows', None)  # Show all rows
        pd.set_option('display.max_columns', None)  # Show all columns
        pd.set_option('display.max_colwidth', None)  # Show full column content
        print('\nAll Player Status: \n', player_status_df.to_string(index=False), '\n')

    def show_game_status(self):

        player_locations_dict = {}
        for player_id, player_ in self.players.items():
            if not player_.is_retired:
                player_name_id = f'{player_.name} (ID: {player_id})'
                if player_.location not in player_locations_dict:
                    player_locations_dict[player_.location] = [player_name_id]
                else:
                    player_locations_dict[player_.location].append(player_name_id)

        gameboard_ = self.gameboard.actual_layout
        locations = list(gameboard_['layout'].keys())
        locations.sort()
        squares = []
        for location in locations:
            square = {
                'Location': '-',
                'Name': '-',
                'Type': '-',
                'Price': '-',
                'Rent': '-',
                'OwnerID': '-',
                'PlayersOnSquare': '-'
            }
            if gameboard_['layout'][location]['is_ownable']:
                square.update({
                    'Location': location,
                    'Name': gameboard_['layout'][location]['name'],
                    'Type': 'Property',
                    'Price': gameboard_['layout'][location]['price'],
                    'Rent': gameboard_['layout'][location]['rent'],
                    'OwnerID': gameboard_['layout'][location]['ownership'] if gameboard_['layout'][location]['ownership'] else '-',
                    'PlayersOnSquare': player_locations_dict.get(location, '-')
                })
            else:
                square.update({
                    'Location': location,
                    'Name': gameboard_['layout'][location]['name'],
                    'Type': 'Function',
                    'PlayersOnSquare': player_locations_dict.get(location, '-')
                })
            squares.append(square)

        gameboard_df = pd.DataFrame(squares, index=locations)
        pd.set_option('display.max_rows', None)  # Show all rows
        pd.set_option('display.max_columns', None)  # Show all columns
        pd.set_option('display.max_colwidth', None)  # Show full column content
        print(f'\nGame ID: {self.game_state["game_id"]}\nCurrent Round: {self.game_state["current_round"]}\nCurrent Player ID: {self.game_state["current_player_id"]}')
        print('\nGameboard Status: \n', gameboard_df.to_string(index=False), '\n')

    def new_game(self):
        print("Let's proceed to create a new game!")
        self.game_state["game_id"] = vars.secure_random_string(12)

        # For Game Parameters
        self.game_parameters = {
            "random_player_orders": vars.DEFAULT_RANDOM_PLAYER_ORDERS,
            "chance_multiplier": vars.DEFAULT_CHANCE_MULTIPLIER,
            "jailbreak_price": vars.DEFAULT_JAILBREAK_PRICE,
            "tax_amount_rate": vars.DEFAULT_TAX_AMOUNT_RATE,
            "go_money": vars.DEFAULT_GO_MONEY,
            "maximum_rounds": vars.DEFAULT_MAXIMUM_ROUNDS,
            "minimum_player": vars.DEFAULT_MINIMUM_PLAYER,
            "maximum_player": vars.DEFAULT_MAXIMUM_PLAYER
        }

        # For Gameboard
        gameboard_design_selection = vars.handle_question_with_options('Load default design [0] or Load existing design [1] ', ['0', '1'])

        gameboard = Gameboard()
        if gameboard_design_selection == '0':
            gameboard.load_default_gameboard()

        if gameboard_design_selection == '1':
            while True:
                gameboard_design_file_name = input('Please insert gameboard design file name (<file_name>.json): [-1 to exit] ')
                if gameboard_design_file_name == '-1':
                    break
                try:
                    gameboard_design_path = vars.BASE_GAMEBOARD_DESIGN_DIR / gameboard_design_file_name
                    gameboard_design = json.load(open(gameboard_design_path, 'r'))
                    design_is_valid = check_design(gameboard_design)
                    if design_is_valid:
                        gameboard.load_design(gameboard_design)
                        break
                    else:
                        print('Invalid design!')
                        return False
                except:
                    continue


            if gameboard_design_file_name == '-1':
                print('User exits')
                return False

        self.gameboard = gameboard
        self.gameboard.game_id = self.game_state["game_id"]

        # For players
        while True:
            number_of_players = input(F'Please enter number of players ({self.game_parameters["minimum_player"]} - {self.game_parameters["maximum_player"]} players): ')
            try:
                if self.game_parameters["maximum_player"] >= float(number_of_players) >= self.game_parameters["minimum_player"] and float(number_of_players) == int(number_of_players):
                    number_of_players = int(number_of_players)
                    break
            except:
                continue

        players_list = []
        player_orders_list = [i for i in range(1, number_of_players + 1)]
        if self.game_parameters["random_player_orders"]:
            print('Player order will be shuffled in each round!')

        for idx, player_order in enumerate(player_orders_list):

            player_name = input(f'Please enter player name for order {idx+1}: [empty for randomly generated strings] ')

            if player_name == '':
                player_name = vars.secure_random_string(12)
            else:
                player_name = str(player_name)

            player_ = Player(player_name, gameboard.actual_layout['size'], self.game_state["game_id"])

            players_list.append(player_)

            self.player_orders.update({player_order: player_.id})

        self.players = {player.id: player for player in players_list}
        start_player_id = min([i for i in self.player_orders.keys()])
        self.game_state['current_player_id'] = self.player_orders[start_player_id]
        print(f'Game (game id: {self.game_state["game_id"]}) has created!')
        return True

    def load_game_state(self, save_file_name):
        try:
            save_path = vars.BASE_SAVE_STATE_PATH / save_file_name
            save_state = json.load(open(save_path, 'r'))
            self.game_state = save_state['game_state']
            self.player_orders = {int(k): v for k, v in save_state['player_orders'].items()}
            # For loading game parameter
            self.game_parameters = {
                "random_player_orders": save_state["game_parameters"]["random_player_orders"],
                "chance_multiplier": int(save_state["game_parameters"]["chance_multiplier"]),
                "jailbreak_price": int(save_state["game_parameters"]["jailbreak_price"]),
                "tax_amount_rate": float(save_state["game_parameters"]["tax_amount_rate"]),
                "go_money": int(save_state["game_parameters"]["go_money"]),
                "maximum_rounds": int(save_state["game_parameters"]["maximum_rounds"]),
                "minimum_player": int(save_state["game_parameters"]["minimum_player"]),
                "maximum_player": int(save_state["game_parameters"]["maximum_player"])
            }
            # For Loading Players
            players = {}
            for player_id, player in save_state['players'].items():
                player_ = Player('', 10, '')
                player_.name = player['name']
                player_.id = player['id']
                player_.location = player['location']
                player_.money = player['money']
                player_.owned_properties = [i for i in player['owned_properties']]  # Directly assign will lead to pass by reference
                player_.is_jailed = player['is_jailed']
                player_.jailed_rounds_count_down = player['jailed_rounds_count_down']
                player_.is_retired = player['is_retired']
                player_.gameboard_size = player['gameboard_size']
                player_.game_id = player['game_id']
                players.update({player_id: player_})
            self.players = players

            # For Loading Gameboard
            gameboard = Gameboard()
            gameboard_design = json.load(open(vars.BASE_GAMEBOARD_DESIGN_DIR / save_state['gameboard_parameters']['design_file_name'], 'r'))
            gameboard.load_design(gameboard_design)
            gameboard.design_file_name = save_state['gameboard_parameters']['design_file_name']
            gameboard.game_id = save_state['gameboard_parameters']['game_id']

            for player_id, player in players.items():
                for location in player.owned_properties:
                    gameboard.actual_layout['layout'][int(location)]['ownership'] = player_id
                    gameboard.actual_layout['layout'][int(location)]['owner_name'] = player.name

            self.gameboard = gameboard
            print(f'Successfully loaded game state from {save_path}')
            return True
        except Exception as e:
            print(f"Error loading save state: {e}")
            return False

    def save_game_state(self, save_file_name):
        save_path = vars.BASE_SAVE_STATE_PATH / save_file_name
        players = {}
        for player_id, player in self.players.items():
            player_ = {
                "name": player.name,
                "id": player.id,
                "location": player.location,
                "money": player.money,
                "owned_properties": [i for i in player.owned_properties],  # Directly assign will lead to pass by reference
                "is_jailed": player.is_jailed,
                "jailed_rounds_count_down": player.jailed_rounds_count_down,
                "is_retired": player.is_retired,
                "gameboard_size": player.gameboard_size,
                "game_id": player.game_id
            }
            players.update({player_id: player_})
        save_state = {
            'game_state': self.game_state,
            'player_orders': self.player_orders,
            'game_parameters': self.game_parameters,
            'players': players,
            'gameboard_parameters': {
                'design_file_name': self.gameboard.design_file_name,
                'game_id': self.gameboard.game_id
            }
        }
        json.dump(save_state, open(save_path, 'w'), indent=4)
        print(f'Saving game status to {save_path}')

    def play_one_round(self):

        print('\nRound: ', self.game_state["current_round"])

        current_player_orders = {k: v for k, v in self.player_orders.items() if k <= self.game_parameters["maximum_player"]}
        current_player_orders_keys = list(current_player_orders.keys())
        if not self.game_parameters["random_player_orders"]:
            current_player_orders_keys.sort()
        else:
            random.shuffle(current_player_orders_keys)

        for idx, current_player_order in enumerate(current_player_orders_keys):
            if not self.game_state["game_over"]:
                current_player = self.players[current_player_orders[current_player_order]]
                if idx < len(current_player_orders_keys) - 1:
                    next_player_order = current_player_orders_keys[idx + 1]
                    next_player_id = current_player_orders[next_player_order]
                else:
                    next_player_id = self.player_orders[min(self.player_orders.keys())]
                if current_player.is_retired:
                    pass

                else:
                    print(f'\n--> Current player: {current_player.name} (player id: {current_player.id})')
                    while True:

                        # Asking show status or continue
                        show_status_or_continue = vars.handle_question_with_options(f'<---- Show status [0], query next player [1] or continue [empty input] ? ', ['0', '1', '2', ''])

                        if show_status_or_continue == '':
                            break

                        elif show_status_or_continue == '1':
                            if not self.game_parameters["random_player_orders"]:
                                next_player = self.players[next_player_id]
                                print(f"\nNext Player: {next_player.name} (id: {next_player.id})\n")
                            else:
                                print(f"\nNext Player: ?\n")

                        else:
                            # Asking show what status
                            user_show_status_selection = vars.handle_question_with_options(f'<---- Show own status [0], specific player status [1], all players status [2], game status [3]? ', ['0', '1', '2', '3'])

                            if user_show_status_selection == '0':
                                self.show_player_status(current_player.id)

                            elif user_show_status_selection == '1':
                                while True:
                                    specific_user_id = input(f'<---- Input specific player id: [-1 to exit show status] ')
                                    if specific_user_id in [v for k, v in self.player_orders.items()] or specific_user_id == '-1':
                                        break

                                if specific_user_id != '-1':
                                    self.show_player_status(specific_user_id)

                            elif user_show_status_selection == '2':
                                self.show_all_players_status()

                            elif user_show_status_selection == '3':
                                self.show_game_status()

                    if current_player.is_jailed:
                        dice = current_player.jailbreak(self.game_parameters["jailbreak_price"])
                        if current_player.money <= 0:
                            self.retire_player(current_player)
                            self.check_only_player_is_left()
                            continue
                    else:
                        dice = current_player.roll_dice()

                    # Normal roll dice or jailbreak successful
                    if dice != [None, None]:
                        print(f"----> {current_player.name} 's dice: {dice}")
                        current_player.move(sum(dice))

                        if current_player.location > current_player.gameboard_size:
                            # Execute Go
                            self.gameboard.actual_layout['layout'][self.gameboard.go_location]['function'](current_player, self.game_parameters)
                            current_player.adjust_location()

                        current_location = self.gameboard.actual_layout['layout'][current_player.location]

                        print(f"----> {current_player.name} landed on {current_location['name']} (location: {current_player.location}).")
                        # Handle on landing on property square
                        if current_location['is_ownable'] and current_location['name'].lower() != 'go':
                            if not current_location['ownership'] and current_player.money > current_location['price']:
                                buy_property_selection = vars.handle_question_with_options(f'<---- {current_location["name"]} is not owned! Do you wanna buy it? [Y / n] ', ['y', 'n', ''])

                                if buy_property_selection == 'y' or buy_property_selection == '':
                                    current_player.buy_property(current_player.location, current_location['price'])
                                    self.change_property_ownership(current_player)
                                    print(f'----> {current_player.name} bought {current_location["name"]}!')
                            elif current_location['ownership'] and current_location['ownership'] != current_player.id:
                                print(f"----> {current_location['name']} is owned by {current_location['owner_name']}, ${current_location['rent']} will be charged!")
                                charged_amount = min([current_player.money, current_location['rent']])
                                self.players[current_location['ownership']].money += charged_amount
                                current_player.money -= charged_amount
                                if current_player.money <= 0:
                                    self.retire_player(current_player)
                                    self.check_only_player_is_left()
                                    continue
                            elif current_location['ownership'] and current_location['ownership'] == current_player.id:
                                print(f"----> {current_player.name} Home Sweet Home!")

                        # Handle on landing on jailed square
                        elif current_location['name'].lower() == 'go to jail':
                            current_location['function'](current_player, self.gameboard.jail_location)

                        elif current_location['name'].lower() != 'go':
                            current_location['function'](current_player, self.game_parameters)
                            if current_player.money <= 0:
                                self.retire_player(current_player)
                                self.check_only_player_is_left()
                                continue

    def play(self):

        save_game = vars.handle_question_with_options('\nDo you want to save the game? [y / N] ? ', ['y', 'n', ''])

        if save_game == 'y':
            save_file_name = vars.handle_question_with_function('Please enter save name [only alphanumeric characters and underscores, ends with .json]: ', vars.is_valid_save_file_name)
            self.save_game_state(save_file_name)
            continue_playing = vars.handle_question_with_options('Continue playing [Y / n] ? ', ['y', 'n', ''])

            if continue_playing == 'n':
                print('See you in the next game!')
                self.game_state["game_over"] = True

        while True and not self.game_state["game_over"]:
            self.play_one_round()
            self.game_state["current_round"] += 1

            save_game = vars.handle_question_with_options('\nDo you want to save the game? [y / N] ? ',['y', 'n', ''])
            if save_game == 'y':
                save_file_name = vars.handle_question_with_function('Please enter save name [only alphanumeric characters and underscores, ends with .json]: ', vars.is_valid_save_file_name)
                self.save_game_state(save_file_name)
                continue_playing = vars.handle_question_with_options('Continue playing [Y / n] ? ', ['y', 'n', ''])

                if continue_playing == 'n':
                    print('See you in the next game!')
                    self.game_state["game_over"] = True

            if self.game_state["current_round"] > self.game_parameters["maximum_rounds"] and not self.game_state["game_over"]:
                player_records = {player.name: player.money for player_id, player in self.players.items()}
                winners = [[name, amount] for name, amount in player_records.items() if amount == max(list(player_records.values()))]
                print(f'\nGame over after {self.game_parameters["maximum_rounds"]} rounds!')
                if len(winners) == 1:
                    print(f'Winner: {winners[0][0]}, Money: {winners[0][1]}')
                else:
                    for idx, winner in enumerate(winners):
                        print(f'Winner {idx+1}: {winner[0]}, Money: {winner[1]}')
                break

    def check_only_player_is_left(self):
        winners = [[player.name, player.money] for player_id, player in self.players.items() if not player.is_retired]
        if len(winners) == 1:
            self.game_state["game_over"] = True
            print('\nGame over when only one player is left!')
            print(f'Winner: {winners[0][0]}, Money: {winners[0][1]}')
