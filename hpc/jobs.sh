cd $VSC_DATA/scripts/lsvd/hpc

sbatch --job-name=cifar10_resnet --clusters=genius --nodes=1 --ntasks=18 --gpus-per-node=2 --time=30:00 --partition=gpu_p100 --mem-per-cpu=5gb --export=date=cifar10,model=resnet,metric=cifar10 train.slurm


cd $VSC_DATA/scripts/lsvd/outputs

tensorboard --logdir=.  --port=6006