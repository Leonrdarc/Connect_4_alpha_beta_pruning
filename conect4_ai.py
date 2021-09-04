import numpy as np
import math
import random

# Definiciones de ciertas constantes para mejor legibilidad del código
ROW_COUNT = 6
COLUMN_COUNT = 7
EMPTY = "_"
MAX_PLAYER = "X"
MIN_PLAYER = "O"
WINDOW_LENGTH = 4
DEPTH = 3
INDENTATION_SPACING=9
MAX_PLAYER_TURN = False

# Crea el tablero que está representado en una matriz
def create_board():
    board = np.array(
        [['_', '_', '_', '_', '_', '_', '_'],
         ['_', '_', '_', '_', '_', '_', '_'],
         ['_', '_', '_', '_', '_', '_', '_'],
         ['_', '_', '_', '_', '_', '_', '_'],
         ['_', '_', '_', 'O', 'X', '_', '_'],
         ['_', '_', '_', 'O', 'X', '_', '_']]
    )
    return np.flip(board, 0)

# Muestra el tablero(matriz) invertido para que se vea como el juego real
def print_board(board, depth):
    indendation = '\t'*(depth-1)*INDENTATION_SPACING
    print(indendation+str(np.flip(board, 0)).replace('\n', '\n'+indendation), "\n")

# Asigna la ficha a la columna escogida en la fila disponible
def drop_piece(board, row, col, piece):
    board[row][col] = piece

# Verifica si en esa columna se puede poner una ficha
def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == EMPTY

# Obtiene la fila disponible en la columna dada
def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == EMPTY:
            return r

# Verifica si el jugador ha ganado
def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Check positively sloped diaganols
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Check negatively sloped diaganols
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True


# Determina si está en un nodo terminal (donde alguien gana)
def is_terminal_node(board):
    return winning_move(board, MIN_PLAYER) or winning_move(board, MAX_PLAYER) or len(get_valid_locations(board)) == 0

# Obtiene las posiciones disponibles
def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

# Algoritmo minimax con poda alfa beta
def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, MAX_PLAYER):
                return (None, 100000000000000)
            elif winning_move(board, MIN_PLAYER):
                return (None, -10000000000000)
            else:  # Game is over, no more valid
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, MAX_PLAYER))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, MAX_PLAYER)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]

            print_board(b_copy, depth) 

            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                print("Poda Alfa con α=", alpha, "y β=", beta)
                break
        return column, value

    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, MIN_PLAYER)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                print("Poda Beta con α=", alpha, "y β=", beta)
                break
            print_board(b_copy, depth)
        return column, value


# Funcion heuristica para evaluar tablero
def score_position(board, piece):
    score = 0

    # Score center column
    center_array = [i for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [i for i in list(board[r, :])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [i for i in list(board[:, c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score posiive sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


def evaluate_window(window, piece):
    score = 0
    opp_piece = MAX_PLAYER if piece == MIN_PLAYER else MIN_PLAYER

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score


# Se inicializan todos los recursos
board = create_board()
best_col, value = minimax(board, DEPTH, -math.inf, math.inf, MAX_PLAYER_TURN)
print_board(board, DEPTH+1)

print("La jugada mas favorable para el jugador", "MAX" if MAX_PLAYER_TURN else "MIN" ,"es en la columna:",
      best_col + 1, "con valor de heuristica:", value)

best_row = get_next_open_row(board, best_col)
drop_piece(board, best_row, best_col, MAX_PLAYER if MAX_PLAYER_TURN else MIN_PLAYER)
print_board(board, 0)