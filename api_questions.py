import requests
import html

# ── Category mapping to Open Trivia API category IDs ──
CATEGORY_MAP = {
    "Python":            18,   # Science & Computers
    "General Knowledge": 9,    # General Knowledge
    "Math":              19,   # Science & Mathematics
}

DIFFICULTY_MAP = {
    "Easy":   "easy",
    "Medium": "medium",
    "Hard":   "hard",
}

def fetch_questions(category, difficulty, amount=5):
    """
    Fetch questions from Open Trivia API.
    Returns list of question dicts in same format as questions.py
    """
    cat_id = CATEGORY_MAP.get(category, 9)
    diff   = DIFFICULTY_MAP.get(difficulty, "medium")

    url = (f"https://opentdb.com/api.php"
           f"?amount={amount}"
           f"&category={cat_id}"
           f"&difficulty={diff}"
           f"&type=multiple")

    try:
        response = requests.get(url, timeout=10)
        data     = response.json()

        if data["response_code"] != 0:
            print("API error — using offline questions")
            return None

        questions = []
        for item in data["results"]:
            # Decode HTML entities (e.g. &amp; → &)
            question    = html.unescape(item["question"])
            correct     = html.unescape(item["correct_answer"])
            incorrects  = [html.unescape(i)
                           for i in item["incorrect_answers"]]

            # Combine and sort options
            all_options = incorrects + [correct]
            all_options.sort()

            # Assign A B C D labels
            labels  = ["A", "B", "C", "D"]
            options = []
            answer  = ""

            for i, opt in enumerate(all_options):
                options.append(f"{labels[i]}. {opt}")
                if opt == correct:
                    answer = labels[i]

            questions.append({
                "question": question,
                "options":  options,
                "answer":   answer
            })

        return questions

    except requests.exceptions.ConnectionError:
        print("No internet — using offline questions")
        return None
    except Exception as e:
        print(f"API error: {e}")
        return None