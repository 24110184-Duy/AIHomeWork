import numpy as np
import random

def generate_puzzle():
    tiles = list(range(9))
    random.shuffle(tiles)
    return np.array(tiles).reshape(3, 3)

def find_blank(puzzle):
    pos = np.argwhere(puzzle == 0)[0]
    return int(pos[0]), int(pos[1])

def p_move(x, y):
    moves = []
    if x > 0:
        moves.append("UP")
    if x < 2:
        moves.append("DOWN")
    if y > 0:
        moves.append("LEFT")
    if y < 2:
        moves.append("RIGHT")
    return moves

def apply_move(puzzle, x, y, move):
    new_puzzle = puzzle.copy()
    if move == "UP":
        new_puzzle[x][y], new_puzzle[x-1][y] = new_puzzle[x-1][y], new_puzzle[x][y]
        return new_puzzle, x-1, y
    elif move == "DOWN":
        new_puzzle[x][y], new_puzzle[x+1][y] = new_puzzle[x+1][y], new_puzzle[x][y]
        return new_puzzle, x+1, y
    elif move == "LEFT":
        new_puzzle[x][y], new_puzzle[x][y-1] = new_puzzle[x][y-1], new_puzzle[x][y]
        return new_puzzle, x, y-1
    elif move == "RIGHT":
        new_puzzle[x][y], new_puzzle[x][y+1] = new_puzzle[x][y+1], new_puzzle[x][y]
        return new_puzzle, x, y+1

def is_solved(puzzle):
    goal = np.array([[1,2,3],[4,5,6],[7,8,0]])
    return np.array_equal(puzzle, goal)

def eight_puzzle():
    puzzle = generate_puzzle()
    print("Trạng thái ban đầu:")
    print(puzzle)

    x, y = find_blank(puzzle)
    step = 0
    max_steps = 1000000
    while not is_solved(puzzle) and step < max_steps:
        moves = p_move(x, y)
        chosen = random.choice(moves)
        puzzle, x, y = apply_move(puzzle, x, y, chosen)
        step += 1
        print(f"Bước {step}: di chuyển {chosen}")
        print(puzzle)

    if is_solved(puzzle):
        print(f"Đã giải xong sau {step} bước!")
    else:
        print(f"Không tìm được lời giải sau {max_steps} bước.")

eight_puzzle()