#!/bin/bash -l

export PATH="${VSC_DATA}/miniconda3/bin:${PATH}"
source activate deepenv

ROOT_DIR="${VSC_DATA}/projects/lsvd"
cd ${ROOT_DIR}/experiments/studies_over_datasets

TASK_NAME=ablation_patchification_svd

python compression_comparison_over_dataset.py --experiment_name=${TASK_NAME} --selected_methods="SVD" --patchify
echo "patchify true done."

python compression_comparison_over_dataset.py --experiment_name=${TASK_NAME} --selected_methods="SVD" --no-patchify
echo "patchify false done."
