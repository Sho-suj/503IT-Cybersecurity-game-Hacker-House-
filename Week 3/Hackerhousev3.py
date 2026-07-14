import random
import time
import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from collections import deque

try:
    import winsound
except ImportError:
    winsound = None


TILE = 36
HUD = 96
WIDTH, HEIGHT = 900, 730

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
LEADERBOARD_FILE = os.path.join(BASE_DIR, "leaderboard.json")

MAP = [
    "#####################",
    "#P..A....#....F.....#",
    "#.#####..#.#####.####",
    "#.....#..#.....#....#",
    "#####.#..#####.#.##.#",
    "#...B.#......#.#....#",
    "#.###.######.#.######",
    "#...#....C...#......#",
    "###.###########.###.#",
    "#.....#.....D...#...#",
    "#.###.#.#########.###",
    "#...#.#.....E.......#",
    "#.#.#.###########.###",
    "#.#.....G.......H...#",
    "#.###############.#.#",
    "#.........I.....#JX.#",
    "#####################",
]

DOOR_LABELS = {
    "A": "1", "B": "2", "C": "3", "D": "4", "E": "5",
    "F": "6", "G": "7", "H": "8", "I": "9", "J": "10",
}

QUESTIONS = {
    "A": {
        "question": "What is a sign of a phishing email?",
        "choices": [
            "A. It comes from someone you know",
            "B. It asks you to urgently click a link or provide personal information",
            "C. It has a company logo",
            "D. It is short",
        ],
        "hint": "Phishing often tries to make you panic or act quickly.",
        "answers": ["b", "it asks you to urgently click a link or provide personal information"],
    },
    "B": {
        "question": "What is the safest way to handle passwords?",
        "choices": [
            "A. Use the same password everywhere",
            "B. Write all passwords on a public note",
            "C. Use unique passwords for each account",
            "D. Share passwords with trusted friends",
        ],
        "hint": "One stolen password should not unlock every account.",
        "answers": ["c", "use unique passwords for each account"],
    },
    "C": {
        "question": "What does multi-factor authentication help protect against?",
        "choices": [
            "A. Someone logging in with only your stolen password",
            "B. Slow internet",
            "C. Low battery",
            "D. Spam emails only",
        ],
        "hint": "It adds an extra step beyond just a password.",
        "answers": ["a", "someone logging in with only your stolen password"],
    },
    "D": {
        "question": "What should you do before clicking a link in an unexpected message?",
        "choices": [
            "A. Click it quickly before it expires",
            "B. Forward it to everyone",
            "C. Check whether the sender and link are legitimate",
            "D. Reply with your password",
        ],
        "hint": "Unexpected links can lead to fake websites.",
        "answers": ["c", "check whether the sender and link are legitimate"],
    },
    "E": {
        "question": "What should you do if a website suddenly asks for sensitive information?",
        "choices": [
            "A. Enter it immediately",
            "B. Check the website address and whether the request makes sense",
            "C. Ignore all security warnings",
            "D. Use a weaker password",
        ],
        "hint": "Fake websites often ask for private details.",
        "answers": ["b", "check the website address and whether the request makes sense"],
    },
    "F": {
        "question": "Why can public Wi-Fi be risky?",
        "choices": [
            "A. It is always faster",
            "B. Other people on the network may be able to spy on your activity",
            "C. It makes your phone heavier",
            "D. It deletes your apps",
        ],
        "hint": "Shared networks are less trustworthy than private ones.",
        "answers": ["b", "other people on the network may be able to spy on your activity"],
    },
    "G": {
        "question": "Why should you update your devices and apps?",
        "choices": [
            "A. Updates only change the colors",
            "B. Updates can fix security weaknesses",
            "C. Updates make passwords unnecessary",
            "D. Updates stop all scams forever",
        ],
        "hint": "Many updates patch known security problems.",
        "answers": ["b", "updates can fix security weaknesses"],
    },
    "H": {
        "question": "Which password is strongest?",
        "choices": [
            "A. password123",
            "B. qwerty",
            "C. Summer2024",
            "D. A long, unique passphrase with mixed characters",
        ],
        "hint": "Longer and less predictable is better.",
        "answers": ["d", "a long, unique passphrase with mixed characters"],
    },
    "I": {
        "question": "What should you check before entering personal information on a website?",
        "choices": [
            "A. That the website address is correct and uses HTTPS",
            "B. That the website has bright colors",
            "C. That the page loads slowly",
            "D. That there are many ads",
        ],
        "hint": "Look carefully at the address bar.",
        "answers": ["a", "that the website address is correct and uses https"],
    },
    "J": {
        "question": "What should you do if you think your account was hacked?",
        "choices": [
            "A. Ignore it",
            "B. Change the password, enable multi-factor authentication, and report suspicious activity",
            "C. Keep using the same password",
            "D. Post your password online to ask for help",
        ],
        "hint": "Act quickly to lock the attacker out.",
        "answers": ["b", "change the password, enable multi-factor authentication, and report suspicious activity"],
    },
}


def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []

    try:
        with open(LEADERBOARD_FILE, "r") as file:
            scores = json.load(file)
            if isinstance(scores, list):
                return scores
    except (json.JSONDecodeError, OSError):
        return []

    return []


def save_score(player_name, finish_time):
    leaderboard = load_leaderboard()
    leaderboard.append({"name": player_name, "time": finish_time})
    leaderboard.sort(key=lambda score: score["time"])
    leaderboard = leaderboard[:10]

    with open(LEADERBOARD_FILE, "w") as file:
        json.dump(leaderboard, file, indent=4)


def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"


def clean_answer(answer):
    return answer.strip().lower().rstrip(".")


class HackerHouse:
    def __init__(self, player_name):
        self.root = tk.Tk()
        self.root.title("Hacker House")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            self.root,
            width=WIDTH,
            height=HEIGHT,
            bg="#010302",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.grid = [list(row) for row in MAP]
        self.player_x, self.player_y = self.find_player()
        self.player_name = player_name
        self.start_time = time.time()
        self.finish_time = 0

        self.keys = set()
        self.unlocked = set()
        self.msg = "Find all 10 security doors. Press E beside a door to hack it."
        self.facing = (1, 0)
        self.alarm = 0
        self.game_over = False

        self.enemy_active = False
        self.enemy_x = None
        self.enemy_y = None
        self.enemy_mode = "hidden"
        self.enemy_target = None
        self.enemy_speed = 0.045
        self.enemy_think_timer = 0
        self.enemy_search_timer = 0

        self.root.bind("<KeyPress>", self.key_down)
        self.root.bind("<KeyRelease>", self.key_up)

        self.loop()
        self.root.mainloop()

    def find_player(self):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == "P":
                    self.grid[y][x] = "."
                    return x, y
        return 1, 1

    def beep(self, freq, dur):
        if winsound:
            try:
                winsound.Beep(freq, dur)
            except RuntimeError:
                pass
        else:
            self.root.bell()

    def key_down(self, event):
        if self.game_over:
            return

        key = event.keysym.lower()
        self.keys.add(key)

        if key == "e":
            self.try_hack()

    def key_up(self, event):
        self.keys.discard(event.keysym.lower())

    def blocked(self, x, y):
        cell = self.grid[y][x]
        return cell == "#" or cell in QUESTIONS

    def move(self, dx, dy):
        nx = self.player_x + dx
        ny = self.player_y + dy
        self.facing = (dx, dy)

        if self.grid[ny][nx] == "X":
            if len(self.unlocked) == 10:
                self.show_win_screen()
            else:
                self.msg = "The exit is sealed. Unlock all 10 doors first."
            return

        if not self.blocked(nx, ny):
            self.player_x = nx
            self.player_y = ny

    def update(self):
        if "w" in self.keys or "up" in self.keys:
            self.move(0, -1)
            self.keys.clear()
        elif "s" in self.keys or "down" in self.keys:
            self.move(0, 1)
            self.keys.clear()
        elif "a" in self.keys or "left" in self.keys:
            self.move(-1, 0)
            self.keys.clear()
        elif "d" in self.keys or "right" in self.keys:
            self.move(1, 0)
            self.keys.clear()

    def ask_security_question(self, door):
        data = QUESTIONS[door]

        popup = tk.Toplevel(self.root)
        popup.title(f"Door {DOOR_LABELS[door]} Security Lock")
        popup.geometry("760x380")
        popup.resizable(False, False)
        popup.configure(bg="#020805")
        popup.transient(self.root)
        popup.grab_set()

        result = {"answer": None}

        tk.Label(
            popup,
            text=data["question"],
            font=("Consolas", 16, "bold"),
            fg="#9cff9c",
            bg="#020805",
            wraplength=700,
            justify="left",
        ).pack(pady=18)

        tk.Label(
            popup,
            text="\n".join(data["choices"]),
            font=("Consolas", 12),
            fg="#b6ffc5",
            bg="#020805",
            justify="left",
        ).pack(anchor="w", padx=40)

        answer_row = tk.Frame(popup, bg="#020805")
        answer_row.pack(pady=24)

        tk.Label(
            answer_row,
            text="Answer:",
            font=("Consolas", 13, "bold"),
            fg="#7cff8a",
            bg="#020805",
        ).grid(row=0, column=0, padx=8)

        answer_var = tk.StringVar()

        answer_box = tk.Entry(
            answer_row,
            textvariable=answer_var,
            font=("Consolas", 13),
            width=18,
            bg="#06170c",
            fg="#caffca",
            insertbackground="#caffca",
            relief="flat",
        )
        answer_box.grid(row=0, column=1, padx=8)

        tk.Label(
            answer_row,
            text=f"Hint: {data['hint']}",
            font=("Consolas", 10),
            fg="#50ff75",
            bg="#020805",
            wraplength=300,
            justify="left",
        ).grid(row=0, column=2, padx=12)

        def submit_answer():
            result["answer"] = answer_var.get()
            popup.destroy()

        tk.Button(
            popup,
            text="SUBMIT",
            command=submit_answer,
            font=("Consolas", 13, "bold"),
            bg="#062d14",
            fg="#9cff9c",
            activebackground="#0b5a28",
            activeforeground="white",
            relief="flat",
            width=14,
        ).pack()

        answer_box.focus()
        popup.bind("<Return>", lambda event: submit_answer())

        self.root.wait_window(popup)
        return result["answer"]

    def try_hack(self):
        dx, dy = self.facing
        tx = self.player_x + dx
        ty = self.player_y + dy
        door = self.grid[ty][tx]

        if door not in QUESTIONS:
            self.msg = "No locked security door in front of you."
            self.beep(180, 60)
            return

        answer = self.ask_security_question(door)

        if answer and clean_answer(answer) in QUESTIONS[door]["answers"]:
            self.grid[ty][tx] = "."
            self.unlocked.add(door)
            self.msg = f"Door {DOOR_LABELS[door]} unlocked. {10 - len(self.unlocked)} remain."

            if len(self.unlocked) == 5:
                self.spawn_enemy()
            elif len(self.unlocked) > 5:
                self.alert_enemy_to_door(tx, ty)

            self.beep(700, 70)
            self.beep(950, 70)
        else:
            self.msg = f"ACCESS DENIED at Door {DOOR_LABELS[door]}."
            self.alarm = 12
            self.beep(120, 160)

    def spawn_enemy(self):
        if self.enemy_active:
            return

        spawn_points = [(18, 1), (1, 15), (18, 13), (10, 15)]
        spawn_points = [p for p in spawn_points if self.walkable_for_enemy(p[0], p[1])]

        if spawn_points:
            spawn = max(
                spawn_points,
                key=lambda p: abs(p[0] - self.player_x) + abs(p[1] - self.player_y),
            )
        else:
            spawn = self.nearest_walkable(18, 1)

        self.enemy_active = True
        self.enemy_mode = "hunt"
        self.enemy_x, self.enemy_y = spawn
        self.enemy_target = None
        self.enemy_think_timer = 0
        self.msg = "WARNING: Unknown presence detected inside the house."

    def alert_enemy_to_door(self, door_x, door_y):
        if not self.enemy_active:
            return

        self.enemy_mode = "alert"
        self.enemy_target = self.nearest_walkable(door_x, door_y)
        self.enemy_speed = 0.16
        self.enemy_search_timer = 0
        self.msg = "ALERT: The enemy heard the unlocked door!"

    def walkable_for_enemy(self, x, y):
        if y < 0 or y >= len(self.grid) or x < 0 or x >= len(self.grid[0]):
            return False

        cell = self.grid[y][x]
        return cell != "#" and cell not in QUESTIONS

    def nearest_walkable(self, x, y):
        x = int(max(0, min(len(self.grid[0]) - 1, round(x))))
        y = int(max(0, min(len(self.grid) - 1, round(y))))

        if self.walkable_for_enemy(x, y):
            return (x, y)

        for radius in range(1, 8):
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if abs(dx) + abs(dy) != radius:
                        continue

                    nx = x + dx
                    ny = y + dy

                    if self.walkable_for_enemy(nx, ny):
                        return (nx, ny)

        return (self.player_x, self.player_y)

    def find_path(self, start, goal):
        start = self.nearest_walkable(start[0], start[1])
        goal = self.nearest_walkable(goal[0], goal[1])

        queue = deque([start])
        came_from = {start: None}
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        while queue:
            current = queue.popleft()

            if current == goal:
                break

            for dx, dy in directions:
                next_cell = (current[0] + dx, current[1] + dy)

                if next_cell not in came_from and self.walkable_for_enemy(next_cell[0], next_cell[1]):
                    came_from[next_cell] = current
                    queue.append(next_cell)

        if goal not in came_from:
            return []

        path = []
        current = goal

        while current is not None:
            path.append(current)
            current = came_from[current]

        path.reverse()
        return path

    def move_enemy_toward(self, target):
        enemy_cell = (round(self.enemy_x), round(self.enemy_y))
        path = self.find_path(enemy_cell, target)

        if len(path) <= 1:
            return

        next_x, next_y = path[1]
        dx = next_x - self.enemy_x
        dy = next_y - self.enemy_y
        distance = max((dx * dx + dy * dy) ** 0.5, 0.001)

        if distance <= self.enemy_speed:
            self.enemy_x = next_x
            self.enemy_y = next_y
        else:
            self.enemy_x += (dx / distance) * self.enemy_speed
            self.enemy_y += (dy / distance) * self.enemy_speed

    def update_enemy(self):
        if not self.enemy_active or self.game_over:
            return

        if self.enemy_mode == "alert" and self.enemy_target:
            self.enemy_speed = 0.16
            self.move_enemy_toward(self.enemy_target)

            if abs(self.enemy_x - self.enemy_target[0]) < 0.2 and abs(self.enemy_y - self.enemy_target[1]) < 0.2:
                self.enemy_mode = "search"
                self.enemy_search_timer = 22
                self.msg = "The enemy reached the alert zone and is searching."

        elif self.enemy_mode == "search":
            self.enemy_search_timer -= 1

            if self.enemy_search_timer <= 0:
                self.enemy_mode = "hunt"
                self.enemy_target = None
                self.enemy_speed = 0.045
                self.msg = "The enemy lost the trail... but it is still hunting."

        else:
            self.enemy_mode = "hunt"
            self.enemy_speed = 0.045 + min(0.025, max(0, len(self.unlocked) - 5) * 0.004)
            self.enemy_think_timer -= 1

            if self.enemy_think_timer <= 0 or self.enemy_target is None:
                guess_x = self.player_x + random.randint(-2, 2)
                guess_y = self.player_y + random.randint(-2, 2)
                self.enemy_target = self.nearest_walkable(guess_x, guess_y)
                self.enemy_think_timer = random.randint(12, 24)

            self.move_enemy_toward(self.enemy_target)

        if abs(self.enemy_x - self.player_x) < 0.45 and abs(self.enemy_y - self.player_y) < 0.45:
            self.game_over = True
            messagebox.showinfo("Caught", "The enemy caught you. Try again.")
            self.root.destroy()
            show_main_menu()

    def draw_tile(self, x, y, cell):
        px = x * TILE + 28
        py = y * TILE + HUD

        if cell == "#":
            fill = "#07120b"
            outline = "#116d32"
        elif cell in QUESTIONS:
            fill = "#123018"
            outline = "#8cff8c"
        elif cell == "X":
            fill = "#0c1d26"
            outline = "#72e8ff"
        else:
            fill = "#020805"
            outline = "#05230f"

        self.canvas.create_rectangle(px, py, px + TILE, py + TILE, fill=fill, outline=outline)

        if cell in QUESTIONS:
            self.canvas.create_text(
                px + TILE / 2,
                py + TILE / 2,
                text=DOOR_LABELS[cell],
                fill="#caffca",
                font=("Consolas", 13, "bold"),
            )

        if cell == "X":
            self.canvas.create_text(
                px + TILE / 2,
                py + TILE / 2,
                text="EXIT",
                fill="#bffaff",
                font=("Consolas", 9, "bold"),
            )

    def draw_enemy(self):
        if not self.enemy_active:
            return

        ex = self.enemy_x * TILE + 28
        ey = self.enemy_y * TILE + HUD

        self.canvas.create_oval(
            ex + 5,
            ey + 5,
            ex + TILE - 5,
            ey + TILE - 5,
            fill="#210606",
            outline="#ff3030",
            width=3,
        )

        self.canvas.create_text(
            ex + TILE / 2,
            ey + TILE / 2,
            text="E",
            fill="#ff9090",
            font=("Consolas", 14, "bold"),
        )

        if self.enemy_mode in ("alert", "search"):
            self.canvas.create_text(
                ex + TILE / 2,
                ey - 13,
                text="!",
                fill="#ff3030",
                font=("Consolas", 28, "bold"),
            )

    def draw(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#010302", outline="")

        for _ in range(24):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            text = random.choice(["0101", "AUTH", "ROOT", "PING", "NULL", "TRACE"])
            color = random.choice(["#063d1a", "#095c28", "#0fa63f"])
            self.canvas.create_text(x, y, text=text, fill=color, font=("Consolas", 8))

        elapsed = time.time() - self.start_time

        self.canvas.create_rectangle(0, 0, WIDTH, HUD, fill="#020a05", outline="#1fff66")
        self.canvas.create_text(
            28,
            18,
            anchor="nw",
            text="HACKER HOUSE",
            fill="#91ff9d",
            font=("Consolas", 24, "bold"),
        )
        self.canvas.create_text(
            30,
            55,
            anchor="nw",
            text=self.msg,
            fill="#b6ffc5",
            font=("Consolas", 12),
        )
        self.canvas.create_text(
            690,
            18,
            anchor="nw",
            text=f"LOCKS: {len(self.unlocked)}/10",
            fill="#50ff75",
            font=("Consolas", 17, "bold"),
        )
        self.canvas.create_text(
            690,
            52,
            anchor="nw",
            text=f"TIME: {format_time(elapsed)}",
            fill="#50ff75",
            font=("Consolas", 17, "bold"),
        )

        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                self.draw_tile(x, y, cell)

        px = self.player_x * TILE + 28
        py = self.player_y * TILE + HUD

        self.canvas.create_oval(
            px + 6,
            py + 6,
            px + TILE - 6,
            py + TILE - 6,
            fill="#dfffe3",
            outline="#45ff68",
            width=3,
        )

        dx, dy = self.facing
        self.canvas.create_line(
            px + TILE / 2,
            py + TILE / 2,
            px + TILE / 2 + dx * 16,
            py + TILE / 2 + dy * 16,
            fill="#45ff68",
            width=3,
        )

        self.draw_enemy()

        if self.alarm > 0:
            self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, outline="#ff2b2b", width=8)
            self.alarm -= 1

    def show_win_screen(self):
        self.game_over = True
        self.finish_time = time.time() - self.start_time
        save_score(self.player_name, self.finish_time)

        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#020805", outline="")

        self.canvas.create_text(
            WIDTH / 2,
            HEIGHT / 2 - 150,
            text="CONGRATS!",
            fill="#7cff8a",
            font=("Consolas", 52, "bold"),
        )

        self.canvas.create_text(
            WIDTH / 2,
            HEIGHT / 2 - 75,
            text="YOU ESCAPED HACKER HOUSE",
            fill="#b6ffc5",
            font=("Consolas", 30, "bold"),
        )

        self.canvas.create_text(
            WIDTH / 2,
            HEIGHT / 2 - 10,
            text=f"Player: {self.player_name}",
            fill="#50ff75",
            font=("Consolas", 18, "bold"),
        )

        self.canvas.create_text(
            WIDTH / 2,
            HEIGHT / 2 + 35,
            text=f"Finished in: {format_time(self.finish_time)}",
            fill="#b6ffc5",
            font=("Consolas", 18),
        )

        def return_to_main_menu():
            self.root.destroy()
            show_main_menu()

        main_menu_button = tk.Button(
            self.root,
            text="MAIN MENU",
            command=return_to_main_menu,
            font=("Consolas", 16, "bold"),
            width=14,
            bg="#062d14",
            fg="#9cff9c",
            activebackground="#0b5a28",
            activeforeground="white",
            relief="flat",
            bd=0,
        )

        self.canvas.create_window(
            WIDTH / 2,
            HEIGHT / 2 + 115,
            window=main_menu_button,
            width=190,
            height=45,
        )

        self.beep(700, 100)
        self.beep(900, 100)
        self.beep(1100, 150)

    def loop(self):
        if not self.game_over:
            self.update()
            self.update_enemy()
            self.draw()
            self.root.after(90, self.loop)


def show_main_menu():
    menu = tk.Tk()
    menu.title("Hacker House - Main Menu")
    menu.geometry("760x650")
    menu.resizable(False, False)
    menu.configure(bg="#020805")

    tk.Label(
        menu,
        text="HACKER HOUSE",
        font=("Consolas", 36, "bold"),
        fg="#7cff8a",
        bg="#020805",
    ).pack(pady=30)

    tk.Label(
        menu,
        text="A cyberpunk security puzzle game",
        font=("Consolas", 14),
        fg="#b6ffc5",
        bg="#020805",
    ).pack(pady=5)

    leaderboard = load_leaderboard()
    leaderboard_text = "LEADERBOARD\n"

    if leaderboard:
        for index, score in enumerate(leaderboard, start=1):
            leaderboard_text += f"{index}. {score['name']} - {format_time(score['time'])}\n"
    else:
        leaderboard_text += "No scores yet."

    tk.Label(
        menu,
        text=leaderboard_text,
        font=("Consolas", 11),
        fg="#b6ffc5",
        bg="#020805",
        justify="left",
    ).pack(pady=12)

    def play_game():
        player_name = simpledialog.askstring(
            "Player Name",
            "Enter your name:",
            parent=menu,
        )

        if not player_name or not player_name.strip():
            return

        menu.destroy()
        HackerHouse(player_name.strip())

    def how_to_play():
        messagebox.showinfo(
            "How To Play",
            "Move around the hacker house and unlock all 10 security doors.\n\n"
            "Each door asks a cybersecurity question.\n"
            "Type the correct letter, such as A, B, C, or D.\n"
            "After 5 doors, an enemy will begin hunting you.\n"
            "Unlock all doors, then reach the exit.",
        )

    def instructions():
        messagebox.showinfo(
            "Instructions",
            "W / Arrow Up: Move up\n"
            "S / Arrow Down: Move down\n"
            "A / Arrow Left: Move left\n"
            "D / Arrow Right: Move right\n\n"
            "E: Hack the door you are facing",
        )

    button_style = {
        "font": ("Consolas", 16, "bold"),
        "width": 18,
        "bg": "#062d14",
        "fg": "#9cff9c",
        "activebackground": "#0b5a28",
        "activeforeground": "white",
        "relief": "flat",
        "bd": 0,
    }

    tk.Button(menu, text="PLAY", command=play_game, **button_style).pack(pady=10)
    tk.Button(menu, text="HOW TO PLAY", command=how_to_play, **button_style).pack(pady=10)
    tk.Button(menu, text="INSTRUCTIONS", command=instructions, **button_style).pack(pady=10)
    tk.Button(menu, text="EXIT", command=menu.destroy, **button_style).pack(pady=10)

    menu.mainloop()


if __name__ == "__main__":
    show_main_menu()