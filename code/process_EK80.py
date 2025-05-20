import os
import echopype as ep
import xarray as xr

#############
# 0. SETTINGS

# dir with individual data files
datadir = 'xxx/project/data_raw/'

# dirs for saving files
savedir = 'xxx/project/data_processed/'

edfiles_converted_dir = savedir + 'edfiles_converted/'
edfiles_combined_dir = savedir + 'edfiles_combined/'
Sv_files_dir = savedir + 'Sv_files/'
MVBS_files_dir = savedir + 'MVBS_files/'

subdirs = [edfiles_converted_dir, 
                  edfiles_combined_dir,
                  Sv_files_dir,
                  MVBS_files_dir]

# check if subdirectories exist; if they don't: create them
for subdir in subdirs:
    if os.path.isdir(subdir) == False:
        os.mkdir(subdir)

# chunk size for combining echodata objects
chunk_size = 100

# define sonar type and settings
sonar_model = 'EK80'

sonar_depth_offset = 4.

sonar_waveform_mode = 'CW'
sonar_encode_mode = 'complex'

# define binning intervals
binning_interval_range = '1m'
binning_interval_time = '60s'

##############################################
### 1. READ .raw TO ECHODATA AND SAVE AS .zarr

# get all filenames and sort them in ascending order

all_files = []
for root, _, files in os.walk(datadir):
    for name in files:
        path = os.path.join(root, name)
        all_files.append(path)

# only take the .raw data files
raw_files = []
for file in all_files:
    if '.raw' in file:
        raw_files.append(file)

raw_files.sort()

# read files and convert to EchoData.zarr


for file in raw_files:
    ed = ep.open_raw(file, sonar_model = sonar_model, use_swap = False)
    ed.to_zarr(edfiles_converted_dir, overwrite=True)

#################################
### 2. COMBINE CHUNKS OF ECHODATA

# read in converted files 
converted_files = os.listdir(edfiles_converted_dir)
converted_files.sort()

# create chunks out of the converted files
chunked_converted_files = [converted_files[i:i + chunk_size] for i in range(0, len(converted_files), chunk_size)]

# create a combined EchoData object for every chunk
dates_times = []

for i, chunk in enumerate(chunked_converted_files):
    ed_list_chunk = []
    for j, file in enumerate(chunk):
        # extract date, time of first file in every chunk for saving later 
        if j == 0:
            first_file = file
            date_time = first_file[-21:-5]
            dates_times.append(date_time)

        # read in every file and append to list
        ed = ep.open_converted(edfiles_converted_dir + file)
        ed_list_chunk.append(ed)

    # combine and save to .zarr
    ed_combined = ep.combine_echodata(ed_list_chunk)   
    ed_combined.to_zarr(edfiles_combined_dir + f'ed_combined_{dates_times[i]}.zarr', overwrite=True)

#################
### 3. COMPUTE SV

# first compute Sv
combined_files = os.listdir(edfiles_combined_dir)
combined_files.sort()

for i, file in enumerate(combined_files):
    ed_combined = ep.open_converted(edfiles_combined_dir + file)

    ed_combined.chunk({'ping_time': 1000, 'range_sample': -1})

    ds_Sv = ep.calibrate.compute_Sv(ed_combined, waveform_mode = sonar_waveform_mode, encode_mode= sonar_encode_mode)
    ds_Sv = ep.consolidate.add_depth(ds_Sv, depth_offset = sonar_depth_offset)

    # save to .zarr and offload computation to disk
    ds_Sv.to_zarr(Sv_files_dir + f'ds_Sv_{dates_times[i]}.zarr', mode='w')

###################
### 4. COMPUTE MVBS
Sv_files = os.listdir(Sv_files_dir)
Sv_files.sort()

for i, file in enumerate(Sv_files):
    ds_Sv = xr.open_dataset(Sv_files_dir + file, engine = 'zarr')

    ds_MVBS = ep.commongrid.compute_MVBS(
        ds_Sv, 
        range_var = 'depth',
        range_bin = binning_interval_range,
        ping_time_bin = binning_interval_time
    )

    ds_MVBS.to_zarr(MVBS_files_dir + f'ds_MVBS_{dates_times[i]}.zarr', mode = 'w')





