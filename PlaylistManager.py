# -*- coding: utf-8 -*-
"""
Created on Sat Aug 14 14:56:12 2021

@author: Axel
"""
import os
from os.path import isfile, isdir
import json
import pandas as pd
import math

import SongFinder as sf
from Constants import *
import NeuralNetwork as nn
import DataParser as dp
import numpy as np

def init_PlaylistManager(folder, sp, list_in, list_out):
    manager = PlaylistManager(folder, sp, list_in, list_out)
    
    manager.init()
    return manager
    
def load_PlaylistManager(folder, sp):
    manager = PlaylistManager(folder, sp)
    manager.load()
    return manager

class PlaylistManager:
    
    def __init__(self, folder, sp, list_in=None, list_out=None):
        self.sp = sp
        
        self.folder = folder
        self.list_in  = list_in
        self.list_out = list_out
        
        if not isdir('data//' + self.folder):
            os.mkdir('data//' + self.folder)
        
        #Song key dataFrame
        self.sk = ItemManager('data//' + self.folder, 'songs.csv')
        
        #Concerned artists
        self.artists = ItemManager('data//' + self.folder, 'artists.csv')
        
        #ML
        self.generate_neural_network()
    
        #Values to have:
            # Number of songs
            # Number of artists
            # Brain age
            # Loss value
    
    def load(self):
        if not os.path.isfile('data//' + self.folder + '//playlist.json'):
            print('Cant load playlist file: %s' % self.folder)
            
        with open('data//' + self.folder + '//playlist.json', 'r') as fp:
            pl = json.load(fp)
            
        self.list_in = pl['in']
        self.list_out = pl['out']
        
    def init(self):
        pl = {'in': self.list_in, 'out': self.list_out}
        
        with open('data//' + self.folder + '//playlist.json', 'w') as fp:
            json.dump(pl, fp)
        
        print('Trying to add songs')
        temp = self.sp.playlist(self.list_in)
        tracks = temp['tracks']
        for t in tracks['items']:
           track = t['track']
           

           artists = track['artists']
           artist_ids = []
           for a in artists:
               #TODO estimate artist attractiveness
               self.artists.recordData(a['id'], {'item_name': a['name']}, overwrite=False)
               self.artists.recordScore(a['id'], NEW_ARTIST_SCORE, sample=0, overwrite=True)
               #TODO use ML
               artist_ids.append(a['id'])
        
        self.sk.recordData(track['id'], {'item_name': track['name'], 'artists': artist_ids}, overwrite=False)
        self.sk.recordScore(track['id'], -1, sample=0, overwrite=False)
        
        #TODO create column loaded_features
        #self.generate_neural_network()
        
        self.fill_with_songs()
            
    def song_listened(self, obs):
        n = self.sk.recordScore(obs['song_id'], obs['listen_fraction'])
        self.sk.recordData(obs['song_id'], {'item_name': obs['song_name'], 'artists': obs['artist']})
        
        for i in range(len(obs['artist'])):
            if not self.artists.containsItem(obs['artist'][i]):
                score = sf.get_avg_artist_score(obs['artist'][i], self.sp, self.brain)
                self.artists.recordScore(obs['artist'][i], score, sample=6)
            
            self.artists.recordData(obs['artist'][i], {'item_name': obs['artist_names'][i]})
            self.artists.recordScore(obs['artist'][i], obs['listen_fraction'])
        
        if n >= SONG_REPEATS:
            #Remove track, move to out playlist
            print("Song '%s' is finished, removing it." % obs['song_name'])
            self.sk.finish_item(obs['song_id'])
            self.sp.playlist_remove_all_occurrences_of_items(self.list_in, [obs['song_id']])
            
            score = self.sk.get_score(obs['song_id'])
            if score>OUT_LIST_TRESHOLD:
                print("Song '%s' was good. Adding it to #Out playlist." % obs['song_name'])
                self.sp.playlist_add_items(self.list_out, [obs['song_id']])
            
            #Add new tracks
            self.fill_with_songs()
            return
        
    def fill_with_songs(self):
        temp = self.sp.playlist(self.list_in)
        tracks = temp['tracks']
        noToAdd = PLAYLIST_SIZE-tracks['total']
        
        songs = []
        for i in range(noToAdd):
            song = sf.find_song(self.sk, self.artists, self.sp, self.brain)
            
            if song is not None:
                songs.append(song)
                self.sk.recordScore(song, -1, sample=0, overwrite=False)
        
        if len(songs)>0:
            print('Adding songs to playlist: %s' % songs)
            self.sp.playlist_add_items(self.list_in, songs)
            
    def generate_neural_network(self):
        dp.populate_finished_songs(self.sp, self.sk)
        self.brain = nn.NeuralNetwork(self.sk)
        
        #Printout ?
        #print('Generated new brain for playlist %s' % self.list_in)
        
class ItemManager:
    #Class to manage the song and artist data
    
    def __init__(self, folder, file):
        self.folder = folder
        self.file = file
        
        if isfile(folder + '/' + file):
            self.items = pd.read_csv(folder + '//' + file, index_col=0)
            self.items.listen_fraction = np.minimum(1, self.items.listen_fraction)
        else:
            self.items = pd.DataFrame(columns=['name', 'item_id', 'listen_fraction', 'samples', 'finished'], index=[])
            
    def containsItem(self, item_id):
        return item_id in self.items.index #self.items.keys()
    
    def get_cell(self, item_id, field):
        if not field in self.items.columns or not item_id in self.items.index:
            return None
        
        val = self.items.at[item_id, field]
        if type(val)==float and math.isnan(val):
            return None
                
        return val
        
    def recordData(self, item_id, features, overwrite=True, save=True):
        if self.containsItem(item_id):
            for f in features.keys():
                if not overwrite and f in self.items.columns:
                    val = self.items.at[item_id, f]
                    
                    if val is not None and type(val)==float and not math.isnan(val):
                        continue
                
                self.items.at[item_id, f] = features[f]
        else:
            tempDict = {item_id: features}
            df = pd.DataFrame(tempDict.values(), index=tempDict.keys())
            self.items = self.items.append(df)
            
        if save:
            self.save_data()
    
    def recordScore(self, item_id, listen_fraction, sample=1, overwrite=True):
        if self.containsItem(item_id):
            if not overwrite and not pd.isnull(self.items.loc[item_id, 'listen_fraction']):
                return 0
            
            n = self.items.at[item_id, 'samples']+1
            
            self.items.at[item_id, 'listen_fraction'] = ((n-1)/n)*self.items.at[item_id, 'listen_fraction'] + (1/n)*listen_fraction
            self.items.at[item_id, 'samples'] = n
            
            self.save_data()
            return n
        else:
            rowDict = {item_id: {'item_id': item_id, 'listen_fraction': listen_fraction, 'samples': sample, 'finished': False}}
            
            df = pd.DataFrame(rowDict.values(), index=rowDict.keys())
            self.items = self.items.append(df)
            
            self.save_data()
            return sample
            
    def save_data(self):
        self.items.to_csv(self.folder + '//' + self.file)
        #with open(self.folder + '//' + self.file, 'w') as fp:
        #    json.dump(self.items, fp)
                
    def get_score(self, item_id):
        return self.items.loc[item_id]['listen_fraction']
        #return self.items[item_id]['listen_fraction']
                
    def get_scores(self, exclude_finished=False):
        #keys = list(self.items.keys()).copy()
        keys = list(self.items.index)
        scores = list(self.items['listen_fraction'])
        finished = list(self.items['finished'])
        
        if exclude_finished:
            i = 0
            while i<len(finished):
                if not finished[i]:
                    keys.pop(i)
                    scores.pop(i)
                    finished.pop(i)
                else:
                    i = i+1

        return keys, scores

    def finish_item(self, item):
        
        if not self.containsItem(item):
            print('Tried to finish item %s but it does not exist' % item)
            return
        
        self.items.at[item, 'finished'] = True
        #self.items[item]['finished'] = True
            
if __name__ == '__main__':
    if not isdir('test'):
        os.mkdir('test')
    
    sk =  SongKey('test')
    
    sk.recordData('id123', 'Namn', 0.5)
    sk.recordData('id123', 'Namn', 1)