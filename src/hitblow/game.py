"""ゲームの進行（入力・表示・ループ）。

★ チームで足す機能は **自分の担当の場所**に書く（1機能=1ファイル）。
   下の「ここに足す」場所は3か所（① 開始時 ② 入力コマンド ③ 勝利時）。
   ペアごとに**別の場所**を直すので、並行作業でも衝突しない。
   import も自分の場所の近くに書くこと（ファイル先頭にまとめない＝衝突回避）。
"""

from .core import judge, make_secret


def play(digits=None):
    # ===== ① 開始時に足す（難易度・あいさつ など）: ここに書く =====
    print("╭─────────────────────────────────────────╮")
    print("│             ☆ ルール説明 ☆              │")
    print("├─────────────────────────────────────────┤")
    print("│ ある桁の数字を当てるゲームです。予想    │")
    print("│ に対して次のフィードバックがあります。  │")
    print("│                                         │")
    print("│  hit  ... 数字も位置も合っている個数    │")
    print("│  blow ... 数字は含まれるが位置が違う個数│")
    print("╰─────────────────────────────────────────╯")

    # 桁数を尋ねるため、デフォルトはNoneにしておく
    if digits is None:
        while True:
            text = input("桁数 > ").strip()
            if text.isdigit() and 1 <= int(text) <= 10:
                digits = int(text)
                break
            print("1 から 10 までの数字で入力してね")

    secret = make_secret(digits)
    print(f"Hit & Blow（{digits} 桁・重複なし）")

    tries = 0
    while True:
        guess = input("予想 > ").strip()

        # ===== ② 入力コマンドに足す（ヒント など）: ここに書く（import もここに） =====
        # 例:  from .hint import hint
        #      if guess == "h":
        #          print(hint(secret)); continue

        if len(guess) != digits or not guess.isdigit():
            print(f"{digits} 桁の数字で入力してね")
            continue
        tries += 1
        hit, blow = judge(secret, guess)
        print(f"  Hit={hit}  Blow={blow}")
        if hit == digits:
            # ===== ③ 勝利時に足す（スコア・履歴 など）: ここに書く =====

            print(f"正解！ {tries} 回で当たり（答え {secret}）")
            break
