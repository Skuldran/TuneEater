# -*- coding: utf-8 -*-
"""
Created on Sat Aug 14 14:48:51 2021

@author: Axel
"""

import time
import os

import Authorization
import SpotifyObserver
import PlaylistManager as pm
from Constants import *


def look_for_new_lists(sp):
    ans = sp.current_user_playlists()
    
    playlists = ans['items']
     
    for p in playlists:
        if p['id'] in managerList.keys():
            continue
        
        if '#TuneEater' in p['name']:
            if p['tracks']['total'] == 0:
                continue
            
            in_id = p['id']
            print('Found new playlist to adopt: %s' % p['name'])
            
            user_ans = sp.me()
            user_id = user_ans['id']
            
            sp.user_playlist_change_details(user_id, in_id, name=p['name'].replace('#TuneEater', '#In'))
            ans = sp.user_playlist_create(user_id, p['name'].replace('#TuneEater', '#Out'), public=False)
            
            #Retrieve the newly generated playlist aswell
            ans = sp.current_user_playlists()
            playlists2 = ans['items']
            
            out_id = None
            for p2 in playlists2:
                if p2['name'] == p['name'].replace('#TuneEater', '#Out'):
                    out_id = p2['id']
                    break
            
            return in_id, out_id
        
        return None, None
            
#handledPlaylists = []
managerList = {}

sp = Authorization.getSpotipy()

if not os.path.isdir('data'):
    os.mkdir('data')
    
## TODO load and save data.
folders = os.listdir('data')

for fold in folders:
    newManager = pm.load_PlaylistManager(fold, sp)
    managerList[newManager.list_in] = newManager


lastPlaylistCheck = 0 #time.time()
lastObservation = time.time()

observer = SpotifyObserver.SpotifyObserver(sp)

while True:
    if time.time() > lastPlaylistCheck+SEARCH_PLAYLISTS_TIME:
        print('Looking for new playlists')
        in_id, out_id = look_for_new_lists(sp)
        lastPlaylistCheck = time.time()
        
        if in_id is not None:
            #print('%s %s' % (in_id, out_id))
            #Create new manager etc
            managerList[in_id] = pm.init_PlaylistManager(in_id, sp, in_id, out_id) #PlaylistManager(in_id, sp, in_id, out_id)
        
    
    if time.time() > lastObservation+OBSERVE_TIME:
        lastObservation = time.time()
        observ = observer.observe()
        if observ is None or observ['context_type'] != 'playlist' or not observ['context'] in managerList.keys():
            continue
        
        managerList[observ['context']].song_listened(observ)