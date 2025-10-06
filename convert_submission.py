import csv
import json
import sys
from collections import defaultdict


def parse_attempt(attempt_text: str) -> list[list[int]]:
    text = attempt_text.strip()
    assert text, "Attempt text is empty"
    assert text[0] == "|" and text[-1] == "|", f"Attempt must start and end with '|': {text}"
    rows = text.strip("|").split("|")
    assert all(rows), f"Attempt contains empty row: {text}"

    matrix: list[list[int]] = []
    width = None
    for row in rows:
        assert row.isdigit(), f"Row contains non-digit characters: {row}"
        digits = [int(ch) for ch in row]
        if width is None:
            width = len(digits)
        else:
            assert len(digits) == width, "Inconsistent row width in attempt"
        matrix.append(digits)

    assert matrix, "Attempt produced an empty matrix"
    return matrix


def parse_output_id(output_id: str) -> tuple[str, int]:
    assert output_id, "Missing output_id"
    if "_" in output_id:
        puzzle_id, suffix = output_id.rsplit("_", 1)
        assert puzzle_id, "Puzzle id is empty"
        assert suffix.isdigit(), f"Non-numeric test index in output_id: {output_id}"
        test_index = int(suffix)
    else:
        puzzle_id = output_id
        test_index = 0
    return puzzle_id, test_index


def build_submission_map(reader: csv.DictReader) -> dict[str, list[dict[str, list[list[int]]]]]:
    puzzle_cases: dict[str, dict[int, list[list[list[int]]]]] = defaultdict(dict)

    for row_number, row in enumerate(reader, start=2):  # account for header line
        output_id = row.get("output_id", "").strip()
        puzzle_id, test_index = parse_output_id(output_id)

        raw_attempts = row.get("output", "").strip()
        assert raw_attempts, f"Missing attempts for {output_id}"
        attempt_strings = raw_attempts.split()
        assert attempt_strings, f"No attempts parsed for {output_id}"

        attempts = [parse_attempt(attempt) for attempt in attempt_strings]

        puzzle_entry = puzzle_cases[puzzle_id]
        assert test_index not in puzzle_entry, f"Duplicate test index {test_index} for {puzzle_id}"
        puzzle_entry[test_index] = attempts

    submission: dict[str, list[dict[str, list[list[int]]]]] = {}
    for puzzle_id in sorted(puzzle_cases):
        cases = puzzle_cases[puzzle_id]
        assert cases, f"No cases collected for {puzzle_id}"

        ordered_cases: list[dict[str, list[list[int]]]] = []
        for expected_index, (case_index, attempts) in enumerate(sorted(cases.items())):
            assert case_index == expected_index, (
                f"Test indices for {puzzle_id} are not contiguous: expected {expected_index}, got {case_index}"
            )

            case_dict = {f"attempt_{idx}": matrix for idx, matrix in enumerate(attempts, start=1)}
            assert case_dict, f"No attempts recorded for {puzzle_id} test {case_index}"
            ordered_cases.append(case_dict)

        submission[puzzle_id] = ordered_cases

    return submission


def main() -> None:
    assert len(sys.argv) == 3, "Usage: python convert_submission.py <input_csv> <output_json>"
    input_path, output_path = sys.argv[1], sys.argv[2]

    with open(input_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        assert reader.fieldnames == ["output_id", "output"], "Unexpected CSV header"
        submission = build_submission_map(reader)

    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(submission, json_file)


if __name__ == "__main__":
    main()
