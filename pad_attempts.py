import json
import sys

def parse_attempt_index(key: str) -> int:
    assert key.startswith("attempt_"), f"Unexpected attempt key: {key}"
    suffix = key.split("_", 1)[1]
    assert suffix.isdigit(), f"Attempt key has non-numeric suffix: {key}"
    return int(suffix)


def pad_attempts(submission: dict[str, list[dict[str, list[list[int]]]]]) -> dict[str, list[dict[str, list[list[int]]]]]:
    padded: dict[str, list[dict[str, list[list[int]]]]] = {}
    for puzzle_id, cases in submission.items():
        assert isinstance(cases, list) and cases, f"Puzzle {puzzle_id} has no cases"
        padded_cases: list[dict[str, list[list[int]]]] = []
        for case_dict in cases:
            assert isinstance(case_dict, dict) and case_dict, "Case is empty"
            attempt_items = sorted(case_dict.items(), key=lambda item: parse_attempt_index(item[0]))
            assert len(attempt_items) <= 4, "Case has more than four attempts"

            previous_index = 0
            ordered_attempts: list[list[list[int]]] = []
            for key, matrix in attempt_items:
                index = parse_attempt_index(key)
                assert index == previous_index + 1, "Attempt indices must be contiguous starting at 1"
                assert isinstance(matrix, list) and matrix, "Attempt matrix must be a non-empty list"
                ordered_attempts.append(matrix)
                previous_index = index

            first_attempt = ordered_attempts[0]
            assert isinstance(first_attempt, list) and first_attempt, "First attempt must exist"

            while len(ordered_attempts) < 4:
                ordered_attempts.append(first_attempt)

            padded_case = {f"attempt_{idx}": matrix for idx, matrix in enumerate(ordered_attempts, start=1)}
            padded_cases.append(padded_case)
        padded[puzzle_id] = padded_cases
    return padded


def main() -> None:
    assert len(sys.argv) == 3, "Usage: python pad_attempts.py <input_json> <output_json>"
    input_path, output_path = sys.argv[1], sys.argv[2]

    with open(input_path, encoding="utf-8") as in_file:
        submission = json.load(in_file)
        assert isinstance(submission, dict) and submission, "Submission JSON must be a non-empty object"

    padded_submission = pad_attempts(submission)

    with open(output_path, "w", encoding="utf-8") as out_file:
        json.dump(padded_submission, out_file)


if __name__ == "__main__":
    main()
