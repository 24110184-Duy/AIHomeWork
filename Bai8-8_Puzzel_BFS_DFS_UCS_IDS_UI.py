import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import heapq
import random
import threading
import time

# =====================================================
# COLORS (modern dark theme)
# =====================================================
BG = "#0f172a"
FRAME = "#1e293b"
BTN = "#3b82f6"
BTN_HOVER = "#2563eb"
TEXT = "#f8fafc"
EMPTY = "#334155"
TILE = "#38bdf8"
TILE_NUM = "#0f172a"
ACCENT = "#f59e0b"
LOG_BG = "#0f172a"
LOG_FG = "#a5f3fc"
BTN_IDS = "#10b981"
BTN_UCS = "#a855f7"
BTN_GREEDY = "#ec4899"  # pink
BTN_ASTAR = "#f97316"  # orange

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
    for dr, dc, move in ((-1, 0, 'U'), (1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R')):
        nr, nc = row + dr, col + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            nxt = nr * 3 + nc
            temp = list(state)
            temp[zero], temp[nxt] = temp[nxt], temp[zero]
            neighbors.append((tuple(temp), move))
    return neighbors


# =====================================================
# HEURISTICS
# =====================================================
def manhattan_distance(state, goal):
    """Tổng khoảng cách Manhattan của mỗi ô đến vị trí đích."""
    goal_pos = {goal[i]: divmod(i, 3) for i in range(9)}
    dist = 0
    for i, val in enumerate(state):
        if val != 0:
            r, c = divmod(i, 3)
            gr, gc = goal_pos[val]
            dist += abs(r - gr) + abs(c - gc)
    return dist


def misplaced_tiles(state, goal):
    """Số ô không đúng vị trí (không tính ô trống)."""
    return sum(1 for i in range(9) if state[i] != goal[i] and state[i] != 0)


# =====================================================
# INVERSION COUNT
# =====================================================
def inversion_count(state):
    arr = [x for x in state if x != 0]
    inv = 0
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
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
# BFS
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


# =====================================================
# DFS
# =====================================================
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
                stack.append((nxt, depth + 1))
    return None, None


# =====================================================
# IDS (Iterative Deepening Search)
# =====================================================
def ids(start, goal, max_depth=50):
    def dls(state, limit, current_path, current_moves):
        if state == goal:
            return list(current_path), list(current_moves)
        if limit == 0:
            return None
        for nxt, move in get_neighbors(state):
            if nxt not in path_set:
                path_set.add(nxt)
                current_path.append(nxt)
                current_moves.append(move)
                result = dls(nxt, limit - 1, current_path, current_moves)
                if result is not None:
                    return result
                current_path.pop()
                current_moves.pop()
                path_set.discard(nxt)
        return None

    for depth_limit in range(max_depth + 1):
        path_set = {start}
        result = dls(start, depth_limit, [start], [])
        if result is not None:
            states, moves = result
            return moves, states, depth_limit

    return None, None, None


# =====================================================
# UCS (Uniform Cost Search)
# =====================================================
def ucs(start, goal):
    counter = 0
    heap = [(0, counter, start)]
    visited = {}
    parent = {}
    move_taken = {}
    cost_map = {start: 0}

    while heap:
        cost, _, state = heapq.heappop(heap)
        if state in visited:
            continue
        visited[state] = cost
        if state == goal:
            path_moves, path_states = [], []
            cur = goal
            while cur != start:
                path_states.append(cur)
                path_moves.append(move_taken[cur])
                cur = parent[cur]
            path_states.append(start)
            path_states.reverse()
            path_moves.reverse()
            return path_moves, path_states, cost

        for nxt, move in get_neighbors(state):
            new_cost = cost + 1
            if nxt not in visited and (nxt not in cost_map or new_cost < cost_map[nxt]):
                cost_map[nxt] = new_cost
                parent[nxt] = state
                move_taken[nxt] = move
                counter += 1
                heapq.heappush(heap, (new_cost, counter, nxt))

    return None, None, None


# =====================================================
# GREEDY BEST-FIRST SEARCH
# =====================================================
def greedy(start, goal, heuristic="manhattan"):
    """
    Greedy Best-First Search: chỉ dùng heuristic h(n), không tính g(n).
    Nhanh nhưng không đảm bảo tìm đường ngắn nhất.
    """
    h_func = manhattan_distance if heuristic == "manhattan" else misplaced_tiles

    counter = 0
    h0 = h_func(start, goal)
    heap = [(h0, counter, start)]
    visited = set()
    parent = {}
    move_taken = {}

    nodes_expanded = 0

    while heap:
        h, _, state = heapq.heappop(heap)
        if state in visited:
            continue
        visited.add(state)
        nodes_expanded += 1

        if state == goal:
            path_moves, path_states = [], []
            cur = goal
            while cur != start:
                path_states.append(cur)
                path_moves.append(move_taken[cur])
                cur = parent[cur]
            path_states.append(start)
            path_states.reverse()
            path_moves.reverse()
            return path_moves, path_states, nodes_expanded

        for nxt, move in get_neighbors(state):
            if nxt not in visited:
                parent[nxt] = state
                move_taken[nxt] = move
                counter += 1
                heapq.heappush(heap, (h_func(nxt, goal), counter, nxt))

    return None, None, nodes_expanded


# =====================================================
# A* SEARCH
# =====================================================
def astar(start, goal, heuristic="manhattan"):
    """
    A* Search: f(n) = g(n) + h(n).
    Tối ưu và đầy đủ khi heuristic là admissible.
    Manhattan distance là admissible cho 8-puzzle.
    """
    h_func = manhattan_distance if heuristic == "manhattan" else misplaced_tiles

    counter = 0
    g0 = 0
    h0 = h_func(start, goal)
    heap = [(g0 + h0, counter, start)]
    visited = {}  # state -> best g
    parent = {}
    move_taken = {}
    g_map = {start: 0}

    nodes_expanded = 0

    while heap:
        f, _, state = heapq.heappop(heap)
        g = g_map.get(state, float('inf'))

        if state in visited:
            continue
        visited[state] = g
        nodes_expanded += 1

        if state == goal:
            path_moves, path_states = [], []
            cur = goal
            while cur != start:
                path_states.append(cur)
                path_moves.append(move_taken[cur])
                cur = parent[cur]
            path_states.append(start)
            path_states.reverse()
            path_moves.reverse()
            return path_moves, path_states, nodes_expanded, g

        for nxt, move in get_neighbors(state):
            new_g = g + 1
            if nxt not in visited and (nxt not in g_map or new_g < g_map[nxt]):
                g_map[nxt] = new_g
                parent[nxt] = state
                move_taken[nxt] = move
                counter += 1
                f_new = new_g + h_func(nxt, goal)
                heapq.heappush(heap, (f_new, counter, nxt))

    return None, None, nodes_expanded, None


# =====================================================
# GUI
# =====================================================
class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle Visual Solver")
        self.root.configure(bg=BG)
        self.running = False
        self.animating = False
        self.stop_animation_flag = False

        # ── Title ────────────────────────────────────
        tk.Label(root, text="8 PUZZLE VISUAL SOLVER",
                 font=("Segoe UI", 26, "bold"), bg=BG, fg=ACCENT).pack(pady=(12, 4))

        # ── Main container ───────────────────────────
        main = tk.Frame(root, bg=BG)
        main.pack(fill="both", expand=True, padx=16, pady=6)

        # ── LEFT PANEL ───────────────────────────────
        left = tk.Frame(main, bg=FRAME, relief="ridge", bd=2)
        left.pack(side="left", fill="y", padx=(0, 10), pady=4)

        # Start state
        start_frame = tk.LabelFrame(left, text=" START STATE ", font=("Segoe UI", 11, "bold"),
                                    bg=FRAME, fg=TEXT, bd=2, relief="groove")
        start_frame.pack(pady=(10, 4), padx=10, fill="x")

        self.start_entries = []
        sf_grid = tk.Frame(start_frame, bg=FRAME)
        sf_grid.pack(pady=6)
        for i in range(3):
            row = []
            for j in range(3):
                e = tk.Entry(sf_grid, width=3, font=("Segoe UI", 22, "bold"),
                             justify="center", bd=2, relief="solid")
                e.grid(row=i, column=j, padx=4, pady=4)
                row.append(e)
            self.start_entries.append(row)

        tk.Button(left, text="🎲  Random Start", font=("Segoe UI", 11, "bold"),
                  bg=BTN, fg="white", activebackground=BTN_HOVER,
                  cursor="hand2", command=self.random_start).pack(pady=(4, 8), padx=10, fill="x")

        # Goal state
        goal_frame = tk.LabelFrame(left, text=" GOAL STATE ", font=("Segoe UI", 11, "bold"),
                                   bg=FRAME, fg=TEXT, bd=2, relief="groove")
        goal_frame.pack(pady=4, padx=10, fill="x")

        self.goal_entries = []
        gf_grid = tk.Frame(goal_frame, bg=FRAME)
        gf_grid.pack(pady=6)
        idx = 0
        for i in range(3):
            row = []
            for j in range(3):
                e = tk.Entry(gf_grid, width=3, font=("Segoe UI", 22, "bold"),
                             justify="center", bd=2, relief="solid")
                val = DEFAULT_GOAL[idx]
                if val != 0:
                    e.insert(0, str(val))
                idx += 1
                e.grid(row=i, column=j, padx=4, pady=4)
                row.append(e)
            self.goal_entries.append(row)

        # ── Algorithm buttons ─────────────────────────
        algo_frame = tk.LabelFrame(left, text=" ALGORITHMS ", font=("Segoe UI", 11, "bold"),
                                   bg=FRAME, fg=TEXT, bd=2, relief="groove")
        algo_frame.pack(pady=(10, 4), padx=10, fill="x")

        btn_cfg = dict(font=("Segoe UI", 11, "bold"), fg="white", cursor="hand2",
                       relief="flat", padx=6, pady=6)

        # Row 0: BFS | DFS
        r0 = tk.Frame(algo_frame, bg=FRAME)
        r0.pack(fill="x", padx=6, pady=(6, 2))
        tk.Button(r0, text="🚀 BFS", bg=BTN, activebackground=BTN_HOVER,
                  command=self.solve_bfs, **btn_cfg).pack(side="left", expand=True, fill="x", padx=(0, 3))
        tk.Button(r0, text="⚡ DFS", bg="#0ea5e9", activebackground="#0284c7",
                  command=self.solve_dfs, **btn_cfg).pack(side="left", expand=True, fill="x", padx=(3, 0))

        # Row 1: IDS | UCS
        r1 = tk.Frame(algo_frame, bg=FRAME)
        r1.pack(fill="x", padx=6, pady=(2, 2))
        tk.Button(r1, text="🔁 IDS", bg=BTN_IDS, activebackground="#059669",
                  command=self.solve_ids, **btn_cfg).pack(side="left", expand=True, fill="x", padx=(0, 3))
        tk.Button(r1, text="💜 UCS", bg=BTN_UCS, activebackground="#9333ea",
                  command=self.solve_ucs, **btn_cfg).pack(side="left", expand=True, fill="x", padx=(3, 0))

        # Row 2: Greedy | A*
        r2 = tk.Frame(algo_frame, bg=FRAME)
        r2.pack(fill="x", padx=6, pady=(2, 6))
        tk.Button(r2, text="🎯 Greedy", bg=BTN_GREEDY, activebackground="#db2777",
                  command=self.solve_greedy, **btn_cfg).pack(side="left", expand=True, fill="x", padx=(0, 3))
        tk.Button(r2, text="⭐ A*", bg=BTN_ASTAR, activebackground="#ea580c",
                  command=self.solve_astar, **btn_cfg).pack(side="left", expand=True, fill="x", padx=(3, 0))

        # ── Heuristic options (for Greedy & A*) ──────
        heuristic_frame = tk.LabelFrame(left, text=" HEURISTIC (Greedy & A*) ",
                                        font=("Segoe UI", 10, "bold"),
                                        bg=FRAME, fg=ACCENT, bd=2, relief="groove")
        heuristic_frame.pack(pady=(0, 4), padx=10, fill="x")

        self.heuristic_var = tk.StringVar(value="manhattan")
        h_inner = tk.Frame(heuristic_frame, bg=FRAME)
        h_inner.pack(pady=4, padx=6, fill="x")

        tk.Radiobutton(h_inner, text="Manhattan Distance",
                       variable=self.heuristic_var, value="manhattan",
                       font=("Segoe UI", 10), bg=FRAME, fg=TEXT,
                       selectcolor=BG, activebackground=FRAME,
                       activeforeground=ACCENT).pack(anchor="w")
        tk.Radiobutton(h_inner, text="Misplaced Tiles",
                       variable=self.heuristic_var, value="misplaced",
                       font=("Segoe UI", 10), bg=FRAME, fg=TEXT,
                       selectcolor=BG, activebackground=FRAME,
                       activeforeground=ACCENT).pack(anchor="w")

        # Heuristic info label
        self.h_info = tk.Label(heuristic_frame,
                               text="Manhattan: |Δrow|+|Δcol| cho mỗi ô",
                               font=("Segoe UI", 9, "italic"),
                               bg=FRAME, fg="#94a3b8", wraplength=200, justify="left")
        self.h_info.pack(padx=6, pady=(0, 4))

        self.heuristic_var.trace_add("write", self._update_h_info)

        # ── Control buttons ───────────────────────────
        ctrl_frame = tk.LabelFrame(left, text=" CONTROLS ", font=("Segoe UI", 11, "bold"),
                                   bg=FRAME, fg=TEXT, bd=2, relief="groove")
        ctrl_frame.pack(pady=(4, 10), padx=10, fill="x")

        r3 = tk.Frame(ctrl_frame, bg=FRAME)
        r3.pack(fill="x", padx=6, pady=6)
        tk.Button(r3, text="🔄 Reset", font=("Segoe UI", 11, "bold"), fg="white",
                  bg="#ef4444", activebackground="#dc2626", cursor="hand2",
                  relief="flat", padx=6, pady=6,
                  command=self.reset).pack(side="left", expand=True, fill="x", padx=(0, 3))
        tk.Button(r3, text="⏹️ Stop", font=("Segoe UI", 11, "bold"), fg="white",
                  bg="#f97316", activebackground="#ea580c", cursor="hand2",
                  relief="flat", padx=6, pady=6,
                  command=self.stop_animation).pack(side="left", expand=True, fill="x", padx=(3, 0))

        # ── RIGHT PANEL ───────────────────────────────
        right = tk.Frame(main, bg=FRAME, relief="ridge", bd=2)
        right.pack(side="right", fill="both", expand=True, pady=4)

        # Board display
        board_outer = tk.Frame(right, bg=FRAME)
        board_outer.pack(pady=(14, 6))

        self.cells = []
        for i in range(3):
            row = []
            for j in range(3):
                lbl = tk.Label(board_outer, text="", width=4, height=2,
                               font=("Segoe UI", 34, "bold"), bg=TILE,
                               fg=TILE_NUM, relief="raised", bd=3)
                lbl.grid(row=i, column=j, padx=7, pady=7)
                row.append(lbl)
            self.cells.append(row)

        # Speed control
        speed_frame = tk.Frame(right, bg=FRAME)
        speed_frame.pack(fill="x", padx=14, pady=4)
        tk.Label(speed_frame, text="⏱ Speed:", font=("Segoe UI", 10),
                 bg=FRAME, fg=TEXT).pack(side="left", padx=(0, 4))
        self.speed_var = tk.DoubleVar(value=0.4)
        tk.Scale(speed_frame, from_=0.1, to=1.5, resolution=0.05,
                 orient="horizontal", variable=self.speed_var,
                 bg=FRAME, fg=TEXT, highlightthickness=0,
                 length=180).pack(side="left")
        tk.Label(speed_frame, text="sec/step", font=("Segoe UI", 9),
                 bg=FRAME, fg="#94a3b8").pack(side="left", padx=4)

        # Status & stats
        self.status = tk.Label(right, text="✅ READY",
                               font=("Segoe UI", 12, "bold"), bg=FRAME, fg="#4ade80")
        self.status.pack(pady=(4, 0))

        self.stats_label = tk.Label(right, text="",
                                    font=("Segoe UI", 10), bg=FRAME, fg=ACCENT)
        self.stats_label.pack()

        # Log area
        log_frame = tk.Frame(right, bg=FRAME)
        log_frame.pack(fill="both", expand=True, pady=(6, 2), padx=12)

        self.log = tk.Text(log_frame, width=48, height=12,
                           font=("Consolas", 10), bg=LOG_BG, fg=LOG_FG,
                           wrap="word", bd=2, relief="sunken")
        scrollbar = tk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=scrollbar.set)
        self.log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Button(right, text="🗑️ Clear Log", font=("Segoe UI", 9),
                  bg="#475569", fg="white", cursor="hand2",
                  command=self.clear_log).pack(pady=(2, 10))

        root.update_idletasks()
        root.minsize(root.winfo_width(), root.winfo_height())

    # =====================================================
    # Heuristic info update
    # =====================================================
    def _update_h_info(self, *args):
        if self.heuristic_var.get() == "manhattan":
            self.h_info.config(text="Manhattan: |Δrow|+|Δcol| cho mỗi ô — admissible, mạnh hơn")
        else:
            self.h_info.config(text="Misplaced Tiles: đếm số ô sai vị trí — admissible, yếu hơn")

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
        except Exception:
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

    def animate(self, path, states, algo, solve_time, extra_info=""):
        self.animating = True
        self.stop_animation_flag = False
        self.clear_log()

        self.write_log(f"========== {algo} ==========")
        self.write_log(f"Solution steps : {len(path)}")
        self.write_log(f"Move sequence  : {' '.join(path)}")
        self.write_log(f"Solving time   : {solve_time:.4f} sec")
        if extra_info:
            self.write_log(extra_info)
        self.write_log("")

        extra_str = f" | {extra_info}" if extra_info else ""
        self.stats_label.config(
            text=f"Steps: {len(path)} | Time: {solve_time:.4f}s{extra_str}"
        )

        for step, state in enumerate(states):
            if self.stop_animation_flag:
                self.status.config(text="⏹️ Animation stopped", fg="#f97316")
                self.animating = False
                return
            self.draw_board(state)
            self.write_log(f"Step {step:>3}: {state[0:3]}  {state[3:6]}  {state[6:9]}")
            time.sleep(self.speed_var.get())

        self.status.config(text=f"✅ {algo} COMPLETED", fg="#4ade80")
        self.animating = False

    def _run_solver(self, algo, solver_func, **kwargs):
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
            t0 = time.time()
            raw = solver_func(start, goal, **kwargs)
            elapsed = time.time() - t0

            if algo == "IDS":
                path, states, depth_limit = raw
                extra = f"Depth limit reached: {depth_limit}" if depth_limit is not None else ""
            elif algo == "UCS":
                path, states, total_cost = raw
                extra = f"Total cost: {total_cost}" if total_cost is not None else ""
            elif algo.startswith("Greedy"):
                path, states, nodes_exp = raw
                extra = f"Nodes expanded: {nodes_exp}"
            elif algo.startswith("A*"):
                path, states, nodes_exp, opt_cost = raw
                extra = f"Nodes expanded: {nodes_exp} | Optimal cost: {opt_cost}"
            else:
                path, states = raw
                extra = ""

            if path is None:
                self.root.after(0, lambda: messagebox.showinfo(
                    "Result", f"{algo}: Không tìm được lời giải!"))
                self.root.after(0, lambda: self.status.config(
                    text="❌ No solution", fg="#ef4444"))
                return

            self.root.after(0, lambda: self.animate(path, states, algo, elapsed, extra))

        threading.Thread(target=run, daemon=True).start()

    # ── Solver buttons ────────────────────────────────
    def _check_busy(self):
        if self.animating:
            messagebox.showwarning("Busy", "Đợi animation kết thúc trước!")
            return True
        return False

    def solve_bfs(self):
        if self._check_busy(): return
        self._run_solver("BFS", bfs)

    def solve_dfs(self):
        if self._check_busy(): return
        self._run_solver("DFS", dfs, limit=35)

    def solve_ids(self):
        if self._check_busy(): return
        self._run_solver("IDS", ids, max_depth=50)

    def solve_ucs(self):
        if self._check_busy(): return
        self._run_solver("UCS", ucs)

    def solve_greedy(self):
        if self._check_busy(): return
        h = self.heuristic_var.get()
        label = "Greedy (Manhattan)" if h == "manhattan" else "Greedy (Misplaced)"
        self._run_solver(label, greedy, heuristic=h)

    def solve_astar(self):
        if self._check_busy(): return
        h = self.heuristic_var.get()
        label = "A* (Manhattan)" if h == "manhattan" else "A* (Misplaced)"
        self._run_solver(label, astar, heuristic=h)

    def reset(self):
        if self.animating:
            self.stop_animation()
        for i in range(3):
            for j in range(3):
                self.start_entries[i][j].delete(0, tk.END)
        for i in range(3):
            for j in range(3):
                self.cells[i][j].config(text="", bg=TILE)
        self.status.config(text="🔄 Reset", fg="#4ade80")
        self.stats_label.config(text="")
        self.clear_log()
        self.write_log("Reset xong. Nhập start state hoặc bấm Random Start.")


# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()