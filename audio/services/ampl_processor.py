import librosa
import numpy as np
import pickle
from audio.dbmanager.redis_dao import AmplitudeRedisHandler


class AmplitudeProcessor:
    @staticmethod
    def process(file):
        music, fs = librosa.load(file)
        music_stft = librosa.stft(music)
        music_amp = librosa.amplitude_to_db(abs(music_stft))
        music_fin_amp = [[0 for i in range(len(music_amp[j]))] for j in range(len(music_amp))]

        for i in range(len(music_amp)):
            for j in range(len(music_amp[i])):
                if music_amp[i][j] >= 0:
                    music_fin_amp[i][j] = music_amp[i][j]

        length = len(music_fin_amp)  # dB array 길이: 1025
        len_unit = int(length / 9)  # 8박자 단위로 자르기 때문에 9로 나누기
        amp_list = []

        for i in range(9):
            amp = round(np.mean(music_fin_amp[(len_unit * i):(len_unit * (i + 1))]), 2)
            if i == 8:
                amp = round(np.mean(music_fin_amp[(len_unit * 8):length]), 2)

            if amp < 0 or amp > 30:
                step = 0
            elif amp == 0:
                step = 1
            else:
                step = int(amp / 3) + 1 if (amp % 3 != 0) else int(amp / 3)

            amp_list.append(step)  # 자른 박자 안에서 평균 진폭 구하기
        return amp_list


if __name__ == '__main__':
    print(AmplitudeProcessor.process("/home/jihee/choleor_media/audio/SLICE/QM8HngracYY/QM8HngracYYㅡ14.wav"))
    for i in range(9, 17):
        _list = AmplitudeProcessor.process(f"/home/jihee/choleor_media/audio/SLICE/GNGbmg_pVlQ/GNGbmg_pVlQㅡ{i}.wav")
        pi_ = pickle.dumps(_list)
        AmplitudeRedisHandler.dao.set(f"GNGbmg_pVlQㅡ{i}", pi_)
