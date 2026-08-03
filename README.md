# 🎯 Python Quiz Game

A feature-rich Quiz Game application built using Python and Tkinter GUI.

## 📌 Features

- 🖥️ Full Graphical User Interface using Tkinter
- 📂 3 Categories — Python, General Knowledge, Math
- ⚙️ 3 Difficulty Levels — Easy (15s), Medium (10s), Hard (5s)
- ⏱️ Live countdown timer with progress bar
- 🌐 Dynamic questions fetched from Quiz API
- 📶 Offline fallback questions when no internet
- 🏆 Top 3 High Scores per category and difficulty
- 📋 Review screen with color-coded answers
- 🔊 Sound effects using pygame
- 💾 Score saving to scores.txt

## 📁 Project Structure

quiz_game/
├── quiz.py            # Terminal version
├── quiz_gui.py        # GUI version (main app)
├── questions.py       # Offline question bank
├── api_questions.py   # Quiz API integration
├── run_once.py        # Creates sound files
├── scores.txt         # Auto-created score file
├── README.md          # Project documentation
└── sounds/
    ├── correct.wav
    ├── wrong.wav
    └── timeout.wav

## ⚙️ Setup Instructions

### Step 1 — Install Python
Download Python from https://python.org (version 3.8+)

### Step 2 — Install Required Libraries
pip install pygame requests

### Step 3 — Create Sound Files
python run_once.py

### Step 4 — Add Quiz API Key
Open api_questions.py and replace:
API_KEY = "YOUR_API_KEY_HERE"
with your key from https://quizapi.io

### Step 5 — Run the Application
python quiz_gui.py

## 🎮 How to Play

1. Enter your name on the Home screen
2. Choose a category (Python / GK / Math)
3. Choose difficulty (Easy / Medium / Hard)
4. Answer each question before the timer runs out
5. View your score and review answers at the end
6. Check Top 3 High Scores for each category

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python 3 | Core programming language |
| Tkinter | GUI framework |
| pygame | Sound effects |
| requests | API integration |
| threading | Background timer and API calls |
| Quiz API | Dynamic questions |

## 👩‍💻 Developer

Name   : Suvvari Navya Sri
Domain : Python Intern
Company: Upskill Campus & UniConverge Technologies Pvt. Ltd.
