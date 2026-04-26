from __future__ import annotations

from clinical_ai.app.evaluation import evaluate_golden_cases, generate_assignment_report


def main() -> int:
    result = evaluate_golden_cases()
    print(generate_assignment_report(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
