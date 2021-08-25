# -*- coding: utf-8 -*-
"""
Created on Sun Aug 15 13:08:40 2021

@author: Axel
"""

import pandas as pd

from keras.models import Sequential
from keras.layers import Dense


X_PARAMETERS = ['popularity', 'danceability', 'energy', 'loudness', 'mode', 'speechiness', \
                'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature']

DUMMIES = ['mode', 'time_signature']

Y_PARAMETERS = ['listen_fraction']

class NeuralNetwork:
    
    def __init__(self, data=None):
        if data is None:
            return
        
        X, y = format_data(data)
        
        N_input = len(X.columns)
        
        self.model = Sequential()
        self.model.add(Dense(16, input_dim=N_input, activation='relu'))
        self.model.add(Dense(16, activation='relu'))
        self.model.add(Dense(16, activation='relu'))
        self.model.add(Dense(1, activation='sigmoid'))
   
        self.model.compile(loss='mean_squared_error', optimizer='adam')
        
        #self.model.compile(optimizer='adam', loss='binary_crossentropy')
        # fit the keras model on the dataset
        self.model.fit(X, y, epochs=500, batch_size=20)
        
        #X, y = format_data(data)
        #self.model.fit(X, y, epoch=150, batch_size=10)
        
    def predict(self, data):
        X, _ = format_data(data)
        
        predictions = self.model.predict(X)
        return predictions
        

def format_data(songKey):
    songKey = songKey.items
    songs = songKey[songKey.finished]
    
    Y_data = songs[Y_PARAMETERS]
    
    X_data = songs[X_PARAMETERS]
    X_data = pd.get_dummies(X_data, columns=DUMMIES)
    
    return X_data, Y_data


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
    
    X, Y = format_data(im)
    
    nn = NeuralNetwork(data = im)
    
    predictions = nn.predict(im)
    
    ev = nn.model.evaluate(X, Y)
    
    