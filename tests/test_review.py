from pathlib import Path

from hitblow.review import PerformanceReviewer


def test_review_three_levels_for_3_digits():
    reviewer = PerformanceReviewer()

    assert reviewer.evaluate(3, 3) == reviewer.perfect
    assert reviewer.evaluate(3, 6) == reviewer.decent
    assert reviewer.evaluate(3, 7) == reviewer.poor


def test_review_changes_by_digits():
    reviewer = PerformanceReviewer()

    assert reviewer.evaluate(4, 5) == reviewer.perfect
    assert reviewer.evaluate(4, 9) == reviewer.decent
    assert reviewer.evaluate(4, 10) == reviewer.poor


def test_csv_has_rules_for_digits_1_to_10():
    reviewer = PerformanceReviewer()

    for digits in range(1, 11):
        assert digits in reviewer.review_table


def test_custom_csv_is_extendable(tmp_path):
    csv_path = Path(tmp_path) / "rules.csv"
    csv_path.write_text(
        "digits,sugoi_max,mazumazu_max,mousukoshi_max\n2,1,2,4\n",
        encoding="utf-8",
    )

    reviewer = PerformanceReviewer(csv_path=csv_path)

    assert reviewer.evaluate(2, 1) == reviewer.perfect
    assert reviewer.evaluate(2, 2) == reviewer.decent
    assert reviewer.evaluate(2, 3) == reviewer.poor
