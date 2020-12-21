import numpy as np
from numpy import dot
from numpy.linalg import norm
import pandas as pd
import matplotlib.pyplot as plt
import librosa.display, librosa
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from audio.models import *
import sys
# from sklearn.metrics.pairwise import cosine_similarity
# import glob
# import os
from audio.dbmanager.redis_dao import SimilarityRedisHandler
import pickle
import warnings

warnings.filterwarnings('ignore')


class SimilarityProcessor:
    def __init__(self, n_clusters, file_path, file, n):
        self.n_clusters = n_clusters
        self.file_path = file_path
        self.file = file
        self.n = n

    @staticmethod
    def cos_sim(A, B):
        return dot(A, B) / (norm(A) * norm(B))

    def get_file_list(self):
        song_list = []
        file_list = []
        for song in os.listdir(self.file_path):
            song_list.append(song)
            for slice in os.listdir(self.file_path + str(song)):
                file_list.append(slice)
        return file_list

    # Extract audio Features: MFCC
    # 처음에 training할 파일들의 feat 추출
    def get_all_feature(self, file_list):
        X = pd.DataFrame()
        columns = []
        for i in range(20):
            columns.append("mfcc" + str(i + 1))

        song_list = []
        data = None
        mfcc_audio = None

        for song in os.listdir(self.file_path):
            song_list.append(song)
            for slice in os.listdir(self.file_path + str(song)):
                audio, fs = librosa.load(self.file_path + str(song) + "/" + str(slice))
                mfcc_audio = librosa.feature.mfcc(audio, sr=fs)

                pca = PCA(n_components=1, whiten=True)  # use pca
                X_pca = pca.fit_transform(mfcc_audio)
                fin_pca = []

                for index in range(len(X_pca)):
                    fin_pca.append(X_pca[index, 0])
                df_pca = pd.Series(fin_pca)

                X = pd.concat([X, df_pca], axis=1)

                data = X.T.copy()
                data.columns = columns
                # print(slice + " completed")
        data.index = [file for file in file_list]

        return data

    # 파일 하나의 feat 추출(user's input audio)
    def get_feature_file(self):
        X = pd.DataFrame()
        columns = []
        for i in range(20):
            columns.append("mfcc" + str(i + 1))

        audio, fs = librosa.load(self.file_path + self.file)
        mfcc_audio = librosa.feature.mfcc(audio, sr=fs)

        pca = PCA(n_components=1, whiten=True)  # use pca
        X_pca = pca.fit_transform(mfcc_audio)
        fin_pca = []

        for index in range(len(X_pca)):
            fin_pca.append(X_pca[index, 0])
        df_pca = pd.Series(fin_pca)

        X = pd.concat([X, df_pca], axis=1)

        data = X.T.copy()
        data.columns = columns
        data.index = [self.file]

        return data

    # check_perform_kmeans: cluster 수별 kmeans 성능 확인
    def check_perform_kmeans(data):
        inertia = []
        K = range(1, 16)
        for k in K:
            kmeanModel = KMeans(n_clusters=k).fit(data)
            kmeanModel.fit(data)
            inertia.append(kmeanModel.inertia_)
        # print (model.inertia_)

        # Plot the elbow
        plt.figure(figsize=(10, 7))
        plt.plot(K, inertia, 'bx-')
        plt.xlabel('# of clusters')
        plt.ylabel('inertia')
        plt.show()

    def cluster_sim(self, data, idx):
        sim_dic = {}

        for i in range(len(data.values)):
            seg1 = data.values[idx]  # 비교할 audio_slice
            seg2 = data.values[i]  # 같은 cluster에 있는 audio_slice 여러개

            seg1_2d = seg1.reshape(-1, 1)  # 차원 축소
            seg2_2d = seg2.reshape(-1, 1)

            sim = SimilarityProcessor.cos_sim(np.squeeze(seg1_2d), np.squeeze(seg2_2d))
            sim = sim * 100  # 퍼센트(%) 단위로 나타냄
            sim = round(sim, 2)  # 소수 둘째자리에서 반올림

            audio_slice_id = data.index[i]

            sim_dic[audio_slice_id] = sim

        final_dic = sorted(sim_dic.items(), reverse=True, key=lambda x: x[1])  # 내림차순 정렬

        return final_dic[1:self.n]

    def process(self):
        new_data = self.get_feature_file()
        new_data.to_csv('/home/jihee/choleor_media/csv/audio_feature.csv', mode='a', header=False)

        # Load audio_feature.csv file
        feat_data = pd.read_csv("/home/jihee/choleor_media/csv/audio_feature.csv", encoding='utf-8', index_col=[0])

        # KMeans Clustering
        model = KMeans(self.n_clusters)
        model.fit(feat_data)
        data_labels = model.predict(feat_data)

        cluster_index = []
        for i in range(len(data_labels)):
            if data_labels[i] == data_labels[len(feat_data) - 1]:
                cluster_index.append(i)

        filter_feat_data = feat_data.iloc[cluster_index]

        idx = 0
        for i in range(len(filter_feat_data)):
            if filter_feat_data.index[i] == self.file:  # 유사도 비교를 원하는 파일명
                idx = i
        return self.cluster_sim(filter_feat_data, idx)

    @staticmethod
    def initialize():
        all = SimilarityProcessor(5, f'{LF_SLICE}/0/', "", 20)
        file_list = all.get_file_list()
        data = all.get_all_feature(file_list)
        data.to_csv(f"/home/jihee/choleor_media/csv/audio_feature.csv", mode='w')

    @staticmethod
    def process_for_user(audioname, partition, start_idx, end_idx):
        for i in range(start_idx, end_idx + 1):
            dict_list = SimilarityProcessor(5, f"{LF_SLICE}{partition}/{audioname}/", f"{audioname}ㅡ{i}.wav",
                                            200).process()
            pi_smlr = pickle.dumps(dict_list)
            SimilarityRedisHandler.dao.set(f"{partition}:{audioname}ㅡ{i}", pi_smlr)


if __name__ == '__main__':
    # SimilarityProcessor.process_for_user("DKpfWL0THsg", 0, 14, 26)
    # print("===========================================================")
    for i in range(6, 10):
        print(pickle.loads(SimilarityRedisHandler.dao.get(f"6:-GAIe9DNFccㅡ{i}")))
