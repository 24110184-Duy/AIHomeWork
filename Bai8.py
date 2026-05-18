import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import random
import threading
import time

# =====================================================
# COLORS (modern dark theme)
# =====================================================
BG = "#0f172a"          # dark slate
FRAME = "#1e293b"       # lighter slate
BTN = "#3b82f6"         # bright blue
BTN_HOVER = "#2563eb"
TEXT = "#f8fafc"
EMPTY = "#334155"        # empty cell
TILE = "#38bdf8"         # cyan tile
TILE_NUM = "#0f172a"
ACCENT = "#f59e0b"       # amber accent
LOG_BG = "#0f172a"
LOG_FG = "#a5f3fc"

# =====================================================
# DEFAULT GOAL
# =====================================================
DEFAULT_GOAL = (
    1, 2, 3,
    8, 0, 4,
    7, 6, 5
)

# =====================================================
# GET NEIGHBORS
# =====================================================
def get_neighbors(state):
    neighbors = []
    zero = state.index(0)
    row, col = divmod(zero, 3)
    for dr, dc, move in ((-1,0,'U'), (1,0,'D'), (0,-1,'L'), (0,1,'R')):
        nr, nc = row + dr, col + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            nxt = nr * 3 + nc
            temp = list(state)
            temp[zero], temp[nxt] = temp[nxt], temp[zero]
            neighbors.append((tuple(temp), move))
    return neighbors

# =====================================================
# INVERSION COUNT
# =====================================================
def inversion_count(state):
    arr = [x for x in state if x != 0]
    inv = 0
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i] > arr[j]:
                inv += 1
    return inv

def is_solvable(start, goal):
    return (inversion_count(start) % 2) == (inversion_count(goal) % 2)

def generate_random_state(goal):
    nums = list(range(9))
    while True:
        random.shuffle(nums)
        state = tuple(nums)
        if is_solvable(state, goal):
            return state

# =====================================================
# BFS & DFS (unchanged)
# =====================================================
def bfs(start, goal):
    queue = deque([start])
    visited = set([start])
    parent = {}
    move_taken = {}
    while queue:
        state = queue.popleft()
        if state == goal:
            path, states = [], []
            cur = goal
            while cur != start:
                states.append(cur)
                path.append(move_taken[cur])
                cur = parent[cur]
            states.append(start)
            states.reverse()
            path.reverse()
            return path, states
        for nxt, move in get_neighbors(state):
            if nxt not in visited:
                visited.add(nxt)
                parent[nxt] = state
                move_taken[nxt] = move
                queue.append(nxt)
    return None, None

def dfs(start, goal, limit=35):
    stack = [(start, 0)]
    visited = set()
    parent = {}
    move_taken = {}
    while stack:
        state, depth = stack.pop()
        if state in visited:
            continue
        visited.add(state)
        if state == goal:
            path, states = [], []
            cur = goal
            while cur != start:
                states.append(cur)
                path.append(move_taken[cur])
                cur = parent[cur]
            states.append(start)
            states.reverse()
            path.reverse()
            return path, states
        if depth >= limit:
            continue
        for nxt, move in reversed(get_neighbors(state)):
            if nxt not in visited:
                parent[nxt] = state
                move_taken[nxt] = move
                stack.append((nxt, depth+1))
    return None, None

# =====================================================
# GUI (enhanced)
# =====================================================
class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle Visual Solver")
        self.root.geometry("1200x800")
        self.root.configure(bg=BG)
        self.running = False
        self.animating = False
        self.stop_animation_flag = False

        # Title
        tk.Label(root, text="8 PUZZLE VISUAL SOLVER",
                 font=("Segoe UI", 32, "bold"), bg=BG, fg=ACCENT).pack(pady=15)

        # Main container
        main = tk.Frame(root, bg=FRAME)
        main.pack(fill="both", expand=True, padx=20, pady=10)

        # Left panel - Input
        left = tk.Frame(main, bg=FRAME, relief="ridge", bd=2)
        left.pack(side="left", fill="both", padx=15, pady=10)

        # Start state frame
        start_frame = tk.LabelFrame(left, text="START STATE", font=("Segoe UI", 14, "bold"),
                                    bg=FRAME, fg=TEXT, bd=2, relief="groove")
        start_frame.pack(pady=10, padx=10, fill="x")

        self.start_entries = []
        sf_grid = tk.Frame(start_frame, bg=FRAME)
        sf_grid.pack(pady=10)
        for i in range(3):
            row = []
            for j in range(3):
                e = tk.Entry(sf_grid, width=3, font=("Segoe UI", 28, "bold"),
                             justify="center", bd=2, relief="solid")
                e.grid(row=i, column=j, padx=5, pady=5)
                row.append(e)
            self.start_entries.append(row)

        tk.Button(left, text="🎲 Random Start", font=("Segoe UI", 12, "bold"),
                  bg=BTN, fg="white", activebackground=BTN_HOVER,
                  cursor="hand2", command=self.random_start).pack(pady=5)

        # Goal state frame
        goal_frame = tk.LabelFrame(left, text="GOAL STATE", font=("Segoe UI", 14, "bold"),
                                   bg=FRAME, fg=TEXT, bd=2, relief="groove")
        goal_frame.pack(pady=10, padx=10, fill="x")

        self.goal_entries = []
        gf_grid = tk.Frame(goal_frame, bg=FRAME)
        gf_grid.pack(pady=10)
        idx = 0
        for i in range(3):
            row = []
            for j in range(3):
                e = tk.Entry(gf_grid, width=3, font=("Segoe UI", 28, "bold"),
                             justify="center", bd=2, relief="solid")
                val = DEFAULT_GOAL[idx]
                if val != 0:
                    e.insert(0, str(val))
                idx += 1
                e.grid(row=i, column=j, padx=5, pady=5)
                row.append(e)
            self.goal_entries.append(row)

        # Control buttons
        ctrl_frame = tk.Frame(left, bg=FRAME)
        ctrl_frame.pack(pady=15)

        tk.Button(ctrl_frame, text="🚀 Solve BFS", font=("Segoe UI", 12, "bold"),
                  bg=BTN, fg="white", width=12, command=self.solve_bfs).grid(row=0, column=0, padx=5)
        tk.Button(ctrl_frame, text="⚡ Solve DFS", font=("Segoe UI", 12, "bold"),
                  bg=BTN, fg="white", width=12, command=self.solve_dfs).grid(row=0, column=1, padx=5)
        tk.Button(ctrl_frame, text="🔄 Reset", font=("Segoe UI", 12, "bold"),
                  bg="#ef4444", fg="white", width=12, command=self.reset).grid(row=0, column=2, padx=5)
        tk.Button(ctrl_frame, text="⏹️ Stop", font=("Segoe UI", 12, "bold"),
                  bg="#f97316", fg="white", width=12, command=self.stop_animation).grid(row=0, column=3, padx=5)

        # Right panel - Visualization
        right = tk.Frame(main, bg=FRAME, relief="ridge", bd=2)
        right.pack(side="right", fill="both", expand=True, padx=15, pady=10)

        # Board display
        board_frame = tk.Frame(right, bg=FRAME)
        board_frame.pack(pady=15)

        self.cells = []
        for i in range(3):
            row = []
            for j in range(3):
                lbl = tk.Label(board_frame, text="", width=4, height=2,
                               font=("Segoe UI", 36, "bold"), bg=TILE,
                               fg=TILE_NUM, relief="raised", bd=3)
                lbl.grid(row=i, column=j, padx=8, pady=8)
                row.append(lbl)
            self.cells.append(row)

        # Speed control
        speed_frame = tk.Frame(right, bg=FRAME)
        speed_frame.pack(fill="x", pady=5)
        tk.Label(speed_frame, text="Animation Speed:", font=("Segoe UI", 11),
                 bg=FRAME, fg=TEXT).pack(side="left", padx=5)
        self.speed_var = tk.DoubleVar(value=0.4)
        speed_scale = tk.Scale(speed_frame, from_=0.1, to=1.2, resolution=0.05,
                               orient="horizontal", variable=self.speed_var,
                               bg=FRAME, fg=TEXT, length=200)
        speed_scale.pack(side="left", padx=5)
        tk.Label(speed_frame, text="sec/step", font=("Segoe UI", 10),
                 bg=FRAME, fg=TEXT).pack(side="left")

        # Status & stats
        self.status = tk.Label(right, text="✅ READY", font=("Segoe UI", 13, "bold"),
                               bg=FRAME, fg="#4ade80")
        self.status.pack(pady=5)

        self.stats_label = tk.Label(right, text="", font=("Segoe UI", 10),
                                    bg=FRAME, fg=ACCENT)
        self.stats_label.pack()

        # Log area with scrollbar
        log_frame = tk.Frame(right, bg=FRAME)
        log_frame.pack(fill="both", expand=True, pady=10, padx=10)

        self.log = tk.Text(log_frame, width=50, height=14,
                           font=("Consolas", 10), bg=LOG_BG, fg=LOG_FG,
                           wrap="word", bd=2, relief="sunken")
        scrollbar = tk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=scrollbar.set)
        self.log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        btn_clear_log = tk.Button(right, text="🗑️ Clear Log", font=("Segoe UI", 10),
                                  bg="#475569", fg="white", command=self.clear_log)
        btn_clear_log.pack(pady=5)

    # =====================================================
    # Helper methods
    # =====================================================
    def read_state(self, entries):
        nums = []
        try:
            for i in range(3):
                for j in range(3):
                    txt = entries[i][j].get().strip()
                    val = 0 if txt == "" else int(txt)
                    nums.append(val)
        except:
            messagebox.showerror("Error", "Input must be numbers (0-8)")
            return None
        if sorted(nums) != list(range(9)):
            messagebox.showerror("Error", "Must contain numbers 0-8 exactly once")
            return None
        return tuple(nums)

    def draw_board(self, state):
        for i in range(9):
            r, c = divmod(i, 3)
            val = state[i]
            if val == 0:
                self.cells[r][c].config(text="", bg=EMPTY)
            else:
                self.cells[r][c].config(text=str(val), bg=TILE, fg=TILE_NUM)
        self.root.update()

    def write_log(self, txt):
        self.log.insert(tk.END, txt + "\n")
        self.log.see(tk.END)

    def clear_log(self):
        if not self.animating:
            self.log.delete(1.0, tk.END)

    def stop_animation(self):
        if self.animating:
            self.stop_animation_flag = True
            self.status.config(text="⏸️ STOPPED", fg="#f97316")

    def random_start(self):
        if self.animating:
            return
        goal = self.read_state(self.goal_entries)
        if not goal:
            return
        state = generate_random_state(goal)
        idx = 0
        for i in range(3):
            for j in range(3):
                self.start_entries[i][j].delete(0, tk.END)
                val = state[idx]
                if val != 0:
                    self.start_entries[i][j].insert(0, str(val))
                idx += 1

    def animate(self, path, states, algo, solve_time):
        self.animating = True
        self.stop_animation_flag = False
        self.clear_log()

        self.write_log(f"========== {algo} ==========")
        self.write_log(f"Solution steps : {len(path)}")
        self.write_log(f"Move sequence  : {' '.join(path)}")
        self.write_log(f"Solving time   : {solve_time:.4f} sec")
        self.write_log("")
        self.stats_label.config(text=f"Steps: {len(path)} | Moves: {len(path)} | Time: {solve_time:.2f}s")

        for step, state in enumerate(states):
            if self.stop_animation_flag:
                self.status.config(text="⏹️ Animation stopped", fg="#f97316")
                self.animating = False
                return
            self.draw_board(state)
            self.write_log(f"Step {step}: {state[0:3]} {state[3:6]} {state[6:9]}")
            time.sleep(self.speed_var.get())

        self.status.config(text=f"✅ {algo} COMPLETED", fg="#4ade80")
        self.animating = False

    def solve_common(self, algo, solver_func, **kwargs):
        if self.animating:
            messagebox.showwarning("Busy", "Please wait, animation in progress")
            return
        start = self.read_state(self.start_entries)
        goal = self.read_state(self.goal_entries)
        if not start or not goal:
            return
        if not is_solvable(start, goal):
            messagebox.showerror("Error", "This puzzle is unsolvable!")
            return

        self.status.config(text=f"⏳ {algo} solving...", fg=ACCENT)
        self.root.update()

        def run():
            start_time = time.time()
            path, states = solver_func(start, goal, **kwargs)
            solve_time = time.time() - start_time
            if path is None:
                self.root.after(0, lambda: messagebox.showinfo("Result", f"{algo} found no solution (depth limit?)"))
                self.root.after(0, lambda: self.status.config(text="❌ No solution", fg="#ef4444"))
                return
            self.root.after(0, lambda: self.animate(path, states, algo, solve_time))

        threading.Thread(target=run, daemon=True).start()

    def solve_bfs(self):
        self.solve_common("BFS", bfs)

    def solve_dfs(self):
        self.solve_common("DFS", dfs, limit=35)

    def reset(self):
        if self.animating:
            self.stop_animation()
        # Clear start entries but keep goal as is
        for i in range(3):
            for j in range(3):
                self.start_entries[i][j].delete(0, tk.END)
        # Clear board display
        for i in range(3):
            for j in range(3):
                self.cells[i][j].config(text="", bg=TILE)
        self.status.config(text="🔄 Reset", fg="#4ade80")
        self.stats_label.config(text="")
        self.clear_log()
        self.write_log("Reset complete. Enter a new start state or click Random Start.")


# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()