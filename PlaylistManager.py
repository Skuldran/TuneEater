# -*- coding: utf-8 -*-
"""
Created on Sat Aug 14 14:56:12 2021

@author: Axel
"""
import os
from os.path import isfile, isdir
import json
import pandas as pd

import SongFinder as sf
from Constants import *

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
        self.sk = ItemManager('data//' + self.folder, 'songs.json')
        
        #Concerned artists
        self.artists = ItemManager('data//' + self.folder, 'artists.json')
        
        #ML
    
    def load(self):
        if not os.path.isfile('data//' + self.folder + '//playlist.json'):
            print('Cant load playlist folder: %s' % self.folder)
            
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
           self.sk.recordData(track['id'], None, -1, sample=0, add=False)
           artists = track['artists']
           for a in artists:
               #TODO estimate artist attractiveness
               self.artists.recordData(a['id'], a['name'], 0.5, sample=0, add=False)
                
        self.fill_with_songs()
            
    def song_listened(self, obs):
        n = self.sk.recordData(obs['song_id'], obs['song_name'], obs['listen_fraction'])
        
        for i in range(len(obs['artist'])):
            self.artists.recordData(obs['artist'][i], obs['artist_names'][0], obs['listen_fraction'])
        
        if n >= SONG_REPEATS:
            #Remove track, move to out playlist
            print("Song '%s' is finsihed, removing it." % obs['song_name'])
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
            song = sf.find_song(self.sk, self.artists, self.sp)
            
            if song is not None:
                songs.append(song)
                self.sk.recordData(song, None, -1, sample=0, add=False)
        
        self.sp.playlist_add_items(self.list_in, songs)
        
class ItemManager:
    #Class to manage the song and artist data
    
    def __init__(self, folder, file):
        self.folder = folder
        self.file = file
        
        if isfile(folder + file):
            self.items = pd.read_csv(folder + '//' + file, index_col=0)
        else:
            self.items = pd.DataFrame(columns=['name', 'item_id', 'listen_fraction', 'samples', 'finished'], index=[])
            
    def containsItem(self, item_id):
        return item_id in self.items.index #self.items.keys()
    
        #return item_id in self.items['item_id']
        
    def recordData(self, item_id, item_name, listen_fraction, sample=1, add=True, finished=False):
        if self.containsItem(item_id):
            if not add:
                return 0
            
            #itemRow = self.items.loc[item_id]
            #itemDict = self.items[item_id]
            
            
            n = self.items.at[item_id, 'samples']+1
            
            self.items.at[item_id, 'listen_fraction'] = ((n-1)/n)*self.items.at[item_id, 'listen_fraction'] + (1/n)*listen_fraction
            self.items.at[item_id, 'samples'] = n
            
            if self.items.at[item_id, 'name'] is None:
                self.items.at[item_id, 'name'] = item_name
            
            #self.items[item_id] = itemRow
            
            #If reached the number of samples
            
            self.save_data()
            return n
        else:
            rowDict = {item_id: {'name': item_name, 'item_id': item_id, 'listen_fraction': listen_fraction, 'samples': sample, 'finished': finished}}
            
            df = pd.DataFrame(rowDict.values(), index=rowDict.keys())
            self.items = self.items.append(df)
            
            #self.items[item_id] = {'name': item_name, 'item_id': item_id, 'listen_fraction': listen_fraction, 'samples': sample, 'finished': finished}
            self.save_data()
            return 1
            
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