# -*- coding: utf-8 -*-
"""
Created on Sun Aug 15 22:45:08 2021

@author: Axel
"""
import os

import json
import pandas as pd

def convert_data(folder):
    with open(folder + '//songs.json', 'r') as fp:
        songDict = json.load(fp)
        
        df_songs = pd.DataFrame(songDict.values(), index=songDict.keys())
        df_songs.to_csv(folder + '//songs.csv')

    with open(folder + '//artists.json', 'r') as fp:
        songDict = json.load(fp)
        
        df_songs = pd.DataFrame(songDict.values(), index=songDict.keys())
        df_songs.to_csv(folder + '//artists.csv')

if not os.path.isdir('data'):
    os.mkdir('data')
    
## TODO load and save data.
folders = os.listdir('data')

for fold in folders:
    convert_data('data//' + fold)