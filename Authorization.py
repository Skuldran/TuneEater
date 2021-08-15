# -*- coding: utf-8 -*-
"""
Created on Sat Aug 14 14:46:40 2021

@author: Axel
"""
import os
import json

import spotipy
from spotipy.oauth2 import SpotifyOAuth

def getSpotipy():
    
    if os.path.isfile('userdata.json'):
        with open('userdata.json', 'r') as fp:
            userdatadict = json.load(fp)
            
    else:
        client_id = input('Enter your client id: ')
        client_secret = input('Enter your client secret id: ')
        redirect_uri = input('Enter your redirect uri: ')
        
        userdatadict = {'SPOTIPY_CLIENT_ID': client_id, 'SPOTIPY_CLIENT_SECRET': client_secret, 'SPOTIPY_REDIRECT_URI': redirect_uri}
        
        with open('userdata.json', 'w') as fp:
            json.dump(userdatadict, fp)
            
    for k in userdatadict.keys():
        os.environ[k] = userdatadict[k]

    scopes = 'user-read-currently-playing, user-read-playback-state, user-modify-playback-state, playlist-modify-private, playlist-read-private, user-library-read'
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scopes))
    
    return sp;