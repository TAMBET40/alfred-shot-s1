import array
import math
import random
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
import wave


WIDTH = 900
HEIGHT = 620
HEALTH = 5
CHAMBER_SIZE = 6
LOW_FRAME_DELAY = 100
DEVELOPER = "Tambet Sarapu"

ESTONIAN_TEXT = {
    "ALFRED SHOT S1": "ALFRED SHOT S1",
    "DEVELOPED BY": "MÄNGU AUTOR",
    "NIGHT SHIFT": "ÖÖVAHETUS",
    "ROUND": "VOOR",
    "YOU": "SINA",
    "RIVAL": "VASTANE",
    "SHELLS LEFT": "PADRUNEID",
    "A  AIM AT RIVAL": "A  SIHI VASTAST",
    "S  AIM AT SELF": "S  SIHI ENNAST",
    "CLICK A TARGET  ·  ESC: QUIT": "VALI SIHTMÄRK  ·  ESC: VÄLJU",
    "YOU WIN!": "VÕITSID!",
    "YOU LOST": "KAOTASID",
    "PRESS R OR CLICK TO RESTART": "UUESTI: VAJUTA R VÕI KLIKI",
    "RESTART": "ALUSTA UUESTI",
    "MENU": "MENÜÜ",
    "PLAY": "MÄNGI",
    "CONTINUE": "JÄTKA",
    "NEW GAME": "UUS MÄNG",
    "LANGUAGE": "KEEL",
    "GRAPHICS": "GRAAFIKA",
    "EXIT": "VÄLJU",
    "BACK": "TAGASI",
    "SELECT LANGUAGE": "VALI KEEL",
    "GRAPHICS QUALITY": "GRAAFIKA KVALITEET",
    "ENGLISH": "INGLISE",
    "ESTONIAN": "EESTI",
    "HIGH": "KÕRGE",
    "LOW": "MADAL",
    "PLAYER": "MÄNGIJA",
    "LINUX": "DEBIAN GNU/LINUX",
    "THINKPAD": "ThinkPad",
    "LIVE": "PÄRIS",
    "BLANK": "TÜHI",
    "Choose your target.": "Vali sihtmärk.",
    "LIVE ROUNDS": "PÄRIS PADRUNEID",
    "BLANK ROUNDS": "TÜHJE PADRUNEID",
    "HIT! THE RIVAL FLIES BACK!": "TABAMUS! VASTANE LENDAB EEMALE!",
    "GAME SETTINGS": "MÄNGU SEADED",
    "MENU": "MENÜÜ",
    "QUALITY": "KVALITEET",
    "CURRENTLY SELECTED": "VALITUD",
    "LOW DETAIL / LIGHTER ON YOUR COMPUTER": "VÄHEM DETAILI / VÄIKSEM KOORMUS",
    "FULL DETAIL / MORE PARTICLES": "TÄISDETAIL / ROHKEM OSAKESI",
    "M: MENU": "M: MENÜÜ",
    "ESC: QUIT": "ESC: VÄLJU",
    "Chamber loaded. Choose your target.": "Padrunid laetud. Vali sihtmärk.",
    "New game. Your turn.": "Uus mäng. Sinu kord.",
    "The rival is down. You win!": "Vastane on maas. Sina võitsid!",
    "The rival grabs the gun and aims at itself...": "Vastane haarab relva ja sihib ennast...",
    "The rival grabs the gun and aims at you...": "Vastane haarab relva ja sihib sind...",
    "You grab the gun and take aim...": "Haarad relva ja sihid...",
    "The rival reaches for the gun...": "Vastane haarab relva...",
    "You reach for the gun...": "Haarad relva...",
    "The rival aims at itself...": "Vastane sihib ennast...",
    "The rival aims at you...": "Vastane sihib sind...",
    "You aim at yourself...": "Sihid ennast...",
    "You aim at the rival...": "Sihid vastast...",
    "The rival fires at itself!": "Vastane tulistab ennast!",
    "The rival fires at you!": "Vastane tulistab sind!",
    "You fire at yourself!": "Tulistad ennast!",
    "You fire at the rival!": "Tulistad vastast!",
    "The rival is hit!": "Vastane sai tabamuse!",
    "New chamber loaded. Your turn.": "Uued padrunid laetud. Sinu kord.",
    "Direct hit!": "Täistabamus!",
    "The rival hit itself.": "Vastane tabas ennast.",
    "You hit yourself.": "Tabasid ennast.",
    "The rival hit you!": "Vastane tabas sind!",
    "Click. Empty shell — you keep your turn.": "Klõps. Tühi padrun — saad uuesti valida.",
    "Click. The rival keeps its turn.": "Klõps. Vastane saab uuesti valida.",
    "The rival fired a blank.": "Vastane tulistas tühja padruniga.",
    "Click. Empty shell.": "Klõps. Tühi padrun.",
}

BG = "#111516"
PANEL = "#1c2221"
PANEL_LIGHT = "#252b29"
TEXT = "#eee7d9"
MUTED = "#aaa596"
RED = "#b84d3f"
MINT = "#83b8a8"
GOLD = "#a78656"


class DuelState:
    def __init__(self):
        self.round_number = 0
        self.new_game()

    def new_game(self):
        self.round_number += 1
        self.player_hp = HEALTH
        self.rival_hp = HEALTH
        self.game_over = False
        self.load_chamber()

    def load_chamber(self):
        live_count = random.randint(2, 4)
        self.chamber = [True] * live_count + [False] * (CHAMBER_SIZE - live_count)
        random.shuffle(self.chamber)
        self.chamber_index = 0
        self.turn = "player"

    @property
    def remaining(self):
        return len(self.chamber) - self.chamber_index

    def fire(self, shooter, target):
        if shooter not in ("player", "rival"):
            raise ValueError(f"Unknown shooter: {shooter!r}")
        valid_targets = ("self", "rival") if shooter == "player" else ("player", "rival")
        if target not in valid_targets:
            raise ValueError(f"Invalid target {target!r} for {shooter}")
        if self.game_over or self.turn != shooter or self.remaining == 0:
            return None

        live = self.chamber[self.chamber_index]
        self.chamber_index += 1
        is_self_shot = target == "self" or (shooter == "rival" and target == "rival")

        if live and target == "rival":
            self.rival_hp -= 1
            message = "The rival hit itself." if shooter == "rival" else "Direct hit!"
        elif live:
            self.player_hp -= 1
            message = "The rival hit you!" if shooter == "rival" else "You hit yourself."
        elif is_self_shot:
            message = "Click. Empty shell — you keep your turn." if shooter == "player" else "Click. The rival keeps its turn."
        else:
            message = "The rival fired a blank." if shooter == "rival" else "Click. Empty shell."

        if self.player_hp == 0 or self.rival_hp == 0:
            self.game_over = True
            self.turn = "game_over"
        elif self.remaining == 0:
            self.turn = "reload"
        elif not live and is_self_shot:
            self.turn = shooter
        else:
            self.turn = "rival" if shooter == "player" else "player"

        return message


class AudioEffects:
    SAMPLE_RATE = 22050
    AMBIENCE_VOLUME = "18000"
    SHOT_VOLUME = "26000"

    def __init__(self):
        self.player = shutil.which("paplay")
        self.temp_dir = tempfile.TemporaryDirectory(prefix="alfred-shot-audio-")
        self.shot_path = f"{self.temp_dir.name}/shot.wav"
        self.click_path = f"{self.temp_dir.name}/click.wav"
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.ambient_thread = None
        self.ambient_process = None
        self.shot_processes = set()
        self.shot_threads = set()
        self.closed = False
        self.unavailable_reported = False
        self._write_shot_effect()

    def _write_shot_effect(self):
        rng = random.Random(9173)
        duration = 0.55
        frame_count = int(self.SAMPLE_RATE * duration)
        samples = array.array("h")
        for index in range(frame_count):
            elapsed = index / self.SAMPLE_RATE
            envelope = math.exp(-elapsed * 17)
            crack = rng.uniform(-1.0, 1.0) * envelope * 0.50
            thump = math.sin(math.tau * (72 * elapsed + 18 * elapsed**2)) * envelope * 0.38
            tail = math.sin(math.tau * 145 * elapsed) * math.exp(-elapsed * 10) * 0.14
            sample = max(-0.9, min(0.9, crack + thump + tail))
            samples.append(round(sample * 32767))
        if sys.byteorder != "little":
            samples.byteswap()
        with wave.open(self.shot_path, "wb") as audio_file:
            audio_file.setnchannels(1)
            audio_file.setsampwidth(2)
            audio_file.setframerate(self.SAMPLE_RATE)
            audio_file.writeframes(samples.tobytes())
        self._write_click_effect()

    def _write_click_effect(self):
        rng = random.Random(4221)
        frame_count = int(self.SAMPLE_RATE * 0.075)
        samples = array.array("h")
        for index in range(frame_count):
            elapsed = index / self.SAMPLE_RATE
            envelope = math.exp(-elapsed * 105)
            click = rng.uniform(-1.0, 1.0) * envelope * 0.18
            ring = math.sin(math.tau * 1180 * elapsed) * envelope * 0.16
            samples.append(round((click + ring) * 32767))
        if sys.byteorder != "little":
            samples.byteswap()
        with wave.open(self.click_path, "wb") as audio_file:
            audio_file.setnchannels(1)
            audio_file.setsampwidth(2)
            audio_file.setframerate(self.SAMPLE_RATE)
            audio_file.writeframes(samples.tobytes())

    def start_ambience(self):
        if self.player is None:
            self._report_unavailable()
            return
        with self.lock:
            if self.closed:
                return
            existing_thread = self.ambient_thread
            if existing_thread and existing_thread.is_alive() and not self.stop_event.is_set():
                return
        if existing_thread and existing_thread.is_alive():
            existing_thread.join(timeout=1)
        with self.lock:
            if self.closed or (self.ambient_thread and self.ambient_thread.is_alive()):
                return
            self.stop_event.clear()
            self.ambient_thread = threading.Thread(
                target=self._play_ambience,
                name="alfred-server-ambience",
                daemon=True,
            )
            self.ambient_thread.start()

    def _play_ambience(self):
        command = [
            self.player,
            "--raw",
            f"--rate={self.SAMPLE_RATE}",
            "--channels=1",
            "--format=s16le",
            f"--volume={self.AMBIENCE_VOLUME}",
        ]
        process = None
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            with self.lock:
                self.ambient_process = process
                should_stop = self.closed or self.stop_event.is_set()
            if should_stop:
                process.terminate()
                return

            frame = 0
            frames_per_chunk = self.SAMPLE_RATE // 10
            while not self.stop_event.is_set():
                samples = array.array(
                    "h",
                    (
                        round(
                            (
                                math.sin(math.tau * 53 * (frame + offset) / self.SAMPLE_RATE) * 0.10
                                + math.sin(math.tau * 79 * (frame + offset) / self.SAMPLE_RATE) * 0.045
                                + math.sin(math.tau * 117 * (frame + offset) / self.SAMPLE_RATE) * 0.018
                            )
                            * 32767
                        )
                        for offset in range(frames_per_chunk)
                    ),
                )
                if sys.byteorder != "little":
                    samples.byteswap()
                process.stdin.write(samples.tobytes())
                process.stdin.flush()
                frame += frames_per_chunk
        except (BrokenPipeError, OSError) as error:
            if not self.stop_event.is_set() and not self.closed:
                print(f"ALFRED SHOT audio: server ambience stopped: {error}", file=sys.stderr)
        finally:
            if process is not None:
                if process.stdin is not None:
                    try:
                        process.stdin.close()
                    except OSError as error:
                        if not self.stop_event.is_set() and not self.closed:
                            print(f"ALFRED SHOT audio: server ambience pipe closed: {error}", file=sys.stderr)
                process.wait()
                message = process.stderr.read().decode(errors="replace").strip()
                if process.returncode and not self.stop_event.is_set() and not self.closed:
                    print(f"ALFRED SHOT audio: {message or 'server ambience playback failed'}", file=sys.stderr)
            with self.lock:
                if self.ambient_process is process:
                    self.ambient_process = None

    def play_shot(self):
        self._play_effect(self.shot_path, "gunshot")

    def play_click(self):
        self._play_effect(self.click_path, "dry-fire click")

    def _play_effect(self, path, name):
        if self.player is None:
            self._report_unavailable()
            return
        with self.lock:
            if self.closed:
                return
            thread = threading.Thread(
                target=self._play_effect_file,
                args=(path, name),
                name="alfred-shot-effect",
                daemon=True,
            )
            self.shot_threads.add(thread)
            thread.start()

    def _play_effect_file(self, path, name):
        process = None
        try:
            try:
                process = subprocess.Popen(
                    [self.player, f"--volume={self.SHOT_VOLUME}", path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                )
            except OSError as error:
                with self.lock:
                    should_report = not self.closed
                if should_report:
                    print(f"ALFRED SHOT audio: {name} playback failed: {error}", file=sys.stderr)
                return

            with self.lock:
                should_stop = self.closed
                if not should_stop:
                    self.shot_processes.add(process)
            if should_stop and process.poll() is None:
                process.terminate()
            _, error_output = process.communicate()
            with self.lock:
                should_report = not self.closed
            if process.returncode and should_report:
                message = error_output.decode(errors="replace").strip()
                print(f"ALFRED SHOT audio: {message or f'{name} playback failed'}", file=sys.stderr)
        finally:
            with self.lock:
                if process is not None:
                    self.shot_processes.discard(process)
                self.shot_threads.discard(threading.current_thread())

    def stop_ambience(self):
        self.stop_event.set()
        with self.lock:
            process = self.ambient_process
            thread = self.ambient_thread
        if process is not None and process.poll() is None:
            process.terminate()
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=1)
        with self.lock:
            if self.ambient_thread is thread and (thread is None or not thread.is_alive()):
                self.ambient_thread = None

    def close(self):
        with self.lock:
            if self.closed:
                return
            self.closed = True
            shots = tuple(self.shot_processes)
            shot_threads = tuple(self.shot_threads)
        self.stop_ambience()
        for process in shots:
            if process.poll() is None:
                process.terminate()
        for process in shots:
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        for thread in shot_threads:
            if thread is not threading.current_thread():
                thread.join(timeout=1)
        self.temp_dir.cleanup()

    def _report_unavailable(self):
        if self.closed or self.unavailable_reported:
            return
        self.unavailable_reported = True
        print(
            "ALFRED SHOT audio: paplay was not found; install PulseAudio or PipeWire "
            "to enable sound.",
            file=sys.stderr,
        )


class AlfredShot:
    def __init__(self, root):
        self.root = root
        self.root.title("ALFRED SHOT S1 — NIGHT SHIFT")
        self.root.geometry(f"{WIDTH}x{HEIGHT + 50}")
        self.root.minsize(760, 580)
        self.root.configure(bg=BG)
        self.audio = AudioEffects()
        self.state = DuelState()
        self.message = "Chamber loaded. Choose your target."
        self.language = "en"
        self.graphics_quality = "low"
        self.screen = "menu"
        self.menu_page = "main"
        self.has_started = False
        self.ammo_notice = None
        self.ammo_notice_after = None
        self.pending_action = None
        self.animation = None
        self.shot_flash_until = 0.0
        self.death_animation = None
        self.hit_reaction = None
        self.room_flash = None
        self.room_flash_after = None
        self.casing_animation = None
        self.rival_sway_y = 0.0
        self.camera_led_tick = 0

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            bg=BG,
            highlightthickness=0,
            takefocus=True,
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.draw)
        self.root.bind("<KeyPress-a>", lambda _event: self.shoot("rival"))
        self.root.bind("<KeyPress-A>", lambda _event: self.shoot("rival"))
        self.root.bind("<KeyPress-s>", lambda _event: self.shoot("self"))
        self.root.bind("<KeyPress-S>", lambda _event: self.shoot("self"))
        self.root.bind("<KeyPress-r>", self.restart_if_over)
        self.root.bind("<KeyPress-R>", self.restart_if_over)
        self.root.bind("<KeyPress-m>", lambda _event: self.open_menu())
        self.root.bind("<KeyPress-M>", lambda _event: self.open_menu())
        self.root.bind("<Escape>", lambda _event: self.close())
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.draw()
        self.root.after(120 if self.graphics_quality == "low" else 60, self.animate_scene)

    def restart_if_over(self, _event=None):
        if self.state.game_over:
            self.state.new_game()
            self.animation = None
            self.death_animation = None
            self.hit_reaction = None
            self.clear_room_flash()
            self.message = "New game. Your turn."
            self.screen = "game"
            self.has_started = True
            self.draw()

    def close(self):
        self.audio.close()
        self.root.destroy()

    def tr(self, value):
        if self.language == "et":
            return ESTONIAN_TEXT.get(value, value)
        return value

    def open_menu(self):
        if self.screen == "game" and (self.animation is not None or self.hit_reaction is not None):
            return
        if self.pending_action is not None:
            self.root.after_cancel(self.pending_action)
            self.pending_action = None
        self.audio.stop_ambience()
        self.screen = "menu"
        self.menu_page = "main"
        self.draw()

    def close_menu(self):
        if self.has_started:
            self.screen = "game"
            self.audio.start_ambience()
            self.draw()
            self.schedule_next_turn()

    def menu_action(self, action):
        if action == "play":
            self.start_game_intro()
            return
        if action == "continue":
            self.close_menu()
            return
        if action == "new_game":
            self.state.new_game()
            self.message = "New game. Your turn."
            self.animation = None
            self.death_animation = None
            self.hit_reaction = None
            self.clear_room_flash()
            self.start_game_intro()
            return
        if action in ("language", "graphics"):
            self.menu_page = action
        elif action == "english":
            self.language = "en"
        elif action == "estonian":
            self.language = "et"
        elif action in ("low", "high"):
            self.graphics_quality = action
        elif action == "back":
            self.menu_page = "main"
        elif action == "exit":
            self.close()
            return
        self.draw()

    def start_game_intro(self):
        self.has_started = True
        self.screen = "game"
        self.audio.start_ambience()
        if self.ammo_notice_after is not None:
            self.root.after_cancel(self.ammo_notice_after)
        live_count = sum(self.state.chamber)
        self.ammo_notice = {
            "live": live_count,
            "blank": len(self.state.chamber) - live_count,
        }
        self.message = "Chamber loaded. Choose your target."
        self.draw()
        self.ammo_notice_after = self.root.after(8000, self.clear_ammo_notice)

    def clear_ammo_notice(self):
        self.ammo_notice = None
        self.ammo_notice_after = None
        if self.screen == "game":
            self.draw()

    def draw_menu_button(self, x, y, label, action, width=300, selected=False):
        left, right = x - width / 2, x + width / 2
        fill = "#263b35" if selected else "#1b2220"
        border = MINT if selected else "#786b53"
        self.canvas.create_rectangle(
            *self.scaled_box(left, y, right, y + 42),
            fill=fill,
            outline=border,
            width=2,
            tags=(f"menu_{action}",),
        )
        self.canvas.create_text(
            *self.scaled_point(x, y + 21),
            text=self.tr(label),
            fill=TEXT,
            font=("TkFixedFont", 12, "bold"),
            tags=(f"menu_{action}",),
        )
        self.canvas.tag_bind(
            f"menu_{action}",
            "<Button-1>",
            lambda _event, selected_action=action: self.menu_action(selected_action),
        )

    def draw_menu(self, width, height):
        canvas = self.canvas
        sx, sy = width / WIDTH, height / HEIGHT
        canvas.create_rectangle(0, 0, width, height, fill="#101311", outline="")
        for y in range(0, 370, 6 if self.graphics_quality == "low" else 3):
            shade = max(15, 27 - y // 30)
            color = f"#{shade:02x}{shade + 3:02x}{shade + 2:02x}"
            canvas.create_line(0, y * sy, width, y * sy, fill=color)
        canvas.create_rectangle(
            15 * sx, 84 * sy, (WIDTH - 15) * sx, 376 * sy,
            fill="#151a18", outline="#3b4039",
        )
        canvas.create_rectangle(
            205 * sx, 105 * sy, 695 * sx, 445 * sy,
            fill="#090d0d", outline="#927d5b", width=2,
        )
        canvas.create_line(220 * sx, 188 * sy, 680 * sx, 188 * sy, fill="#514936")
        canvas.create_text(
            WIDTH / 2 * sx, 138 * sy, text=self.tr("ALFRED SHOT S1"),
            fill="#e4c990", font=("TkFixedFont", 27, "bold"),
        )
        canvas.create_text(
            WIDTH / 2 * sx, 174 * sy, text=self.tr("NIGHT SHIFT"),
            fill="#ab8960", font=("TkFixedFont", 11, "bold"),
        )
        canvas.create_text(
            WIDTH / 2 * sx, 462 * sy, text=self.tr("M: MENU") + "    ·    " + self.tr("ESC: QUIT"),
            fill="#837b69", font=("TkFixedFont", 9),
        )
        canvas.create_text(
            WIDTH / 2 * sx, 481 * sy,
            text=f"{self.tr('DEVELOPED BY')}: {DEVELOPER}",
            fill="#a5a08c", font=("TkFixedFont", 9, "bold"),
        )
        if self.menu_page == "main":
            labels = []
            if self.has_started:
                labels.append(("CONTINUE", "continue"))
                labels.append(("NEW GAME", "new_game"))
            else:
                labels.append(("PLAY", "play"))
            labels.extend((("LANGUAGE", "language"), ("GRAPHICS", "graphics"), ("EXIT", "exit")))
            y = 216 if len(labels) == 4 else 197
            for label, action in labels:
                self.draw_menu_button(WIDTH / 2, y, label, action)
                y += 52
        elif self.menu_page == "language":
            canvas.create_text(
                WIDTH / 2 * sx, 210 * sy, text=self.tr("SELECT LANGUAGE"),
                fill=TEXT, font=("TkFixedFont", 13, "bold"),
            )
            self.draw_menu_button(WIDTH / 2, 245, "ENGLISH", "english", selected=self.language == "en")
            self.draw_menu_button(WIDTH / 2, 297, "ESTONIAN", "estonian", selected=self.language == "et")
            self.draw_menu_button(WIDTH / 2, 365, "BACK", "back", width=180)
        else:
            canvas.create_text(
                WIDTH / 2 * sx, 210 * sy, text=self.tr("GRAPHICS QUALITY"),
                fill=TEXT, font=("TkFixedFont", 13, "bold"),
            )
            canvas.create_text(
                WIDTH / 2 * sx, 232 * sy,
                text=self.tr("CURRENTLY SELECTED") + ": " + self.tr(self.graphics_quality.upper()),
                fill=MINT, font=("TkFixedFont", 9, "bold"),
            )
            self.draw_menu_button(WIDTH / 2, 250, "LOW", "low", selected=self.graphics_quality == "low")
            self.draw_menu_button(WIDTH / 2, 302, "HIGH", "high", selected=self.graphics_quality == "high")
            description = "LOW DETAIL / LIGHTER ON YOUR COMPUTER" if self.graphics_quality == "low" else "FULL DETAIL / MORE PARTICLES"
            canvas.create_text(
                WIDTH / 2 * sx, 356 * sy, text=self.tr(description),
                fill="#aaa596", font=("TkFixedFont", 8),
            )
            self.draw_menu_button(WIDTH / 2, 382, "BACK", "back", width=180)
    def draw(self, _event=None):
        canvas = self.canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 1)
        height = max(canvas.winfo_height(), 1)
        if self.screen != "game":
            self.draw_menu(width, height)
            return
        sx, sy = width / WIDTH, height / HEIGHT
        rival_parts = False

        def xy(x, y):
            return x * sx, y * sy

        def rect(x1, y1, x2, y2, fill, outline="", tags=()):
            if rival_parts:
                tags = (*tags, "rival_character")
            canvas.create_rectangle(
                *xy(x1, y1), *xy(x2, y2),
                fill=fill, outline=outline, tags=tags
            )

        def oval(x1, y1, x2, y2, fill, outline="", tags=()):
            if rival_parts:
                tags = (*tags, "rival_character")
            canvas.create_oval(
                *xy(x1, y1), *xy(x2, y2),
                fill=fill, outline=outline, tags=tags
            )

        def line(points, fill, thickness=1, tags=()):
            if rival_parts:
                tags = (*tags, "rival_character")
            scaled = [coordinate for pair in points for coordinate in xy(*pair)]
            canvas.create_line(*scaled, fill=fill, width=max(1, thickness * sx), tags=tags)

        def text(x, y, value, color=TEXT, size=12, bold=False, anchor="center", tags=()):
            if rival_parts:
                tags = (*tags, "rival_character")
            canvas.create_text(
                *xy(x, y),
                text=value,
                fill=color,
                font=("TkFixedFont", max(8, round(size * min(sx, sy))), "bold" if bold else "normal"),
                anchor=anchor,
                tags=tags,
            )

        def polygon(points, fill, outline="", tags=()):
            if rival_parts:
                tags = (*tags, "rival_character")
            scaled = [coordinate for pair in points for coordinate in xy(*pair)]
            canvas.create_polygon(scaled, fill=fill, outline=outline, tags=tags)

        # A compact 1980s CRT-inspired room, drawn entirely with Canvas shapes.
        rect(0, 0, WIDTH, HEIGHT, "#101311")
        low_detail = self.graphics_quality == "low"
        if not low_detail:
            for y in range(0, 370, 3):
                shade = max(15, 27 - y // 30)
                color = f"#{shade:02x}{shade + 3:02x}{shade + 2:02x}"
                line(((0, y), (WIDTH, y)), color)
        rect(15, 84, WIDTH - 15, 376, "#151a18", "#3b4039")
        for x in range(24, WIDTH, 112 if low_detail else 56):
            line(((x, 92), (x, 375)), "#222925")
        for y in (111, 190, 269, 348):
            line(((16, y), (WIDTH - 16, y)), "#202622")
        polygon(((0, 360), (WIDTH, 360), (WIDTH, HEIGHT), (0, HEIGHT)), "#171916")
        floor_step = 120 if low_detail else 34
        for y in range(382, HEIGHT, floor_step):
            line(((0, y), (WIDTH, y)), "#24251f")
        for x in range(-500, 1400, 220 if low_detail else 110):
            line(((450, 365), (x, HEIGHT)), "#20221e")
        grain = random.Random(1984)
        for _ in range(0 if low_detail else 34):
            x, y = grain.randint(20, WIDTH - 20), grain.randint(90, 365)
            shade = grain.choice(("#20231f", "#24231d", "#191f1d"))
            rect(x, y, x + 2, y + 2, shade)

        # Cool work lights and a warm central lamp give the room distinct light zones.
        for x, radius, color in ((259, 64, "#203033"), (450, 40, "#363023"),
                                 (641, 64, "#203033")):
            polygon(((x - radius, 118), (x + radius, 118),
                     (x + radius * 0.48, 355), (x - radius * 0.48, 355)),
                    color)
        polygon(((16, 360), (370, 360), (318, 376), (16, 376)), "#18272a")
        polygon(((530, 360), (884, 360), (884, 376), (582, 376)), "#18272a")
        polygon(((355, 360), (545, 360), (584, 376), (316, 376)), "#30291f")

        rect(36, 159, 178, 278, "#191c19", "#574a39")
        rect(43, 166, 171, 271, "#24221c", "#302c24")
        rect(48, 171, 54, 227, "#39413a")
        rect(48, 171, 51, 227, "#d39b51")
        text(107, 191, "LAST", "#c5a16b", 12, True)
        text(107, 211, "ROUND", "#c5a16b", 12, True)
        line(((58, 232), (156, 232)), "#6a4936", 2)
        rect(50, 239, 164, 260, "#34231d", "#76503b")
        text(107, 250, "NO EXIT", "#d86c50", 9, True)
        for x, lamp_color, halo_color in (
            (259, "#75b5b3", "#294447"),
            (450, "#efb764", "#51402a"),
            (641, "#75b5b3", "#294447"),
        ):
            line(((x, 84), (x, 102)), "#8e927e", 2)
            rect(x - 24, 99, x + 24, 106, "#303a3a", "#9a835d")
            polygon(((x - 39, 106), (x + 39, 106),
                     (x + 29, 119), (x - 29, 119)),
                    "#343d39", "#a58b5e")
            oval(x - 18, 111, x + 18, 123, halo_color, "#bca274")
            oval(x - 10, 113, x + 10, 119, lamp_color, "#f5dfa4")
            line(((x - 5, 116), (x + 5, 116)), "#fff4d2", 1)

        # Wall-mounted clock and a red service alarm break up the bare wall.
        rect(544, 139, 597, 171, "#202422", "#796c54")
        rect(548, 143, 593, 167, "#171c1b", "#423f34")
        oval(551, 145, 570, 164, "#b9ad8a", "#66583d")
        oval(556, 150, 565, 159, "#262a27", "#806b48")
        line(((560, 154), (560, 149)), "#e7d6ae", 1)
        line(((560, 154), (564, 156)), "#e7d6ae", 1)
        text(581, 155, "SERVICE", "#9eac9d", 5, True)
        rect(604, 145, 616, 171, "#292522", "#8d795c")
        oval(606, 145, 614, 155, "#9d3f37", "#d67e55")
        rect(608, 159, 612, 167, "#dca650", "#e7c982")

        line(((178, 173), (206, 173), (218, 183)), "#5e5542", 2)
        line(((694, 164), (724, 177), (746, 177)), "#514a3c", 2)

        # Estonia's blue-black-white flag hangs crooked on the wall.
        line(((274, 124), (274, 171)), "#9a835d", 3)
        polygon(((277, 128), (333, 133), (333, 168), (277, 164)),
                "#24231f", "#9d845b")
        polygon(((279, 130), (331, 135), (331, 146), (279, 142)), "#4891c7")
        polygon(((279, 142), (331, 146), (331, 157), (279, 153)), "#252a2b")
        polygon(((279, 153), (331, 157), (331, 167), (279, 164)), "#e6e1d4")
        oval(270, 120, 278, 128, "#bca274", "#42372a")

        # A moonlit window, Linux penguin sign, monitors, and old server racks.
        rect(714, 161, 858, 285, "#111820", "#927d5b")
        rect(721, 168, 851, 278, "#152333", "#4d5b61")
        oval(766, 181, 813, 228, "#b8b59b")
        oval(781, 174, 820, 215, "#152333")
        for x, y, radius in ((739, 187, 2), (830, 194, 2), (744, 222, 1),
                             (835, 177, 1), (812, 239, 1), (730, 206, 1)):
            oval(x - radius, y - radius, x + radius, y + radius, "#d5d3b6")
        polygon(((721, 250), (744, 234), (759, 245), (779, 226),
                 (799, 246), (818, 231), (851, 250), (851, 278), (721, 278)),
                "#202b32")
        polygon(((721, 264), (751, 249), (770, 262), (796, 245),
                 (823, 260), (851, 247), (851, 278), (721, 278)),
                "#293338")
        line(((786, 168), (786, 278)), "#796b54", 3)
        line(((721, 236), (851, 236)), "#796b54", 3)

        rect(180, 122, 257, 202, "#34352e", "#c2a371")
        rect(185, 127, 252, 197, "#11191b", "#6f7a70")
        rect(189, 131, 248, 193, "#202a2a", "#3f5048")
        text(218, 137, "GNU / LINUX", "#d7c59f", 7, True)
        oval(204, 143, 232, 169, "#121719", "#c5aa78")
        oval(210, 146, 226, 165, "#e5ddc8")
        polygon(((204, 153), (232, 153), (237, 177), (230, 187),
                 (206, 187), (199, 177)), "#101619", "#c5aa78")
        oval(207, 156, 229, 182, "#e7dfca")
        oval(212, 149, 215, 153, "#111516")
        oval(222, 149, 225, 153, "#111516")
        polygon(((215, 154), (223, 154), (219, 160)), "#e2a53e", "#bd8132")
        polygon(((199, 184), (211, 183), (207, 189), (195, 188)), "#dfa13a")
        polygon(((224, 183), (236, 184), (239, 188), (227, 189)), "#dfa13a")
        text(218, 192, "DEBIAN", "#b9c9b5", 6, True)

        for x, label, tint in ((187, "CAM 01", "#91bca5"), (590, "SYSTEM", "#c39a63")):
            rect(x - 4, 201, x + 99, 272, "#121615", "#77684f")
            rect(x, 205, x + 95, 262, "#101c1b", "#423f34")
            rect(x + 4, 209, x + 91, 258, "#1c322f", "#594d39")
            text(x + 10, 214, label, tint, 7, True, "nw")
            if label == "CAM 01":
                rect(x + 7, 225, x + 88, 255, "#13201d", "#73816a")
                # The surveillance feed shows two server racks with blinking status LEDs.
                for rack_x in (x + 12, x + 51):
                    rect(rack_x, 229, rack_x + 32, 251, "#202724", "#9a8b68")
                    rect(rack_x + 2, 231, rack_x + 30, 249, "#111715", "#4d5c50")
                    for row in range(3):
                        rack_y = 233 + row * 5
                        rect(rack_x + 4, rack_y, rack_x + 21, rack_y + 3,
                             "#293531", "#536355")
                        rect(rack_x + 6, rack_y + 1, rack_x + 19, rack_y + 2,
                             "#6e7664")
                        led = row + (0 if rack_x == x + 12 else 3)
                        oval(rack_x + 24, rack_y, rack_x + 27, rack_y + 3,
                             "#75d79a", "#b8e3ab",
                             tags=(f"camera_led_{led}", "camera_led"))
                line(((x + 9, 253), (x + 86, 253)), "#81906a", 1)
                oval(x + 77, 215, x + 80, 218, "#d34b42")
                text(x + 84, 216, "REC", "#d0bc83", 4, True, "e")
            elif not low_detail:
                line(((x + 9, 222), (x + 84, 222)), "#526458", 1)
                for bar_index, bar_height in enumerate((13, 23, 18, 30, 20, 34, 24)):
                    bar_x = x + 12 + bar_index * 10
                    rect(bar_x, 251 - bar_height, bar_x + 5, 251, "#577c68" if bar_index % 2 else "#9a7951")
            line(((x + 48, 272), (x + 48, 281)), "#76674d", 3)
            polygon(((x + 29, 282), (x + 67, 282), (x + 76, 286),
                     (x + 21, 286)), "#34322b", "#77684f")

        for x in (186, 596):
            rect(x, 291, x + 91, 356, "#151917", "#897552")
            rect(x + 5, 296, x + 86, 351, "#242824", "#403e34")
            for unit in range(2 if low_detail else 3):
                top = 300 + unit * 17
                rect(x + 10, top, x + 81, top + 13, "#171b1a", "#60533e")
                if not low_detail:
                    line(((x + 16, top + 4), (x + 56, top + 4)), "#665d48", 1)
                    line(((x + 16, top + 8), (x + 46, top + 8)), "#3c4c46", 1)
                    for light_index, light_color in enumerate(("#a34e3e", "#8ba875", "#c49b58")):
                        oval(x + 66 + light_index * 5, top + 4,
                             x + 69 + light_index * 5, top + 7, light_color)
            line(((x + 3, 354), (x + 88, 354)), "#b3996b", 2)

        # A small old vodka bottle sits on top of the right-hand server rack.
        polygon(((652, 290), (650, 282), (653, 278), (654, 266),
                 (660, 261), (666, 266), (667, 278), (671, 283),
                 (669, 290)), "#38504a", "#b39a70")
        rect(656, 254, 664, 265, "#b08a50", "#5a4932")
        line(((658, 256), (658, 263)), "#e0bf79", 1)
        polygon(((653, 276), (668, 276), (669, 288), (652, 288)),
                "#d8d0b8", "#8a7049")
        text(660, 282, "VODKA", "#773b36", 4, True)
        line(((654, 269), (665, 269)), "#a8b8a2", 1)

        # A hooded warden with a lit respirator and layered, armored coat.
        rival_parts = True
        polygon(((357, 188), (365, 151), (389, 128), (402, 105),
                 (421, 121), (450, 110), (478, 122), (500, 107),
                 (513, 135), (539, 150), (543, 193), (522, 253), (379, 253)),
                "#171719", "#80684d")
        polygon(((376, 180), (393, 144), (419, 130), (483, 130),
                 (509, 148), (526, 182), (511, 235), (489, 251),
                 (411, 251), (389, 234)),
                "#403d39", "#b09366")
        polygon(((374, 179), (392, 143), (420, 128), (451, 122),
                 (480, 130), (508, 148), (526, 182), (512, 169),
                 (486, 147), (451, 140), (416, 147), (390, 168)),
                "#242727", "#776448")
        line(((390, 151), (410, 140), (433, 137)), "#a48358", 2)
        line(((468, 137), (491, 143), (509, 159)), "#a48358", 2)
        polygon(((397, 174), (419, 154), (481, 154), (503, 175),
                 (497, 218), (474, 239), (426, 239), (403, 218)),
                "#24292a", "#c2a371")
        polygon(((402, 177), (429, 166), (439, 176), (426, 188), (405, 188)),
                "#201919", "#8d6048")
        polygon(((461, 176), (472, 166), (499, 177), (496, 189), (475, 188)),
                "#201919", "#8d6048")
        for x in (409, 471):
            oval(x - 5, 170, x + 23, 191, "#6d3828", "#bd7950")
            oval(x, 174, x + 18, 187, "#171b1b", "#d09b64")
            oval(x + 6, 176, x + 13, 185, "#ff8c56")
            oval(x + 8, 177, x + 11, 184, "#ffe4a3")
        polygon(((437, 183), (450, 177), (463, 184), (458, 205),
                 (450, 211), (442, 205)), "#4b4137", "#c3a16e")
        oval(442, 188, 458, 204, "#191c1b", "#8e7958")
        oval(446, 191, 454, 199, "#d78b50", "#e7bb78")
        oval(448, 193, 452, 197, "#171b1a")
        line(((390, 141), (407, 132), (419, 126)), "#83745d", 2)
        line(((487, 129), (504, 137), (517, 151)), "#82745c", 2)
        for x, y in ((386, 154), (395, 146), (508, 151), (515, 163)):
            line(((x, y), (x + 5, y + 4)), "#a28c68", 1)
        line(((450, 168), (440, 194), (452, 205), (441, 217), (450, 238)),
             "#a89067", 2)
        line(((456, 184), (465, 195), (460, 202)), "#d0b98b", 1)
        line(((430, 215), (424, 226), (431, 233)), "#d0b98b", 1)
        polygon(((413, 207), (432, 211), (449, 208), (468, 212), (487, 205),
                 (480, 226), (450, 234), (420, 225)),
                "#171b1a", "#807052")
        for x in (423, 432, 441, 450, 459, 468, 477):
            line(((x, 213), (x, 222)), "#b19c71", 1)
        line(((427, 229), (450, 235), (474, 228)), "#6b5942", 2)
        for x, y in ((401, 164), (495, 165), (407, 222), (490, 223)):
            oval(x - 2, y - 2, x + 2, y + 2, "#c2a371")
        polygon(((392, 227), (508, 227), (558, 287), (582, 373),
                 (318, 373), (342, 287)), "#252a2b", "#8b7554")
        polygon(((393, 236), (450, 264), (422, 371), (331, 371),
                 (350, 292)), "#41403a", "#73644b")
        polygon(((507, 236), (450, 264), (478, 371), (569, 371),
                 (550, 292)), "#22292a", "#665b47")
        polygon(((392, 243), (410, 252), (373, 355), (350, 365),
                 (362, 296)), "#505044", "#77705b")
        polygon(((509, 243), (490, 252), (527, 355), (550, 365),
                 (538, 296)), "#1c2221", "#625d4c")
        polygon(((402, 231), (450, 265), (498, 231), (488, 259),
                 (450, 279), (412, 259)), "#684234", "#c49a61")
        polygon(((389, 242), (413, 251), (395, 273), (369, 266)),
                "#343b39", "#b18d5c")
        polygon(((511, 242), (487, 251), (505, 273), (531, 266)),
                "#202727", "#b18d5c")
        for x, y in ((392, 254), (405, 259), (508, 254), (495, 259)):
            oval(x - 3, y - 3, x + 3, y + 3, "#c8a56e", "#292722")
        polygon(((424, 267), (450, 278), (476, 267), (491, 358),
                 (450, 369), (409, 358)), "#303536", "#8c7552")
        line(((450, 279), (450, 352)), "#ae8a5a", 2)
        line(((420, 288), (398, 348)), "#9b7850", 2)
        line(((480, 288), (502, 348)), "#151a18", 3)
        polygon(((431, 301), (450, 289), (469, 301), (464, 323),
                 (450, 331), (436, 323)), "#202321", "#c1a06b")
        polygon(((440, 306), (450, 297), (460, 306), (458, 318),
                 (450, 323), (442, 318)), "#8c4a39", "#e0b876")
        line(((450, 300), (450, 317)), "#f0d39a", 2)
        line(((445, 308), (455, 308)), "#f0d39a", 2)
        for y in range(291, 352, 12):
            line(((356, y), (362, y + 3)), "#92785a", 1)
            line(((544, y), (538, y + 3)), "#92785a", 1)
        line(((375, 287), (355, 355)), "#656757", 3)
        line(((525, 287), (545, 355)), "#202624", 3)
        for x, y in ((394, 275), (405, 279), (495, 279), (506, 275),
                     (382, 315), (518, 315), (371, 342), (529, 342)):
            oval(x - 2, y - 2, x + 2, y + 2, "#c0a475")
        line(((364, 288), (374, 299), (369, 311)), "#8e7757", 2)
        line(((535, 288), (526, 301), (532, 315)), "#8e7757", 2)
        oval(388, 232, 510, 253, "#171b19")
        rival_parts = False

        sway = math.sin(time.monotonic() * 1.8) * 2.2
        if self.state.rival_hp == 0 and self.death_animation is None:
            canvas.delete("rival_character")
        elif self.death_animation is None:
            canvas.move("rival_character", 0, sway * sy)
        else:
            elapsed = time.monotonic() - self.death_animation["started"]
            progress = min(1.0, elapsed / 1.55)
            canvas.scale("rival_character", 450 * sx, 250 * sy, 1.0 - 0.62 * progress, 1.0 - 0.62 * progress)
            canvas.move("rival_character", progress * 360 * sx, (-progress * 300 + sway) * sy)
        if self.hit_reaction is not None and self.death_animation is None:
            hit_x, hit_y = self.hit_flight_offset(
                min(1.0, (time.monotonic() - self.hit_reaction["started"]) / 1.1)
            )
            canvas.move("rival_character", hit_x * sx, hit_y * sy)
        self.rival_sway_y = sway * sy if self.death_animation is None else 0.0

        # A heavy plank tabletop, reinforced with worn iron edging.
        polygon(((145, 365), (755, 365), (828, 474), (72, 474)), "#292720", "#a08051")
        polygon(((151, 369), (749, 369), (817, 467), (83, 467)), "#453729")
        polygon(((151, 369), (749, 369), (817, 389), (83, 389)), "#52402d")
        polygon(((83, 390), (817, 390), (828, 408), (72, 408)), "#493a29")
        polygon(((72, 409), (828, 409), (828, 428), (72, 428)), "#403326")
        polygon(((72, 429), (828, 429), (828, 448), (72, 448)), "#4b3b29")
        polygon(((72, 449), (828, 449), (817, 467), (83, 467)), "#3c3024")
        line(((145, 365), (755, 365)), "#d8bc82", 3)
        if low_detail:
            for y in (399, 434):
                line(((83, y), (817, y)), "#725035")
        else:
            for top_x in (294, 450, 606):
                bottom_x = 450 + (top_x - 450) * 1.24
                line(((top_x, 369), (bottom_x, 467)), "#2b2119", 2)
                line(((top_x + 2, 370), (bottom_x + 2, 465)), "#735338", 1)
            for index, y in enumerate((383, 399, 416, 434, 451)):
                inset = (y - 365) * 0.64
                line(((145 - inset, y), (755 + inset, y)), "#725035" if index % 2 else "#30241a")
            for x, y, length in (
                (226, 390, 52), (691, 391, 40), (302, 446, 67),
                (596, 444, 54), (510, 379, 38), (181, 422, 29),
                (344, 403, 34), (464, 454, 45), (747, 430, 31),
                (127, 443, 39), (555, 389, 28), (390, 434, 31),
            ):
                line(((x, y), (x + length, y - 2)), "#8a6743", 1)
                line(((x + 3, y + 2), (x + length - 2, y)), "#35271b", 1)
            for x, y in ((169, 380), (735, 380), (98, 458), (802, 458),
                         (286, 378), (614, 378), (110, 462), (790, 462)):
                oval(x - 4, y - 4, x + 4, y + 4, "#211f1a", "#a68a60")
                oval(x - 1, y - 1, x + 1, y + 1, "#d0b17a")
            for x, y, radius in ((267, 424, 3), (558, 414, 2), (717, 445, 3), (190, 451, 2)):
                oval(x - radius, y - radius, x + radius, y + radius, "#5a3027")
            for x, y in ((241, 411), (678, 424), (524, 455)):
                line(((x, y), (x + 18, y - 3), (x + 27, y - 2)), "#795638")
            line(((102, 393), (145, 396), (165, 404)), "#2d2119", 2)
            line(((103, 395), (144, 398), (162, 405)), "#806044", 1)
            line(((734, 443), (776, 439), (795, 435)), "#30231a", 2)
            for x, y in ((212, 404), (248, 439), (327, 386), (573, 426),
                         (648, 455), (704, 400), (159, 438), (761, 417)):
                oval(x - 3, y - 2, x + 4, y + 2, "#30231d")
                oval(x - 1, y - 1, x + 2, y + 1, "#79583a")
            polygon(((90, 384), (176, 387), (181, 390), (94, 388)),
                    "#191d1c", "#9d845b")
            polygon(((724, 387), (806, 383), (802, 388), (720, 391)),
                    "#191d1c", "#9d845b")
            line(((92, 385), (174, 388)), "#d0b77f", 1)
            line(((724, 388), (804, 384)), "#d0b77f", 1)
            polygon(((280, 417), (292, 414), (295, 418), (283, 422)),
                    "#282723", "#a68a60")
            polygon(((642, 439), (654, 436), (657, 440), (645, 444)),
                    "#282723", "#a68a60")
            for x, y in ((285, 418), (647, 440)):
                oval(x - 1, y - 1, x + 1, y + 1, "#d0b17a")
        polygon(((76, 469), (824, 469), (828, 478), (72, 478)), "#211f1c", "#8b704c")
        line(((80, 471), (820, 471)), "#b39463", 1)
        for x in range(100, 821, 144 if low_detail else 48):
            oval(x - 2, 471, x + 2, 475, "#c2a371")

        self.draw_table_laptop(rect, oval, polygon, line, text, low_detail)

        # A field notebook and a chipped enamel mug make the table feel used.
        polygon(((550, 418), (653, 414), (674, 441), (565, 448)),
                "#201f1b", "#a68a60")
        polygon(((554, 416), (651, 412), (668, 437), (562, 444)),
                "#c2b393", "#40372a")
        line(((562, 421), (649, 417), (664, 434)), "#8e7958", 1)
        line(((568, 426), (614, 424)), "#726b5a", 1)
        line(((570, 431), (625, 429)), "#726b5a", 1)
        text(643, 433, "FIELD LOG", "#594d39", 5, True, "e")
        line(((669, 414), (695, 438)), "#c6a567", 3)
        line(((669, 414), (666, 410)), "#d7d0bc", 2)
        polygon(((726, 403), (757, 403), (754, 429), (730, 429)),
                "#1c2524", "#b39a70")
        oval(726, 399, 757, 408, "#b8ad91", "#d2bd8c")
        oval(730, 401, 753, 406, "#30291f", "#77654a")
        oval(752, 408, 765, 423, "", "#b39a70")
        oval(755, 411, 761, 420, "#493a29", "#493a29")
        line(((733, 428), (752, 428)), "#d0b77f", 1)
        if not low_detail:
            line(((737, 397), (734, 392)), "#b9b29f", 1)
            line(((745, 397), (747, 392)), "#b9b29f", 1)

        if self.animation is None:
            self.draw_table_weapon(polygon, line, oval)
        else:
            self.draw_weapon_animation(canvas, xy, sx, sy)

        polygon(((72, 474), (828, 474), (828, 501), (72, 501)), "#30231a", "#59422d")
        line(((78, 476), (822, 476)), "#775438", 2)
        rect(215, 501, 238, 557, "#29231d")
        rect(662, 501, 685, 557, "#29231d")

        if self.death_animation is not None:
            self.draw_death_effect(canvas, xy, sx, sy)
        # Heads-up display.
        rect(20, 18, WIDTH - 20, 69, "#080b0b", "#79715d")
        line(((27, 24), (WIDTH - 27, 24)), "#262b27")
        text(38, 42, self.tr("ALFRED SHOT S1"), "#e4c990", 19, True, "w")
        text(296, 44, self.tr("NIGHT SHIFT"), "#887759", 9, True, "w")
        text(WIDTH - 38, 44, f"{self.tr('ROUND')} {self.state.round_number:02d}", MINT, 11, True, "e")

        rect(781, 82, 875, 111, "#111715", "#8d795c", ("game_menu",))
        text(828, 97, self.tr("MENU"), TEXT, 10, True, tags=("game_menu",))
        canvas.tag_bind("game_menu", "<Button-1>", lambda _event: self.open_menu())
        if self.ammo_notice is not None:
            rect(574, 78, 770, 138, "#101817", "#d0b77f", ("ammo_notice",))
            line(((582, 86), (762, 86)), "#8d795c", 1)
            text(672, 101, f"{self.tr('LIVE ROUNDS')}: {self.ammo_notice['live']}",
                 "#ef8064", 10, True)
            text(672, 122, f"{self.tr('BLANK ROUNDS')}: {self.ammo_notice['blank']}",
                 "#78bdeb", 10, True)

        rect(195, 491, 705, 531, "#090c0c", "#85724e")
        text(WIDTH / 2, 505, self.tr(self.message).upper(), "#e4c990", 10, True)
        text(WIDTH / 2, 541, f"{self.tr('SHELLS LEFT')}: {self.state.remaining} / {CHAMBER_SIZE}", MUTED, 11, True)

        if self.state.game_over and self.death_animation is None:
            rect(270, 247, 630, 356, "#101313", "#b29a70")
            winner = self.tr("YOU WIN!") if self.state.player_hp else self.tr("YOU LOST")
            text(WIDTH / 2, 279, winner, TEXT, 21, True)
            text(WIDTH / 2, 313, self.tr("PRESS R OR CLICK TO RESTART"), MINT, 11, True)
            self.draw_button(353, 418, 547, 464, self.tr("RESTART"), "restart")
            self.draw_room_flash(canvas, xy, sx, sy)
            self.draw_ejected_casing(canvas, xy, sx, sy)
            return

        self.draw_button(229, 553, 431, 599, self.tr("A  AIM AT RIVAL"), "rival")
        self.draw_button(469, 553, 671, 599, self.tr("S  AIM AT SELF"), "self")
        if height >= 660:
            text(WIDTH / 2, HEIGHT - 3, self.tr("CLICK A TARGET  ·  ESC: QUIT"), "#74746b", 9)

        if time.monotonic() < self.shot_flash_until:
            rect(15, 84, WIDTH - 15, 376, "", "#ab5240")

        canvas.tag_bind("button_rival", "<Button-1>", lambda _event: self.shoot("rival"))
        canvas.tag_bind("button_self", "<Button-1>", lambda _event: self.shoot("self"))
        canvas.tag_bind("button_restart", "<Button-1>", lambda _event: self.restart_if_over())
        self.draw_room_flash(canvas, xy, sx, sy)
        self.draw_ejected_casing(canvas, xy, sx, sy)

    def draw_table_laptop(self, rect, oval, polygon, line, text, low_detail=False):
        # A reinforced ThinkPad-style shell with a readable status dashboard.
        polygon(((121, 431), (303, 431), (326, 452), (108, 452)),
                "#111615", "#a68a60")
        polygon(((126, 429), (300, 429), (319, 448), (116, 448)),
                "#252b29", "#77745f")
        polygon(((133, 432), (293, 432), (306, 445), (122, 445)),
                "#1b211f", "#4b5047")
        line(((128, 431), (300, 431), (317, 447)), "#c2a371", 1)
        if low_detail:
            for x in (139, 159, 179, 199, 219, 239):
                rect(x, 434, x + 12, 436, "#9d9279")
            for x in (144, 164, 184, 204, 224):
                rect(x, 438, x + 12, 440, "#77715f")
        else:
            for row in range(3):
                for col in range(10):
                    x = 136 + col * 12
                    y = 434 + row * 3
                    rect(x, y, x + 8, y + 1,
                         "#b0a182" if row == 0 else "#77715f")
        rect(256, 434, 283, 442, "#171b1a", "#71654e")
        line(((259, 436), (280, 436)), "#514a3d", 1)
        oval(200, 436, 210, 444, "#353531", "#a68a60")
        oval(203, 438, 207, 442, "#bd3037")
        line(((115, 448), (319, 448)), "#101312", 2)
        for x in (124, 315):
            oval(x - 2, 447, x + 2, 450, "#171b1a", "#c1a473")

        polygon(((126, 380), (300, 380), (305, 430), (128, 430)),
                "#111615", "#c0a472")
        rect(131, 383, 295, 426, "#080d10", "#66736c")
        rect(136, 388, 290, 422, "#10201e", "#30443c")
        rect(138, 388, 288, 396, "#651f28")
        rect(140, 390, 286, 394, "#b43238")
        oval(143, 390, 148, 394, "#ffe2a0")
        text(156, 392, self.tr("LINUX"), "#f4ead3", 7, True, "w")
        text(284, 392, "T480", "#f0d7b1", 6, True, "e")
        rect(139, 397, 288, 421, "#132320")
        line(((181, 398), (181, 420)), "#3a5146", 1)
        line(((138, 409), (289, 409)), "#3a5146", 1)
        text(147, 403, self.tr("YOU"), "#9bd5c0", 7, True, "w")
        text(147, 415, self.tr("RIVAL"), "#eb907a", 7, True, "w")
        for index in range(HEALTH):
            x = 188 + index * 14
            rect(x, 402, x + 10, 407, MINT if index < self.state.player_hp else "#343b37")
            rect(x, 414, x + 10, 419, RED if index < self.state.rival_hp else "#343331")
            if index < self.state.player_hp:
                line(((x + 2, 403), (x + 7, 403)), "#c2eadb", 1)
            if index < self.state.rival_hp:
                line(((x + 2, 415), (x + 7, 415)), "#ffc1ad", 1)
        text(278, 405, f"{self.state.player_hp}/{HEALTH}", TEXT, 7, True)
        text(278, 417, f"{self.state.rival_hp}/{HEALTH}", TEXT, 7, True)
        text(286, 436, self.tr("THINKPAD"), "#d3bc8d", 6, True, "e")
        rect(136, 426, 155, 428, "#c2a371")
        rect(140, 426, 142, 428, "#b9383b")

    def draw_death_effect(self, canvas, xy, sx, sy):
        if self.death_animation is None:
            return
        elapsed = time.monotonic() - self.death_animation["started"]
        progress = min(1.0, elapsed / 1.55)
        seed = self.death_animation["seed"]
        center_x, center_y = 450, 286
        if elapsed < 0.32:
            burst = 1.0 - elapsed / 0.32
            points = []
            for index in range(16):
                angle = index * math.tau / 16
                radius = (15 if index % 2 == 0 else 8) * (0.45 + 0.55 * (1 - burst))
                points.extend((center_x + math.cos(angle) * radius,
                               center_y + math.sin(angle) * radius))
            canvas.create_polygon(
                *[coordinate for point in zip(points[::2], points[1::2]) for coordinate in xy(*point)],
                fill="#bd302d",
                outline="#ed5542",
                width=max(1, round(2 * sx)),
            )

        particle_count = 14 if self.graphics_quality == "low" else 38
        for index in range(particle_count):
            angle = index * math.tau / particle_count + (seed % 23) * 0.09
            speed = 65 + (index * 37 % 150)
            distance = 5 + speed * progress
            x = center_x + math.cos(angle) * distance + progress * 105
            y = center_y + math.sin(angle) * distance - progress * 55 + progress * progress * 75
            radius = max(2.2, (7 - progress * 3.5) * (0.7 + (index % 4) * 0.16))
            color = ("#ef493b", "#c72e2c", "#982329", "#ff7351")[index % 4]
            canvas.create_rectangle(
                *xy(x - radius, y - radius),
                *xy(x + radius, y + radius),
                fill=color,
                outline="",
            )

    def draw_button(self, x1, y1, x2, y2, label, action):
        active = self.state.turn == "player" and not self.state.game_over and self.animation is None
        if action == "restart":
            fill, border = "#203b34", MINT
        elif not active:
            fill, border = "#222523", "#42433d"
        elif action == "rival":
            fill, border = "#482520", RED
        else:
            fill, border = "#1d332e", MINT
        self.canvas.create_rectangle(
            *self.scaled_box(x1, y1, x2, y2),
            fill=fill,
            outline=border,
            width=2,
            tags=(f"button_{action}",),
        )
        self.canvas.create_text(
            *self.scaled_point((x1 + x2) / 2, (y1 + y2) / 2),
            text=label,
            fill=TEXT,
            font=("TkFixedFont", 11, "bold"),
            tags=(f"button_{action}",),
        )

    def scaled_point(self, x, y):
        return (
            x * self.canvas.winfo_width() / WIDTH,
            y * self.canvas.winfo_height() / HEIGHT,
        )

    def scaled_box(self, x1, y1, x2, y2):
        return (*self.scaled_point(x1, y1), *self.scaled_point(x2, y2))

    def shoot(self, target):
        if self.screen != "game" or self.state.turn != "player" or self.state.game_over or self.animation is not None:
            return
        self.begin_shot("player", target)

    def begin_shot(self, shooter, target):
        if self.animation is not None or self.state.turn != shooter or self.state.game_over:
            return
        self.animation = {
            "shooter": shooter,
            "target": target,
            "started": time.monotonic(),
        }
        if shooter == "rival":
            self.message = (
                "The rival grabs the gun and aims at itself..."
                if target == "rival"
                else "The rival grabs the gun and aims at you..."
            )
        else:
            self.message = "You grab the gun and take aim..."
        self.draw()
        frame_delay = LOW_FRAME_DELAY if self.graphics_quality == "low" else 50
        self.root.after(frame_delay, self.animate_shot)

    def animate_scene(self):
        if self.room_flash is not None and self.room_flash_stage() is None:
            self.room_flash = None
            self.room_flash_after = None
        self.camera_led_tick += 1
        if self.screen == "game":
            for led in range(6):
                is_on = (self.camera_led_tick + led * 3) % (8 + led % 3 * 4) < 3
                self.canvas.itemconfigure(
                    f"camera_led_{led}",
                    fill=("#75d79a" if led % 2 == 0 else "#e2ad51") if is_on else "#28322e",
                    outline="#b8e3ab" if is_on else "#465148",
                )
        if self.death_animation is not None:
            elapsed = time.monotonic() - self.death_animation["started"]
            if elapsed >= 1.55:
                self.death_animation = None
                self.message = "The rival is down. You win!"
                self.draw()
                self.root.after(250, self.animate_scene)
                return
            self.draw()
            self.root.after(130 if self.graphics_quality == "low" else 80, self.animate_scene)
            return

        if self.hit_reaction is not None:
            elapsed = time.monotonic() - self.hit_reaction["started"]
            if elapsed >= 1.1:
                self.hit_reaction = None
                self.draw()
                self.schedule_next_turn()
                self.root.after(250, self.animate_scene)
                return
            self.draw()
            frame_delay = 120 if self.graphics_quality == "low" else 45
            self.root.after(frame_delay, self.animate_scene)
            return

        sway_y = math.sin(time.monotonic() * 1.8) * 2.2
        target_sway_y = sway_y * self.canvas.winfo_height() / HEIGHT
        if self.state.rival_hp > 0:
            self.canvas.move("rival_character", 0, target_sway_y - self.rival_sway_y)
            self.rival_sway_y = target_sway_y
        self.root.after(120 if self.graphics_quality == "low" else 60, self.animate_scene)

    @staticmethod
    def hit_flight_offset(progress):
        flight = math.sin(math.pi * max(0.0, min(1.0, progress)))
        return 455 * flight, -345 * flight

    def draw_table_weapon(self, polygon, line, oval):
        polygon(((326, 452), (359, 463), (415, 427), (403, 416)),
                "#30231b", "#876744")
        polygon(((333, 446), (360, 455), (402, 425), (393, 419)),
                "#765333", "#b28a58")
        polygon(((356, 450), (384, 456), (436, 419), (415, 407)),
                "#4b3828", "#9d7950")
        polygon(((393, 433), (424, 440), (461, 405), (441, 396)),
                "#252b2a", "#a48b64")
        polygon(((406, 425), (429, 432), (469, 391), (454, 385)),
                "#343b39", "#c0aa80")
        line(((421, 410), (466, 390)), "#d5bc8d", 2)
        line(((429, 416), (474, 395)), "#171c1b", 2)
        line(((427, 412), (466, 394)), "#718078", 1)
        line(((434, 418), (474, 399)), "#718078", 1)
        polygon(((452, 392), (468, 382), (501, 364), (510, 370),
                 (477, 404), (461, 412)), "#303735", "#b6a27c")
        line(((469, 388), (499, 369)), "#d3c09a", 3)
        line(((475, 395), (505, 375)), "#171b1a", 3)
        line(((473, 389), (499, 371)), "#77817a", 1)
        line(((479, 396), (503, 377)), "#77817a", 1)
        line(((498, 369), (506, 366), (511, 369), (507, 375)), "#171b1a", 2)
        polygon(((407, 431), (420, 435), (414, 445), (401, 441)), "#211d19", "#9b7952")
        line(((402, 438), (395, 447), (405, 450), (414, 442)), "#c0a475", 2)
        line(((348, 449), (373, 445)), "#c49a61", 2)
        line(((365, 454), (382, 450)), "#3c281c", 2)
        polygon(((377, 444), (388, 447), (403, 435), (396, 431)),
                "#262b29", "#aa8c5e")
        line(((382, 444), (394, 436)), "#d0b17a", 2)
        line(((367, 450), (378, 448)), "#b48851", 1)
        oval(423, 419, 433, 429, "#252a28", "#d0b17a")

    def draw_weapon_animation(self, canvas, xy, sx, sy):
        animation = self.animation
        if animation is None:
            return
        elapsed = time.monotonic() - animation["started"]
        shooter, target = animation["shooter"], animation["target"]
        reach = min(1.0, elapsed / 0.55)
        lift = max(0.0, min(1.0, (elapsed - 0.55) / 1.0))
        lift = lift * lift * (3 - 2 * lift)

        if shooter == "rival":
            shoulder = (526, 292)
            pickup = (437, 426)
            aim = (452, 231) if target == "rival" else (451, 369)
            angle = 0 if target == "rival" else math.pi
            sleeve, glove = "#454b43", "#a38d67"
        else:
            shoulder = (748, 594)
            pickup = (437, 426)
            aim = (478, 530) if target == "self" else (451, 372)
            angle = math.pi if target == "self" else 0
            sleeve, glove = "#353d39", "#9d8662"

        hand = (
            pickup[0] + (aim[0] - pickup[0]) * lift,
            pickup[1] + (aim[1] - pickup[1]) * lift,
        )
        wrist = (
            shoulder[0] + (hand[0] - shoulder[0]) * reach,
            shoulder[1] + (hand[1] - shoulder[1]) * reach,
        )
        elbow_start = (shoulder[0] + (pickup[0] - shoulder[0]) * 0.48,
                       shoulder[1] + (pickup[1] - shoulder[1]) * 0.40)
        elbow_aim = (hand[0] + (34 if shooter == "rival" else -28),
                     hand[1] + (24 if shooter == "rival" else 35))
        elbow = (
            elbow_start[0] + (elbow_aim[0] - elbow_start[0]) * reach,
            elbow_start[1] + (elbow_aim[1] - elbow_start[1]) * reach,
        )

        def scaled(*points):
            return [coordinate for point in points for coordinate in xy(*point)]

        thickness = max(11, 23 * sx)
        canvas.create_line(
            *scaled(shoulder, elbow, wrist),
            fill="#151a18", width=thickness + 5, capstyle=tk.ROUND, joinstyle=tk.ROUND,
        )
        canvas.create_line(
            *scaled(shoulder, elbow, wrist),
            fill=sleeve, width=thickness, capstyle=tk.ROUND, joinstyle=tk.ROUND,
        )
        ex, ey = xy(*elbow)
        canvas.create_oval(ex - thickness / 2, ey - thickness / 2,
                           ex + thickness / 2, ey + thickness / 2,
                           fill=sleeve, outline="#111615", width=max(1, round(2 * sx)))
        wx, wy = xy(*wrist)
        canvas.create_oval(wx - 10 * sx, wy - 9 * sy, wx + 10 * sx, wy + 9 * sy,
                           fill=glove, outline="#171b19", width=max(1, round(2 * sx)))

        if elapsed >= 0.40:
            self.draw_held_weapon(canvas, xy, hand, angle, sx, sy)
        duration = self.shot_animation_duration(animation)
        if duration - 0.28 <= elapsed <= duration - 0.06:
            self.draw_muzzle_flash(canvas, xy, hand, angle, elapsed, sx, sy)

    def draw_held_weapon(self, canvas, xy, center, angle, sx, sy):
        cosine, sine = math.cos(angle), math.sin(angle)

        def transform(point):
            x, y = point
            return xy(center[0] + x * cosine - y * sine,
                      center[1] + x * sine + y * cosine)

        body = [(-8, 8), (-8, -14), (-6, -25), (6, -25),
                (8, -14), (8, 8), (14, 19), (9, 24), (2, 12)]
        points = [coordinate for point in body for coordinate in transform(point)]
        canvas.create_polygon(points, fill="#202725", outline="#c1a473",
                              width=max(1, round(2 * sx)))
        for offset in (-3, 3):
            start = transform((offset, -23))
            end = transform((offset, -53))
            canvas.create_line(*start, *end, fill="#b9a17a", width=max(2, round(3 * sx)))
            canvas.create_line(*start, *end, fill="#303936", width=max(1, round(1 * sx)))
            inner_start = transform((offset, -27))
            inner_end = transform((offset, -49))
            canvas.create_line(*inner_start, *inner_end, fill="#717a72", width=max(1, round(1 * sx)))
        sight_a, sight_b = transform((-3, -48)), transform((3, -48))
        canvas.create_line(*sight_a, *sight_b, fill="#c7aa78", width=max(1, round(2 * sx)))
        rear_a, rear_b = transform((-5, -24)), transform((5, -24))
        canvas.create_line(*rear_a, *rear_b, fill="#d2bb8c", width=max(1, round(2 * sx)))
        receiver_points = [
            transform(point)
            for point in ((-5, -18), (5, -18), (5, -5), (3, 1), (-3, 1), (-5, -5))
        ]
        canvas.create_polygon(
            [coordinate for point in receiver_points for coordinate in point],
            fill="#39413e",
            outline="#c1a473",
            width=max(1, round(1 * sx)),
        )
        for bolt in ((-3, -14), (3, -9), (-2, -4)):
            bx, by = transform(bolt)
            canvas.create_oval(
                bx - 1.8 * sx, by - 1.8 * sy, bx + 1.8 * sx, by + 1.8 * sy,
                fill="#d1bb8c", outline="#171b1a",
            )
        trigger_points = [
            transform(point)
            for point in ((6, 8), (12, 14), (12, 19), (7, 20), (4, 15))
        ]
        canvas.create_line(
            [coordinate for point in trigger_points for coordinate in point],
            fill="#c1a473",
            width=max(1, round(2 * sx)),
            smooth=True,
        )
        trigger_a, trigger_b = transform((8, 10)), transform((6, 16))
        canvas.create_line(*trigger_a, *trigger_b, fill="#d3bc8d", width=max(1, round(2 * sx)))
        grip_a, grip_b = transform((6, 12)), transform((14, 23))
        canvas.create_line(*grip_a, *grip_b, fill="#765238", width=max(3, round(7 * sx)))
        grip_line_a, grip_line_b = transform((8, 15)), transform((12, 21))
        canvas.create_line(*grip_line_a, *grip_line_b, fill="#b18b5d", width=max(1, round(2 * sx)))
        canvas.create_oval(
            *xy(center[0] - 3, center[1] - 3),
            *xy(center[0] + 3, center[1] + 3),
            fill="#b9955d", outline="#161a18",
        )

    def draw_muzzle_flash(self, canvas, xy, center, angle, elapsed, sx, sy):
        muzzle_x = center[0] + math.sin(angle) * 44
        muzzle_y = center[1] - math.cos(angle) * 44
        pulse = 1.0 + ((elapsed * 80) % 1.0) * 0.25
        points = []
        for index in range(12):
            radius = (20 if index % 2 == 0 else 8) * pulse
            direction = index * math.pi / 6
            points.append((muzzle_x + math.cos(direction) * radius,
                           muzzle_y + math.sin(direction) * radius))
        scaled = [coordinate for point in points for coordinate in xy(*point)]
        canvas.create_polygon(scaled, fill="#edb65f", outline="#fff0b0", width=max(1, round(2 * sx)))
        canvas.create_oval(*xy(muzzle_x - 5, muzzle_y - 5),
                           *xy(muzzle_x + 5, muzzle_y + 5), fill="#fff2b1", outline="")

    def draw_ejected_casing(self, canvas, xy, sx, sy):
        if self.casing_animation is None:
            return
        elapsed = time.monotonic() - self.casing_animation["started"]
        if elapsed < 0:
            return
        progress = min(1.0, elapsed / 0.72)
        if progress >= 1.0:
            self.casing_animation = None
            return
        origin_x, origin_y = self.casing_animation["origin"]
        x = origin_x + 35 * progress
        y = origin_y - 52 * progress + 48 * progress * progress
        spin = math.sin(progress * math.tau * 2)
        width = max(2.0, 7.0 * abs(spin))
        height = 5.0
        canvas.create_oval(
            *xy(x - width / 2, y - height / 2),
            *xy(x + width / 2, y + height / 2),
            fill="#d9a64d", outline="#ffe39a", width=max(1, round(sx)),
            tags=("ejected_casing",),
        )
        canvas.create_line(
            *xy(x - width / 2 + 1, y - 1),
            *xy(x + width / 2 - 1, y - 1),
            fill="#fff0b0", width=max(1, round(sx)),
            tags=("ejected_casing",),
        )

    def draw_room_flash(self, canvas, xy, sx, sy):
        stage = self.room_flash_stage()
        if stage is None:
            return
        if stage == "dark":
            canvas.create_rectangle(
                *xy(0, 0), *xy(WIDTH, HEIGHT),
                fill="#020304", outline="", tags=("room_flash",),
            )
        elif stage == "bright":
            canvas.create_rectangle(
                *xy(0, 0), *xy(WIDTH, HEIGHT),
                fill="#fff2d5", outline="", tags=("room_flash",),
            )
            for lamp_x in (259, 450, 641):
                points = (
                    (lamp_x - 32, 116), (lamp_x + 32, 116),
                    (lamp_x + 70, 369), (lamp_x - 70, 369),
                )
                scaled_points = [coordinate for point in points for coordinate in xy(*point)]
                canvas.create_polygon(
                    *scaled_points, fill="#ffe5a0", stipple="gray50",
                    outline="", tags=("room_flash",),
                )
                canvas.create_oval(
                    *xy(lamp_x - 20, 107), *xy(lamp_x + 20, 129),
                    fill="#fffdf3", outline="#fffefa",
                    width=max(1, round(2 * sx)), tags=("room_flash",),
                )
        else:
            canvas.create_rectangle(
                *xy(0, 0), *xy(WIDTH, HEIGHT),
                fill="#090a0d", stipple="gray25", outline="", tags=("room_flash",),
            )
            for lamp_x in (259, 450, 641):
                canvas.create_oval(
                    *xy(lamp_x - 12, 111), *xy(lamp_x + 12, 125),
                    fill="#e69a54", outline="#ffe0a0", tags=("room_flash",),
                )

    def animate_shot(self):
        animation = self.animation
        if animation is None:
            return
        elapsed = time.monotonic() - animation["started"]
        shooter, target = animation["shooter"], animation["target"]
        duration = self.shot_animation_duration(animation)
        if elapsed < 0.55:
            self.message = "The rival reaches for the gun..." if shooter == "rival" else "You reach for the gun..."
        elif elapsed < duration - 0.28:
            if shooter == "rival":
                self.message = "The rival aims at itself..." if target == "rival" else "The rival aims at you..."
            else:
                self.message = "You aim at yourself..." if target == "self" else "You aim at the rival..."
        else:
            if shooter == "rival":
                self.message = "The rival fires at itself!" if target == "rival" else "The rival fires at you!"
            else:
                self.message = "You fire at yourself!" if target == "self" else "You fire at the rival!"
        if elapsed < duration:
            self.draw()
            frame_delay = LOW_FRAME_DELAY if self.graphics_quality == "low" else 50
            self.root.after(frame_delay, self.animate_shot)
            return

        rival_hp_before_shot = self.state.rival_hp
        player_hp_before_shot = self.state.player_hp
        round_was_live = (
            self.state.chamber_index < len(self.state.chamber)
            and self.state.chamber[self.state.chamber_index]
        )
        aim_position = {
            ("rival", "rival"): (452, 231),
            ("rival", "player"): (451, 369),
            ("player", "self"): (478, 530),
            ("player", "rival"): (451, 372),
        }[(shooter, target)]
        self.animation = None
        self.message = self.state.fire(shooter, target)
        if round_was_live:
            self.audio.play_shot()
        else:
            self.audio.play_click()
        self.shot_flash_until = time.monotonic() + 0.18
        if self.state.rival_hp == 0:
            self.hit_reaction = None
            self.death_animation = {
                "started": time.monotonic(),
                "seed": random.randrange(10000),
            }
            self.message = "The rival is hit!"
        elif self.state.rival_hp < rival_hp_before_shot:
            self.hit_reaction = {"started": time.monotonic()}
            self.message = "HIT! THE RIVAL FLIES BACK!"
        if round_was_live:
            self.casing_animation = {
                "started": time.monotonic() + 0.08,
                "origin": aim_position,
            }
        if (
            self.state.player_hp < player_hp_before_shot
            or self.state.rival_hp < rival_hp_before_shot
        ):
            self.room_flash = {"started": time.monotonic()}
            self.room_flash_after = self.root.after(
                80 if self.graphics_quality == "low" else 45,
                self.animate_room_flash,
            )
        self.draw()
        self.root.after(190, self.draw)
        if self.hit_reaction is None:
            self.schedule_next_turn()

    @staticmethod
    def shot_animation_duration(animation):
        return 2.2 if animation["shooter"] == "rival" else 2.0

    def room_flash_stage(self):
        if self.room_flash is None:
            return None
        elapsed = time.monotonic() - self.room_flash["started"]
        if elapsed < 0.16:
            return "dark"
        if elapsed < 0.28:
            return "bright"
        if elapsed < 0.42:
            return "dark"
        if elapsed < 0.54:
            return "bright"
        if elapsed < 0.74:
            return "dim"
        return None

    def clear_room_flash(self):
        if self.room_flash_after is not None:
            self.root.after_cancel(self.room_flash_after)
        self.room_flash = None
        self.room_flash_after = None

    def animate_room_flash(self):
        if self.room_flash_stage() is None:
            self.room_flash = None
            self.room_flash_after = None
            self.draw()
            return
        self.draw()
        self.room_flash_after = self.root.after(
            80 if self.graphics_quality == "low" else 45,
            self.animate_room_flash,
        )

    def schedule_next_turn(self):
        if self.state.game_over:
            return
        if self.state.turn == "rival":
            self.pending_action = self.root.after(550, self.rival_turn)
        elif self.state.turn == "reload":
            self.pending_action = self.root.after(700, self.reload_chamber)

    def rival_turn(self):
        self.pending_action = None
        if self.state.game_over or self.state.turn != "rival":
            return
        target = "player" if random.random() < 0.68 else "rival"
        self.begin_shot("rival", target)

    def reload_chamber(self):
        self.pending_action = None
        if self.state.turn != "reload" or self.state.game_over:
            return
        self.state.load_chamber()
        self.message = "New chamber loaded. Your turn."
        self.draw()


def self_test():
    audio = AudioEffects()
    try:
        for path, min_duration, max_amplitude in (
            (audio.shot_path, 0.25, 0.9),
            (audio.click_path, 0.03, 0.4),
        ):
            with wave.open(path, "rb") as sound_file:
                assert sound_file.getnchannels() == 1
                assert sound_file.getsampwidth() == 2
                assert sound_file.getframerate() == AudioEffects.SAMPLE_RATE
                assert sound_file.getnframes() > AudioEffects.SAMPLE_RATE * min_duration
                samples = array.array("h", sound_file.readframes(sound_file.getnframes()))
                if sys.byteorder != "little":
                    samples.byteswap()
                assert max(samples) > 500
                assert min(samples) < -500
                assert max(samples) <= round(max_amplitude * 32767)
                assert min(samples) >= -round(max_amplitude * 32767)
    finally:
        audio.close()

    state = DuelState()
    assert state.round_number == 1
    assert state.player_hp == state.rival_hp == HEALTH
    assert len(state.chamber) == CHAMBER_SIZE
    assert 2 <= sum(state.chamber) <= 4
    for _ in range(100):
        state.load_chamber()
        assert len(state.chamber) == CHAMBER_SIZE
        assert 2 <= sum(state.chamber) <= 4
        assert state.remaining == CHAMBER_SIZE

    state.chamber = [True, False]
    state.chamber_index = 0
    before_invalid_action = (
        state.player_hp,
        state.rival_hp,
        state.chamber_index,
        state.turn,
    )
    for shooter, target in (("other", "player"), ("player", "other"), ("rival", "self")):
        try:
            state.fire(shooter, target)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Invalid shot was accepted: {shooter!r}, {target!r}")
        assert (
            state.player_hp,
            state.rival_hp,
            state.chamber_index,
            state.turn,
        ) == before_invalid_action

    state.turn = "rival"
    assert state.fire("player", "rival") is None
    assert state.chamber_index == 0 and state.player_hp == state.rival_hp == HEALTH
    state.turn = "player"

    state.chamber = [False, True]
    state.chamber_index = 0
    assert state.fire("player", "self") == "Click. Empty shell — you keep your turn."
    assert state.remaining == 1
    assert state.turn == "player" and state.player_hp == HEALTH
    assert state.fire("player", "rival") == "Direct hit!"
    assert state.remaining == 0
    assert state.turn == "reload" and state.rival_hp == HEALTH - 1
    assert state.fire("player", "rival") is None

    state.load_chamber()
    assert state.turn == "player" and state.remaining == CHAMBER_SIZE
    state.chamber = [False, True, False]
    state.chamber_index = 0
    state.turn = "rival"
    assert state.fire("rival", "rival") == "Click. The rival keeps its turn."
    assert state.turn == "rival" and state.rival_hp == HEALTH - 1
    assert state.fire("rival", "rival") == "The rival hit itself."
    assert state.turn == "player" and state.rival_hp == HEALTH - 2

    state.chamber = [False, True]
    state.chamber_index = 0
    state.turn = "rival"
    assert state.fire("rival", "player") == "The rival fired a blank."
    assert state.turn == "player" and state.remaining == 1
    state.chamber = [True, False]
    state.chamber_index = 0
    state.turn = "rival"
    assert state.fire("rival", "player") == "The rival hit you!"
    assert state.player_hp == HEALTH - 1 and state.turn == "player"

    state.chamber = [True, False]
    state.chamber_index = 0
    state.turn = "player"
    assert state.fire("player", "self") == "You hit yourself."
    assert state.player_hp == HEALTH - 2 and state.turn == "rival"

    state.chamber = [False]
    state.chamber_index = 0
    state.turn = "player"
    assert state.fire("player", "self") == "Click. Empty shell — you keep your turn."
    assert state.remaining == 0 and state.turn == "reload"
    state.load_chamber()
    assert state.chamber_index == 0 and state.remaining == CHAMBER_SIZE

    state.chamber = [True]
    state.chamber_index = 0
    state.turn = "player"
    state.rival_hp = 1
    assert state.fire("player", "rival") == "Direct hit!"
    assert state.game_over and state.turn == "game_over" and state.rival_hp == 0
    assert state.fire("player", "self") is None

    state.chamber = [True]
    state.chamber_index = 0
    state.turn = "rival"
    state.player_hp = 1
    state.game_over = False
    assert state.fire("rival", "player") == "The rival hit you!"
    assert state.game_over and state.turn == "game_over" and state.player_hp == 0
    completed_round = state.round_number
    state.new_game()
    assert state.round_number == completed_round + 1
    assert state.player_hp == state.rival_hp == HEALTH
    assert not state.game_over and state.turn == "player"
    assert state.remaining == CHAMBER_SIZE
    assert AlfredShot.shot_animation_duration({"shooter": "rival"}) > AlfredShot.shot_animation_duration(
        {"shooter": "player"}
    )

    simulation_rng = random.Random(3317)
    for seed in range(100):
        random.seed(seed)
        simulated = DuelState()
        for _ in range(1000):
            if simulated.game_over:
                break
            if simulated.turn == "reload":
                simulated.load_chamber()
                continue
            shooter = simulated.turn
            target = simulation_rng.choice(
                ("self", "rival") if shooter == "player" else ("player", "rival")
            )
            simulated.fire(shooter, target)
            assert 0 <= simulated.player_hp <= HEALTH
            assert 0 <= simulated.rival_hp <= HEALTH
            assert 0 <= simulated.chamber_index <= len(simulated.chamber)
        assert simulated.game_over, f"Game simulation {seed} did not terminate"

    print("Shot/click sounds, invalid actions, duel rules, and 100 complete games: OK")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        window = tk.Tk()
        AlfredShot(window)
        window.mainloop()
