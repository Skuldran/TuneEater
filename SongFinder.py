# -*- coding: utf-8 -*-
"""
Created on Sat Aug 14 19:58:44 2021

@author: Axel
"""

import random

from Constants import *

def find_song(songKey, artistKey, sp):
    #Choose random artist based on attractiveness
    artists, weights = artistKey.get_scores()
    
    pick = random.choices(artists, weights)[0]
    #Choose random song
    song_list = get_artist_songs(sp, pick)
    
    #Count how many songs are in this artist already
    n = 0
    i = 0
    #print('Song list: %s' % songKey.songs.keys())
    while i < len(song_list):
        song = song_list[i]
        
        #print('Comparing %s' % song)
        if songKey.containsItem(song):
            n = n+1
            song_list.remove(song)
        else:
            i = i+1
    
    if len(song_list) == 0:
        artistKey.finish_item(pick)
        return find_song(songKey, artistKey, sp)
    
    #TODO Pick the best tracks according to ML
    random.shuffle(song_list)

    #If it was the 10th song from this artist, expand by adding all related artists
    #print('n: %g' % n)
    if n==ARTIST_BRANCH_TRESHOLD:
        print('Adding related artists')
        add_related_artists(pick, artistKey, sp)
    
    return song_list[0]
    
    #If it was the 10th song from this artist, expand by adding all related artists
    
    
def get_artist_songs(sp, artist_id):
    temp = sp.artist_albums(artist_id)
    albums = temp['items']
    
    song_list = []
    
    for alb in albums:
        temp = sp.album_tracks(alb['id'])
        tracks = temp['items']
        
        for trk in tracks:
            song_list.append(trk['id'])
            
    return song_list

def add_related_artists(artist, artistKey, sp):
    #Find related artists
    temp = sp.artist_related_artists(artist)
    
    artists = temp['artists']
    for art in artists:
        #TODO adjust score according to ML algorithm
        print('Adding artist: %s' % art['name'])
        artistKey.recordData(art['id'], art['name'], 0.5, sample=0, add=False)
            
    