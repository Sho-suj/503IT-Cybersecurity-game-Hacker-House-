import random
import tkinter as tk
from tkinter import simpledialog, messagebox

try:
    import winsound
except ImportError:
    winsound = None


TILE = 36
HUD = 96
WIDTH, HEIGHT = 900, 700

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


class HackerHouse2D:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hacker House - 2D")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="#010302", highlightthickness=0)
        self.canvas.pack()

        self.grid = [list(row) for row in MAP]
        self.player_x, self.player_y = self.find_player()
        self.keys = set()
        self.unlocked = set()
        self.msg = "Find all 10 security doors. Press E beside a door to hack it."
        self.facing = (1, 0)
        self.alarm = 0

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
        nx, ny = self.player_x + dx, self.player_y + dy
        self.facing = (dx, dy)

        if self.grid[ny][nx] == "X":
            if len(self.unlocked) == 10:
                messagebox.showinfo("Escaped", "You breached every lock and escaped Hacker House.")
                self.root.destroy()
            else:
                self.msg = "The exit is sealed. Unlock all 10 doors first."
            return

        if not self.blocked(nx, ny):
            self.player_x, self.player_y = nx, ny

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
        tx, ty = self.player_x + dx, self.player_y + dy
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
        px, py = x * TILE + 28, y * TILE + HUD

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
            self.canvas.create_text(px + TILE / 2, py + TILE / 2, text="EXIT", fill="#bffaff", font=("Consolas", 9, "bold"))

    def draw(self):
        self.canvas.delete("all")

        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#010302", outline="")

        for _ in range(24):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            text = random.choice(["0101", "AUTH", "ROOT", "PING", "NULL", "TRACE"])
            color = random.choice(["#063d1a", "#095c28", "#0fa63f"])
            self.canvas.create_text(x, y, text=text, fill=color, font=("Consolas", 8))

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

    def loop(self):
        self.update()
        self.draw()
        self.root.after(90, self.loop)


if __name__ == "__main__":
    HackerHouse2D()