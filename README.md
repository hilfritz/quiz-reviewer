# IBM Maximo C1000-183 Quiz App

A Flask quiz app for IBM Maximo Manage v9.0 Functional Deployment - Professional practice.

## Included files

```text
maximo_quiz_app_final/
├── app.py
├── questions.csv
├── score_history.csv
├── requirements.txt
├── templates/
│   └── quiz.html
└── static/
    └── style.css
```

## Features

- Loads active questions from `questions.csv`
- Shows questions one by one
- Supports single-answer and multi-answer questions
- Calculates score after submit
- Uses 67% passing score
- Shows PASSED / FAILED
- Shows wrong questions with correct answers
- Allows restart
- Saves attempt results to `score_history.csv`
- Saves wrong question IDs in score history

## Run locally

```bash
cd maximo_quiz_app_final
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Notes

- Only questions with `status = active` are shown.
- Multi-answer questions use comma-separated values, for example: `B,E`.
- The app normalizes answer order, so `E,B` is treated the same as `B,E`.


## Properties

The app reads settings from `app.properties`.

```properties
show_answer_when_proceeding=true
passing_percent=67
```

### `show_answer_when_proceeding`

When set to `true`, clicking **Check Answer** reveals:

- whether your answer is correct or incorrect
- the correct answer
- the explanation from `questions.csv`

Then clicking **Next** moves to the next question.

When set to `false`, the app behaves like a normal quiz and only shows results after final submit.

## Explanation column

`questions.csv` now includes:

```text
explanation
```

This is used when showing feedback after each question and when reviewing mistakes at the end.


## Advanced Operations Pack Added

The question bank includes an advanced operations pack covering:

- priority
- dispatching dashboard
- skill level
- craft/qualification matching
- work zone
- resource utilization
- resource leveling
- scheduling and dispatching scenarios
