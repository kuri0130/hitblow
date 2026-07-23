"""ゲームの進行（入力・表示・ループ）。

★ チームで足す機能は **自分の担当の場所**に書く（1機能=1ファイル）。
   下の「ここに足す」場所は3か所（① 開始時 ② 入力コマンド ③ 勝利時）。
   ペアごとに**別の場所**を直すので、並行作業でも衝突しない。
   import も自分の場所の近くに書くこと（ファイル先頭にまとめない＝衝突回避）。
"""

from .core import judge, make_secret
from .rule import explain_rules


def _select_mode():
    """モード選択メニューを表示して mode 文字列を返す。"""
    print("╭────────────────────────────────╮")
    print("│       モードを選んでね         │")
    print("├────────────────────────────────┤")
    print("│  1: 通常モード                 │")
    print("│  2: 制限時間モード（3桁・7秒） │")
    print("╰────────────────────────────────╯")
    while True:
        choice = input("モード > ").strip()
        if choice == "1":
            return "normal"
        elif choice == "2":
            return "timelimit"


def _read_guess_normal(digits, se):
    """通常モード用の入力処理。1文字ずつ読み取り、確定した guess を返す。"""
    import sys

    if sys.platform == "win32":
        import msvcrt
    else:
        import tty
        import termios

    print("予想 > ", end="", flush=True)
    guess = ""
    while True:
        # 1文字入力されるまで待機（Enter不要）
        if sys.platform == "win32":
            char = msvcrt.getwch()
        else:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                char = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        # Ctrl+C (ASCIIコード: \x03) が押されたらプログラムを強制終了する
        if char == "\x03":
            raise KeyboardInterrupt

        # Enterキーが押されたら入力確定してループを抜ける
        elif char in ("\r", "\n"):
            # 桁数が丁度で、かつすべて数字の場合のみ決定できる
            if len(guess) == digits and guess.isdigit():
                print()
                break
            else:
                # 桁数が足りない、または余っているなどの場合は whoosh を鳴らして入力を続けさせる
                se.whoosh()
                continue

        # Backspaceキーで1文字削除（削除時もwhooshを鳴らす）
        elif char == "\x08":
            if len(guess) > 0:
                guess = guess[:-1]
                # 画面上の文字を消す（バックスペース、空白、バックスペース）
                sys.stdout.write("\b \b")
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

    return guess.strip()


def _read_guess_timelimit(digits, se, time_limit=10.0):
    """制限時間モード用の入力処理。

    タイマーバーを別スレッドで表示しながら入力を受け付ける。
    時間切れの場合は None を返す。
    """
    import sys
    import threading
    import time

    if sys.platform == "win32":
        import msvcrt
    else:
        import tty
        import termios

    # --- タイマーバーの設定 ---
    BAR_WIDTH = 30
    timeout_event = threading.Event()  # タイムアウト通知用
    done_event = threading.Event()  # 入力完了通知用
    start_time = time.time()
    output_lock = threading.Lock()  # ターミナル出力の排他制御

    # --- 初期レイアウト: バー行(1行目) + 入力行(2行目) ---
    initial_bar = f"⏱ \033[92m[{'█' * BAR_WIDTH}]\033[0m {time_limit:.1f}s"
    sys.stdout.write(initial_bar + "\n")
    sys.stdout.write("予想 > ")
    sys.stdout.flush()

    def _draw_bar():
        """サブスレッド: 0.1秒ごとにバー行だけを更新する。

        ANSI エスケープで カーソル保存 → 1行上へ → バー描画 → カーソル復帰
        することで、入力行のカーソル位置・内容を壊さない。
        """
        while not done_event.is_set():
            elapsed = time.time() - start_time
            remaining = max(0.0, time_limit - elapsed)
            ratio = remaining / time_limit
            filled = int(BAR_WIDTH * ratio)
            empty = BAR_WIDTH - filled

            # 残り時間に応じて色を変える
            if ratio > 0.5:
                color = "\033[92m"  # 緑
            elif ratio > 0.2:
                color = "\033[93m"  # 黄
            else:
                color = "\033[91m"  # 赤

            reset = "\033[0m"
            bar_text = (
                f"⏱ {color}[{'█' * filled}{'░' * empty}]{reset} {remaining:.1f}s "
            )

            with output_lock:
                # カーソル保存 → 1行上へ移動 → 行頭へ → バー描画 → カーソル復帰
                sys.stdout.write(f"\033[s\033[1A\r{bar_text}\033[u")
                sys.stdout.flush()

            if remaining <= 0:
                timeout_event.set()
                return

            done_event.wait(0.1)

    # タイマーバー描画スレッドを開始
    bar_thread = threading.Thread(target=_draw_bar, daemon=True)
    bar_thread.start()

    guess = ""
    timed_out = False

    while True:
        # タイムアウトチェック
        if timeout_event.is_set():
            timed_out = True
            break

        if sys.platform == "win32":
            # Windows: ノンブロッキングでキー入力をポーリング
            if msvcrt.kbhit():
                char = msvcrt.getwch()
            else:
                time.sleep(0.05)
                continue
        else:
            # Unix 系: select で入力待ち
            import select

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
                if rlist:
                    char = sys.stdin.read(1)
                else:
                    continue
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        # Ctrl+C
        if char == "\x03":
            done_event.set()
            bar_thread.join()
            raise KeyboardInterrupt

        # Enter
        elif char in ("\r", "\n"):
            if len(guess) == digits and guess.isdigit():
                break
            else:
                se.whoosh()
                continue

        # Backspace
        elif char == "\x08":
            if len(guess) > 0:
                guess = guess[:-1]
                with output_lock:
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                se.whoosh()
            continue

        # 文字入力
        if char.isdigit():
            se.beep()
        else:
            se.whoosh()

        guess += char
        with output_lock:
            sys.stdout.write(char)
            sys.stdout.flush()

    # タイマー描画スレッドを停止
    done_event.set()
    bar_thread.join()

    # バー行をクリア（1行上に移動 → クリア → 戻る）
    sys.stdout.write(f"\033[1A\r" + " " * (BAR_WIDTH + 20) + f"\r\033[1B")
    sys.stdout.flush()

    if timed_out:
        print()
        return None

    print()
    return guess.strip()


def play(digits=None):

    # ===== ① 開始時に足す（難易度・あいさつ など）: ここに書く =====

    # --- モード選択 ---
    mode = _select_mode()
    explain_rules(mode)

    if mode == "timelimit":
        digits = 3
    else:
        # 桁数を尋ねるため、デフォルトはNoneにしておく
        if digits is None:
            while True:
                text = input(
                    "予想する数字の桁数を決めます\n1 から 10 までの数字で入力してね > "
                ).strip()
                if text.isdigit() and 1 <= int(text) <= 10:
                    digits = int(text)
                    break

    secret = make_secret(digits)
    print(f"Hit & Blow（{digits} 桁・重複なし）")
    if mode == "timelimit":
        print("⏱ 制限時間: 7秒 / 1ターン")

    # sound.py から SoundEmitter を読み込んでインスタンス化(効果音)
    from .sound import SoundEmitter

    se = SoundEmitter()

    tries = 0

    while True:
        # --- モードに応じた入力処理 ---
        if mode == "timelimit":
            guess = _read_guess_timelimit(digits, se)
            if guess is None:
                # タイムアウト → ゲームオーバー
                print("⏰ 時間切れ！ ゲームオーバー！")
                print(f"答えは {secret} でした")
                break
        else:
            guess = _read_guess_normal(digits, se)

        # ===== ② 入力コマンドに足す（ヒント など）: ここに書く（import もここに） =====

        se.beep()

        tries += 1
        hit, blow = judge(secret, guess)
        import time

        is_final = hit == digits
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
            from .review import PerformanceReviewer

            print(f"正解！ {tries} 回で当たり（答え {secret}）")
            reviewer = PerformanceReviewer()
            print(reviewer.make_message(digits, tries))
            break
