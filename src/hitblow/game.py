"""ゲームの進行（入力・表示・ループ）。

★ チームで足す機能は **自分の担当の場所**に書く（1機能=1ファイル）。
   下の「ここに足す」場所は3か所（① 開始時 ② 入力コマンド ③ 勝利時）。
   ペアごとに**別の場所**を直すので、並行作業でも衝突しない。
   import も自分の場所の近くに書くこと（ファイル先頭にまとめない＝衝突回避）。
"""

from .core import judge, make_secret


def play(digits=None):

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

    # ===== ① 開始時に足す（難易度・あいさつ など）: ここに書く =====

    # sound.py から SoundEmitter を読み込んでインスタンス化(効果音)
    from .sound import SoundEmitter
    se = SoundEmitter()

    tries = 0

    while True:
        # ===== 変更ここから: input() の代わりに1文字ずつ読み取る =====
        import sys
        import msvcrt

        print("予想 > ", end="", flush=True)
        guess = ""
        while True:
            # 1文字入力されるまで待機（Enter不要）
            char = msvcrt.getwch()

            # Ctrl+C (ASCIIコード: \x03) が押されたらプログラムを強制終了する
            if char == '\x03':
                raise KeyboardInterrupt

            # Enterキーが押されたら入力確定してループを抜ける
            elif char in ('\r', '\n'):
                print()
                break
            
            # Backspaceキーで1文字削除（削除時もwhooshを鳴らす）
            elif char == '\x08':
                if len(guess) > 0:
                    guess = guess[:-1]
                    # 画面上の文字を消す（バックスペース、空白、バックスペース）
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
                    se.whoosh()
                continue
            
            # 入力された文字が数字ならbeep、それ以外(abcなど)ならwhoosh
            if char.isdigit():
                se.beep()
            else:
                se.whoosh()
            
            guess += char
            sys.stdout.write(char)
            sys.stdout.flush()
            
        guess = guess.strip()
        # ===== 変更ここまで =====

        # ===== ② 入力コマンドに足す（ヒント など）: ここに書く（import もここに） =====

        se.beep()

        tries += 1
        hit, blow = judge(secret, guess)
        import time
        is_final = (hit == digits)
        if is_final:
            print("  Hit=", end="", flush=True)
            time.sleep(0.8)
            print(f"{hit}  Blow={blow}")
        else:
            print("  Hit=", end="", flush=True)
            time.sleep(0.8)
            print(f"{hit}", end="", flush=True)
            time.sleep(0.8)
            print("  Blow=", end="", flush=True)
            time.sleep(0.8)
            print(f"{blow}")
        if hit == digits:
            # ===== ③ 勝利時に足す（スコア・履歴 など）: ここに書く =====

            print(f"正解！ {tries} 回で当たり（答え {secret}）")
            break