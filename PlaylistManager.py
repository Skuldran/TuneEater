# -*- coding: utf-8 -*-
"""
Created on Sat Aug 14 14:56:12 2021

@author: Axel
"""
import os
from os.path import isfile, isdir
import json

import SongFinder as sf

def init_PlaylistManager(folder, sp, list_in, list_out):
    manager = PlaylistManager(folder, sp, list_in, list_out)
    #manager.list_in = list_in
    #manager.list_out = list_out
    

    
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
        self.sk = SongKey('data//' + self.folder, 'songs.json')
        
        #Concerned artists
        self.artists = SongKey('data//' + self.folder, 'artists.json')
        
        #ML
        
        # #
        # if created:
        #     print('Trying to add songs')
        #     temp = self.sp.playlist(self.list_in)
        #     tracks = temp['tracks']
        #     for t in tracks['items']:
        #         track = t['track']
        #         self.sk.recordData(track['id'], None, -1, sample=0, add=False)
        #         artists = track['artists']
        #         for a in artists:
        #             #TODO estimate artist attractiveness
        #             self.artists.recordData(a['id'], a['name'], 0.5, sample=0, add=False)
                    
        #     self.fill_with_songs()
    
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
        
        for art in obs['artist']:
            self.artists.recordData(art, None, obs['listen_fraction'])
        
        if n >= 1:
            #Remove track, move to out playlist
            #print(obs['song_id'])
            self.sk.finish_song(obs['song_id'])
            self.sp.playlist_remove_all_occurrences_of_items(self.list_in, [obs['song_id']])
            
            score = self.sk.get_score(obs['song_id'])
            if score>0:
                self.sp.playlist_add_items(self.list_out, [obs['song_id']])
            
            #Add new tracks
            self.fill_with_songs()
            return
        
    def fill_with_songs(self):
        temp = self.sp.playlist(self.list_in)
        tracks = temp['tracks']
        noToAdd = 20-tracks['total']
        
        songs = []
        for i in range(noToAdd):
            song = sf.find_song(self.sk, self.artists, self.sp)
            
            if song is not None:
                songs.append(song)
                self.sk.recordData(song, None, -1, sample=0, add=False)
        
        self.sp.playlist_add_items(self.list_in, songs)
        
class SongKey:
    
    def __init__(self, folder, file):
        self.folder = folder
        self.file = file
        
        if isfile(folder + file):
            with open(folder + '//' +  file, 'r') as fp:
                self.songs = json.load(fp)
        else:
            self.songs = {}
            
    def containsSong(self, song_id):
        return song_id in self.songs.keys()
    
        #return song_id in self.songs['song_id']
        
    def recordData(self, song_id, song_name, listen_fraction, sample=1, add=True, finished=False):
        if self.containsSong(song_id):
            if not add:
                return 0
            
            songDict = self.songs[song_id]
            
            n = songDict['samples']+1
            
            songDict['listen_fraction'] = ((n-1)/n)*songDict['listen_fraction'] + (1/n)*listen_fraction
            songDict['samples'] = n
            
            if songDict['name'] is None:
                songDict['name'] = song_name
            self.songs[song_id] = songDict
            
            #If reached the number of samples
            
            
            self.save_data()
            return n
        else:
            self.songs[song_id] = {'name': song_name, 'song_id': song_id, 'listen_fraction': listen_fraction, 'samples': sample, 'finished': finished}
            self.save_data()
            return 1
            
    def save_data(self):
        with open(self.folder + '//' + self.file, 'w') as fp:
            json.dump(self.songs, fp)
                
    def get_score(self, song_id):
        return self.songs[song_id]['listen_fraction']
                
    def get_scores(self, exclude_finished=False):
        #keys = list(self.songs.keys()).copy()
        keys = []
        scores = []
        
        for k in self.songs.keys():
            if exclude_finished and self.songs[k]['finished']:
                continue
            
            keys.append(k)
            scores.append(self.songs[k]['listen_fraction'])

        return keys, scores

    def finish_song(self, song):
        
        if not self.containsSong(song):
            print('Tried to finish item %s but it does not exist' % song)
            return
        
        self.songs[song]['finished'] = True
            
if __name__ == '__main__':
    if not isdir('test'):
        os.mkdir('test')
    
    sk =  SongKey('test')
    
    sk.recordData('id123', 'Namn', 0.5)
    sk.recordData('id123', 'Namn', 1)