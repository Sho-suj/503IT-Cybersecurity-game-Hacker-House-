import random
import tkinter as tk
from tkinter import simpledialog, messagebox

try:
    import winsound
except ImportError:
    winsound = None


TILE = 36
HUD = 96
WIDTH, HEIGHT = 900, 730
SCAN_WORDS = ["0101", "AUTH", "ROOT", "PING", "NULL", "TRACE"]

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
    "A": "1",
    "B": "2",
    "C": "3",
    "D": "4",
    "E": "5",
    "F": "6",
    "G": "7",
    "H": "8",
    "I": "9",
    "J": "10",
}

QUESTIONS = {
    "A": ("What is my name?", ["sujal khadka"]),
    "B": ("hello?", ["how are you"]),
    "C": ("blue?", ["green"]),
    "D": ("keyboard", ["mouse"]),
    "E": ("print", ["hello world"]),
    "F": ("What", ["who"]),
    "G": ("hey hey?", ["idiot"]),
    "H": ("traffic?", ["light"]),
    "I": ("software?", ["hardware"]),
    "J": ("hashtag", ["ey"]),
}


def draw_scan_background(canvas, width=WIDTH, height=HEIGHT, amount=36):
    canvas.create_rectangle(0, 0, width, height, fill="#010302", outline="", tags="scan_base")
    draw_scan_text(canvas, width, height, amount)


def draw_scan_text(canvas, width=WIDTH, height=HEIGHT, amount=36):
    canvas.delete("scan_text")

    for _ in range(amount):
        x = random.randint(0, width)
        y = random.randint(0, height)
        text = random.choice(SCAN_WORDS)
        color = random.choice(["#063d1a", "#095c28", "#0fa63f"])
        canvas.create_text(x, y, text=text, fill=color, font=("Consolas", 8), tags="scan_text")


def flicker_scan_text(canvas, width=WIDTH, height=HEIGHT, amount=54, delay=140):
    try:
        if not canvas.winfo_exists():
            return

        draw_scan_text(canvas, width, height, amount)
        canvas.tag_lower("scan_text", "ui_content")
        canvas.after(delay, lambda: flicker_scan_text(canvas, width, height, amount, delay))
    except tk.TclError:
        return


class HackerHouse:
    def __init__(self):
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
        self.keys = set()
        self.unlocked = set()
        self.msg = "Find all 10 security doors. Press E beside a door to hack it."
        self.facing = (1, 0)
        self.alarm = 0
        self.game_over = False

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

    def try_hack(self):
        dx, dy = self.facing
        tx = self.player_x + dx
        ty = self.player_y + dy
        door = self.grid[ty][tx]

        if door not in QUESTIONS:
            self.msg = "No locked security door in front of you."
            self.beep(180, 60)
            return

        question, answers = QUESTIONS[door]
        answer = simpledialog.askstring(
            f"Door {DOOR_LABELS[door]} Security Lock",
            question,
            parent=self.root,
        )

        if answer and answer.strip().lower() in answers:
            self.grid[ty][tx] = "."
            self.unlocked.add(door)
            self.msg = f"Door {DOOR_LABELS[door]} unlocked. {10 - len(self.unlocked)} remain."
            self.beep(700, 70)
            self.beep(950, 70)
        else:
            self.msg = f"ACCESS DENIED at Door {DOOR_LABELS[door]}."
            self.alarm = 12
            self.beep(120, 160)

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

    def draw(self):
        self.canvas.delete("all")
        draw_scan_background(self.canvas, amount=24)

        self.canvas.create_rectangle(0, 0, WIDTH, HUD, fill="#020a05", outline="#1fff66")
        self.canvas.create_text(28, 18, anchor="nw", text="HACKER HOUSE", fill="#91ff9d", font=("Consolas", 24, "bold"))
        self.canvas.create_text(30, 55, anchor="nw", text=self.msg, fill="#b6ffc5", font=("Consolas", 12))
        self.canvas.create_text(690, 22, anchor="nw", text=f"LOCKS: {len(self.unlocked)}/10", fill="#50ff75", font=("Consolas", 18, "bold"))

        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                self.draw_tile(x, y, cell)

        px = self.player_x * TILE + 28
        py = self.player_y * TILE + HUD

        self.canvas.create_oval(px + 6, py + 6, px + TILE - 6, py + TILE - 6, fill="#dfffe3", outline="#45ff68", width=3)

        dx, dy = self.facing
        self.canvas.create_line(
            px + TILE / 2,
            py + TILE / 2,
            px + TILE / 2 + dx * 16,
            py + TILE / 2 + dy * 16,
            fill="#45ff68",
            width=3,
        )

        if self.alarm > 0:
            self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, outline="#ff2b2b", width=8)
            self.alarm -= 1

    def show_win_screen(self):
        self.game_over = True
        self.canvas.delete("all")
        draw_scan_background(self.canvas, amount=48)

        self.canvas.create_rectangle(0, 0, WIDTH, HUD, fill="#020a05", outline="#1fff66", tags="ui_content")
        self.canvas.create_text(28, 18, anchor="nw", text="HACKER HOUSE", fill="#91ff9d", font=("Consolas", 24, "bold"))
        self.canvas.create_text(30, 55, anchor="nw", text="FINAL SYSTEM STATUS: ALL LOCKS OPEN", fill="#b6ffc5", font=("Consolas", 12))
        self.canvas.create_text(690, 22, anchor="nw", text="LOCKS: 10/10", fill="#50ff75", font=("Consolas", 18, "bold"))

        self.canvas.create_rectangle(72, 165, 505, 525, fill="#020a05", outline="#1fff66", width=2)
        self.canvas.create_rectangle(92, 185, 485, 505, fill="#041009", outline="#116d32")
        self.canvas.create_text(112, 210, anchor="nw", text="SYSTEM LOG", fill="#7cff8a", font=("Consolas", 18, "bold"))

        win_lines = [
            "> AUTH BYPASS COMPLETE",
            "> 10 SECURITY QUESTIONS CLEARED",
            "> DOOR LOCKS RELEASED",
            "> EXIT ROUTE UNSEALED",
            "> PLAYER ACCESS: GRANTED",
            "> SESSION RESULT: SUCCESS",
        ]

        for index, line in enumerate(win_lines):
            self.canvas.create_text(
                112,
                260 + index * 34,
                anchor="nw",
                text=line,
                fill="#b6ffc5",
                font=("Consolas", 13, "bold"),
            )

        self.canvas.create_rectangle(545, 165, 835, 525, fill="#020a05", outline="#1fff66", width=2)
        self.canvas.create_rectangle(565, 185, 815, 505, fill="#041009", outline="#116d32")

        self.canvas.create_text(690, 245, text="CONGRATS!", fill="#7cff8a", font=("Consolas", 38, "bold"))
        self.canvas.create_text(690, 310, text="YOU ESCAPED", fill="#b6ffc5", font=("Consolas", 26, "bold"))
        self.canvas.create_text(690, 370, text="HACKER HOUSE", fill="#50ff75", font=("Consolas", 22, "bold"))
        self.canvas.create_text(690, 435, text="All 10 security doors were breached.", fill="#b6ffc5", font=("Consolas", 16))

        self.canvas.create_rectangle(72, 595, 835, 652, fill="#020a05", outline="#1fff66")
        self.canvas.create_text(
            96,
            613,
            anchor="nw",
            text="MISSION COMPLETE: QUESTION LOCKS CLEARED | EXIT ROUTE UNSEALED | PLAYER STATUS SAFE",
            fill="#91ff9d",
            font=("Consolas", 12, "bold"),
        )

        flicker_scan_text(self.canvas, amount=48)

        self.beep(700, 100)
        self.beep(900, 100)
        self.beep(1100, 150)

    def loop(self):
        if not self.game_over:
            self.update()

        if not self.game_over:
            self.draw()
            self.root.after(90, self.loop)


def show_main_menu():
    menu = tk.Tk()
    menu.title("Hacker House - Main Menu")
    menu.geometry(f"{WIDTH}x{HEIGHT}")
    menu.resizable(False, False)
    menu.configure(bg="#020805")

    canvas = tk.Canvas(
        menu,
        width=WIDTH,
        height=HEIGHT,
        bg="#010302",
        highlightthickness=0,
    )
    canvas.pack()

    draw_scan_background(canvas, amount=54)

    canvas.create_rectangle(0, 0, WIDTH, HUD, fill="#020a05", outline="#1fff66", tags="ui_content")
    canvas.create_text(28, 18, anchor="nw", text="HACKER HOUSE", fill="#91ff9d", font=("Consolas", 24, "bold"))
    canvas.create_text(30, 55, anchor="nw", text="MAIN MENU: SECURITY TRAINING SIMULATION", fill="#b6ffc5", font=("Consolas", 12))
    canvas.create_text(690, 22, anchor="nw", text="LOCKS: 0/10", fill="#50ff75", font=("Consolas", 18, "bold"))

    canvas.create_rectangle(58, 150, 392, 575, fill="#020a05", outline="#1fff66", width=2)
    canvas.create_rectangle(82, 178, 368, 545, fill="#041009", outline="#116d32")
    canvas.create_text(225, 225, text="HACKER HOUSE", fill="#7cff8a", font=("Consolas", 30, "bold"))
    canvas.create_text(225, 270, text="Cybersecurity puzzle game", fill="#b6ffc5", font=("Consolas", 13))
    canvas.create_text(225, 318, text="Unlock 10 security doors", fill="#91ff9d", font=("Consolas", 12, "bold"))
    canvas.create_text(225, 342, text="Answer questions. Reach EXIT.", fill="#91ff9d", font=("Consolas", 12, "bold"))

    canvas.create_rectangle(470, 150, 848, 575, fill="#020a05", outline="#1fff66", width=2)
    canvas.create_rectangle(492, 178, 826, 545, fill="#041009", outline="#116d32")
    canvas.create_text(515, 210, anchor="nw", text="SECURITY TERMINAL", fill="#7cff8a", font=("Consolas", 18, "bold"))

    menu_lines = [
        "> TRAINING MODE ONLINE",
        "> ACTIVE LOCKS: 10",
        "> QUESTION BANK READY",
        "> MOVEMENT KEYS ENABLED",
        "> DOOR HACK KEY: E",
        "> STATUS: WAITING FOR PLAYER",
    ]

    for index, line in enumerate(menu_lines):
        canvas.create_text(
            515,
            265 + index * 38,
            anchor="nw",
            text=line,
            fill="#b6ffc5",
            font=("Consolas", 13, "bold"),
        )

    def play_game():
        menu.destroy()
        HackerHouse()

    def how_to_play():
        messagebox.showinfo(
            "How To Play",
            "Move around the hacker house and unlock all 10 security doors.\n\n"
            "Each door asks a cybersecurity or technology question.\n"
            "Answer correctly to unlock the door.\n"
            "Unlock all doors, then reach the exit.\n\n"
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

    play_button = tk.Button(menu, text="PLAY", command=play_game, **button_style)
    help_button = tk.Button(menu, text="HOW TO PLAY", command=how_to_play, **button_style)
    exit_button = tk.Button(menu, text="EXIT", command=menu.destroy, **button_style)

    canvas.create_window(225, 405, window=play_button)
    canvas.create_window(225, 465, window=help_button)
    canvas.create_window(225, 525, window=exit_button)
    flicker_scan_text(canvas, amount=54)

    menu.mainloop()


if __name__ == "__main__":
    show_main_menu()