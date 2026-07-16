"""勝利時レビューの判定ロジック。"""

import csv
from pathlib import Path


class PerformanceReviewer:
    """桁数と試行回数から3段階レビューを返す。"""

    perfect = "すばらしい"
    decent = "まずまずだね"
    poor = "もう少しだよ"

    DEFAULT_CSV_PATH = Path(__file__).with_name("review_rules.csv")
    LEVEL_NAMES = (perfect, decent, poor)

    def __init__(self, csv_path=None, review_table=None):
        self.review_table = self._load_review_table_from_csv(
            csv_path or self.DEFAULT_CSV_PATH
        )
        if review_table:
            for digits, rules in review_table.items():
                self.review_table[digits] = list(rules)

    def _load_review_table_from_csv(self, csv_path):
        table = {}
        with Path(csv_path).open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                digits = int(row["digits"])
                table[digits] = [
                    (int(row["sugoi_max"]), self.LEVEL_NAMES[0]),
                    (int(row["mazumazu_max"]), self.LEVEL_NAMES[1]),
                    (int(row["mousukoshi_max"]), self.LEVEL_NAMES[2]),
                ]
        return table

    # 指定された桁数のルールを返す（未定義なら補完する）
    def _resolve_rules(self, digits):
        if digits in self.review_table:
            return self.review_table[digits]

        # 未定義の桁数でも使えるように、素朴な式で対応表を補完する
        excellent = max(1, digits + 1)
        decent = max(excellent + 1, digits * 2)
        return [
            (excellent, self.perfect),
            (decent, self.decent),
            (999, self.poor),
        ]

    # 指定された桁数と試行回数からレビューを評価する
    def evaluate(self, digits, tries):
        rules = self._resolve_rules(digits)
        for max_tries, level in rules:
            if tries <= max_tries:
                return level
        return self.poor

    def make_message(self, digits, tries):
        level = self.evaluate(digits, tries)
        return f"総評: {level}！"
