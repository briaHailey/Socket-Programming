"""
Name: Bria Weisblat
Date: 10/23/24
Assignment: Assignment #4
Due Date: 10/30/24
About this project: This project allows two people to play Tic-Tac-Toe over the internet. This
project uses socket programming to establish a server and a client that send moves back and
forth to play Tic-Tac-Toe.
Assumptions: Assume players take turns properly and in order. Assume the connection will not
be lost mid-game. Assume the client and server will not crash.
All work below was performed solely by Bria Weisblat.
"""

from socket import *
import sys

def display_board(board):
    print("  1 2 3")
    print("A " + ' '.join(board[0]))
    print("B " + ' '.join(board[1]))
    print("C " + ' '.join(board[2]))

def convert_move_to_index(move):
    # Dict that converts row letter into an index
    row_map = {'A': 0, 'B': 1, 'C': 2}

    # Dict that converts column number into an index
    col_map = {'1': 0, '2': 1, '3': 2}

    # If the entered move is valid
    if len(move) == 2 and move[0] in row_map and move[1] in col_map:
        # Convert the row move
        row = row_map[move[0]]
        # Convert the column move
        col = col_map[move[1]]
        # Return the row and column
        return row, col
    # For an invalid move
    return -1, -1

def check_done(board):
    # Check rows and columns
    for i in range(3):
        # Check each row for a '#' win
        if all(cell == '#' for cell in board[i]):
            return '#'
        # Check each column for a '#' win
        if all(board[j][i] == '#' for j in range(3)):
            return '#'
        # Check each row for a 'O' win
        if all(cell == 'O' for cell in board[i]):
            return 'O'
        # Check each column for a 'O' win
        if all(board[j][i] == 'O' for j in range(3)):
            return 'O'

    # Check first diagonal for '#' win
    if all(board[i][i] == '#' for i in range(3)):
        return '#'
    # Check second diagonal for '#' win
    if all(board[i][2 - i] == '#' for i in range(3)):
        return '#'
    # Check first diagonal for 'O' win
    if all(board[i][i] == 'O' for i in range(3)):
        return 'O'
    # Check second diagonal for 'O' win
    if all(board[i][2 - i] == 'O' for i in range(3)):
        return 'O'

    # Check for a tie
    if all(cell in ['#', 'O'] for row in board for cell in row):
        return 'TIE'

    # The game is not over yet
    return None


def play_game(client_socket):
    # Create the starting board
    board = [['.' for _ in range(3)] for _ in range(3)]
    print("Waiting for opponent's first move. Don't type anything!")

    while True:
        # Get the client's move
        data = client_socket.recv(1024).decode()

        # Convert the move to index form
        move_row, move_col = convert_move_to_index(data)

        # Update the board with the client's move
        board[move_row][move_col] = '#'
        display_board(board)

        # Check if the game is over
        result = check_done(board)

        # Send the updated board to the client
        client_socket.send(''.join([''.join(row) for row in board]).encode())

        if result:
            display_board(board)
            message = "Player '{}' wins!".format(result) if result != 'TIE' else "It's a tie!"
            client_socket.send(message.encode())
            break

        # Prompt the server user to enter a move
        player_move = input(f"Opponent played {move_row}{move_col}. Your move ([ABC][123]): ").strip().upper()

        # Convert the move to index form
        move_row, move_col = convert_move_to_index(player_move)

        # Update the board with the server's move
        board[move_row][move_col] = 'O'
        display_board(board)

        # Send the server's move to the client
        client_socket.send(''.join([''.join(row) for row in board]).encode())

        client_socket.send(player_move.encode())

        # Check if the game is over after your move
        result = check_done(board)
        if result:
            display_board(board)
            print("Player '{}' wins!".format(result) if result != 'TIE' else "It's a tie!")
            break

# Count the number of command line arguments
n = len(sys.argv)

# If there is not one command line argument
if n != 2:
    # Print error message
    print("Usage: server_port")
    exit()

# Create a socket
s = socket()
# Get the hostname of the machine that the server is running on
h = gethostname()

# Convert the port number from a string to an int
port = int(sys.argv[1])

# Bind the socket to the address and the port
s.bind((h, port))

# Listen for connections
s.listen(1)

# Print the name of the script and the port number
print(f"{sys.argv[0]} {sys.argv[1]}")

# Loop to wait for another connection when the client exists after a game is completed
while True:
        print("Waiting for opponent to connect....")
        client_socket, addr = s.accept()
        print(f"Receive opponent connection from {addr}")
        play_game(client_socket)
        client_socket.close()
