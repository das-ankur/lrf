import os
import pickle
import numpy as np
import torch
from torchvision.transforms import v2
from torchvision.datasets import ImageNet, ImageFolder
from torch.utils.data import DataLoader, Subset

from utils.utils import plot_result, calc_compression_metrics, make_result_dir
from utils.configs import parse_args

args = parse_args()      

script_dir = os.path.dirname(os.path.abspath(__file__))
experiment_dir = os.path.join(script_dir, args.experiment_name)
if not os.path.exists(experiment_dir):
    os.makedirs(experiment_dir)

experiment_dir = make_result_dir(experiment_dir, args)

transforms = v2.Compose([v2.ToImage()])

# dataset = ImageNet(root=args.data_dir, split="val", transform=transforms)
dataset = ImageFolder(root=args.data_dir, transform=transforms)
indices = np.arange(5000)
subset = Subset(dataset, indices=indices)
dataloader = DataLoader(subset, batch_size=1, shuffle=False)

# initiating metrics
compression_ratios = {method: [] for method in args.selected_methods}
bpps = {method: [] for method in args.selected_methods}
# reconstructed_images = {method: [] for method in args.selected_methods}
psnr_values = {method: [] for method in args.selected_methods}
ssim_values = {method: [] for method in args.selected_methods}

image_num = len(dataloader)
compression_ratios, bpps, psnr_values, ssim_values = calc_compression_metrics(dataloader, compression_ratios, bpps, psnr_values, ssim_values, args)

# fixing values of bpp for x-axis in the plots
x_axis_fixed_values = np.linspace(0, 1, 50)

# plotting the results: PSNR vs bpp
fig_data_dict = {"xlabel": "bpp", "ylabel": "PSNR (dB)", "title": "Comprison of Different Compression Methods", "xlim": (0,1)}
plot_result(x_values=bpps, y_values=psnr_values, x_axis_fixed_values=x_axis_fixed_values, plot_num=image_num, figure_data=fig_data_dict, save_dir=experiment_dir, file_name="compression_methods_comparison_psnr")

# plotting the results: PSNR vs bpp
fig_data_dict["ylabel"] = "SSIM"
plot_result(x_values=bpps, y_values=ssim_values, x_axis_fixed_values=x_axis_fixed_values, plot_num=image_num, figure_data=fig_data_dict, save_dir=experiment_dir, file_name="compression_methods_comparison_ssim")


# saving the results
save_dict = {
    "compression_ratios": compression_ratios,
    "bpps": bpps,
    "psnr_values" : psnr_values,
    "ssim_values" : ssim_values,
    "x_axis_fixed_values": x_axis_fixed_values
}
with open(os.path.join(experiment_dir, 'results.pkl'), 'wb') as f:
    pickle.dump(save_dict, f)

