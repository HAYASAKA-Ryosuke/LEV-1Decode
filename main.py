import numpy as np
import pybeads as be

class Morse:
    def __init__(self, sample_rate, dot_length, space_length):
        self.sample_rate = sample_rate
        self.dot_length = dot_length
        self.space_length = space_length

    def count_length(self, data, condition):
        """条件に一致するデータの長さをカウントする関数"""
        count = 0
        for value in data:
            if condition(value):
                count += 1
            else:
                break
        return count

    def dot_or_dash(self, data):
        """ドットかダッシュを判定する関数"""
        length = self.count_length(data, lambda x: x)
        return ('.', length) if length < self.dot_length else ('-', length)

    def sleep(self, data):
        """間隔を判定する関数"""
        length = self.count_length(data, lambda x: not x)
        return (' ' if length > self.space_length else '', length)

    def decode_string(self, data):
        """モールスコードを文字列にデコードする関数"""
        morse_dict = {
            ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E",
            "..-.": "F", "--.": "G", "....": "H", "..": "I", ".---": "J",
            "-.-": "K", ".-..": "L", "--": "M", "-.": "N", "---": "O",
            ".--.": "P", "--.-": "Q", ".-.": "R", "...": "S", "-": "T",
            "..-": "U", "...-": "V", ".--": "W", "-..-": "X", "-.--": "Y",
            "--..": "Z", ".----": "1", "..---": "2", "...--": "3", "....-": "4",
            ".....": "5", "-....": "6", "--...": "7", "---..": "8", "----.": "9",
            "-----": "0", "--..--": ",", ".-.-.-": ".", "..--..": "?",
            "-..-.": "/", "-.--.": "(", "-.--.-": ")", ".-...": "&",
            "---...": ":", "-.-.-.": ";", "-...-": "=", ".----.": "'",
            "..--.-": "_", "-....-": "-", ".-.-.": "+", ".-..-.": "\"",
            "...-..-": "$", ".--.-.": "@"
        }
        return ''.join(morse_dict.get(char, '') for char in data.split())

    def decode_identify(self, data):
        """データをモールス符号にデコードする関数"""
        result = ''
        count = 0
        while count < len(data):
            if data[count]:
                char, length = self.dot_or_dash(data[count:])
                result += char
                count += length
            else:
                char, length = self.sleep(data[count:])
                result += char
                count += length
        return result

    def decode(self, data):
        return self.decode_string(self.decode_identify(data))

THRESHOLD = 0.008

fc = 0.006
d = 1
r = 8
amp = 0.3
lam0 = 0.5 * amp
lam1 = 5 * amp
lam2 = 4 * amp
Nit = 15
pen = 'L1_v2'

sample_rate = 400
dot_length = sample_rate  / 8
space_length = dot_length * 2
morse = Morse(sample_rate, dot_length, space_length)

L = 4000
x = np.fromfile('lev1_cw.f32', 'float32')
y = x[:x.size//L*L].reshape(-1, L)

for i in range(len(y)):
    # ベースラインを補正する
    signal_est, bg_est, cost = be.beads(y[i], d, fc, r, Nit, lam0, lam1, lam2, pen, conv=None)
    # デコード｡ノイズを取り除くために閾値でデータを分けた｡
    print(morse.decode(signal_est < THRESHOLD))
