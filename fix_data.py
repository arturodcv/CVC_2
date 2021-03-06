#!/usr/bin/env python3

import numpy as np
import math
import pandas as pd
import os
import time
from glob import glob
import shutil
#from tqdm import tqdm
import pickle

from nest_values import *
from funciones   import *


#import datatable as dt

############################################################ Move Files #######################################################################

create_folder(sd_path); #remove_contents(sd_path)
create_folder(df_folder); #remove_contents(df_folder)
create_folder(positions_path); #remove_contents(positions_path)

files = glob('*spike_detector*')
for file in files:
    shutil.move(file, sd_path + '/' + file)

files = glob('*positions-*')
for file in files:
    shutil.move(file, positions_path + '/' + file)
    
########################################################### Read files ###################################################################
files = glob(positions_path + '/*')
pos = []
for file in files:
    positions = pd.read_table(file,names = ['Number','x_pos','y_pos'], index_col=False, sep = ' ')
    pos.append(positions)

positions = pd.concat(pos)
del(pos)
positions.to_pickle('positions_.pkl')

#########################

dist =  0.1
select = radius
d = dist*select

x_pos = positions["x_pos"]
y_pos = positions["y_pos"]
if radius < math.sqrt(2) * num_hipercolumns * 50:
    positions = positions.loc[(x_pos**2 + y_pos**2  <= d**2) ]

##########################  

layers_to_record = load_dict('to_record_layer')
spike_detectors = load_dict('to_record_sd')


######################################################### To dataframe ###################################################################

print('Fixing the data...')
lengths = []
exc_activity = []
inh_activity = []
total_data = []
exc_data = []
inh_data = []
t = time.time()
spike_detectors = list(spike_detectors.values())
for layer, spk in zip(layers_to_record,spike_detectors):
    data = []
    num_layer = layers_to_record[layer][0]
    files = glob('spk_detectors_folder/spike_detector-' + str(spk[0]) + '-*')
    if files == []:
        files = glob('spk_detectors_folder/spike_detector-' + '0' + str(spk[0]) + '-*')

    for spk_detector in files:
        t = time.time()
        df = pd.read_table(spk_detector,names = ['Number','Time'], index_col=False)
        data.append(df)

    data = pd.concat(data)
    data = data.set_index(([pd.Index([i for i in range(0,len(data))])]))
    data['Number'] = data.Number.astype(float)
    data = pd.merge(data,positions,how = 'left',on = 'Number' )
    data.dropna(subset = ["x_pos","y_pos"], inplace=True) 
    
    if layer[2:5] == 'exc':
        exc_data.append(data)
        exc_activity.append(len(data))
    else: 
        inh_activity.append(len(data))
        inh_data.append(data)
    total_data.append(data)
   
    data.to_pickle(df_folder + '/data_' + str(layer) +'.pkl')
    
    lengths.append(len(data))
    del(data)

total_data = pd.concat(total_data)
total_data.to_pickle(df_folder + '/data_total_.pkl')
exc_data = pd.concat(exc_data)
exc_data.to_pickle(df_folder + '/data_exc_.pkl')
inh_data = pd.concat(inh_data)
inh_data.to_pickle(df_folder + '/data_inh_.pkl')

del(positions); del(total_data)

print('Tiempo tratamiento de datos: '+str(np.around(time.time() - t)) + ' s')


print("\nExc / Inh / Total number of spikes: ", sum(exc_activity), sum(inh_activity), sum(lengths)); print("\n")





