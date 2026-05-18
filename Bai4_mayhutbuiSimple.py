import numpy as np
import random

matrix = np.array([[random.randint(0, 1) for _ in range(4)] for _ in range(4)])

def p_move(x, y):
    moves = []
    if x > 0:
        moves.append("UP")
    if y > 0:
        moves.append("LEFT")
    if x < 3:
        moves.append("DOWN")
    if y < 3:
        moves.append("RIGHT")
    return moves

def vacuum(matrix):
    x = random.randint(0, 3)
    y = random.randint(0, 3)
    print(f"Vị trí ban đầu: ({x}, {y})")

    step = 0
    while True:
        moves = p_move(x, y)
        chosen = random.choice(moves)

        if matrix[x][y] == 1:
            print(f"Bước {step}: ({x},{y}) bẩn → hút bụi! Di chuyển: {chosen}")
            matrix[x][y] = 0
            print("S")
        else:
            print(f"Bước {step}: ({x},{y}) sạch. Di chuyển: {chosen}")
        print (matrix)

        if chosen == "UP":    x -= 1
        elif chosen == "DOWN":  x += 1
        elif chosen == "LEFT":  y -= 1
        elif chosen == "RIGHT": y += 1

        step += 1

        if not matrix.any():
            print("Tất cả ô đã sạch!")
            break

print("Ma trận ban đầu:")
print(matrix)
vacuum(matrix)