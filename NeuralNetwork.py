# -*- coding: utf-8 -*-
"""
Created on Sun Aug 15 13:08:40 2021

@author: Axel
"""

import pandas as pd
import numpy as np
from numpy import random

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense


X_PARAMETERS = ['popularity', 'danceability', 'energy', 'loudness', 'mode', 'speechiness', \
                'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature']

X_PARAMETERS.remove('popularity')

DUMMIES = ['mode', 'time_signature']

Y_VALUE = 'listen_fraction'

class NeuralNetwork:
    
    
    def __init__(self, data=None):
        if data is None:
            return
        
        songs = data.items
        songs = songs[songs.finished]
        songs = songs[songs.loaded_features]
        
        if len(songs.index) < 100:
            self.alive = False
            print('Generated placeholder brain.')
            return
        
        self.alive = True
        
        X = songs[X_PARAMETERS]
        Y = songs[[Y_VALUE]]
        
        #map_dict = {}
        for v in DUMMIES:
            X[v] = v + '_' + X[v].astype(str)
        
            dummies = pd.get_dummies(X[v]) 
            X = pd.concat([X, dummies], axis=1)
            
            #for token, value in enumerate(X[v].unique()):
            #    map_dict[value] = token
            
            del X[v]
        
        self.save = X
        
        self.template = pd.DataFrame([], columns=X.columns, index=[])
        #self.map_dict = map_dict
        
        N_input = len(X.columns)
        
        self.model = Sequential()
        self.model.add(Dense(16, input_dim=N_input, activation='relu'))
        self.model.add(Dense(8, activation='relu'))
        self.model.add(Dense(1, activation='sigmoid'))
   
        self.model.compile(loss='mean_squared_error', optimizer='adam')
        self.model.fit(X, Y, epochs=500, batch_size=20)
        
        print('Generated new brain.')
        
        
    def predict(self, data):
        if not self.alive:
            return list(random.rand(len(data)))
        
        #Filter out song without audio features
        data = data[data.loaded_features]
        X = format_data(data, self.template)
        
        predictions = self.model.predict(X)
        predictions = [c[0] for c in predictions]
        return predictions
        

def format_data(X, template):
    
    for v in DUMMIES:
        X[v] = v + '_' + X[v].astype(str)
        
        dummies = pd.get_dummies(X[v]) 
        X = pd.concat([X, dummies], axis=1)
        
        #for token, value in enumerate(X[v].unique()):
        #    map_dict[value] = token
        
       # X[v].replace(map_dict, inplace=True)
        del X[v]
    
    out = template.copy()
    
    
    
    for c in X.columns:
        if c in template.columns:
            out[c] = X[c]
        else:
            print('Field %s is not in the template.' % c)
    
    out = out.fillna(0)        
    return out

if __name__ == '__main__':
    import Authorization
    import PlaylistManager as pm
    import DataParser as dp
    
    sp = Authorization.getSpotipy()
    sng = '3EMsFUjaG51Q2HUZUMixKG'
    
    im = pm.ItemManager('data/1H7DUJCLXdj0HhytxDXDU5', 'songs.csv')
    #songs, _ = im.get_scores()
    #song_data = fetch_song_values(sp, songs)
    dp.populate_finished_songs(sp, im)
    
    #X, Y = format_data(im)
    
    songs = im.items
    songs = songs[songs.finished]
        
    X = songs[X_PARAMETERS]
    Y = songs[[Y_VALUE]]
    
    Xd = songs[DUMMIES]
    
    map_dict = {}
    i = 0
    for v in DUMMIES:
        X[v] = v + '_' + X[v].astype(str)
        
        dummies = pd.get_dummies(X[v]) 
        X = pd.concat([X, dummies], axis=1)
        
        for token, value in enumerate(X[v].unique()):
            map_dict[value] = token
            i = i+1
        
        X[v].replace(map_dict, inplace=True)
        del X[v]
    
    in_template = pd.DataFrame([], columns=X.columns, index=[])
    #nn = NeuralNetwork(data = im)
    #predictions = nn.predict(im)
    #ev = nn.model.evaluate(X, Y)
    
#    N = len(X.index)
#    N_input = len(X.columns)
#    
#    trainI = np.random.choice(Y.index, size=int(N/2), replace=False);
#    trainIndex = X.index.isin(trainI);
#
#    X_train = X.iloc[trainIndex]
#    Y_train = Y.iloc[trainIndex]
#    
#    X_test = X.iloc[~trainIndex]
#    Y_test = Y.iloc[~trainIndex]
#    
#    testModel = Sequential()
#    testModel.add(Dense(16, input_dim=N_input, activation='relu'))
#    testModel.add(Dense(16, activation='relu'))
#    testModel.add(Dense(16, activation='relu'))
#    testModel.add(Dense(1, activation='sigmoid'))
#   
#    testModel.compile(loss='mean_squared_error', optimizer='adam')
#    testModel.fit(X_train, Y_train, epochs=1000, batch_size=20)
#    
#    testModel.evaluate(X_test, Y_test)
    
    