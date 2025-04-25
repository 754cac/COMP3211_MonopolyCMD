import random
import vars


def go(player, game_parameters):
    print(f'!! Welcome Back {player.name}! Get ${game_parameters["go_money"]}!')
    player.money += game_parameters['go_money']


def income_tax(player, game_parameters):
    tax_amount = int((player.money * game_parameters["tax_amount_rate"]) // 10 * 10)
    print(f'!! {player.name} is being charged for ${tax_amount} as income tax!')
    player.money -= tax_amount


def chance(player, game_parameters):
    print(f'!! {player.name} got a Chance!')
    is_gain = random.choice([True, False])
    if is_gain:
        gain_money = game_parameters['chance_multiplier'] * random.choice(range(20))
        print(f'!! Yay! {player.name} got {gain_money}!')
        player.money += gain_money
    else:
        loss_money = game_parameters['chance_multiplier'] * random.choice(range(30))
        print(f'!! Ooops! {player.name} loss {loss_money}!')
        player.money -= loss_money


def free_parking(player, game_parameters):
    print(f'!! {player.name} is taking a break and Parking!')


def just_visiting_or_in_jail(player, game_parameters):
    if not player.is_jailed:
        print(f'!! {player.name} is visiting someone!')
    else:
        player.jailbreak(game_parameters['jailbreak_price'])


def go_to_jail(player, jail_location):
    if not player.is_jailed:
        player.jailed(jail_location)
        print(f'!! {player.name} is jailed!')
    else:
        print(f'!! {player.name} is jailed already!')


def retire(player):
    if not player.is_retired:
        player.retired()
        print(f'!! {player.name} is retired!')
    else:
        print(f'!! {player.name} is retired already!')


available_functions = {
    "Go": go,
    "Income Tax": income_tax,
    "Just Visiting / In Jail": just_visiting_or_in_jail,
    "Chance": chance,
    "Free Parking": free_parking,
    "Go To Jail": go_to_jail,
}
