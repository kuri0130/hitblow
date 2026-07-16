#数字入力時と削除時に効果音を鳴らす。

import numpy as np

try:
    import sounddevice as sd
except OSError:
    print("sounddeviceモジュールの読み込みに失敗しました。効果音は無効化されます。")
    sd = None

class SoundEmitter:
    def __init__(self, fs=44100):
        self.fs = fs
        self.enabled = sd is not None

    def _play(self, wave):
        if not self.enabled:
            return
        try:
            sd.play(wave, self.fs)
        except Exception:
            pass

    def beep(self):
        """「ピッ」という電子音"""
        duration = 0.05
        freq = 1500
        t = np.linspace(0, duration, int(self.fs * duration), False)
        wave = 0.5 * np.sin(2 * np.pi * freq * t)
        
        # フェードアウト処理
        fade_len = int(len(wave) * 0.2)
        wave[-fade_len:] *= np.linspace(1, 0, fade_len)
        
        self._play(wave)

    def whoosh(self):
        """「シュッ」という不正な入力に対する効果音（ノイズを急減衰）"""
        duration = 0.15  # 少し長めに
        t = np.linspace(0, duration, int(self.fs * duration), False)
        
        # ホワイトノイズを生成
        noise = np.random.uniform(-0.5, 0.5, len(t))
        
        # 急激に音量を下げるエンベロープ（減衰音）
        envelope = np.exp(-15 * t)
        wave = noise * envelope
        
        sd.play(wave, self.fs)