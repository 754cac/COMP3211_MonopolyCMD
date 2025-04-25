import json
import pandas as pd
import vars
from functions import available_functions


def check_design(design):

    count = 0
    if design["enforce_square_design"]:
        if design["size"] % 4 != 0:
            print("Error: Board size must be multiple of 4 to enforce square gameboard design!")
            count += 1

    # Check if design size is bigger than the board size
    all_locations_indice = [i['location'] for i in design['properties']] + [i['location'] for i in design['functions']]
    for i in range(1, design["size"]+1):
        if i not in all_locations_indice:
            print("Error: There exist empty loactions or location index / size mismatch!")
            count += 1
            break

    # Check if design size is bigger than the board size
    if int(design['size']) != len(design['properties']) + len(design['functions']):
        print("Error: Board Size must be equal to sum of properties and functions!")
        count += 1

    # Check if any field is empty
    break_all_loops = False
    for item in ['properties', 'functions']:
        for row in design[item]:
            for k, v in row.items():
                if k == '' or v == '':
                    print("Error: There exist empty field in gameboard design.")
                    count += 1
                    break_all_loops = True
                    break
            if break_all_loops:
                break
        if break_all_loops:
            break

    # Check if locations are unique:
    locations = [row['location'] for row in design['properties']]
    if len(locations) - len(set(locations)) > 0:
        print("Error: Duplicate locations detected.")
        count += 1

    # Check if Properties location are unique:
    properties_names = [row['name'] for row in design['properties']]
    if len(properties_names) - len(set(properties_names)) > 0:
        print("Error: Duplicate property name detected.")
        count += 1

    # Check if Just Visiting / In Jail exist if Go To Jail Exist
    functions_names = [row['name'] for row in design['functions']]
    if "Go To Jail" in functions_names and not "Just Visiting / In Jail" in functions_names:
        print("Error: Just Visiting / In Jail needs to exist if Go To Jail exists")
        count += 1

    if "Go" not in functions_names:
        print("Error: Go does not exist.")
        count += 1

    if count == 0:
        print("Design is valid!")
        return True

    return False


class Gameboard:

    def __init__(self):
        # self.__design = {}
        self.actual_layout = {}
        self.game_id = None
        self.go_location = None
        self.jail_location = None
        self.design_file_name = None
        self.square_size = None

    def load_default_gameboard(self):

        default_design_path = vars.DEFAULT_GAMEBOARD_DESIGN_PATH
        default_design = {}
        if default_design_path.is_file():
            try:
                default_design = json.load(open(default_design_path, "r"))
                self.design_file_name = default_design_path.name
            except:
                default_design = {}

        if not check_design(default_design):
            self.actual_layout = {} 
            return

        # self.__design = default_design

        layout = {}
        for row in default_design['properties']:
            layout.update({
                int(row['location']): {
                    "name": row['name'],
                    "price": row['price'],
                    "rent": row['rent'],
                    "is_ownable": row['is_ownable'],
                    "ownership": None,
                    "owner_name": ''
                }
            })
        for row in default_design['functions']:

            if row['name'].lower() == 'go':
                self.go_location = int(row['location'])
            elif row['name'].lower() == 'just visiting / in jail':
                self.jail_location = int(row['location'])

            try:
                layout.update({
                    int(row['location']): {
                        "name": row['name'],
                        "function": available_functions[row['name']],
                        "is_ownable": row['is_ownable']
                    }
                })
            except KeyError:
                print('Function is not defined :', row['name'])
        self.actual_layout = {
            'size': default_design['size'],
            "layout": layout
        }

    def load_design(self, design):
        layout = {}
        for row in design['properties']:
            layout.update({
                int(row['location']): {
                    "name": row['name'],
                    "price": row['price'],
                    "rent": row['rent'],
                    "is_ownable": row['is_ownable'],
                    "ownership": None,
                    "owner_name": ''
                }
            })
        for row in design['functions']:

            if row['name'].lower() == 'go':
                self.go_location = int(row['location'])
            elif row['name'].lower() == 'just visiting / in jail':
                self.jail_location = int(row['location'])

            try:
                layout.update({
                    int(row['location']): {
                        "name": row['name'],
                        "function": available_functions[row['name']],
                        "is_ownable": row['is_ownable']
                    }
                })
            except KeyError:
                print('Function is not defined :', row['name'])
        self.actual_layout = {
            'size': design['size'],
            "layout": layout
        }

    @staticmethod
    def square_checker(square, square_type='property'):
        if square_type not in ['property', 'function']:
            raise ValueError("Square type must be property or function.")
        if square_type == 'property':
            property_square_type = {
                "location": int,
                "name": str,
                "price": int,
                "rent": int,
                "role": str,
                "is_ownable": bool
            }
            assert square.keys() == property_square_type.keys()
            for k, v in property_square_type.items():
                assert type(square[k]) == v

        else:
            function_square_type = {
                "location": int,
                "name": str,
                "role": str,
                "is_ownable": bool
            }
            assert square.keys() == function_square_type.keys()
            for k, v in function_square_type.items():
                assert type(square[k]) == v

        return True

    @staticmethod
    def start_or_load_design_gameboard():

        start_or_load = vars.handle_question_with_options("Start a new design [0] or Load an existing design [1] ? ", ['0', '1'])
        if start_or_load == '0':

            save_file_name = vars.handle_question_with_function("Enter the name of the saved gameboard design: ", vars.is_valid_save_file_name)
            save_file_path = vars.BASE_GAMEBOARD_DESIGN_DIR / save_file_name
            gameboard_size = int(vars.handle_question_with_function("Enter the size of the gameboard design: ", vars.is_valid_type, [int]))
            enforce_square_design = vars.SQUARE_DESIGN
            new_design = {
                "enforce_square_design": enforce_square_design,
                "size": gameboard_size,
                "properties": [],
                "functions": [],
            }
        else:
            design_file_name = vars.handle_question_with_function("Enter existing design file name : ", vars.is_valid_save_file_name)
            save_file_path = vars.BASE_GAMEBOARD_DESIGN_DIR / design_file_name
            try:
                new_design = json.load(open(save_file_path, 'r'))
            except:
                print("Design file does not exist!")
                print("Initialize a new design!")
                gameboard_size = int(vars.handle_question_with_function("Enter the size of the gameboard design: ", vars.is_valid_type,[int]))
                enforce_square_design = vars.SQUARE_DESIGN
                new_design = {
                    "enforce_square_design": enforce_square_design,
                    "size": gameboard_size,
                    "properties": [],
                    "functions": [],
                }
        '''
        blank_property_square = {
            "location": None,
            "name": None,
            "price": None,
            "rent": None,
            "role": None,
            "is_ownable": None
        },
        blank_function_square = {
            "location": None,
            "name": None,
            "role": None,
            "is_ownable": None
        }
        '''

        while True:
            cell_type = vars.handle_question_with_options("Edit a property [0], Edit a function [1], change gameboard size [2], view current design [3], check design for validity [4], discard design [5] and save & exit [empty]: ", ['0', '1', '2', '3', '4', '5', ''])

            properties_dict = {row['location']: row for row in new_design['properties']}
            available_property_locations_for_update = list(properties_dict.keys())
            available_property_locations_for_update.sort()

            functions_dict = {row['location']: row for row in new_design['functions']}
            available_function_locations_for_update = list(functions_dict.keys())
            available_function_locations_for_update.sort()

            available_locations_for_insert = [i for i in range(1, new_design['size']+1) if i not in available_property_locations_for_update and i not in available_function_locations_for_update]

            if cell_type == '':
                json.dump(new_design, open(save_file_path, 'w'), indent=4)
                print(f"Design file saved : {save_file_path}")
                break
            elif cell_type == '0':
                property_selection = vars.handle_question_with_options("Insert a property [0], Update a property [1] , Delete a property [2] or up a level [empty]: ", ['0', '1', '2', ''])
                if property_selection == '0':
                    print(f'Available locations: {available_locations_for_insert}')
                    location = int(vars.handle_question_with_function('Enter the location of the property: ', vars.is_valid_type, [int]))
                    if location in available_locations_for_insert:
                        name = vars.handle_question_with_function('Enter the name of the property: ', vars.is_valid_type, [str])
                        price = int(vars.handle_question_with_function('Enter the price of the property: ', vars.is_valid_type, [int]))
                        rent = int(vars.handle_question_with_function('Enter the rent of the property: ', vars.is_valid_type, [int]))
                        role = "property"
                        is_ownable = vars.handle_question_with_function('Is the property ownable ? ', vars.is_valid_type, [bool])
                        new_property_square = {
                            "location": int(location),
                            "name": name,
                            "price": int(price),
                            "rent": int(rent),
                            "role": role,
                            "is_ownable": is_ownable
                        }
                        properties_dict.update({location: new_property_square})
                        properties = [v for k, v in properties_dict.items()]
                        new_design['properties'] = properties
                    else:
                        print(f'Can not insert to an existing property / function!')

                elif property_selection == '1':
                    print(f'Available locations: {available_property_locations_for_update}')
                    location_selection = int(vars.handle_question_with_function('Enter the location to update: ', vars.is_valid_type, [int]))
                    if location_selection in available_property_locations_for_update:
                        original_location = properties_dict[location_selection]['location']
                        original_name = properties_dict[location_selection]['name']
                        original_price = properties_dict[location_selection]['price']
                        original_rent = properties_dict[location_selection]['rent']
                        original_is_ownable = properties_dict[location_selection]['is_ownable']

                        location = vars.handle_question_with_function('Update the location of the property [enter new value to update or empty to keep the old]: ', vars.is_valid_type, [int, True])
                        name = vars.handle_question_with_function('Update the name of the property [enter new value to update or empty to keep the old] : ', vars.is_valid_type, [str, True])
                        price = vars.handle_question_with_function('Update the price of the property [enter new value to update or empty to keep the old] : ', vars.is_valid_type, [int, True])
                        rent = vars.handle_question_with_function('Update the rent of the property [enter new value to update or empty to keep the old] : ', vars.is_valid_type, [int, True])
                        is_ownable = vars.handle_question_with_function('Is the property ownable [enter new value to update or empty to keep the old] ? ', vars.is_valid_type, [bool, True])

                        existing_property_square = {
                            "location": int(original_location if location == '' else location),
                            "name": original_name if name == '' else name,
                            "price": int(original_price if price == '' else price),
                            "rent": int(original_rent if rent == '' else rent),
                            "role": 'property',
                            "is_ownable": original_is_ownable if is_ownable == '' else is_ownable
                        }
                        if location == '':
                            properties_dict.update({original_location: existing_property_square})
                        else:
                            properties_dict.update({location: existing_property_square})
                            del properties_dict[original_location]

                        properties = [v for k, v in properties_dict.items()]
                        new_design['properties'] = properties
                    else:
                        print(f'Can not update non existing property!')

                elif property_selection == '2':
                    print(f'Available locations: {available_property_locations_for_update}')
                    location_selection = int(vars.handle_question_with_function('Enter the location to delete: ', vars.is_valid_type, [int]))
                    if location_selection in available_property_locations_for_update:
                        del properties_dict[location_selection]
                        properties = [v for k, v in properties_dict.items()]
                        new_design['properties'] = properties
                    else:
                        print(f'Can not delete non existing property!')

            elif cell_type == '1':
                function_selection = vars.handle_question_with_options("Insert a function [0], Delete a function [1] or up a level [empty]: ", ['0', '1', ''])

                if function_selection == '0':
                    print(f'Available locations: {available_locations_for_insert}')
                    location = int(vars.handle_question_with_function('Enter the location of the function: ', vars.is_valid_type, [int]))
                    if location in available_locations_for_insert:
                        name = vars.handle_question_with_options('Enter the name of the function: ',  [i for i in available_functions.keys()], True)
                        role = "function"
                        is_ownable = False
                        new_function_square = {
                            "location": int(location),
                            "name": name,
                            "role": role,
                            "is_ownable": is_ownable
                        }
                        new_design['functions'].append(new_function_square)
                    else:
                        print(f'Can not insert to an existing property / function!')

                elif function_selection == '1':
                    print(f'Available locations: {available_function_locations_for_update}')
                    location_selection = int(vars.handle_question_with_function('Enter the location to delete: ', vars.is_valid_type, [int]))
                    if location_selection in available_function_locations_for_update:
                        del functions_dict[location_selection]
                        functions = [v for k, v in functions_dict.items()]
                        new_design['functions'] = functions
                    else:
                        print(f'Can not delete non existing function!')

            elif cell_type == '2':
                gameboard_size = int(vars.handle_question_with_function("Update the size of the gameboard design: ", vars.is_valid_type, [int]))
                new_design['size'] = gameboard_size

            elif cell_type == '3':
                squares = []
                for property_square in new_design['properties']:
                    square = {
                        'Location': property_square['location'],
                        'Name': property_square['name'],
                        'Role': 'property',
                        'Price': property_square['price'],
                        'Rent': property_square['rent'],
                    }
                    squares.append(square)

                for function_square in new_design['functions']:
                    square = {
                        'Location': function_square['location'],
                        'Name': function_square['name'],
                        'Role': 'function',
                        'Price': '-',
                        'Rent': '-',
                    }
                    squares.append(square)

                squares = sorted(squares, key=lambda x: x['Location'])
                gameboard_df = pd.DataFrame(squares)
                pd.set_option('display.max_rows', None)  # Show all rows
                pd.set_option('display.max_columns', None)  # Show all columns
                pd.set_option('display.max_colwidth', None)  # Show full column content
                if len(gameboard_df) > 0:
                    print(f'\nGameboard Size: {new_design["size"]}\nGameboard Status: \n', gameboard_df.to_string(index=False), '\n')
                else:
                    print('\nGameboard Size: 0\nGameboard Status: \n', 'Empty', '\n')

            elif cell_type == '4':
                check_design(new_design)

            elif cell_type == '5':
                print("Discard current design!")
                break



