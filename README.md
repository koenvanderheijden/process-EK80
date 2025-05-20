# process-EK80
Documentation on how to process Simrad EK-80 files with the Python package [EchoPype](https://echopype.readthedocs.io/en/latest/). In the implementation here the actual processing is done on the supercomputer [Betzy](https://documentation.sigma2.no/hpc_machines/betzy.html), but for smaller quantities of files this should work on a local computer too.  

**Author**

Koen van der Heijden, koen.heijden [AT] uib.no

**README modified (created)**

20.05.2025 (20.05.2025)

## 0 | Preliminaries
This repo is essentially a wrapper of EchoPype that I use to process large amounts of EK-80 files on Betzy. I'd recommend going through EchoPype's [excellent documentation](https://echopype.readthedocs.io/en/latest/) and [examples](https://echopype-examples.readthedocs.io/en/latest/). The code here is heavily based on particularly [example 4](https://echopype-examples.readthedocs.io/en/latest/krill_freq_diff.html).

The [documentation](https://documentation.sigma2.no/index.html) on Betzy and High Performance Computing in general on the NRIS website is also useful. 

## 1 | Overview
EK-80 echosounders save huge amounts of data in lots of different files that all contain a small part of the time series. ```process_EK80.py``` processes this in the following steps:

1. Find all relevant (```.raw```) files in your data directory
2. Convert all individual ```.raw``` files to ```EchoData``` objects and save them as ```.zarr```.
3. Combine many individual files into larger chunks, and save these chunks as ```.zarr```. The size of these chunks is limited by RAM; I combine individual files into chunks of 100 files (roughly 10 GB).
4. Compute the Volume Backscattering Strenght (Sv) of these chunked files, and save these Sv-files as ```.zarr```.
5. Compute the Mean Volume Backscattering Strength (MVBS), binned averages of Sv across ping time and depth, and save these MVBS-files as ```.zarr```.

The output from each individual step is saved to disk to reduce memory usage and enable lazy loading.

Overall, this process reduces the echo data in size drastically. The total reduction depends on the bin intervals in step 5, but for a depth interval of 1m the size of the final MVBS-file is
- 0.1%  of the original data volume when binned in 5s intervals, and
- 0.01% of the original data volume when binned in 60 second intervals.

So the processed MVBS-files can then be processed and interpreted further on a normal laptop.

## 2 | Running ```process_EK80.py```
The processing file is located in ```code/process_EK80.py```.

### 2.1 | File structure
Under ```0. SETTINGS``` of ```process_EK80.py```, change ```datadir = 'xxx/project/data_raw'``` to the directory that contains all your .raw files. On Betzy, this is usually something like ```'/cluster/projects/nnXXXXX/data_raw/```. ```./data_raw``` can consists of subfolders in which the files are stored (see diagram below).

Also change ```savedir = 'xxx/project/data_processed'``` to the directory where you want to save your processed files. On Betzy, this is usually something like ```/cluster/projects/nnXXXXX/data_processed/``` or ```/cluster/work/users/$USERNAME/project/```. The script ```read_EK80.py``` should automatically create the subdirectories that are necessary.

```
project
└───data_raw
│   └───period1
│   │   │   file111.idx
│   │   │   file111.raw
│   │   │   file112.idx
│   │   │   file112.raw
│   │   │   ...
│   │
│   └───period2
│       │   file211.idx
│       │   file211.raw
│       │   file212.idx
│       │   file212.raw
│       │   ...
│   
└───data_processed
    └───edfiles_converted
    │   │   ...
    │
    └───edfiles_combined
    │   │   ...
    │
    └───Sv_files
    │   │   ...
    │
    └───MVBS_files
        │   ...

```

### 2.2 | Other settings
The other settings under ```0. SETTINGS``` depend on the sonar used. The standard settings are only optimized and tested for the EK-80 data I have worked with, they might be different for other datasets. 

The depth offset can be found in the ```EchoData``` objects. You can use ```code/find_EK80_depth``` to find the depth offset.

### 2.3 | Submitting your script to Betzy 
First make sure you've installed all necessary packages (```EchoPype```, ```xarray```) on your account on Betzy. 

Then, get an [estimate](https://documentation.sigma2.no/jobs/choosing-memory-settings.html#choosing-memory-settings) of the required time and [adjust the jobscript](https://documentation.sigma2.no/jobs/job_scripts/slurm_parameter.html) as needed. 

Once all settings are right, you can submit the script to Betzy (or another Slurm HPC) using jobscript.sh. You do this in the Betzy terminal using

```sbatch jobscript.sh```

and you can then check the progress using

```squeue --me```

The slurm reports are stored in ```code/reports``` (create this folder first).

##### 2.3.1 | Required time

Get an estimate of the required time by only processing one 'chunk' of data and checking the walltime in the associated jobscript.

Estimates from my dataset:
- 110 files (~10 GB): 8.6 minutes
- 6703 files (~670 GB): 10.3 hours 

##### 2.3.2 | Jobscript details
I use the [preprocessing node](https://documentation.sigma2.no/jobs/job_types/betzy_job_types.html#job-types-betzy) (```#SBATCH --partition=preproc```) as this code is not parallelized but uses a lot of memory. I just one node and one CPU, but use almost all the memory of the node using
```
#SBATCH --nodes=1   ## Number of nodes that will be allocated
#SBATCH --ntasks-per-node=1   ## Number of tasks per node
#SBATCH --cpus-per-task=1
#SBATCH --mem=800GB
#SBATCH --exclusive 
```

Which module to load under ```module load JupyterLab/4.2.0-GCCcore-13.2.0``` might depend on your setup.


