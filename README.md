# MonopolyCMD

## Overview

MonopolyCMD (MCMD) is a command-line implementation of the classic Monopoly board game, designed for multiplayer gameplay using Python. This document outlines the system requirements, features, and instructions for players and gameboard designers.

## Features

### Functional Requirements

1. **Game Start**  
   - Start a new game with a predefined gameboard (REQ-001).
   - Players can name themselves using input or random strings (REQ-002).

2. **Gameplay Mechanics**  
   - Roll dice and move tokens (REQ-003).
   - Buy properties on unowned squares (REQ-004).
   - Pay rent on properties owned by others (REQ-005).
   - Handle special squares according to game rules (REQ-006).

3. **Game State Management**  
   - Save the game state to a JSON file (REQ-007).
   - Load a game state from a JSON file (REQ-008).

4. **Status Queries**  
   - View personal and other players' statuses (REQ-009).
   - See overall game status, including squares and player positions (REQ-010).

5. **Designing Gameboards**  
   - Create and organize squares (REQ-011).
   - Load and customize existing gameboards (REQ-012).
   - Save designed gameboards (REQ-013).

## System Architecture

<p align="center">
<img src="./Report/Design document/Architecture.png" alt="MonopolyCMD Architecture" width="150">
</p>

MonopolyCMD follows the Model-View-Controller (MVC) pattern, enhancing maintainability and scalability.

1. **Model**: 
   - Stores game data and board design in a JSON file, allowing players to save progress and resume later.

2. **View**: 
   - The Var class handles user input and validation, displaying game information and prompting player actions.

3. **Controller**: 
   - The Game class manages interactions between the model and view, processing user inputs and enforcing game rules.

### Class Diagram

<p align="center">
<img src="./Report/Design document/Class.png" alt="MonopolyCMD Class Diagram" width="738">
</p>

## Class Responsibilities

### 1 Class: Main
- Starts the game model and initializes the application.

### 2 Class: Model
- Selects the mode for player engagement (Play or Design) and manages user input.

### 3 Class: Game
- Manages the overall state and mechanics of the game, including player turns and transactions.

### 4 Class: Gameboard
- Manages the layout and design of the gameboard, including loading and saving designs.

### 5 Function: check_design
- Validates the gameboard design against required specifications.

### 6 Class: Player
- Represents a player, managing attributes like location, money, and owned properties.

### Turn Activity Diagram

<p align="center">
<img src="./Report/Design document/TurnActivity.png" alt="Turn Activity Diagram" width="738">
</p>

#### Overview
The activity diagram illustrates the flow of actions during a player's turn, capturing decision points and actions based on the square landed on.

#### Activities and Flow
1. **Start of Player's Turn**: The player begins their turn.
2. **Player Actions**: Options include showing status, querying the next player, or rolling dice.
3. **After Rolling Dice**: The player may land on various square types, each with specific actions (e.g., buying properties, paying rent, or going to jail).
4. **If Sent to Jail**: The player can pay a fine, roll for a double, or retire if unable to pay.
5. **End of Player's Turn**: The turn ends after completing actions based on the square landed on.

### Non-Functional Requirements

- Respond to user commands within 1 second (REQ-014).
- Save and load game state within 2 seconds (REQ-015).
- Provide clear error messages for invalid commands (REQ-016).
- Offer help instructions for all commands (REQ-017).
- Ensure JSON files are not corrupted during saves (REQ-018).
- Handle exceptions gracefully during load operations (REQ-019).
- Ensure compatibility with Windows operating systems (REQ-020).

### System Interfaces

- Save and load game states to/from JSON files (REQ-021).
- Support user interactions and input commands (REQ-022).

## Getting Started

### Prerequisites

- Ensure you have Python installed on your machine.

### Installation

1. Download the MonopolyCMD source code from GitHub.
2. Unzip the downloaded file into a desired folder on your PC.

### Setting Up a Python Environment for MonopolyCMD

To ensure a smooth experience while running MonopolyCMD, it's recommended to create a dedicated Python environment. Follow these steps to set it up:

#### Step 1: Install Python

Make sure you have Python installed on your system. You can download it from the [official Python website](https://www.python.org/downloads/).

#### Step 2: Install Virtualenv

To create a virtual environment, you'll need `virtualenv`. You can install it using pip:
```bash
pip install virtualenv
```
Step 3: Create a Virtual Environment
Navigate to the directory where you want to create your virtual environment and run:

```bash
virtualenv mc_env
```
Step 4: Activate the Virtual Environment
On Windows:
```bash
mc_env\Scripts\activate
```
Step 5: Install Required Packages
If there are any specific packages required for MonopolyCMD, install them using pip. For example:

```bash
pip install -r requirements.txt
```
Running the Game
Open the Windows Command Prompt or Windows PowerShell.
Navigate to the directory where you unzipped the code.
Run the following command to start the game:
```bash
python main.py
```
### Gameplay Instructions
Upon starting, players can choose to start a new game or load an existing one.
Players can check various statuses, roll dice, and manage their properties through simple commands.
Designing Gameboards
Gameboard designers can create or edit gameboards by selecting the design option at the start, following prompts to insert, update, or delete properties.
