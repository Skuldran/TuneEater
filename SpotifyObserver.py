# -*- coding: utf-8 -*-
"""
Created on Sat Aug 14 12:19:55 2021

@author: Axel
"""
import time

import Authorization

def observeSong(sp):
    play = sp.current_playback()
    if play is None:
        return None
    
    song = play['item']
    context = play['context']
    if context is None:
        context_type = None
    else:
        #context = context['uri']
        context_type = context['type']
        uri = context['uri']
        context = uri.split(':')[-1]
            
    song_playtime = play['progress_ms']
    song_id = song['id']
    song_length = song['duration_ms']
    song_name = song['name']
    artist_temp = song['artists']
    
    artists = []
    artist_names = []
    for art in artist_temp:
        artists.append(art['id'])
        artist_names.append(art['name'])
    
    
    return {'song_id': song_id, 'playtime': song_playtime, 'length': song_length, 'song_name': song_name, 'context': context, 'context_type': context_type, 'artist': artists, 'artist_names': artist_names}
    
class SpotifyObserver:
    
    def __init__(self, sp):
        self.sp = sp
        play = observeSong(self.sp)
        self.last_observation = play
        self.last_timestamp = time.time()
        
        self.last_observation = None #observeSong(sp)
        print('Observer initialized.')
        
    def observe(self):
        play = observeSong(self.sp)
        
        if play is None or self.last_observation is None:
            self.last_observation = play
            return None
        
        delta_t = time.time()-self.last_timestamp
        self.last_timestamp = time.time()
        
        if play['song_id'] != self.last_observation['song_id']:
            listen_id = self.last_observation['song_id']
            listen_time = self.last_observation['playtime'] + (delta_t*1000 - play['playtime'])
            listen_fraction = listen_time / self.last_observation['length']
            print('This guy listened to %s for %g ms (%s %%).' % (self.last_observation['song_name'], listen_time, str(int(100*listen_fraction))))
            out = self.last_observation
            out['listen_fraction'] = listen_fraction
            #out = {'song_id': listen_id, 'song_name': self.last_observation['name'],'listen_fraction': listen_fraction, 'context': self.last_observation['context'], 'context_type': self.last_observation['context_type'], 'artist': self.last_observation['artist']}
        else:
            out = None

        self.last_observation = play
        
        return out
        
if __name__ == '__main__':
    sp = Authorization.getSpotipy()
    
    observer = SpotifyObserver(sp)
    
    while True:
        time.sleep(5)
        obs = observer.observe()
        
        if obs is not None:
            print(obs)
            #break
        