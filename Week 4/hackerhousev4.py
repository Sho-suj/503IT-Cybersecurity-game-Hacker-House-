import json
import math
import os
import random
import struct
import tempfile
import time
import tkinter as tk
import wave
from collections import deque

try:
    import winsound
except ImportError:
    winsound = None


TILE = 36
HUD = 96
WIDTH, HEIGHT = 900, 730
MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT = 640, 520

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
LEADERBOARD_FILE = os.path.join(BASE_DIR, "leaderboard.json")

SCAN_WORDS = ["0101", "AUTH", "ROOT", "PING", "NULL", "TRACE"]

DIFFICULTIES = {
    "easy": {
        "label": "EASY",
        "spawn_after": 5,
        "patrol_speed": 0.035,
        "search_speed": 0.060,
        "investigate_speed": 0.115,
        "chase_speed": 0.085,
        "final_speed": 0.180,
        "detection_range": 4,
        "track_time": 5.0,
    },
    "normal": {
        "label": "NORMAL",
        "spawn_after": 3,
        "patrol_speed": 0.050,
        "search_speed": 0.080,
        "investigate_speed": 0.150,
        "chase_speed": 0.120,
        "final_speed": 0.205,
        "detection_range": 6,
        "track_time": 6.0,
    },
    "hard": {
        "label": "HARD",
        "spawn_after": 2,
        "patrol_speed": 0.065,
        "search_speed": 0.100,
        "investigate_speed": 0.180,
        "chase_speed": 0.155,
        "final_speed": 0.235,
        "detection_range": 8,
        "track_time": 7.0,
    },
}

DOOR_COOLDOWN_SECONDS = 5.0

HACKING_LINES = [
    "> connecting to door lock...",
    "> injecting bypass script...",
    "> decrypting access layer...",
    "> opening question terminal...",
]

MAP = [
    "#####################",
    "#P...#....A...#.....#",
    "#.#.#.###.#.#.###.#.#",
    "#.#B#.....#.#.....#.#",
    "#.#.#.###.#.###.#.#.#",
    "#...#C..#.....#.#...#",
    "###.#.#.#####.#.#.###",
    "#...#.#D....#...#...#",
    "#.###.#####.#.###.#.#",
    "#E....#...F.#.....#.#",
    "#.#.###.#.#####.#.#.#",
    "#.#...G.#.....#H....#",
    "#.###.#.###.#.###.#.#",
    "#...#.#...I.#....#..#",
    "###.#.###.#.###.#...#",
    "#...J.#....#....#..X#",
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


def clean_answer(answer):
    return answer.strip().lower().rstrip(".")


def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:05.2f}"


def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []

    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as file:
            scores = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(scores, list):
        return []

    clean_scores = []

    for score in scores:
        if not isinstance(score, dict):
            continue

        name = str(score.get("name", "")).strip()

        try:
            finish_time = float(score.get("time", 0))
        except (TypeError, ValueError):
            continue

        if name and finish_time > 0:
            clean_scores.append({"name": name, "time": finish_time})

    clean_scores.sort(key=lambda item: item["time"])
    return clean_scores[:10]


def save_score(player_name, finish_time):
    leaderboard = load_leaderboard()
    player_name = player_name.strip()[:20] or "Player"
    finish_time = float(finish_time)

    best_by_name = {}

    for score in leaderboard:
        name_key = score["name"].lower()
        if name_key not in best_by_name or score["time"] < best_by_name[name_key]["time"]:
            best_by_name[name_key] = score

    name_key = player_name.lower()
    old_score = best_by_name.get(name_key)
    is_new_record = old_score is None or finish_time < old_score["time"]

    if is_new_record:
        best_by_name[name_key] = {"name": player_name, "time": finish_time}

    updated_scores = sorted(best_by_name.values(), key=lambda item: item["time"])[:10]

    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as file:
        json.dump(updated_scores, file, indent=4)

    return is_new_record


def configure_fullscreen_window(root):
    root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
    root.resizable(True, True)

    screen_width = max(MIN_WINDOW_WIDTH, root.winfo_screenwidth())
    screen_height = max(MIN_WINDOW_HEIGHT, root.winfo_screenheight())
    root.geometry(f"{screen_width}x{screen_height}+0+0")

    try:
        root.state("zoomed")
    except tk.TclError:
        pass

    def toggle_fullscreen(event=None):
        root.attributes("-fullscreen", not bool(root.attributes("-fullscreen")))
        return "break"

    root.bind("<F11>", toggle_fullscreen)


class SoundManager:
    def __init__(self, root):
        self.root = root
        self.sample_rate = 22050
        self.cache_dir = os.path.join(tempfile.gettempdir(), "hacker_house_sounds")
        self.files = {}
        self.looping = None
        self.loop_after_id = None
        self.fallback_loop_id = None

        try:
            os.makedirs(self.cache_dir, exist_ok=True)
        except OSError:
            pass

        self.effects = {
            "click": [(720, 45, 0.20)],
            "blocked": [(190, 70, 0.25)],
            "unlock": [(700, 75, 0.30), (0, 20, 0.0), (980, 85, 0.30)],
            "damage": [(150, 100, 0.42), (0, 25, 0.0), (90, 140, 0.42)],
            "spawn": [(140, 120, 0.34), (220, 120, 0.30), (330, 150, 0.28)],
            "alert": [(920, 70, 0.34), (560, 70, 0.34), (1050, 90, 0.34)],
            "win": [(700, 100, 0.30), (900, 100, 0.30), (1120, 160, 0.30)],
            "captured": [(120, 180, 0.45), (80, 240, 0.45)],
            "warning_loop": [(880, 130, 0.28), (0, 120, 0.0), (880, 130, 0.28), (0, 500, 0.0)],
        }

        if winsound:
            for name, notes in self.effects.items():
                self.files[name] = self._write_wave(name, notes)

    def _write_wave(self, name, notes):
        path = os.path.join(self.cache_dir, f"{name}.wav")

        if os.path.exists(path):
            return path

        try:
            with wave.open(path, "w") as sound_file:
                sound_file.setnchannels(1)
                sound_file.setsampwidth(2)
                sound_file.setframerate(self.sample_rate)

                for frequency, duration_ms, volume in notes:
                    frame_count = max(1, int(self.sample_rate * duration_ms / 1000))

                    for index in range(frame_count):
                        if frequency <= 0:
                            sample = 0
                        else:
                            fade = min(1.0, index / 80, (frame_count - index) / 80)
                            wave_value = math.sin(2 * math.pi * frequency * index / self.sample_rate)
                            sample = int(32767 * volume * fade * wave_value)

                        sound_file.writeframes(struct.pack("<h", sample))

            return path
        except OSError:
            return None

    def _tone_file(self, frequency, duration_ms):
        name = f"tone_{int(frequency)}_{int(duration_ms)}"
        path = os.path.join(self.cache_dir, f"{name}.wav")

        if os.path.exists(path):
            return path

        return self._write_wave(name, [(frequency, duration_ms, 0.34)])

    def play(self, name):
        if self.looping:
            return

        if winsound and self.files.get(name):
            try:
                winsound.PlaySound(self.files[name], winsound.SND_FILENAME | winsound.SND_ASYNC)
                return
            except RuntimeError:
                pass

        try:
            self.root.bell()
        except tk.TclError:
            pass

    def play_loop(self, name, delay_ms=0):
        if self.looping == name:
            return

        if self.loop_after_id is not None:
            try:
                self.root.after_cancel(self.loop_after_id)
            except tk.TclError:
                pass
            self.loop_after_id = None

        def start_loop():
            self.loop_after_id = None

            if self.looping == name:
                return

            self.stop_loop()
            self.looping = name

            if winsound and self.files.get(name):
                try:
                    winsound.PlaySound(
                        self.files[name],
                        winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP,
                    )
                    return
                except RuntimeError:
                    pass

            self._fallback_loop()

        if delay_ms > 0:
            self.loop_after_id = self.root.after(delay_ms, start_loop)
        else:
            start_loop()

    def _fallback_loop(self):
        if not self.looping:
            return

        try:
            self.root.bell()
            self.fallback_loop_id = self.root.after(650, self._fallback_loop)
        except tk.TclError:
            self.looping = None
            self.fallback_loop_id = None

    def stop_loop(self):
        if self.loop_after_id is not None:
            try:
                self.root.after_cancel(self.loop_after_id)
            except tk.TclError:
                pass
            self.loop_after_id = None

        if self.fallback_loop_id is not None:
            try:
                self.root.after_cancel(self.fallback_loop_id)
            except tk.TclError:
                pass
            self.fallback_loop_id = None

        if self.looping and winsound:
            try:
                winsound.PlaySound(None, 0)
            except RuntimeError:
                pass

        self.looping = None

    def tone(self, frequency, duration_ms):
        if winsound:
            try:
                tone_path = self._tone_file(max(37, int(frequency)), max(30, int(duration_ms)))

                if tone_path:
                    winsound.PlaySound(tone_path, winsound.SND_FILENAME)
                    return

                winsound.Beep(max(37, int(frequency)), max(30, int(duration_ms)))
                return
            except RuntimeError:
                pass

        try:
            self.root.bell()
        except tk.TclError:
            pass


class ResponsiveCanvas(tk.Canvas):
    def __init__(self, master, design_width=WIDTH, design_height=HEIGHT, **kwargs):
        super().__init__(master, width=design_width, height=design_height, **kwargs)
        self.design_width = design_width
        self.design_height = design_height
        self.scale_factor = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.bind("<Configure>", lambda event: self.update_transform(), add="+")

    def update_transform(self):
        width = max(1, self.winfo_width())
        height = max(1, self.winfo_height())
        self.scale_factor = max(0.1, min(width / self.design_width, height / self.design_height))
        self.offset_x = (width - self.design_width * self.scale_factor) / 2
        self.offset_y = (height - self.design_height * self.scale_factor) / 2

    def font(self, size, weight=None):
        self.update_transform()
        scaled_size = max(7, int(round(size * self.scale_factor)))
        if weight:
            return ("Consolas", scaled_size, weight)
        return ("Consolas", scaled_size)

    def _x(self, value):
        return self.offset_x + value * self.scale_factor

    def _y(self, value):
        return self.offset_y + value * self.scale_factor

    def _scale_value(self, value, minimum=1):
        return max(minimum, int(round(value * self.scale_factor)))

    def _scale_font(self, font):
        if isinstance(font, (tuple, list)) and len(font) >= 2 and isinstance(font[1], int):
            scaled = list(font)
            scaled[1] = self._scale_value(font[1], 7)
            return tuple(scaled)
        return font

    def _scale_kwargs(self, kwargs, scale_width=False):
        scaled = kwargs.copy()
        if "font" in scaled:
            scaled["font"] = self._scale_font(scaled["font"])
        if "width" in scaled and isinstance(scaled["width"], (int, float)):
            scaled["width"] = self._scale_value(scaled["width"], 5 if scale_width else 1)
        return scaled

    def _coords(self, args):
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]

        scaled = []
        for index, value in enumerate(args):
            if index % 2 == 0:
                scaled.append(self._x(value))
            else:
                scaled.append(self._y(value))
        return scaled

    def create_rectangle(self, *args, **kwargs):
        self.update_transform()
        return super().create_rectangle(*self._coords(args), **self._scale_kwargs(kwargs))

    def create_oval(self, *args, **kwargs):
        self.update_transform()
        return super().create_oval(*self._coords(args), **self._scale_kwargs(kwargs))

    def create_line(self, *args, **kwargs):
        self.update_transform()
        return super().create_line(*self._coords(args), **self._scale_kwargs(kwargs))

    def create_polygon(self, *args, **kwargs):
        self.update_transform()
        return super().create_polygon(*self._coords(args), **self._scale_kwargs(kwargs))

    def create_text(self, *args, **kwargs):
        self.update_transform()
        coords = self._coords(args)
        return super().create_text(*coords, **self._scale_kwargs(kwargs, scale_width=True))

    def create_window(self, *args, **kwargs):
        self.update_transform()
        coords = self._coords(args)
        scaled = kwargs.copy()

        if "width" in scaled and isinstance(scaled["width"], (int, float)):
            scaled["width"] = self._scale_value(scaled["width"], 20)
        if "height" in scaled and isinstance(scaled["height"], (int, float)):
            scaled["height"] = self._scale_value(scaled["height"], 20)

        return super().create_window(*coords, **scaled)

    def create_screen_rectangle(self, *args, **kwargs):
        return super().create_rectangle(*args, **kwargs)

    def create_screen_text(self, x, y, **kwargs):
        if "font" in kwargs:
            kwargs = kwargs.copy()
            kwargs["font"] = self._scale_font(kwargs["font"])
        return super().create_text(x, y, **kwargs)


def draw_scan_background(canvas, width=WIDTH, height=HEIGHT, amount=36):
    if isinstance(canvas, ResponsiveCanvas):
        canvas.update_transform()
        actual_width = max(1, canvas.winfo_width())
        actual_height = max(1, canvas.winfo_height())
        canvas.create_screen_rectangle(0, 0, actual_width, actual_height, fill="#010302", outline="", tags="scan_base")

        for _ in range(amount):
            x = random.randint(0, actual_width)
            y = random.randint(0, actual_height)
            text = random.choice(SCAN_WORDS)
            color = random.choice(["#063d1a", "#095c28", "#0fa63f"])
            canvas.create_screen_text(x, y, text=text, fill=color, font=("Consolas", 8), tags="scan_text")
        return

    canvas.create_rectangle(0, 0, width, height, fill="#010302", outline="", tags="scan_base")

    for _ in range(amount):
        x = random.randint(0, width)
        y = random.randint(0, height)
        text = random.choice(SCAN_WORDS)
        color = random.choice(["#063d1a", "#095c28", "#0fa63f"])
        canvas.create_text(x, y, text=text, fill=color, font=("Consolas", 8), tags="scan_text")


def animate_scan_background(canvas, width=WIDTH, height=HEIGHT, amount=54, delay=140):
    try:
        if not canvas.winfo_exists():
            return

        canvas.delete("scan_text")

        if isinstance(canvas, ResponsiveCanvas):
            canvas.update_transform()
            actual_width = max(1, canvas.winfo_width())
            actual_height = max(1, canvas.winfo_height())

            for _ in range(amount):
                x = random.randint(0, actual_width)
                y = random.randint(0, actual_height)
                text = random.choice(SCAN_WORDS)
                color = random.choice(["#063d1a", "#095c28", "#0fa63f"])
                canvas.create_screen_text(x, y, text=text, fill=color, font=("Consolas", 8), tags="scan_text")

            canvas.tag_raise("scan_text", "scan_base")
            canvas.after(delay, lambda: animate_scan_background(canvas, width, height, amount, delay))
            return

        for _ in range(amount):
            x = random.randint(0, width)
            y = random.randint(0, height)
            text = random.choice(SCAN_WORDS)
            color = random.choice(["#063d1a", "#095c28", "#0fa63f"])
            canvas.create_text(x, y, text=text, fill=color, font=("Consolas", 8), tags="scan_text")

        canvas.tag_raise("scan_text", "scan_base")
        canvas.after(delay, lambda: animate_scan_background(canvas, width, height, amount, delay))
    except tk.TclError:
        return


class HackerHouseApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hacker House")
        configure_fullscreen_window(self.root)

        self.canvas = ResponsiveCanvas(self.root, bg="#010302", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.root.update_idletasks()
        self.canvas.update_transform()
        self.sound = SoundManager(self.root)

        self.scene = ""
        self.widgets = []
        self.resize_job = None
        self.keys = set()
        self.pending_name = ""
        self.pending_difficulty = "normal"
        self.selected_difficulty = "normal"
        self.difficulty = DIFFICULTIES[self.selected_difficulty]
        self.name_var = None
        self.quiz = None
        self.quiz_answer_var = None
        self.hacking = None
        self.paused_scene = None
        self.pause_started = None
        self.confirm_action = None
        self.confirm_message = ""

        self.reset_game_state("Player")

        self.root.bind("<KeyPress>", self.key_down)
        self.root.bind("<KeyRelease>", self.key_up)
        self.canvas.bind("<Configure>", self.on_resize, add="+")
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

        self.show_main_menu()
        animate_scan_background(self.canvas, amount=54)
        self.root.after(90, self.loop)

    def run(self):
        self.root.mainloop()

    def close_app(self):
        self.sound.stop_loop()
        self.root.destroy()

    def reset_game_state(self, player_name):
        if hasattr(self, "sound"):
            self.sound.stop_loop()

        self.difficulty = DIFFICULTIES[self.selected_difficulty]
        self.grid = [list(row) for row in MAP]
        self.player_x, self.player_y = self.find_player()
        self.player_name = player_name.strip()[:20] or "Player"
        self.start_time = time.time()
        self.total_pause_time = 0.0
        self.finish_time = 0
        self.new_record = False

        self.keys = set()
        self.unlocked = set()
        self.door_cooldowns = {}
        self.hacking = None
        self.quiz = None
        self.quiz_answer_var = None
        self.max_lives = 3
        self.lives = self.max_lives
        self.msg = "Find all 10 security doors. Press E beside a door to hack it."
        self.facing = (1, 0)
        self.alarm = 0
        self.damage_flash = 0
        self.capture_sequence = False
        self.capture_timer = 0
        self.capture_elapsed_time = None
        self.game_over = False
        self.has_keycard = False
        self.keycard_active = False
        self.keycard_pos = None
        self.exit_active = False
        self.final_chase = False

        self.enemy_active = False
        self.enemy_x = None
        self.enemy_y = None
        self.enemy_mode = "hidden"
        self.enemy_target = None
        self.enemy_last_position = None
        self.enemy_stuck_timer = 0
        self.enemy_think_timer = 0
        self.enemy_search_timer = 0
        self.enemy_search_origin = None
        self.enemy_search_points = []
        self.enemy_patrol_points = []
        self.enemy_patrol_index = 0
        self.enemy_track_timer = 0.0
        self.enemy_speed = self.difficulty["patrol_speed"]

    def cleanup_widgets(self):
        for widget in self.widgets:
            try:
                if widget.winfo_exists():
                    widget.destroy()
            except tk.TclError:
                pass
        self.widgets = []

    def clear_scene(self):
        self.cleanup_widgets()
        self.canvas.delete("all")

    def on_resize(self, event=None):
        if event is not None and event.widget is not self.canvas:
            return

        if self.resize_job is not None:
            self.root.after_cancel(self.resize_job)

        self.resize_job = self.root.after(80, self.redraw_scene)

    def redraw_scene(self):
        self.resize_job = None

        if self.scene == "menu":
            self.draw_main_menu()
        elif self.scene == "name":
            if self.name_var is not None:
                self.pending_name = self.name_var.get()
            self.draw_name_screen()
        elif self.scene == "difficulty":
            self.draw_difficulty_screen()
        elif self.scene == "leaderboard":
            self.draw_leaderboard_screen()
        elif self.scene == "how_to_play":
            self.draw_how_to_play_screen()
        elif self.scene == "hacking":
            self.draw_hacking_screen()
        elif self.scene == "quiz":
            if self.quiz_answer_var is not None:
                self.quiz["answer"] = self.quiz_answer_var.get()
            self.draw_quiz_screen()
        elif self.scene == "pause":
            self.draw_pause_screen()
        elif self.scene == "confirm":
            self.draw_confirm_screen()
        elif self.scene == "win":
            self.draw_win_screen()
        elif self.scene == "captured":
            self.draw_captured_screen()

    def button_style(self, font_size=15, danger=False):
        if danger:
            return {
                "font": self.canvas.font(font_size, "bold"),
                "bg": "#2d0707",
                "fg": "#ffb0b0",
                "activebackground": "#5a1010",
                "activeforeground": "white",
                "relief": "flat",
                "bd": 0,
            }

        return {
            "font": self.canvas.font(font_size, "bold"),
            "bg": "#062d14",
            "fg": "#9cff9c",
            "activebackground": "#0b5a28",
            "activeforeground": "white",
            "relief": "flat",
            "bd": 0,
        }

    def add_button(self, text, command, x, y, width, height, font_size=15, danger=False):
        def clicked():
            self.sound.play("click")
            command()

        button = tk.Button(self.root, text=text, command=clicked, **self.button_style(font_size, danger=danger))
        self.widgets.append(button)
        self.canvas.create_window(x, y, window=button, width=width, height=height)
        return button

    def add_entry(self, variable, x, y, width, height, font_size=15):
        entry = tk.Entry(
            self.root,
            textvariable=variable,
            font=self.canvas.font(font_size, "bold"),
            bg="#06170c",
            fg="#caffca",
            insertbackground="#caffca",
            relief="flat",
            justify="center",
        )
        self.widgets.append(entry)
        self.canvas.create_window(x, y, window=entry, width=width, height=height)
        return entry

    def beep(self, freq, dur):
        self.sound.tone(freq, dur)

    def elapsed_time(self):
        if self.capture_sequence and self.capture_elapsed_time is not None:
            return max(0.0, self.capture_elapsed_time)

        elapsed = time.time() - self.start_time - self.total_pause_time

        if self.scene in ("pause", "confirm") and self.pause_started is not None:
            elapsed -= time.time() - self.pause_started

        return max(0.0, elapsed)

    def set_scene(self, scene):
        self.scene = scene

    def show_main_menu(self):
        self.sound.stop_loop()
        self.set_scene("menu")
        self.keys.clear()
        self.draw_main_menu()

    def draw_main_menu(self):
        self.clear_scene()
        draw_scan_background(self.canvas, amount=54)

        self.canvas.create_rectangle(58, 150, 392, 605, fill="#020a05", outline="#1fff66", width=2)
        self.canvas.create_rectangle(82, 178, 368, 575, fill="#041009", outline="#116d32")
        self.canvas.create_text(225, 225, text="HACKER HOUSE", fill="#7cff8a", font=("Consolas", 30, "bold"))
        self.canvas.create_text(225, 270, text="Cybersecurity puzzle game", fill="#b6ffc5", font=("Consolas", 13))
        self.canvas.create_text(225, 318, text="Unlock 10 security doors", fill="#91ff9d", font=("Consolas", 12, "bold"))
        self.canvas.create_text(225, 342, text="Answer questions. Reach EXIT.", fill="#91ff9d", font=("Consolas", 12, "bold"))

        self.canvas.create_rectangle(470, 150, 848, 605, fill="#020a05", outline="#1fff66", width=2)
        self.canvas.create_rectangle(492, 178, 826, 575, fill="#041009", outline="#116d32")
        self.canvas.create_text(515, 210, anchor="nw", text="SECURITY TERMINAL", fill="#7cff8a", font=("Consolas", 18, "bold"))

        menu_lines = [
            "> TRAINING MODE ONLINE",
            "> ACTIVE LOCKS: 10",
            "> QUESTION BANK READY",
            "> DIFFICULTY SELECT: ENABLED",
            "> FINAL CHASE: ENABLED",
            "> STATUS: WAITING FOR PLAYER",
        ]

        for index, line in enumerate(menu_lines):
            self.canvas.create_text(
                515,
                265 + index * 38,
                anchor="nw",
                text=line,
                fill="#b6ffc5",
                font=("Consolas", 13, "bold"),
                width=300,
            )

        preview_scores = load_leaderboard()[:3]
        preview_text = "FASTEST ESCAPES\n"

        if preview_scores:
            for index, score in enumerate(preview_scores, start=1):
                preview_text += f"{index}. {score['name'][:12]} - {format_time(score['time'])}\n"
        else:
            preview_text += "No records yet."

        self.canvas.create_text(
            515,
            505,
            anchor="nw",
            text=preview_text,
            fill="#91ff9d",
            font=("Consolas", 12, "bold"),
            width=285,
        )

        self.add_button("PLAY", self.show_name_screen, 225, 390, 230, 38)
        self.add_button("LEADERBOARD", self.show_leaderboard_screen, 225, 438, 230, 38)
        self.add_button("HOW TO PLAY", self.show_how_to_play_screen, 225, 486, 230, 38)
        self.add_button("EXIT", self.close_app, 225, 534, 230, 38)

    def show_name_screen(self):
        self.set_scene("name")
        self.pending_name = self.player_name if self.player_name != "Player" else ""
        self.draw_name_screen()

    def draw_name_screen(self):
        self.clear_scene()
        draw_scan_background(self.canvas, amount=50)

        self.canvas.create_rectangle(190, 155, 710, 575, fill="#020a05", outline="#1fff66", width=2)
        self.canvas.create_rectangle(225, 190, 675, 540, fill="#041009", outline="#116d32", width=2)
        self.canvas.create_text(450, 245, text="PLAYER ACCESS", fill="#7cff8a", font=("Consolas", 30, "bold"))
        self.canvas.create_text(
            450,
            300,
            text="Enter your name for the leaderboard.",
            fill="#b6ffc5",
            font=("Consolas", 14, "bold"),
            width=370,
        )

        self.name_var = tk.StringVar(value=self.pending_name)
        name_entry = self.add_entry(self.name_var, 450, 365, 300, 42, font_size=15)
        name_entry.focus_set()
        name_entry.select_range(0, tk.END)
        name_entry.bind("<Return>", lambda event: self.start_game_from_name())

        self.add_button("START", self.start_game_from_name, 375, 450, 140, 38, font_size=13)
        self.add_button("BACK", self.show_main_menu, 525, 450, 140, 38, font_size=13)

    def start_game_from_name(self):
        name = self.name_var.get().strip() if self.name_var is not None else ""
        if not name:
            name = "Player"
        self.pending_name = name
        self.show_difficulty_screen()

    def show_difficulty_screen(self):
        self.set_scene("difficulty")
        self.draw_difficulty_screen()

    def draw_difficulty_screen(self):
        self.clear_scene()
        draw_scan_background(self.canvas, amount=54)

        self.canvas.create_rectangle(78, 95, 822, 640, fill="#020a05", outline="#1fff66", width=2)
        self.canvas.create_rectangle(110, 130, 790, 595, fill="#041009", outline="#116d32", width=2)
        self.canvas.create_text(450, 175, text="SELECT DIFFICULTY", fill="#7cff8a", font=("Consolas", 30, "bold"))
        self.canvas.create_text(
            450,
            218,
            text=f"PLAYER: {self.pending_name[:20] or 'Player'}",
            fill="#b6ffc5",
            font=("Consolas", 13, "bold"),
        )

        cards = [
            ("easy", 240, "Enemy appears after 5 correct answers.\nSlow patrols, short detection range."),
            ("normal", 450, "Enemy appears after 3 correct answers.\nBalanced speed, stronger detection."),
            ("hard", 660, "Enemy appears after 2 correct answers.\nFast standard speed, wide detection."),
        ]

        for key, x, body in cards:
            config = DIFFICULTIES[key]
            self.canvas.create_rectangle(x - 92, 270, x + 92, 500, fill="#020a05", outline="#1fff66", width=2)
            self.canvas.create_rectangle(x - 75, 292, x + 75, 478, fill="#06170c", outline="#116d32", width=1)
            self.canvas.create_text(x, 325, text=config["label"], fill="#50ff75", font=("Consolas", 19, "bold"))
            self.canvas.create_text(
                x,
                390,
                text=body,
                fill="#b6ffc5",
                font=("Consolas", 10, "bold"),
                width=140,
            )
            self.add_button(config["label"], lambda choice=key: self.start_game(self.pending_name, choice), x, 530, 145, 38, font_size=12)

        self.add_button("BACK", self.show_name_screen, 450, 585, 160, 38, font_size=12)

    def start_game(self, player_name, difficulty_key=None):
        self.sound.stop_loop()
        self.cleanup_widgets()
        if difficulty_key:
            self.selected_difficulty = difficulty_key
            self.pending_difficulty = difficulty_key
        self.reset_game_state(player_name)
        self.set_scene("game")
        self.root.focus_set()
        self.draw_game()

    def show_leaderboard_screen(self):
        self.set_scene("leaderboard")
        self.draw_leaderboard_screen()

    def draw_leaderboard_screen(self):
        self.clear_scene()
        draw_scan_background(self.canvas, amount=54)

        self.canvas.create_rectangle(135, 95, 765, 635, fill="#020a05", outline="#1fff66", width=2)
        self.canvas.create_rectangle(170, 135, 730, 590, fill="#041009", outline="#116d32", width=2)
        self.canvas.create_text(450, 180, text="LEADERBOARD", fill="#7cff8a", font=("Consolas", 30, "bold"))

        scores = load_leaderboard()

        self.canvas.create_text(220, 235, anchor="nw", text="RANK", fill="#50ff75", font=("Consolas", 13, "bold"))
        self.canvas.create_text(335, 235, anchor="nw", text="PLAYER", fill="#50ff75", font=("Consolas", 13, "bold"))
        self.canvas.create_text(585, 235, anchor="nw", text="TIME", fill="#50ff75", font=("Consolas", 13, "bold"))

        if scores:
            for index, score in enumerate(scores[:10], start=1):
                y = 275 + (index - 1) * 28
                self.canvas.create_text(220, y, anchor="nw", text=f"{index:02d}", fill="#b6ffc5", font=("Consolas", 12, "bold"))
                self.canvas.create_text(335, y, anchor="nw", text=score["name"][:18], fill="#b6ffc5", font=("Consolas", 12, "bold"), width=200)
                self.canvas.create_text(585, y, anchor="nw", text=format_time(score["time"]), fill="#91ff9d", font=("Consolas", 12, "bold"))
        else:
            self.canvas.create_text(450, 350, text="No escape records yet.", fill="#b6ffc5", font=("Consolas", 16, "bold"))

        self.add_button("BACK", self.show_main_menu, 450, 545, 170, 40, font_size=13)

    def show_how_to_play_screen(self):
        self.set_scene("how_to_play")
        self.draw_how_to_play_screen()

    def draw_how_to_play_screen(self):
        self.clear_scene()
        draw_scan_background(self.canvas, amount=54)

        self.canvas.create_rectangle(100, 75, 800, 655, fill="#020a05", outline="#1fff66", width=2)
        self.canvas.create_rectangle(135, 115, 765, 605, fill="#041009", outline="#116d32", width=2)
        self.canvas.create_text(450, 155, text="HOW TO PLAY", fill="#7cff8a", font=("Consolas", 30, "bold"))

        panel = tk.Frame(self.root, bg="#041009")
        self.widgets.append(panel)
        self.canvas.create_window(450, 365, window=panel, width=590, height=360)

        text_box = tk.Text(
            panel,
            bg="#041009",
            fg="#b6ffc5",
            insertbackground="#9cff9c",
            relief="flat",
            bd=0,
            wrap="word",
            font=self.canvas.font(11, "bold"),
            padx=18,
            pady=14,
            highlightthickness=0,
        )
        text_box.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(
            panel,
            orient="vertical",
            command=text_box.yview,
            bg="#062d14",
            troughcolor="#020805",
            activebackground="#0b5a28",
            relief="flat",
            bd=0,
            width=max(10, int(13 * self.canvas.scale_factor)),
        )
        scrollbar.pack(side="right", fill="y")
        text_box.configure(yscrollcommand=scrollbar.set)

        text_box.tag_configure("heading", foreground="#50ff75", font=self.canvas.font(14, "bold"), spacing1=6, spacing3=4)
        text_box.tag_configure("body", foreground="#b6ffc5", font=self.canvas.font(11, "bold"), spacing3=2)

        instructions = [
            ("DIFFICULTY", [
                "Choose Easy, Normal, or Hard before the maze starts.",
                "Difficulty changes enemy speed, detection range, and spawn timing.",
            ]),
            ("OBJECTIVE", [
                "Unlock all 10 security doors by answering the cybersecurity questions.",
                "After every lock is open, collect the keycard, then press E at the EXIT.",
            ]),
            ("CONTROLS", [
                "W / Arrow Up: Move up",
                "S / Arrow Down: Move down",
                "A / Arrow Left: Move left",
                "D / Arrow Right: Move right",
                "E: Hack the door you are facing",
                "Escape: Pause the game",
            ]),
            ("LIVES AND ENEMY", [
                "You have 3 lives shown as green hearts.",
                "Wrong answers remove one life and lock that door for 5 seconds.",
                "During cooldown, the enemy can track and chase your location.",
                "When all doors unlock, the enemy enters final chase mode.",
                "Lose all lives and the enemy will chase and capture you.",
            ]),
        ]

        for heading, lines in instructions:
            text_box.insert("end", f"{heading}\n", "heading")
            for line in lines:
                text_box.insert("end", f"> {line}\n", "body")
            text_box.insert("end", "\n", "body")

        text_box.configure(state="disabled")

        self.add_button("BACK", self.show_main_menu, 450, 605, 170, 40, font_size=13)

    def show_pause_menu(self):
        if self.scene not in ("game", "hacking", "quiz"):
            return

        if self.scene == "quiz" and self.quiz_answer_var is not None and self.quiz is not None:
            self.quiz["answer"] = self.quiz_answer_var.get()

        self.paused_scene = self.scene
        self.pause_started = time.time()
        self.sound.stop_loop()
        self.set_scene("pause")
        self.keys.clear()
        self.cleanup_widgets()
        self.draw_pause_screen()

    def draw_pause_screen(self):
        self.cleanup_widgets()
        self.draw_game(decrement_effects=False)

        self.canvas.create_rectangle(155, 135, 745, 600, fill="#020a05", outline="#1fff66", width=3)
        self.canvas.create_rectangle(190, 175, 710, 560, fill="#041009", outline="#116d32", width=2)
        self.canvas.create_text(450, 230, text="PAUSED", fill="#7cff8a", font=("Consolas", 38, "bold"))
        self.canvas.create_text(
            450,
            285,
            text="Gameplay, timers, enemy movement, animations, and cooldowns are frozen.",
            fill="#b6ffc5",
            font=("Consolas", 13, "bold"),
            width=440,
        )

        self.add_button("RESUME", self.resume_game, 450, 355, 220, 42, font_size=14)
        self.add_button("RESTART LEVEL", lambda: self.show_confirm("restart"), 450, 415, 220, 42, font_size=14)
        self.add_button("MAIN MENU", lambda: self.show_confirm("menu"), 450, 475, 220, 42, font_size=14, danger=True)

    def resume_game(self):
        if self.pause_started is not None:
            self.total_pause_time += time.time() - self.pause_started

        resume_scene = self.paused_scene or "game"
        self.paused_scene = None
        self.pause_started = None
        self.set_scene(resume_scene)
        self.root.focus_set()

        if self.capture_sequence and self.lives <= 0:
            self.sound.play_loop("warning_loop")

        if resume_scene == "quiz":
            self.draw_quiz_screen()
        elif resume_scene == "hacking":
            self.draw_hacking_screen()
        else:
            self.draw_game()

    def show_confirm(self, action):
        self.confirm_action = action
        self.confirm_message = (
            "Restart the level? All progress in this run will be lost."
            if action == "restart"
            else "Return to the main menu? Your current run will be lost."
        )
        self.set_scene("confirm")
        self.draw_confirm_screen()

    def draw_confirm_screen(self):
        self.cleanup_widgets()
        self.draw_game(decrement_effects=False)

        self.canvas.create_rectangle(175, 210, 725, 520, fill="#100303", outline="#ff3030", width=3)
        self.canvas.create_rectangle(210, 245, 690, 485, fill="#190707", outline="#7a1d1d", width=2)
        self.canvas.create_text(450, 290, text="CONFIRM", fill="#ffb0b0", font=("Consolas", 30, "bold"))
        self.canvas.create_text(
            450,
            350,
            text=self.confirm_message,
            fill="#b6ffc5",
            font=("Consolas", 13, "bold"),
            width=390,
        )

        self.add_button("YES", self.confirm_yes, 380, 430, 145, 38, font_size=13, danger=True)
        self.add_button("NO", self.confirm_no, 520, 430, 145, 38, font_size=13)

    def confirm_yes(self):
        action = self.confirm_action
        self.confirm_action = None
        self.pause_started = None
        self.paused_scene = None

        if action == "restart":
            self.start_game(self.player_name, self.selected_difficulty)
        else:
            self.show_main_menu()

    def confirm_no(self):
        self.confirm_action = None
        self.set_scene("pause")
        self.draw_pause_screen()

    def key_down(self, event):
        key = event.keysym.lower()

        if key == "escape":
            if self.scene == "pause":
                self.resume_game()
            elif self.scene == "confirm":
                self.confirm_no()
            else:
                self.show_pause_menu()
            return

        if self.scene != "game" or self.game_over or self.capture_sequence:
            return

        self.keys.add(key)

        if key == "e":
            self.try_hack()

    def key_up(self, event):
        self.keys.discard(event.keysym.lower())

    def find_player(self):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == "P":
                    self.grid[y][x] = "."
                    return x, y
        return 1, 1

    def in_bounds(self, x, y):
        return 0 <= y < len(self.grid) and 0 <= x < len(self.grid[0])

    def blocked(self, x, y):
        if not self.in_bounds(x, y):
            return True

        cell = self.grid[y][x]
        return cell == "#" or cell in QUESTIONS

    def walkable_for_enemy(self, x, y):
        if not self.in_bounds(x, y):
            return False

        cell = self.grid[y][x]
        return cell != "#" and cell not in QUESTIONS

    def reachable_tiles_from(self, x, y):
        start = self.nearest_walkable(x, y)
        queue = deque([start])
        distances = {start: 0}

        while queue:
            current = queue.popleft()

            for nxt in self.neighbors(current[0], current[1]):
                if nxt not in distances:
                    distances[nxt] = distances[current] + 1
                    queue.append(nxt)

        return distances

    def move(self, dx, dy):
        nx = self.player_x + dx
        ny = self.player_y + dy
        self.facing = (dx, dy)

        if not self.in_bounds(nx, ny):
            return

        if self.grid[ny][nx] == "X":
            if len(self.unlocked) < len(QUESTIONS):
                self.msg = "The exit is sealed. Unlock all 10 doors first."
            elif not self.has_keycard:
                self.msg = "The exit requires the keycard. Find it before escaping."
            else:
                self.msg = "Keycard ready. Face the EXIT and press E to escape."
            return

        if self.grid[ny][nx] == "K":
            self.has_keycard = True
            self.keycard_active = False
            self.keycard_pos = None
            self.grid[ny][nx] = "."
            self.player_x = nx
            self.player_y = ny
            self.msg = "KEYCARD COLLECTED. Reach the glowing EXIT and press E."
            self.sound.play("unlock")
            return

        if not self.blocked(nx, ny):
            self.player_x = nx
            self.player_y = ny

    def update_player(self):
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
        if self.scene != "game" or self.capture_sequence or self.game_over:
            return

        dx, dy = self.facing
        tx = self.player_x + dx
        ty = self.player_y + dy

        if not self.in_bounds(tx, ty):
            self.msg = "No locked security door in front of you."
            self.sound.play("blocked")
            return

        door = self.grid[ty][tx]

        if door == "X":
            if len(self.unlocked) < len(QUESTIONS):
                self.msg = "The exit is sealed. Unlock all 10 doors first."
                self.sound.play("blocked")
            elif not self.has_keycard:
                self.msg = "ACCESS DENIED. A keycard is required for the EXIT."
                self.sound.play("blocked")
            else:
                self.complete_game()
            return

        if door not in QUESTIONS:
            self.msg = "No locked security door in front of you."
            self.sound.play("blocked")
            return

        cooldown = self.door_cooldowns.get(door, 0)
        if cooldown > 0:
            self.msg = f"Door {DOOR_LABELS[door]} is cooling down. Retry in {math.ceil(cooldown)}s."
            self.sound.play("blocked")
            return

        self.show_hacking_screen(door, tx, ty)

    def show_hacking_screen(self, door, tx, ty):
        self.set_scene("hacking")
        self.keys.clear()
        self.hacking = {
            "door": door,
            "x": tx,
            "y": ty,
            "progress": 0.0,
            "text": "\n".join(HACKING_LINES),
        }
        self.draw_hacking_screen()

    def draw_hacking_screen(self):
        self.cleanup_widgets()
        self.draw_game(decrement_effects=False)

        if not self.hacking:
            return

        progress = self.hacking["progress"]
        full_text = self.hacking["text"]
        visible_count = min(len(full_text), int(progress * 46))
        visible_text = full_text[:visible_count]
        cursor = "_" if int(progress * 4) % 2 == 0 else " "
        percent = min(100, int((visible_count / max(1, len(full_text))) * 100))
        bar_units = 22
        filled = min(bar_units, int(bar_units * percent / 100))
        progress_bar = "[" + "#" * filled + "." * (bar_units - filled) + f"] {percent:03d}%"

        self.canvas.create_rectangle(105, 145, 795, 600, fill="#010302", outline="#1fff66", width=3)
        self.canvas.create_rectangle(135, 180, 765, 565, fill="#041009", outline="#116d32", width=2)
        self.canvas.create_text(
            165,
            215,
            anchor="nw",
            text=f"HACKING DOOR {DOOR_LABELS[self.hacking['door']]}",
            fill="#7cff8a",
            font=("Consolas", 22, "bold"),
        )
        self.canvas.create_text(
            165,
            275,
            anchor="nw",
            text=visible_text + cursor,
            fill="#b6ffc5",
            font=("Consolas", 14, "bold"),
            width=560,
        )
        self.canvas.create_text(
            165,
            485,
            anchor="nw",
            text=progress_bar,
            fill="#50ff75",
            font=("Consolas", 14, "bold"),
            width=560,
        )

    def update_hacking(self):
        if self.scene != "hacking" or not self.hacking:
            return

        self.hacking["progress"] += 0.09
        total_needed = len(self.hacking["text"]) / 46 + 0.55

        if self.hacking["progress"] >= total_needed:
            door = self.hacking["door"]
            tx = self.hacking["x"]
            ty = self.hacking["y"]
            self.hacking = None
            self.show_quiz_screen(door, tx, ty)
        else:
            self.draw_hacking_screen()

    def show_quiz_screen(self, door, tx, ty):
        self.scene = "quiz"
        self.keys.clear()
        self.quiz = {"door": door, "x": tx, "y": ty, "answer": ""}
        self.draw_quiz_screen()

    def draw_quiz_screen(self):
        self.cleanup_widgets()
        self.draw_game(decrement_effects=False)

        if not self.quiz:
            return

        data = QUESTIONS[self.quiz["door"]]

        self.canvas.create_rectangle(60, 70, 840, 680, fill="#010302", outline="#1fff66", width=3)
        self.canvas.create_rectangle(90, 100, 810, 650, fill="#041009", outline="#116d32", width=2)

        frame = tk.Frame(self.root, bg="#041009")
        self.widgets.append(frame)
        self.canvas.create_window(450, 375, window=frame, width=680, height=500)

        wrap = max(320, int(610 * self.canvas.scale_factor))

        tk.Label(
            frame,
            text=f"DOOR {DOOR_LABELS[self.quiz['door']]} SECURITY LOCK",
            font=self.canvas.font(19, "bold"),
            fg="#7cff8a",
            bg="#041009",
            anchor="w",
        ).pack(fill="x", padx=18, pady=(16, 8))

        tk.Label(
            frame,
            text=data["question"],
            font=self.canvas.font(15, "bold"),
            fg="#d7ffdc",
            bg="#041009",
            wraplength=wrap,
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=18, pady=(0, 12))

        for choice in data["choices"]:
            tk.Label(
                frame,
                text=choice,
                font=self.canvas.font(11, "bold"),
                fg="#b6ffc5",
                bg="#041009",
                wraplength=wrap,
                justify="left",
                anchor="w",
            ).pack(fill="x", padx=32, pady=3)

        tk.Label(
            frame,
            text=f"HINT: {data['hint']}",
            font=self.canvas.font(10, "bold"),
            fg="#50ff75",
            bg="#041009",
            wraplength=wrap,
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=18, pady=(14, 8))

        answer_row = tk.Frame(frame, bg="#041009")
        answer_row.pack(fill="x", padx=18, pady=(0, 12))

        tk.Label(
            answer_row,
            text="Answer:",
            font=self.canvas.font(13, "bold"),
            fg="#7cff8a",
            bg="#041009",
        ).pack(side="left", padx=(0, 10))

        self.quiz_answer_var = tk.StringVar(value=self.quiz.get("answer", ""))
        answer_entry = tk.Entry(
            answer_row,
            textvariable=self.quiz_answer_var,
            font=self.canvas.font(13, "bold"),
            width=12,
            bg="#06170c",
            fg="#caffca",
            insertbackground="#caffca",
            relief="flat",
            justify="center",
        )
        answer_entry.pack(side="left", ipady=4)
        answer_entry.focus_set()
        answer_entry.bind("<Return>", lambda event: self.submit_quiz_answer())

        button_row = tk.Frame(frame, bg="#041009")
        button_row.pack(anchor="w", padx=18, pady=(0, 12))

        submit_button = tk.Button(
            button_row,
            text="SUBMIT",
            command=lambda: (self.sound.play("click"), self.submit_quiz_answer()),
            **self.button_style(12),
        )
        cancel_button = tk.Button(
            button_row,
            text="CANCEL",
            command=lambda: (self.sound.play("click"), self.cancel_quiz()),
            **self.button_style(12),
        )
        submit_button.pack(side="left", padx=(0, 10), ipadx=12, ipady=4)
        cancel_button.pack(side="left", ipadx=12, ipady=4)

    def submit_quiz_answer(self):
        if not self.quiz:
            return

        answer = self.quiz_answer_var.get() if self.quiz_answer_var is not None else ""
        door = self.quiz["door"]
        tx = self.quiz["x"]
        ty = self.quiz["y"]
        self.quiz = None
        self.quiz_answer_var = None
        self.cleanup_widgets()
        self.scene = "game"
        self.root.focus_set()

        if answer and clean_answer(answer) in QUESTIONS[door]["answers"]:
            self.grid[ty][tx] = "."
            self.unlocked.add(door)
            self.msg = f"Door {DOOR_LABELS[door]} unlocked. {len(QUESTIONS) - len(self.unlocked)} remain."

            if len(self.unlocked) >= self.difficulty["spawn_after"]:
                if self.enemy_active:
                    self.alert_enemy_to_door(tx, ty)
                else:
                    self.spawn_enemy()

            if len(self.unlocked) == len(QUESTIONS):
                self.activate_keycard_phase()

            self.sound.play("unlock")
        else:
            self.take_damage(door)

        if self.scene == "game":
            self.draw_game()

    def find_exit(self):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == "X":
                    return x, y
        return len(self.grid[0]) - 2, len(self.grid) - 2

    def choose_keycard_position(self):
        exit_x, exit_y = self.find_exit()
        reachable = self.reachable_tiles_from(self.player_x, self.player_y)
        choices = []

        for point, distance in reachable.items():
            x, y = point
            if self.grid[y][x] != ".":
                continue

            exit_distance = abs(x - exit_x) + abs(y - exit_y)
            if distance >= 5 and exit_distance >= 4:
                choices.append((point, distance + exit_distance))

        if choices:
            return max(choices, key=lambda item: item[1])[0]

        for point in reachable:
            x, y = point
            if self.grid[y][x] == ".":
                return point

        return self.nearest_walkable(self.player_x, self.player_y)

    def activate_keycard_phase(self):
        self.exit_active = True
        self.final_chase = True
        self.enemy_track_timer = 9999.0

        if not self.has_keycard and not self.keycard_active:
            key_x, key_y = self.choose_keycard_position()
            self.keycard_pos = (key_x, key_y)
            self.keycard_active = True
            self.grid[key_y][key_x] = "K"

        if not self.enemy_active:
            self.spawn_enemy()

        self.enemy_mode = "final_chase"
        self.enemy_speed = self.maximum_enemy_speed()
        self.enemy_target = self.nearest_walkable(self.player_x, self.player_y)
        self.msg = "ALL DOORS OPEN. KEYCARD SPAWNED. FINAL CHASE ACTIVE."
        self.sound.play("alert")

    def cancel_quiz(self):
        self.quiz = None
        self.quiz_answer_var = None
        self.cleanup_widgets()
        self.scene = "game"
        self.root.focus_set()
        self.msg = "Hack cancelled. Find the next locked security door."
        self.draw_game()

    def take_damage(self, door):
        self.lives = max(0, self.lives - 1)
        self.alarm = 14
        self.damage_flash = 14
        self.msg = f"ACCESS DENIED at Door {DOOR_LABELS[door]}. Life lost."
        self.door_cooldowns[door] = DOOR_COOLDOWN_SECONDS
        self.enemy_track_timer = max(self.enemy_track_timer, self.difficulty["track_time"])

        if not self.enemy_active:
            self.spawn_enemy()

        self.msg = f"ACCESS DENIED at Door {DOOR_LABELS[door]}. Retry in {DOOR_COOLDOWN_SECONDS:.0f}s."
        self.sound.play("damage")

        if self.lives <= 0:
            self.start_capture_sequence()

    def update_game_timers(self):
        expired = []

        for door, remaining in self.door_cooldowns.items():
            new_remaining = max(0.0, remaining - 0.09)
            self.door_cooldowns[door] = new_remaining

            if new_remaining <= 0:
                expired.append(door)

        for door in expired:
            self.door_cooldowns.pop(door, None)

        if self.enemy_track_timer > 0:
            self.enemy_track_timer = max(0.0, self.enemy_track_timer - 0.09)

    def spawn_enemy(self, play_sound=True):
        if self.enemy_active:
            return

        reachable = self.reachable_tiles_from(self.player_x, self.player_y)
        possible_spawns = [
            point
            for point, distance in reachable.items()
            if distance >= 6 and point != (self.player_x, self.player_y)
        ]

        if possible_spawns:
            spawn = max(possible_spawns, key=lambda point: reachable[point])
        elif reachable:
            spawn = max(reachable, key=lambda point: reachable[point])
        else:
            spawn = self.nearest_walkable(self.player_x, self.player_y)

        self.enemy_active = True
        self.enemy_mode = "patrol"
        self.enemy_x, self.enemy_y = float(spawn[0]), float(spawn[1])
        self.enemy_target = self.make_patrol_target()
        self.enemy_last_position = spawn
        self.enemy_stuck_timer = 0
        self.enemy_think_timer = 0
        self.msg = "WARNING: Unknown presence detected inside the house."

        if play_sound:
            self.sound.play("spawn")

    def alert_enemy_to_door(self, door_x, door_y):
        if not self.enemy_active:
            return

        self.enemy_mode = "investigate"
        self.enemy_target = self.nearest_walkable(door_x, door_y)
        self.enemy_search_origin = self.enemy_target
        self.enemy_search_points = self.build_search_points(*self.enemy_target)
        self.enemy_search_timer = 60
        self.enemy_speed = self.difficulty["investigate_speed"]
        self.sound.play("alert")

    def enemy_cell(self):
        return int(round(self.enemy_x)), int(round(self.enemy_y))

    def neighbors(self, x, y):
        options = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return [(nx, ny) for nx, ny in options if self.walkable_for_enemy(nx, ny)]

    def nearest_walkable(self, x, y):
        x = int(round(x))
        y = int(round(y))

        if self.walkable_for_enemy(x, y):
            return x, y

        queue = deque([(x, y)])
        seen = {(x, y)}

        while queue:
            cx, cy = queue.popleft()

            for nx, ny in [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)]:
                if (nx, ny) in seen or not self.in_bounds(nx, ny):
                    continue

                if self.walkable_for_enemy(nx, ny):
                    return nx, ny

                seen.add((nx, ny))
                queue.append((nx, ny))

        return self.player_x, self.player_y

    def find_path(self, start, goal):
        start = self.nearest_walkable(start[0], start[1])
        goal = self.nearest_walkable(goal[0], goal[1])

        queue = deque([start])
        came_from = {start: None}

        while queue:
            current = queue.popleft()

            if current == goal:
                break

            for nxt in self.neighbors(current[0], current[1]):
                if nxt not in came_from:
                    came_from[nxt] = current
                    queue.append(nxt)

        if goal not in came_from:
            return []

        path = []
        current = goal

        while current is not None:
            path.append(current)
            current = came_from[current]

        path.reverse()
        return path

    def make_general_player_target(self):
        options = []

        for dy in range(-3, 4):
            for dx in range(-3, 4):
                tx = self.player_x + dx
                ty = self.player_y + dy

                if abs(dx) + abs(dy) <= 4 and self.walkable_for_enemy(tx, ty):
                    options.append((tx, ty))

        if options and random.random() < 0.55:
            return random.choice(options)

        return self.nearest_walkable(self.player_x, self.player_y)

    def make_patrol_target(self):
        if not self.enemy_active:
            return self.nearest_walkable(self.player_x, self.player_y)

        reachable = self.reachable_tiles_from(*self.enemy_cell())
        patrol_options = [
            point
            for point, distance in reachable.items()
            if distance >= 4 and point != self.enemy_cell()
        ]

        if patrol_options:
            return random.choice(patrol_options)

        return self.make_general_player_target()

    def can_enemy_detect_player(self):
        if not self.enemy_active:
            return False

        path = self.find_path(self.enemy_cell(), (self.player_x, self.player_y))

        if not path:
            return False

        return len(path) - 1 <= self.difficulty["detection_range"]

    def maximum_enemy_speed(self):
        return max(config["final_speed"] for config in DIFFICULTIES.values())

    def build_search_points(self, x, y):
        points = []

        for dy in range(-2, 3):
            for dx in range(-2, 3):
                tx = x + dx
                ty = y + dy

                if abs(dx) + abs(dy) <= 3 and self.walkable_for_enemy(tx, ty):
                    points.append((tx, ty))

        random.shuffle(points)
        return points or [self.nearest_walkable(x, y)]

    def pick_search_target(self):
        while self.enemy_search_points:
            point = self.enemy_search_points.pop(0)
            if self.walkable_for_enemy(point[0], point[1]):
                return point

        return self.make_general_player_target()

    def move_enemy_toward(self, target):
        if target is None:
            return True

        target = self.nearest_walkable(target[0], target[1])
        start = self.enemy_cell()
        path = self.find_path(start, target)

        if not path:
            return False

        if len(path) == 1:
            next_x, next_y = target
        else:
            next_x, next_y = path[1]

        dx = next_x - self.enemy_x
        dy = next_y - self.enemy_y
        distance = math.hypot(dx, dy)

        if distance <= 0.001:
            self.enemy_x = float(next_x)
            self.enemy_y = float(next_y)
        elif distance <= self.enemy_speed:
            self.enemy_x = float(next_x)
            self.enemy_y = float(next_y)
        else:
            self.enemy_x += (dx / distance) * self.enemy_speed
            self.enemy_y += (dy / distance) * self.enemy_speed

        self.enemy_x = max(0.0, min(float(len(self.grid[0]) - 1), self.enemy_x))
        self.enemy_y = max(0.0, min(float(len(self.grid) - 1), self.enemy_y))

        return abs(self.enemy_x - target[0]) < 0.12 and abs(self.enemy_y - target[1]) < 0.12

    def ensure_enemy_can_reach_player(self):
        if not self.enemy_active:
            self.spawn_enemy()

        reachable = self.reachable_tiles_from(self.player_x, self.player_y)
        enemy_position = self.enemy_cell()

        if enemy_position in reachable:
            return

        possible_spawns = [
            point
            for point, distance in reachable.items()
            if distance >= 4 and point != (self.player_x, self.player_y)
        ]

        if possible_spawns:
            spawn = max(possible_spawns, key=lambda point: reachable[point])
        elif reachable:
            spawn = max(reachable, key=lambda point: reachable[point])
        else:
            spawn = self.nearest_walkable(self.player_x, self.player_y)

        self.enemy_x = float(spawn[0])
        self.enemy_y = float(spawn[1])
        self.enemy_target = self.nearest_walkable(self.player_x, self.player_y)

    def update_enemy(self):
        if not self.enemy_active or self.game_over:
            return

        self.enemy_think_timer += 1
        old_x, old_y = self.enemy_x, self.enemy_y

        player_detected = self.can_enemy_detect_player()

        if self.final_chase:
            self.enemy_mode = "final_chase"
        elif self.enemy_track_timer > 0 or player_detected:
            self.enemy_mode = "chase"

        if self.enemy_mode == "final_chase":
            self.enemy_speed = self.maximum_enemy_speed()
            self.enemy_target = self.nearest_walkable(self.player_x, self.player_y)
            reached = self.move_enemy_toward(self.enemy_target)

            if reached or self.enemy_think_timer % 4 == 0:
                self.enemy_target = self.nearest_walkable(self.player_x, self.player_y)

        elif self.enemy_mode == "chase":
            self.enemy_speed = self.difficulty["chase_speed"]
            self.enemy_target = self.nearest_walkable(self.player_x, self.player_y)
            reached = self.move_enemy_toward(self.enemy_target)

            if reached or self.enemy_think_timer % 5 == 0:
                self.enemy_target = self.nearest_walkable(self.player_x, self.player_y)

            if self.enemy_track_timer <= 0 and not player_detected:
                self.enemy_mode = "search"
                self.enemy_search_points = self.build_search_points(self.player_x, self.player_y)
                self.enemy_search_timer = 45
                self.enemy_target = self.pick_search_target()

        elif self.enemy_mode == "investigate":
            self.enemy_speed = self.difficulty["investigate_speed"]
            reached = self.move_enemy_toward(self.enemy_target)

            if reached:
                self.enemy_mode = "search"
                self.enemy_speed = self.difficulty["search_speed"]
                self.enemy_target = self.pick_search_target()
                self.enemy_search_timer = 60

        elif self.enemy_mode == "search":
            self.enemy_speed = self.difficulty["search_speed"]
            self.enemy_search_timer -= 1

            if self.enemy_target is None:
                self.enemy_target = self.pick_search_target()

            reached = self.move_enemy_toward(self.enemy_target)

            if reached:
                self.enemy_target = self.pick_search_target()

            if self.enemy_search_timer <= 0:
                self.enemy_mode = "patrol"
                self.enemy_target = self.make_patrol_target()

        else:
            self.enemy_mode = "patrol"
            self.enemy_speed = self.difficulty["patrol_speed"]

            if self.enemy_think_timer % 12 == 0 or self.enemy_target is None:
                self.enemy_target = self.make_patrol_target()

            reached = self.move_enemy_toward(self.enemy_target)

            if reached:
                self.enemy_target = self.make_patrol_target()

        moved_distance = abs(self.enemy_x - old_x) + abs(self.enemy_y - old_y)

        if moved_distance < 0.002:
            self.enemy_stuck_timer += 1
        else:
            self.enemy_stuck_timer = 0

        if self.enemy_stuck_timer > 14:
            self.enemy_stuck_timer = 0

            if self.enemy_mode in ("chase", "final_chase"):
                self.enemy_target = self.nearest_walkable(self.player_x, self.player_y)
                self.ensure_enemy_can_reach_player()
            elif self.enemy_mode == "search":
                self.enemy_target = self.pick_search_target()
            elif self.enemy_mode == "investigate":
                self.enemy_mode = "search"
                self.enemy_target = self.pick_search_target()
            else:
                self.enemy_target = self.make_patrol_target()

        if abs(self.enemy_x - self.player_x) < 0.42 and abs(self.enemy_y - self.player_y) < 0.42:
            self.lives = 0
            self.start_capture_sequence()

    def start_capture_sequence(self):
        if self.capture_sequence or self.game_over:
            return

        self.keys.clear()
        self.capture_elapsed_time = self.elapsed_time()
        self.capture_sequence = True
        self.capture_timer = 0
        self.damage_flash = 18
        self.msg = "CRITICAL FAILURE: Security entity is closing in."

        if not self.enemy_active:
            self.spawn_enemy(play_sound=False)

        self.ensure_enemy_can_reach_player()
        self.enemy_mode = "capture"
        self.enemy_target = self.nearest_walkable(self.player_x, self.player_y)
        self.enemy_speed = max(0.22, self.maximum_enemy_speed())
        self.sound.play_loop("warning_loop", delay_ms=310)

    def update_capture_sequence(self):
        if not self.capture_sequence or self.game_over:
            return

        self.capture_timer += 1
        self.enemy_mode = "capture"
        self.enemy_speed = max(0.22, self.maximum_enemy_speed())
        self.enemy_target = self.nearest_walkable(self.player_x, self.player_y)
        self.ensure_enemy_can_reach_player()

        if self.enemy_active:
            self.move_enemy_toward(self.enemy_target)

        caught = (
            self.enemy_active
            and abs(self.enemy_x - self.player_x) < 0.42
            and abs(self.enemy_y - self.player_y) < 0.42
        )

        if caught or self.capture_timer >= 85:
            self.show_captured_screen()

    def draw_tile(self, x, y, cell):
        px = x * TILE + 28
        py = y * TILE + HUD

        if cell == "#":
            fill = "#07120b"
            outline = "#116d32"
        elif cell in QUESTIONS:
            fill = "#123018"
            outline = "#8cff8c"
        elif cell == "K":
            fill = "#232000"
            outline = "#ffe66d"
        elif cell == "X":
            fill = "#0c1d26" if not self.exit_active else "#052b2d"
            outline = "#72e8ff" if not self.exit_active else "#29fff2"
        else:
            fill = "#020805"
            outline = "#05230f"

        self.canvas.create_rectangle(px, py, px + TILE, py + TILE, fill=fill, outline=outline)

        if cell in QUESTIONS:
            label = DOOR_LABELS[cell]
            font_size = 11 if len(label) > 1 else 13
            self.canvas.create_text(
                px + TILE / 2,
                py + TILE / 2,
                text=label,
                fill="#caffca",
                font=("Consolas", font_size, "bold"),
            )

            cooldown = self.door_cooldowns.get(cell, 0)
            if cooldown > 0:
                self.canvas.create_rectangle(px + 3, py + 3, px + TILE - 3, py + TILE - 3, outline="#ff3030", width=2)
                self.canvas.create_text(
                    px + TILE / 2,
                    py + TILE - 8,
                    text=f"{math.ceil(cooldown)}",
                    fill="#ffb0b0",
                    font=("Consolas", 9, "bold"),
                )

        if cell == "K":
            self.canvas.create_text(
                px + TILE / 2,
                py + TILE / 2,
                text="KEY",
                fill="#fff0a0",
                font=("Consolas", 9, "bold"),
            )

        if cell == "X":
            self.canvas.create_text(
                px + TILE / 2,
                py + TILE / 2,
                text="EXIT",
                fill="#bffaff",
                font=("Consolas", 9, "bold"),
            )

    def draw_heart_icon(self, x, y, filled=True):
        fill = "#35ff6b" if filled else "#06170c"
        outline = "#8cff8c" if filled else "#155f2f"

        self.canvas.create_oval(x, y, x + 13, y + 13, fill=fill, outline=outline, width=2)
        self.canvas.create_oval(x + 11, y, x + 24, y + 13, fill=fill, outline=outline, width=2)
        self.canvas.create_polygon(
            x + 1,
            y + 8,
            x + 23,
            y + 8,
            x + 12,
            y + 26,
            fill=fill,
            outline=outline,
        )

    def draw_lives(self):
        self.canvas.create_text(
            455,
            28,
            anchor="nw",
            text="LIVES:",
            fill="#50ff75",
            font=("Consolas", 15, "bold"),
        )

        for index in range(self.max_lives):
            self.draw_heart_icon(525 + index * 34, 24, index < self.lives)

    def draw_enemy(self):
        if not self.enemy_active:
            return

        ex = self.enemy_x * TILE + 28
        ey = self.enemy_y * TILE + HUD

        if self.enemy_mode == "capture":
            fill = "#4b0000"
            outline = "#ff1010"
        elif self.enemy_mode in ("investigate", "final_chase", "chase"):
            fill = "#3b0505"
            outline = "#ff3030"
        elif self.enemy_mode == "search":
            fill = "#331107"
            outline = "#ff8530"
        else:
            fill = "#210606"
            outline = "#d53030"

        self.canvas.create_oval(
            ex + 5,
            ey + 5,
            ex + TILE - 5,
            ey + TILE - 5,
            fill=fill,
            outline=outline,
            width=3,
        )

        self.canvas.create_text(
            ex + TILE / 2,
            ey + TILE / 2,
            text="E",
            fill="#ffb0b0",
            font=("Consolas", 14, "bold"),
        )

        if self.enemy_mode in ("investigate", "search", "chase", "final_chase", "capture"):
            self.canvas.create_text(
                ex + TILE / 2,
                ey - 13,
                text="!",
                fill="#ff3030",
                font=("Consolas", 30, "bold"),
            )

    def draw_game(self, decrement_effects=True):
        self.canvas.delete("all")
        draw_scan_background(self.canvas, amount=24)

        elapsed = self.elapsed_time()

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
            width=410,
        )
        self.canvas.create_text(
            690,
            18,
            anchor="nw",
            text=f"LOCKS: {len(self.unlocked)}/{len(QUESTIONS)}",
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

        self.draw_lives()
        self.canvas.create_text(
            455,
            62,
            anchor="nw",
            text=f"KEYCARD: {'YES' if self.has_keycard else 'NO'}",
            fill="#ffe66d" if self.has_keycard else "#50ff75",
            font=("Consolas", 11, "bold"),
        )
        self.canvas.create_text(
            690,
            78,
            anchor="nw",
            text=f"MODE: {self.difficulty['label']}",
            fill="#50ff75",
            font=("Consolas", 11, "bold"),
        )

        if self.enemy_active:
            self.canvas.create_text(
                545,
                78,
                anchor="nw",
                text=f"ENEMY: {self.enemy_mode.upper()}",
                fill="#ffb0b0" if self.enemy_mode in ("chase", "final_chase", "capture") else "#b6ffc5",
                font=("Consolas", 10, "bold"),
                width=135,
            )

        active_cooldowns = [
            f"{DOOR_LABELS[door]}:{math.ceil(seconds)}s"
            for door, seconds in sorted(self.door_cooldowns.items())
            if seconds > 0
        ]

        if active_cooldowns:
            self.canvas.create_text(
                285,
                100,
                anchor="nw",
                text="COOLDOWN " + "  ".join(active_cooldowns),
                fill="#ffb0b0",
                font=("Consolas", 11, "bold"),
                width=360,
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

        if self.capture_sequence:
            self.canvas.create_text(
                WIDTH / 2,
                HEIGHT / 2 - 90,
                text="CAPTURE IMMINENT",
                fill="#ff3030",
                font=("Consolas", 28, "bold"),
            )
            self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, outline="#ff3030", width=10)

        if self.alarm > 0:
            self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, outline="#ff2b2b", width=8)
            if decrement_effects:
                self.alarm -= 1

        if self.damage_flash > 0:
            self.canvas.create_text(
                WIDTH / 2,
                122,
                text="LIFE LOST",
                fill="#ff4a4a",
                font=("Consolas", 24, "bold"),
            )
            self.canvas.create_rectangle(10, 10, WIDTH - 10, HEIGHT - 10, outline="#ff3030", width=4)
            if decrement_effects:
                self.damage_flash -= 1

    def complete_game(self):
        self.sound.stop_loop()
        self.game_over = True
        self.finish_time = self.elapsed_time()
        self.new_record = save_score(self.player_name, self.finish_time)
        self.scene = "win"
        self.draw_win_screen()
        self.sound.play("win")

    def draw_win_screen(self):
        self.clear_scene()
        draw_scan_background(self.canvas, amount=48)

        self.canvas.create_rectangle(0, 0, WIDTH, HUD, fill="#020a05", outline="#1fff66")
        self.canvas.create_text(28, 18, anchor="nw", text="HACKER HOUSE", fill="#91ff9d", font=("Consolas", 24, "bold"))
        self.canvas.create_text(30, 55, anchor="nw", text="FINAL SYSTEM STATUS: ALL LOCKS OPEN", fill="#b6ffc5", font=("Consolas", 12))
        self.canvas.create_text(690, 22, anchor="nw", text=f"LOCKS: {len(QUESTIONS)}/{len(QUESTIONS)}", fill="#50ff75", font=("Consolas", 18, "bold"))

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

        self.canvas.create_rectangle(545, 165, 835, 545, fill="#020a05", outline="#1fff66", width=2)
        self.canvas.create_rectangle(565, 185, 815, 525, fill="#041009", outline="#116d32")

        record_text = "NEW RECORD SAVED" if self.new_record else "BEST TIME KEPT"
        self.canvas.create_text(690, 230, text="CONGRATS!", fill="#7cff8a", font=("Consolas", 38, "bold"))
        self.canvas.create_text(690, 295, text="YOU ESCAPED", fill="#b6ffc5", font=("Consolas", 26, "bold"))
        self.canvas.create_text(690, 355, text=f"PLAYER: {self.player_name}", fill="#50ff75", font=("Consolas", 17, "bold"), width=240)
        self.canvas.create_text(690, 400, text=f"TIME: {format_time(self.finish_time)}", fill="#b6ffc5", font=("Consolas", 18, "bold"))
        self.canvas.create_text(690, 445, text=record_text, fill="#91ff9d", font=("Consolas", 15, "bold"))

        self.add_button("MAIN MENU", self.show_main_menu, 690, 490, 190, 42, font_size=15)

        self.canvas.create_rectangle(72, 595, 835, 652, fill="#020a05", outline="#1fff66")
        self.canvas.create_text(
            96,
            613,
            anchor="nw",
            text="MISSION COMPLETE: QUESTION LOCKS CLEARED | EXIT ROUTE UNSEALED | PLAYER STATUS SAFE",
            fill="#91ff9d",
            font=("Consolas", 12, "bold"),
            width=720,
        )

    def show_captured_screen(self):
        self.sound.stop_loop()
        self.game_over = True
        self.capture_sequence = False
        self.keys.clear()
        self.scene = "captured"
        self.draw_captured_screen()
        self.sound.play("captured")

    def draw_captured_screen(self):
        self.clear_scene()
        draw_scan_background(self.canvas, amount=58)

        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#080101", outline="")
        draw_scan_background(self.canvas, amount=36)

        self.canvas.create_rectangle(95, 120, 805, 610, fill="#100303", outline="#ff3030", width=3)
        self.canvas.create_rectangle(125, 150, 775, 580, fill="#190707", outline="#7a1d1d", width=2)

        self.canvas.create_text(
            WIDTH / 2,
            210,
            text="YOU WERE CAPTURED",
            fill="#ff4a4a",
            font=("Consolas", 42, "bold"),
        )
        self.canvas.create_text(
            WIDTH / 2,
            275,
            text="All 3 lives were lost.",
            fill="#ffb0b0",
            font=("Consolas", 18, "bold"),
        )
        self.canvas.create_text(
            WIDTH / 2,
            320,
            text="The security entity locked onto your signal.",
            fill="#b6ffc5",
            font=("Consolas", 14, "bold"),
            width=540,
        )

        for index in range(self.max_lives):
            self.draw_heart_icon(400 + index * 34, 360, False)

        self.add_button("RESTART", lambda: self.start_game(self.player_name), WIDTH / 2, 445, 210, 42, font_size=15, danger=True)
        self.add_button("MAIN MENU", self.show_main_menu, WIDTH / 2, 505, 210, 42, font_size=15, danger=True)

    def loop(self):
        if self.scene == "game":
            if self.capture_sequence:
                self.update_capture_sequence()
                if self.scene == "game":
                    self.draw_game()
            else:
                self.update_game_timers()
                self.update_player()

                if self.scene == "game":
                    self.update_enemy()

                if self.scene == "game":
                    self.draw_game()

        elif self.scene == "hacking":
            self.update_hacking()

        self.root.after(90, self.loop)


if __name__ == "__main__":
    HackerHouseApp().run()
