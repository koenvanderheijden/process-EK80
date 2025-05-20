#!/bin/bash

#SBATCH --job-name process_EK80   ## Name of the job
#SBATCH --output ./reports/slurm-%j.out   ## Name of the output-script (%j will be replaced with job number)
#SBATCH --account nn11029K   ## The billed account

#SBATCH --partition=preproc
#SBATCH --time=11:00:00   ## Walltime of the job
#SBATCH --nodes=1   ## Number of nodes that will be allocated
#SBATCH --ntasks-per-node=1   ## Number of tasks per node
#SBATCH --cpus-per-task=1
#SBATCH --mem=800GB
#SBATCH --exclusive

set -o errexit   ## Exit the script on any error
set -o nounset   ## Treat any unset variables as an error

   ## Command to be run

module load JupyterLab/4.2.0-GCCcore-13.2.0
python process_EK80.py
