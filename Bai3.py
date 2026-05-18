import random
GOAL = "123456780"
visited = []
def print_board(state):
    print(state[0], state[1], state[2])
    print(state[3], state[4], state[5])
    print(state[6], state[7], state[8])
    print()
def random_state():
    numbers = [str(i) for i in range(9)]
    random.shuffle(numbers)
    return ''.join(numbers)
def move_up(state):
    zero = state.index('0')
    if zero not in [0, 1, 2]:
        state = list(state)
        state[zero], state[zero - 3] = (
            state[zero - 3],
            state[zero]
        )
        return ''.join(state)
    return None
def move_down(state):
    zero = state.index('0')
    if zero not in [6, 7, 8]:
        state = list(state)
        state[zero], state[zero + 3] = (
            state[zero + 3],
            state[zero]
        )
        return ''.join(state)
    return None
def move_left(state):
    zero = state.index('0')
    if zero not in [0, 3, 6]:
        state = list(state)
        state[zero], state[zero - 1] = (
            state[zero - 1],
            state[zero]
        )
        return ''.join(state)
    return None
def move_right(state):
    zero = state.index('0')
    if zero not in [2, 5, 8]:
        state = list(state)
        state[zero], state[zero + 1] = (
            state[zero + 1],
            state[zero]
        )
        return ''.join(state)
    return None
def model_based_reflex_agent(state):
    if state == GOAL:
        return state
    visited.append(state)
    possible_moves = [
        move_up(state),
        move_down(state),
        move_left(state),
        move_right(state)
    ]
    for new_state in possible_moves:
        if new_state is not None and new_state not in visited:
            return new_state
    return state
state = random_state()
print("TRANG THAI BAN DAU:\n")
print_board(state)
for step in range(30):
    new_state = model_based_reflex_agent(state)
    print("BUOC", step + 1)
    print_board(new_state)
    if new_state == GOAL:
        print("DA TIM THAY GOAL!")
        break
    state = new_state
else:
    print("KHONG TIM THAY GOAL!")