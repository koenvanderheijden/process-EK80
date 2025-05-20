import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates  as mdates

import echopype as ep

datadir = '/cluster/projects/nn11029k/DML_echodata/tt2223_02_DML1_2/'

# get all filenames and sort them in ascending order
all_files = os.listdir(datadir)
all_files.sort()

file = all_files[0] # also checked for idx = -1 and idx = int(len(all_files) / 2); depth is the same 

sonar_model = 'EK80'
ed = ep.open_raw(datadir + file, sonar_model = sonar_model)

#### CALCULATE DEPTH OFFSET
# following https://echopype.readthedocs.io/en/latest/data-proc-additional.html

transducer_offset_z = ed['Platform']['transducer_offset_z']
water_level = ed['Platform']['water_level']
vertical_offset = ed['Platform']['vertical_offset']

transducer_depth_array = transducer_offset_z - water_level - vertical_offset
transducer_depth_array

if np.all(transducer_depth_array == transducer_depth_array[0][0]):
    transducer_depth = transducer_depth_array[0][0].data
    print(f'TRANSDUCER DEPTH = {transducer_depth} m')
else:
    print('TRANSDUCER DEPTH NOT CONSTANT')