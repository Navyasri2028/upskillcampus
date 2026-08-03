import os
import time
import threading
from questions import questions

timer_expired = False
answer_given = None

def display_welcome():
    print("=" * 45)
    print("        🎯 PYTHON QUIZ GAME")
    print("=" * 45)
    name = input("Enter your name: ").strip()
    return name

def choose_category():
    categories = list(questions.keys())
    print("\n📂 Available Categories:")
    for i, cat in enumerate(categories, 1):
        print(f"   {i}. {cat}")
    while True:
        choice = input("\nChoose category (enter number): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(categories):
            selected = categories[int(choice) - 1]
            print(f"✅ You selected: {selected}")
            return selected
        print("❌ Invalid! Try again.")

def choose_difficulty():
    difficulties = {
        "1": ("Easy",   15),
        "2": ("Medium", 30),
        "3": ("Hard",   50)
    }
    print("\n⚙️  Choose Difficulty:")
    print("   1. Easy   (15 seconds)")
    print("   2. Medium (30 seconds)")
    print("   3. Hard   (50 seconds)")
    while True:
        choice = input("\nEnter choice (1/2/3): ").strip()
        if choice in difficulties:
            level, time_limit = difficulties[choice]
            print(f"✅ Difficulty: {level} ({time_limit}s per question)")
            return level, time_limit
        print("❌ Invalid! Enter 1, 2 or 3.")

def countdown_timer(seconds):
    global timer_expired, answer_given
    for i in range(seconds, 0, -1):
        if answer_given is not None:
            return
        print(f"\r⏳ Time left: {i}s   ", end="", flush=True)
        time.sleep(1)
    timer_expired = True
    print("\r⌛ Time's up!          ")

def ask_question(q_num, question_data, time_limit):
    global timer_expired, answer_given
    timer_expired = False
    answer_given = None

    print(f"\nQ{q_num}: {question_data['question']}")
    for option in question_data["options"]:
        print(f"   {option}")

    timer_thread = threading.Thread(
        target=countdown_timer, args=(time_limit,))
    timer_thread.daemon = True
    timer_thread.start()

    answer = input("\nYour answer (A/B/C/D): ").strip().upper()
    answer_given = answer

    if timer_expired:
        print(f"❌ Too slow! Correct answer: {question_data['answer']}")
        return False
    if answer not in ["A", "B", "C", "D"]:
        print(f"⚠️ Invalid! Correct answer: {question_data['answer']}")
        return False
    if answer == question_data["answer"]:
        print("✅ Correct!")
        return True
    else:
        print(f"❌ Wrong! Correct answer: {question_data['answer']}")
        return False

def play_quiz(name, category, difficulty, time_limit):
    quiz_questions = questions[category][difficulty]  # ← updated line
    score = 0
    total = len(quiz_questions)

    print(f"\n{'=' * 45}")
    print(f"  📘 Category  : {category}")
    print(f"  👤 Player    : {name}")
    print(f"  ⚙️  Difficulty : {difficulty}")
    print(f"  ⏱️  Timer     : {time_limit}s per question")
    print(f"  📝 Questions : {total}")
    print(f"{'=' * 45}")
    print("\nStarting in 3 seconds...")
    time.sleep(3)

    for i, q in enumerate(quiz_questions, 1):
        if ask_question(i, q, time_limit):
            score += 1

    return score, total

def show_result(name, category, difficulty, score, total):
    percentage = (score / total) * 100
    print("\n" + "=" * 45)
    print("           🎯 GAME OVER!")
    print("=" * 45)
    print(f"  👤 Player     : {name}")
    print(f"  📘 Category   : {category}")
    print(f"  ⚙️  Difficulty  : {difficulty}")
    print(f"  ✅ Score      : {score}/{total}")
    print(f"  📊 Percentage : {percentage:.1f}%")
    print("-" * 45)
    if percentage == 100:
        print("  🏅 OUTSTANDING! Perfect Score!")
    elif percentage >= 80:
        print("  🌟 EXCELLENT! Great job!")
    elif percentage >= 60:
        print("  👍 GOOD JOB! Keep it up!")
    elif percentage >= 40:
        print("  📚 AVERAGE. Practice more!")
    else:
        print("  💪 KEEP TRYING! You can do it!")
    print("=" * 45)

def save_score(name, category, difficulty, score, total):
    try:
        with open("scores.txt", "a") as f:
            f.write(f"{name} | {category} | {difficulty} | {score}/{total}\n")
        print("💾 Score saved!")
    except Exception as e:
        print(f"⚠️ Could not save score: {e}")

def show_high_scores():
    try:
        if not os.path.exists("scores.txt"):
            print("\nNo scores recorded yet!")
            return

        scores = []
        with open("scores.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        name = parts[0].strip()
                        category = parts[1].strip()
                        score_part = parts[-1].strip()
                        score_val, total_val = score_part.split("/")
                        percentage = (int(score_val) / int(total_val)) * 100
                        scores.append((name, category, score_part, percentage))

        scores.sort(key=lambda x: x[3], reverse=True)
        print("\n" + "=" * 45)
        print("        🏆 TOP 3 HIGH SCORES")
        print("=" * 45)
        medals = ["🥇", "🥈", "🥉"]
        for i, (name, category, score, pct) in enumerate(scores[:3]):
            print(f"  {medals[i]} {name} | {category} | {score} | {pct:.1f}%")
        print("=" * 45)

    except Exception as e:
        print(f"⚠️ Could not load scores: {e}")

def main():
    name = display_welcome()
    while True:
        category = choose_category()
        difficulty, time_limit = choose_difficulty()
        score, total = play_quiz(name, category, difficulty, time_limit)
        show_result(name, category, difficulty, score, total)
        save_score(name, category, difficulty, score, total)
        show_high_scores()
        again = input("\n🔄 Play again? (yes/no): ").strip().lower()
        if again != "yes":
            print(f"\n👋 Thanks for playing, {name}! Goodbye!")
            break

if __name__ == "__main__":
    main()