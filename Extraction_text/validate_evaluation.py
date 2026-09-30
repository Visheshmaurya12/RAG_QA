
import json
from pathlib import Path

DATASET_PATH = Path(
    "data/evaluation/evaluation_questions.json"
)


def main():
    if not DATASET_PATH.exists():
        print(f"Dataset not found: {DATASET_PATH}")
        return

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        questions = json.load(file)

    if not isinstance(questions, list) or not questions:
        print("ERROR: Dataset must be a non-empty list.")
        return

    seen_ids = set()
    errors = []

    for item in questions:
        question_id = item.get("id")
        question = item.get("question")

        if not question_id or question_id in seen_ids:
            errors.append(f"Missing or duplicate ID: {question_id}")
        seen_ids.add(question_id)

        if not question or not question.strip():
            errors.append(f"{question_id}: question is empty")

        if not isinstance(item.get("answerable"), bool):
            errors.append(f"{question_id}: answerable must be true/false")

        if not isinstance(item.get("expected_concepts"), list):
            errors.append(f"{question_id}: expected_concepts must be a list")

        if not isinstance(item.get("expected_source_pages"), list):
            errors.append(f"{question_id}: expected_source_pages must be a list")

        if item.get("answerable") is True:
            if not item.get("expected_concepts"):
                errors.append(f"{question_id}: add expected concepts")

            if not item.get("expected_source_pages"):
                errors.append(f"{question_id}: add verified source pages")

    if errors:
        print("Evaluation dataset needs corrections:")
        for error in errors:
            print("-", error)
    else:
        print(f"PASS: {len(questions)} evaluation questions are valid.")


if __name__ == "__main__":
    main()
    