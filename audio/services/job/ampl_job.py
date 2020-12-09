from audio.services.job import rediswq
import librosa
import numpy as np
import pickle
from django_redis import get_redis_connection


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


q = rediswq.RedisWQ(name="ampl-wq", host="redis")
print("Worker with sessionID: " + q.sessionID())
print("Initial queue state: empty=" + str(q.empty()))
while not q.empty():
    item = q.lease(lease_secs=10, block=True, timeout=2)
    if item is not None:
        path = item.decode('UTF-8')
        plist = path.split("/")
        res = pickle.dumps(process(path))
        get_redis_connection("amplitude").rpush(plist[-3] + ">" + plist[-1], res)
        q.complete(item)
    else:
        print("Waiting for work")
print("Queue empty, exiting")
