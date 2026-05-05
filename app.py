from flask import Flask, render_template, request
import csv
from pathlib import Path
from datetime import datetime
import uuid

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
QUESTIONS_FILE = BASE_DIR / "questions.csv"
SCORE_HISTORY_FILE = BASE_DIR / "score_history.csv"
PROPERTIES_FILE = BASE_DIR / "app.properties"

DEFAULT_CONFIG = {
    "show_answer_when_proceeding": "true",
    "passing_percent": "67",
}


def load_properties():
    config = DEFAULT_CONFIG.copy()

    if PROPERTIES_FILE.exists():
        for line in PROPERTIES_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()

    return config


def config_bool(config, key):
    return str(config.get(key, "")).strip().lower() in {"true", "1", "yes", "y", "on"}


def config_float(config, key, default):
    try:
        return float(config.get(key, default))
    except (TypeError, ValueError):
        return float(default)


def normalize_answer(values):
    """Normalize single or multi-answer values so A,C and C,A are treated the same."""
    if values is None:
        return ""
    if isinstance(values, str):
        values = [values]
    cleaned = [v.strip().upper() for v in values if v and v.strip()]
    return ",".join(sorted(cleaned))


def load_questions():
    with QUESTIONS_FILE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [r for r in rows if r.get("status", "").strip().lower() == "active"]


def load_history():
    if not SCORE_HISTORY_FILE.exists():
        return []
    with SCORE_HISTORY_FILE.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_score(total, correct, score_percent, passed, wrong_question_ids):
    file_empty = not SCORE_HISTORY_FILE.exists() or SCORE_HISTORY_FILE.stat().st_size == 0
    fieldnames = [
        "attempt_id", "datetime_finished", "total_questions", "total_correct",
        "score_percent", "passed", "wrong_question_ids"
    ]

    with SCORE_HISTORY_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if file_empty:
            writer.writeheader()

        writer.writerow({
            "attempt_id": str(uuid.uuid4()),
            "datetime_finished": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_questions": total,
            "total_correct": correct,
            "score_percent": score_percent,
            "passed": "active" if passed else "inactive",
            "wrong_question_ids": ",".join(wrong_question_ids)
        })


@app.route("/", methods=["GET"])
def index():
    config = load_properties()
    passing_percent = config_float(config, "passing_percent", 67)
    questions = load_questions()
    history = load_history()

    return render_template(
        "quiz.html",
        questions=questions,
        results=None,
        history=history,
        passing_percent=passing_percent,
        show_answer_when_proceeding=config_bool(config, "show_answer_when_proceeding")
    )


@app.route("/submit", methods=["POST"])
def submit():
    config = load_properties()
    passing_percent = config_float(config, "passing_percent", 67)
    questions = load_questions()

    total = len(questions)
    correct = 0
    wrong = []

    for q in questions:
        qid = q["id"]
        user_answer = normalize_answer(request.form.getlist(f"answer_{qid}"))
        correct_answer = normalize_answer(q["correct_answer"])

        if user_answer == correct_answer:
            correct += 1
        else:
            wrong.append({
                "id": qid,
                "source": q.get("source", ""),
                "question": q["question"],
                "choice_a": q.get("choice_a", ""),
                "choice_b": q.get("choice_b", ""),
                "choice_c": q.get("choice_c", ""),
                "choice_d": q.get("choice_d", ""),
                "choice_e": q.get("choice_e", ""),
                "user_answer": user_answer if user_answer else "No answer",
                "correct_answer": correct_answer,
                "difficulty": q.get("difficulty", ""),
                "remarks": q.get("remarks", ""),
                "explanation": q.get("explanation", q.get("remarks", ""))
            })

    score_percent = round((correct / total) * 100, 2) if total else 0
    passed = score_percent >= passing_percent
    wrong_question_ids = [w["id"] for w in wrong]

    save_score(total, correct, score_percent, passed, wrong_question_ids)

    results = {
        "total": total,
        "correct": correct,
        "score_percent": score_percent,
        "passed": passed,
        "wrong": wrong
    }

    return render_template(
        "quiz.html",
        questions=questions,
        results=results,
        history=load_history(),
        passing_percent=passing_percent,
        show_answer_when_proceeding=config_bool(config, "show_answer_when_proceeding")
    )


if __name__ == "__main__":
    app.run(debug=True)
