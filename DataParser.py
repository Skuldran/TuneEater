# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 15:25:27 2021

@author: Axel
"""

import pandas as pd

AUDIO_FEATURES = ['danceability', 'energy', 'loudness', 'mode', 'speechiness', 'acousticness', \
                  'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature']

CATEGORY_FEATURES = ['mode', 'time_signature']

TRACK_FEATURES = ['explicit', 'popularity']

def populate_artists(sp, artistManager):
    artists, _ = artistManager.get_scores()
    
    i = 0
    while i < len(artists):
        if artistManager.get_cell(artists[i], 'loaded_genres'):
            artists.pop(i)
        else:
            i = i+1
            
    
            
def populate_finished_songs(sp, songManager):
    songs, _ = songManager.get_scores(exclude_finished=True)
    
    i = 0
    while i < len(songs):
        if songManager.get_cell(songs[i], 'loaded_features'):
            songs.pop(i)
        else:
            i = i+1
    
    df = fetch_song_values(sp, songs)
    
    for sn in df.index:
        for field in df.columns:
            songManager.recordData(sn, {field: df.at[sn, field]}, save=False)
            
    songManager.save_data()
    

def fetch_song_values(sp, songs):
    df = pd.DataFrame([], index = [])
    
    if not type(songs) == list:
        songs = [songs]
    
    batches = chunks(songs, 50)
    
    for b in batches:
        songJSON = sp.tracks(b)
        for item in songJSON['tracks']:
            extract_features(df, item, TRACK_FEATURES)
            
        songJSON = sp.audio_features(songs)
        for item in songJSON:
            extract_features(df, item, AUDIO_FEATURES)
    
    return df

def extract_features(df, item, features):
    song_id = item['id']
    
    for feat in features:
        df.at[song_id, feat] = item[feat]

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def serve_song_features():
    return

if __name__=='__main__':
    import Authorization
    import PlaylistManager as pm
    
    sp = Authorization.getSpotipy()
    sng = '3EMsFUjaG51Q2HUZUMixKG'
    
    im = pm.ItemManager('data/1H7DUJCLXdj0HhytxDXDU5', 'songs.csv')
    #songs, _ = im.get_scores()
    #song_data = fetch_song_values(sp, songs)
    populate_finished_songs(sp, im)