import tkinter as tk
from tkinter import font
import threading
import time
import os
import winsound  # Windows only
import pygame
pygame.mixer.init()
from api_questions import fetch_questions
from questions import questions as offline_questions

# =====================
#   COLOR THEME
# =====================
BG_COLOR      = "#0f172a"
CARD_COLOR    = "#1e293b"
PRIMARY       = "#0ea5e9"
PRIMARY_HOVER = "#0284c7"
SUCCESS       = "#22c55e"
DANGER        = "#f43f5e"
WARNING       = "#f97316"
TEXT_COLOR    = "#ffffff"
SUBTEXT       = "#94a3b8"

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯Quiz Game")
        self.root.geometry("700x500")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(True, True)
        # Make window responsive when maximized
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.root.state("zoomed")   # ✅ Opens maximized on Windows

        # Game state variables
        self.player_name   = tk.StringVar()
        self.category      = ""
        self.difficulty    = ""
        self.time_limit    = 10
        self.score         = 0
        self.q_index       = 0
        self.quiz_questions = []
        self.timer_running = False
        self.time_left     = 0
        self.user_answers = []

        self.show_home()

    # =====================
    #   HOME SCREEN
    # =====================
    def show_home(self):
        self.clear()

        tk.Label(self.root, text="🎯Quiz Game",
                 font=("Helvetica", 28, "bold"),
                 bg=BG_COLOR, fg=PRIMARY).pack(pady=(60, 5))

        tk.Label(self.root, text="Test your knowledge!",
                 font=("Helvetica", 13),
                 bg=BG_COLOR, fg=SUBTEXT).pack(pady=(0, 30))

        tk.Label(self.root, text="Enter Your Name:",
                 font=("Helvetica", 12),
                 bg=BG_COLOR, fg=TEXT_COLOR).pack()

        entry = tk.Entry(self.root, textvariable=self.player_name,
                         font=("Helvetica", 14), width=25,
                         bg=CARD_COLOR, fg=TEXT_COLOR,
                         insertbackground=TEXT_COLOR,
                         relief="flat", bd=8)
        entry.pack(pady=10)
        entry.focus()
        
        btn = tk.Button(self.root, text="Start Quiz ▶",
              font=("Helvetica", 13, "bold"),
              bg=PRIMARY, fg=TEXT_COLOR,
              activebackground=PRIMARY_HOVER,
              relief="flat", padx=20, pady=10,
              cursor="hand2",
              command=self.validate_name)
        btn.pack(pady=20)
        self.add_hover(btn, PRIMARY_HOVER, PRIMARY)

    def animate_title(self, label, colors, i=0):
        label.config(fg=colors[i % len(colors)])
        self.root.after(800, self.animate_title,
                        label, colors, i + 1)

        title = tk.Label(self.root, text="🎯 Python Quiz Game",
                 font=("Helvetica", 28, "bold"),
                 bg=BG_COLOR, fg=PRIMARY)
        title.pack(pady=(60, 5))
        self.animate_title(title, [PRIMARY, "#a855f7", "#6d28d9"])

    def validate_name(self):
        name = self.player_name.get().strip()
        if not name:
            self.show_message("⚠️ Please enter your name!", WARNING)
            return
        self.show_category()

    # =====================
    #   HELPER METHODS
    # =====================
    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_message(self, msg, color=DANGER):
        popup = tk.Toplevel(self.root)
        popup.title("")
        popup.geometry("320x120")
        popup.configure(bg=CARD_COLOR)
        popup.resizable(False, False)
        popup.grab_set()

        tk.Label(popup, text=msg,
                 font=("Helvetica", 12),
                 bg=CARD_COLOR, fg=color,
                 wraplength=280).pack(pady=20)

        tk.Button(popup, text="OK",
                  font=("Helvetica", 11),
                  bg=PRIMARY, fg=TEXT_COLOR,
                  relief="flat", padx=15, pady=5,
                  command=popup.destroy).pack()

    def add_hover(self, btn, hover_color, normal_color):
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_color))
        btn.bind("<Leave>", lambda e: btn.config(bg=normal_color))

    # =====================
    #   CATEGORY SCREEN
    # =====================
    def show_category(self):
        self.clear()

        tk.Label(self.root,
                 text=f"👋 Hello, {self.player_name.get().strip()}!",
                 font=("Helvetica", 18, "bold"),
                 bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(40, 5))

        tk.Label(self.root, text="Choose a Category",
                 font=("Helvetica", 13),
                 bg=BG_COLOR, fg=SUBTEXT).pack(pady=(0, 25))

        categories = {
            "🐍  Python":           "Python",
            "🌍  General Knowledge": "General Knowledge",
            "➗  Math":             "Math"
        }

        for label, value in categories.items():
            btn = tk.Button(self.root, text=label,
                      font=("Helvetica", 13, "bold"),
                      bg=CARD_COLOR, fg=TEXT_COLOR,
                      relief="flat", padx=20, pady=12,
                      width=25, cursor="hand2",
                      command=lambda v=value: self.set_category(v))
            btn.pack(pady=6)
            self.add_hover(btn, PRIMARY, CARD_COLOR)

    def set_category(self, value):
        self.category = value
        self.show_difficulty()

    # =====================
    #   DIFFICULTY SCREEN
    # =====================
    def show_difficulty(self):
        self.clear()

        tk.Label(self.root, text="⚙️ Choose Difficulty",
                 font=("Helvetica", 22, "bold"),
                 bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(40, 5))

        tk.Label(self.root,
                 text=f"Category: {self.category}",
                 font=("Helvetica", 12),
                 bg=BG_COLOR, fg=SUBTEXT).pack(pady=(0, 25))

        difficulties = {
            "🟢  Easy   (15 seconds)":   ("Easy",   15),
            "🟡  Medium (30 seconds)":   ("Medium", 30),
            "🔴  Hard   (50 seconds)":   ("Hard",   50),
        }

        colors = [SUCCESS, WARNING, DANGER]

        for (label, (level, tl)), color in zip(difficulties.items(), colors):
            btn = tk.Button(self.root, text=label,
                  font=("Helvetica", 13, "bold"),
                  bg=CARD_COLOR, fg=color,
                  activebackground=CARD_COLOR,
                  relief="flat", padx=20, pady=12,
                  width=25, cursor="hand2",
                  command=lambda l=level, t=tl: self.set_difficulty(l, t))
            btn.pack(pady=6)
            self.add_hover(btn, PRIMARY, CARD_COLOR)

        back_btn = tk.Button(self.root, text="← Back",
              font=("Helvetica", 11),
              bg=BG_COLOR, fg=SUBTEXT,
              activebackground=BG_COLOR,
              relief="flat", padx=10, pady=5,
              cursor="hand2",
              command=self.show_category)
        back_btn.pack(pady=(15, 0))
        self.add_hover(back_btn, CARD_COLOR, BG_COLOR)

    def set_difficulty(self, level, time_limit):
        self.difficulty     = level
        self.time_limit     = time_limit
        self.score          = 0
        self.q_index        = 0
        self.user_answers   = []
        self.show_loading()  # ← show loading screen while fetching

    def show_loading(self):
        self.clear()

        tk.Label(self.root, text="⏳ Loading Questions...",
                font=("Helvetica", 20, "bold"),
                bg=BG_COLOR, fg=PRIMARY).pack(pady=(150, 10))

        tk.Label(self.root,
                text="Fetching fresh questions from internet...",
                font=("Helvetica", 12),
                bg=BG_COLOR, fg=SUBTEXT).pack()

        # Fetch in background thread so UI doesn't freeze
        threading.Thread(target=self.load_questions,
                        daemon=True).start()

    def load_questions(self):
        # Try fetching from API
        fetched = fetch_questions(
            self.category,
            self.difficulty,
            amount=5
        )

        if fetched:
            self.quiz_questions = fetched
            print(f"✅ Loaded {len(fetched)} questions from API")
        else:
            # Fallback to offline questions
            self.quiz_questions = offline_questions[self.category][self.difficulty]
            print("⚠️ Using offline questions")

        # Update UI from main thread
        self.root.after(0, self.show_question)

    # =====================
    #   QUESTION SCREEN
    # =====================
    def show_question(self):
        self.clear()
        self.timer_running = False

        if self.q_index >= len(self.quiz_questions):
            self.show_result()
            return

        q_data = self.quiz_questions[self.q_index]
        total  = len(self.quiz_questions)

        # Top bar
        top = tk.Frame(self.root, bg=CARD_COLOR)
        top.pack(fill="x", padx=0, pady=0)

        tk.Label(top,
                 text=f"Q {self.q_index+1}/{total}  |  "
                      f"{self.category}  |  {self.difficulty}",
                 font=("Helvetica", 10),
                 bg=CARD_COLOR, fg=SUBTEXT).pack(side="left", padx=15, pady=8)

        self.timer_label = tk.Label(top,
                 text=f"⏱ {self.time_limit}s",
                 font=("Helvetica", 11, "bold"),
                 bg=CARD_COLOR, fg=WARNING)
        self.timer_label.pack(side="right", padx=15, pady=8)

        # Timer progress bar
        self.progress_canvas = tk.Canvas(
            self.root, width=660, height=10,
            bg=CARD_COLOR, highlightthickness=0)
        self.progress_canvas.pack(pady=(0, 10))
        self.progress_bar = self.progress_canvas.create_rectangle(
            0, 0, 660, 10, fill=SUCCESS, width=0)

        # Score
        tk.Label(self.root,
                 text=f"Score: {self.score}/{total}",
                 font=("Helvetica", 10),
                 bg=BG_COLOR, fg=SUBTEXT).pack(anchor="e", padx=20)

        # Question
        tk.Label(self.root,
                 text=q_data["question"],
                 font=("Helvetica", 14, "bold"),
                 bg=BG_COLOR, fg=TEXT_COLOR,
                 wraplength=620, justify="center").pack(pady=(20, 25))

        # Answer buttons
        self.ans_buttons = []
        for opt in q_data["options"]:
            btn = tk.Button(self.root, text=opt,
                            font=("Helvetica", 12),
                            bg=CARD_COLOR, fg=TEXT_COLOR,
                            activebackground=PRIMARY,
                            relief="flat", padx=10, pady=10,
                            width=40, cursor="hand2",
                            command=lambda o=opt[0]: self.check_answer(o))
            btn.pack(pady=4)
            self.ans_buttons.append(btn)

        # Start timer
        self.time_left     = self.time_limit
        self.timer_running = True
        threading.Thread(target=self.run_timer, daemon=True).start()

    def run_timer(self):
        total_width = 660
        while self.time_left > 0 and self.timer_running:
            time.sleep(1)
            self.time_left -= 1
            if self.timer_running:
                # Update timer label color
                color = SUCCESS if self.time_left > 5 else DANGER
                self.timer_label.config(
                    text=f"⏱ {self.time_left}s", fg=color)
                # Update progress bar width
                width = int((self.time_left / self.time_limit) * total_width)
                self.progress_canvas.coords(
                    self.progress_bar, 0, 0, width, 10)
                self.progress_canvas.itemconfig(
                    self.progress_bar, fill=color)

            if self.time_left == 0 and self.timer_running:
                self.timer_running = False
                self.user_answers.append("—")
                self.play_sound("timeout")       # ← add this
                self.show_feedback(False, "⌛ Time's up!", auto_next=True)

    def check_answer(self, selected):
        self.timer_running = False
        self.user_answers.append(selected)
        correct    = self.quiz_questions[self.q_index]["answer"]
        is_correct = (selected == correct)
        if is_correct:
            self.score += 1
            self.play_sound("correct")
        else:
            self.play_sound("wrong")
        msg = "✅ Correct!" if is_correct else f"❌ Wrong! Answer: {correct}"
        self.show_feedback(is_correct, msg)

    def play_sound(self, sound_type):
        try:
            sounds = {
                "correct": "sounds/correct.wav",
                "wrong":   "sounds/wrong.wav",
                "timeout": "sounds/timeout.wav"
            }
            path = sounds.get(sound_type)
            if path and os.path.exists(path):
                threading.Thread(
                    target=lambda: (
                        pygame.mixer.Sound(path).play(),
                        time.sleep(1)
                    ),
                    daemon=True).start()
        except Exception as e:
            print(f"Sound error: {e}")
            self.root.bell()

    def show_feedback(self, is_correct, msg, auto_next=False):
        # Disable all buttons
        for btn in self.ans_buttons:
            btn.config(state="disabled")

        color = SUCCESS if is_correct else DANGER
        fb = tk.Label(self.root, text=msg,
                      font=("Helvetica", 13, "bold"),
                      bg=BG_COLOR, fg=color)
        fb.pack(pady=8)

        if auto_next:
            self.root.after(1500, self.next_question)
        else:
            tk.Button(self.root, text="Next ▶",
                      font=("Helvetica", 12, "bold"),
                      bg=PRIMARY, fg=TEXT_COLOR,
                      relief="flat", padx=15, pady=8,
                      cursor="hand2",
                      command=self.next_question).pack(pady=8)

    def next_question(self):
        self.q_index += 1
        self.show_question()

    # =====================
    #   RESULT SCREEN
    # =====================
    def show_result(self):
        self.clear()
        total      = len(self.quiz_questions)
        percentage = (self.score / total) * 100

        tk.Label(self.root, text="🎯 Game Over!",
                 font=("Helvetica", 24, "bold"),
                 bg=BG_COLOR, fg=PRIMARY).pack(pady=(30, 5))

        # Result card
        card = tk.Frame(self.root, bg=CARD_COLOR,
                        padx=30, pady=20)
        card.pack(pady=10, padx=60, fill="x")

        info = [
            ("👤 Player",     self.player_name.get().strip()),
            ("📘 Category",   self.category),
            ("⚙️ Difficulty", self.difficulty),
            (f"✅ Score",     f"{self.score}/{total}"),
            ("📊 Percentage", f"{percentage:.1f}%"),
        ]

        for label, value in info:
            row = tk.Frame(card, bg=CARD_COLOR)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, font=("Helvetica", 11),
                     bg=CARD_COLOR, fg=SUBTEXT,
                     width=16, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=("Helvetica", 11, "bold"),
                     bg=CARD_COLOR, fg=TEXT_COLOR,
                     anchor="w").pack(side="left")

        # Remark
        if percentage == 100:
            remark, color = "🏅 OUTSTANDING! Perfect Score!", SUCCESS
        elif percentage >= 80:
            remark, color = "🌟 EXCELLENT! Great job!", SUCCESS
        elif percentage >= 60:
            remark, color = "👍 GOOD JOB! Keep it up!", WARNING
        elif percentage >= 40:
            remark, color = "📚 AVERAGE. Practice more!", WARNING
        else:
            remark, color = "💪 KEEP TRYING! You can do it!", DANGER

        tk.Label(self.root, text=remark,
                 font=("Helvetica", 13, "bold"),
                 bg=BG_COLOR, fg=color).pack(pady=8)

        # Buttons
        btn_frame = tk.Frame(self.root, bg=BG_COLOR)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="🔄 Play Again",
                  font=("Helvetica", 11, "bold"),
                  bg=PRIMARY, fg=TEXT_COLOR,
                  relief="flat", padx=15, pady=8,
                  cursor="hand2",
                  command=self.show_category).pack(side="left", padx=8)

        tk.Button(btn_frame, text="🏆 High Scores",
                  font=("Helvetica", 11, "bold"),
                  bg=CARD_COLOR, fg=TEXT_COLOR,
                  relief="flat", padx=15, pady=8,
                  cursor="hand2",
                  command=self.show_high_scores).pack(side="left", padx=8)

        tk.Button(btn_frame, text="📋 Review",
                  font=("Helvetica", 11, "bold"),
                  bg=CARD_COLOR, fg=TEXT_COLOR,
                  relief="flat", padx=15, pady=8,
                  cursor="hand2",
                  command=self.show_review).pack(side="left", padx=8)

        tk.Button(btn_frame, text="🏠 Home",
                  font=("Helvetica", 11, "bold"),
                  bg=CARD_COLOR, fg=TEXT_COLOR,
                  relief="flat", padx=15, pady=8,
                  cursor="hand2",
                  command=self.show_home).pack(side="left", padx=8)
        
        self.save_score()

    # =====================
    #   SAVE & HIGH SCORES
    # =====================
    def save_score(self):
        try:
            total = len(self.quiz_questions)
            with open("scores.txt", "a") as f:
                f.write(f"{self.player_name.get().strip()} | "
                        f"{self.category} | "
                        f"{self.difficulty} | "
                        f"{self.score}/{total}\n")
        except Exception as e:
            print(f"Could not save score: {e}")

    def show_high_scores(self):
        popup = tk.Toplevel(self.root)
        popup.title("🏆 High Scores")
        popup.geometry("680x580")
        popup.configure(bg=BG_COLOR)
        popup.resizable(True, True)
        popup.grab_set()

        tk.Label(popup, text="🏆 High Scores",
                font=("Helvetica", 18, "bold"),
                bg=BG_COLOR, fg=PRIMARY).pack(pady=(15, 5))

        tk.Label(popup, text="Top 3 per Category & Difficulty",
                font=("Helvetica", 11),
                bg=BG_COLOR, fg=SUBTEXT).pack(pady=(0, 10))

        # ── Scrollable area ──
        container = tk.Frame(popup, bg=BG_COLOR)
        container.pack(fill="both", expand=True, padx=15, pady=5)

        canvas    = tk.Canvas(container, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical",
                                command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_COLOR)

        scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse scroll
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(
                int(-1*(e.delta/120)), "units"))

        # ── Load and group scores ──
        try:
            # grouped = { "Python": { "Easy": [...], "Medium": [...] } }
            grouped = {}
            categories  = ["Python", "General Knowledge", "Math"]
            difficulties = ["Easy", "Medium", "Hard"]

            # Initialize all groups empty
            for cat in categories:
                grouped[cat] = {}
                for diff in difficulties:
                    grouped[cat][diff] = []

            if os.path.exists("scores.txt"):
                with open("scores.txt", "r") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            parts = line.split("|")
                            if len(parts) == 4:
                                name       = parts[0].strip()
                                cat        = parts[1].strip()
                                diff       = parts[2].strip()
                                score_part = parts[3].strip()
                                sv, tv     = score_part.split("/")
                                pct        = (int(sv) / int(tv)) * 100
                                if cat in grouped and diff in grouped[cat]:
                                    grouped[cat][diff].append(
                                        (name, score_part, pct))

            # ── Display per Category ──
            diff_colors = {
                "Easy":   SUCCESS,
                "Medium": WARNING,
                "Hard":   DANGER
            }
            medals = ["🥇", "🥈", "🥉"]
            cat_icons = {
                "Python":            "🐍",
                "General Knowledge": "🌍",
                "Math":              "➗"
            }

            for cat in categories:
                # Category header
                cat_frame = tk.Frame(scroll_frame, bg=CARD_COLOR,
                                    padx=15, pady=10)
                cat_frame.pack(fill="x", pady=(8, 2), padx=5)

                tk.Label(cat_frame,
                        text=f"{cat_icons[cat]}  {cat}",
                        font=("Helvetica", 14, "bold"),
                        bg=CARD_COLOR, fg=PRIMARY).pack(anchor="w")

                # Difficulty rows inside category
                for diff in difficulties:
                    diff_frame = tk.Frame(scroll_frame, bg=BG_COLOR,
                                        padx=20, pady=6)
                    diff_frame.pack(fill="x", padx=5)

                    # Difficulty label
                    tk.Label(diff_frame,
                            text=f"⚙️ {diff}",
                            font=("Helvetica", 11, "bold"),
                            bg=BG_COLOR,
                            fg=diff_colors[diff]).pack(anchor="w")

                    scores = grouped[cat][diff]
                    scores.sort(key=lambda x: x[2], reverse=True)
                    top3   = scores[:3]

                    if not top3:
                        tk.Label(diff_frame,
                                text="   No scores yet",
                                font=("Helvetica", 10),
                                bg=BG_COLOR, fg=SUBTEXT).pack(anchor="w")
                    else:
                        for i, (name, score_part, pct) in enumerate(top3):
                            row = tk.Frame(diff_frame, bg=BG_COLOR)
                            row.pack(fill="x", pady=1)

                            tk.Label(row,
                                    text=f"  {medals[i]}  {name}",
                                    font=("Helvetica", 10, "bold"),
                                    bg=BG_COLOR, fg=TEXT_COLOR,
                                    width=20, anchor="w").pack(side="left")

                            tk.Label(row,
                                    text=f"Score: {score_part}",
                                    font=("Helvetica", 10),
                                    bg=BG_COLOR, fg=SUBTEXT,
                                    width=12, anchor="w").pack(side="left")

                            tk.Label(row,
                                    text=f"{pct:.1f}%",
                                    font=("Helvetica", 10, "bold"),
                                    bg=BG_COLOR,
                                    fg=diff_colors[diff]).pack(side="left")

                    # Divider
                    tk.Frame(diff_frame, bg=CARD_COLOR,
                            height=1).pack(fill="x", pady=(5, 0))

        except Exception as e:
            tk.Label(scroll_frame, text=f"Error loading scores: {e}",
                    bg=BG_COLOR, fg=DANGER,
                    font=("Helvetica", 11)).pack(pady=20)

        # ── Close Button ──
        tk.Button(popup, text="Close",
                font=("Helvetica", 12, "bold"),
                bg=PRIMARY, fg=TEXT_COLOR,
                relief="flat", padx=20, pady=8,
                cursor="hand2",
                command=popup.destroy).pack(pady=12)

        

    def show_review(self):
        popup = tk.Toplevel(self.root)
        popup.title("📋 Answer Review")
        popup.geometry("650x550")
        popup.configure(bg=BG_COLOR)
        popup.resizable(True, True)
        popup.grab_set()

        tk.Label(popup, text="📋 Answer Review",
             font=("Helvetica", 18, "bold"),
             bg=BG_COLOR, fg=PRIMARY).pack(pady=(15, 5))

        tk.Label(popup,
             text=f"Score: {self.score}/{len(self.quiz_questions)}",
             font=("Helvetica", 12),
             bg=BG_COLOR, fg=SUBTEXT).pack(pady=(0, 10))

        # ── Scrollable area ──
        container = tk.Frame(popup, bg=BG_COLOR)
        container.pack(fill="both", expand=True, padx=15, pady=5)

        canvas    = tk.Canvas(container, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical",
                              command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_COLOR)

        scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse scroll support
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(
                int(-1*(e.delta/120)), "units"))

        # ── Each Question Card ──
        for i, q in enumerate(self.quiz_questions):
            user_ans  = self.user_answers[i] if i < len(self.user_answers) else "—"
            correct   = q["answer"]
            is_correct = user_ans == correct

            # Card frame
            card = tk.Frame(scroll_frame, bg=CARD_COLOR,
                        padx=15, pady=12)
            card.pack(fill="x", pady=6, padx=5)
   
            # Question number + status
            status_color = SUCCESS if is_correct else DANGER
            status_icon  = "✅ Correct" if is_correct else "❌ Wrong"

            header = tk.Frame(card, bg=CARD_COLOR)
            header.pack(fill="x")

            tk.Label(header,
                 text=f"Q{i+1}.",
                 font=("Helvetica", 12, "bold"),
                 bg=CARD_COLOR, fg=PRIMARY).pack(side="left")

            tk.Label(header,
                 text=status_icon,
                 font=("Helvetica", 11, "bold"),
                 bg=CARD_COLOR, fg=status_color).pack(side="right")

            # Question text
            tk.Label(card,
                 text=q["question"],
                 font=("Helvetica", 12, "bold"),
                 bg=CARD_COLOR, fg=TEXT_COLOR,
                 wraplength=560, justify="left",
                 anchor="w").pack(anchor="w", pady=(5, 10))

            # Divider line
            tk.Frame(card, bg=PRIMARY, height=1).pack(fill="x", pady=(0, 8))

            # Options
            for opt in q["options"]:
                opt_letter = opt[0]  # A, B, C or D

                # Determine color for each option
                if opt_letter == correct and opt_letter == user_ans:
                    # User answered correctly — green background
                    opt_bg   = SUCCESS
                    opt_fg   = "#ffffff"
                    prefix   = "✔ "
                elif opt_letter == correct:
                    # Correct answer user missed — green background
                    opt_bg   = SUCCESS
                    opt_fg   = "#ffffff"
                    prefix   = "✔ "
                elif opt_letter == user_ans:
                    # User's wrong answer — red background
                    opt_bg   = DANGER
                    opt_fg   = "#ffffff"
                    prefix   = "✘ "
                else:
                    # Other options — normal
                    opt_bg   = BG_COLOR
                    opt_fg   = SUBTEXT
                    prefix   = "   "

                opt_frame = tk.Frame(card, bg=opt_bg,
                                 padx=10, pady=6)
                opt_frame.pack(fill="x", pady=2)

                tk.Label(opt_frame,
                     text=f"{prefix}{opt}",
                     font=("Helvetica", 11),
                     bg=opt_bg, fg=opt_fg,
                     anchor="w").pack(anchor="w")

            # Your answer vs correct answer summary
            summary = tk.Frame(card, bg=CARD_COLOR)
            summary.pack(fill="x", pady=(10, 0))

            tk.Label(summary,
                 text=f"Your Answer:  {user_ans}",
                 font=("Helvetica", 10),
                 bg=CARD_COLOR,
                 fg=SUCCESS if is_correct else DANGER).pack(side="left")

            tk.Label(summary,
                 text=f"Correct Answer:  {correct}",
                 font=("Helvetica", 10),
                 bg=CARD_COLOR, fg=SUCCESS).pack(side="right")

        # ── Close Button ──
        tk.Button(popup, text="Close",
              font=("Helvetica", 12, "bold"),
              bg=PRIMARY, fg=TEXT_COLOR,
              relief="flat", padx=20, pady=8,
              cursor="hand2",
              command=popup.destroy).pack(pady=15)

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()