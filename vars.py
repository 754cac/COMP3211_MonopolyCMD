import pathlib as pl
import json
import string
import random
import re


def secure_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def is_valid_save_file_name(s):
    pattern = r'^[\w]+\.json$'
    return bool(re.match(pattern, s))


def is_valid_type(s, type_functions):
    try:
        if len(type_functions) > 1 and type_functions[1]:
            return s == '' or (type_functions[0](s) and type(type_functions[0](s)) == type_functions[0])
        else:
            return type_functions[0](s) and type(type_functions[0](s)) == type_functions[0]
    except Exception as e:
        print(f'Non valid entry: {e}')

    return False

def handle_question_with_options(question, options, case_sensitive=False):
    while True and len(options) > 0:
        answer = input(question)
        if case_sensitive:
            if answer in options:
                return answer
        else:
            if answer.lower() in options:
                return answer.lower()


def handle_question_with_function(question, check_function, extra_input=[]):
    while True and check_function is not None:
        answer = input(question)
        if len(extra_input) > 0:
            if check_function(answer, extra_input):
                return answer
        else:
            if check_function(answer):
                return answer


SQUARE_DESIGN = True
BASE_GAMEBOARD_DESIGN_DIR = pl.Path.cwd() / "data" / "gameboard_design"
BASE_GAMEBOARD_DESIGN_DIR.mkdir(exist_ok=True)
BASE_SAVE_STATE_PATH = pl.Path.cwd() / "data" / "save_state"
DEFAULT_GAMEBOARD_DESIGN_PATH = BASE_GAMEBOARD_DESIGN_DIR / "default_gameboard.json"
DEFAULT_GAMEBOARD_DESIGN = {}
if DEFAULT_GAMEBOARD_DESIGN_PATH.is_file():
    try:
        DEFAULT_GAMEBOARD_DESIGN = json.load(open(DEFAULT_GAMEBOARD_DESIGN_PATH, "r"))
    except:
        DEFAULT_GAMEBOARD_DESIGN = {}

DEFAULT_RANDOM_PLAYER_ORDERS = False
DEFAULT_CHANCE_MULTIPLIER = 10 # Default 10
DEFAULT_JAILBREAK_PRICE = 150
DEFAULT_TAX_AMOUNT_RATE = 0.1 # Default 0.1
DEFAULT_GO_MONEY = 1500 # 1500
DEFAULT_MAXIMUM_ROUNDS = 100
DEFAULT_MINIMUM_PLAYER = 2
DEFAULT_MAXIMUM_PLAYER = 6
PLAYER_DEFAULT_PROPERTIES = {
    "location": 1,
    "money": 1500,
    "owned_properties": [],
    "is_jailed": False,
    "jailed_rounds_count_down": 3,
    "is_retired": False
}

DEFAULT_FUNCTIONS_LIST = ["Go", "Income Tax", "Just Visiting / In Jail", "Chance", "Free Parking", "Go To Jail"]

TITLE_TEXT = '''
 __    __     ______     __   __     ______     ______   ______     __         __  __    
/\ "-./  \   /\  __ \   /\ "-.\ \   /\  __ \   /\  == \ /\  __ \   /\ \       /\ \_\ \   
\ \ \-./\ \  \ \ \/\ \  \ \ \-.. \  \ \ \/\ \  \ \  _-/ \ \ \/\ \  \ \ \____  \ \____ \  
 \ \_\ \ \_\  \ \_____\  \ \_\  \_\  \ \_____\  \ \_\    \ \_____\  \ \_____\  \/\_____\ 
  \/_/  \/_/   \/_____/   \/_/ \/_/   \/_____/   \/_/     \/_____/   \/_____/   \/_____/ 
                                                                                         
'''
