"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy
import numpy as np
import random


X = "X"
O = "O"
EMPTY = None


def MAX_VALUE(state):
    if terminal(state):
        return utility(state)
    v = float('-inf')
    for action in actions(state):
        v = max(v, MIN_VALUE(result(state, action)))
    return v

    
def MIN_VALUE(state):
    if terminal(state):
        return utility(state)
    v = float('inf')
    for action in actions(state):
        v = min(v, MAX_VALUE(result(state, action)))
    return v
        
    
def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    count = 0
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] != EMPTY:
                count += 1
    
    if (count % 2) == 1:
        return O
    else:
        return X                    
            

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == EMPTY:
                actions.add((i, j))
    return actions            
 

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = deepcopy(board)
    if new_board[action[0]][action[1]] != EMPTY:
        raise Exception
    else:
        new_board[action[0]][action[1]] = player(board)
        return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # check the rows
    for i in range(len(board)):
        if len(set(board[i])) == 1:
            x = list(set(board[i]))
            if x[0] is not None:
                return x[0]
        
    # for columns
    for i in range(len(board)):
        result = []
        for j in range(len(board)):
            result.append(board[j][i])
        if len(set(result)) == 1 and result[0] is not None:
            return result[0]
    
    # for diagonals             
    l = len(board)
    diag_o = [board[i][i] for i in range(l)]
    if len(set(diag_o)) == 1 and diag_o[0] is not None:
        return diag_o[0]
    diag_t = [board[l-1-i][i] for i in range(l-1,-1,-1)]
    if len(set(diag_t)) == 1 and diag_t[0] is not None:
        return diag_t[0]         
    
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    initial_array = np.array(board)
    result = list(initial_array.flatten())
    
    if winner(board) is not None or result.count(None) == 0:
        return True
    else:
        return False
    

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    elif terminal(board):
        return 0
    

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if board == initial_state():
        return random.choice([(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)])
    
    if player(board) == X:
        v = float('-inf')
        act = None
        for action in actions(board):
            res = MIN_VALUE(result(board, action))
            if res >= v:
                v = res
                act = action
    
    elif player(board) == O:   
        v = float('inf')
        act = None
        for action in actions(board):
            res = MAX_VALUE(result(board, action))
            if res <= v:
                v = res
                act = action
    return act