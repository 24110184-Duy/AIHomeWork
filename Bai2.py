GOAL = "123456780"
def print_board(state):

    print(state[0], state[1], state[2])
    print(state[3], state[4], state[5])
    print(state[6], state[7], state[8])
    print()
def move_up(state):
    zero = state.index('0')
    if zero not in [0, 1, 2]:
        state = list(state)
        state[zero], state[zero - 3] = (
            state[zero - 3],
            state[zero]
        )
        return ''.join(state)
    return state
def move_down(state):
    zero = state.index('0')
    if zero not in [6, 7, 8]:
        state = list(state)
        state[zero], state[zero + 3] = (
            state[zero + 3],
            state[zero]
        )
        return ''.join(state)
    return state
def move_left(state):
    zero = state.index('0')
    if zero not in [0, 3, 6]:
        state = list(state)
        state[zero], state[zero - 1] = (
            state[zero - 1],
            state[zero]
        )
        return ''.join(state)
    return state
def move_right(state):
    zero = state.index('0')
    if zero not in [2, 5, 8]:
        state = list(state)
        state[zero], state[zero + 1] = (
            state[zero + 1],
            state[zero]
        )
        return ''.join(state)
    return state
def simple_reflex_agent(state):
    zero = state.index('0')
    # RULE 1: ĐÃ ĐẠT GOAL
    if state == GOAL:
        return state

    # RULE 2
    if zero == 0:
        return move_right(state)

    # RULE 3
    if zero == 1:
        return move_right(state)

    # RULE 4
    if zero == 2:
        return move_down(state)

    # RULE 5
    if zero == 3:
        return move_right(state)

    # RULE 6
    if zero == 4:
        return move_right(state)

    # RULE 7
    if zero == 5:
        return move_down(state)

    # RULE 8
    if zero == 6:
        return move_right(state)

    # RULE 9
    if zero == 7:
        return move_right(state)

    # RULE 10
    return state
state = input("NHAP TRANG THAI BAN DAU (0 LA O TRONG): ")

print("\nTRANG THAI BAN DAU:\n")
print_board(state)

# CHẠY AGENT
for step in range(20):
    new_state = simple_reflex_agent(state)
    print("BUOC", step + 1)
    print_board(new_state)
    if new_state == GOAL:
        print("DA TIM THAY GOAL!")
        break
    state = new_state
else:
    print("KHONG TIM THAY GOAL!")