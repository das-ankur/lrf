import math

import numpy as np
import torch
import torch_dct as dct
import matplotlib.pyplot as plt

from skimage import data, img_as_float
from skimage.transform import resize, rescale
from einops import rearrange


def mae(image1, image2):
    return np.mean(np.abs(image1 - image2))


def mse(image1, image2):
    return np.mean((image1 - image2) ** 2)


def psnr(image1, image2):
    mse_value = mse(image1, image2)
    if mse_value == 0:
        return float("inf")  # If the MSE is zero, the PSNR is infinite
    max_pixel = np.max(image1)
    psnr_value = 20 * math.log10(max_pixel / math.sqrt(mse_value))
    return psnr_value


def compress_rescale(image, compression_ratio):
    """Compress the image using resizing."""
    scale = compression_ratio**-0.5
    scaled_image = rescale(image, scale, channel_axis=2)
    rescaled_image = resize(scaled_image, image.shape)
    return rescaled_image


def compress_dct(image, compression_ratio):
    """Compress the image using SVD."""
    image = torch.tensor(image, dtype=torch.float32).permute(-1, 0, 1)
    M, N = image.shape[-2:]

    dct_image = dct.dct_2d(image)

    # Keep only a certain number of low-frequency components
    R = math.floor(math.sqrt(M * N / compression_ratio))
    mask = torch.zeros_like(dct_image)
    mask[:, :R, :R] = 1  # Keep top-left corner according to R
    compressed_dct_image = dct_image * mask
    reconstructed = dct.idct_2d(compressed_dct_image)
    return torch.clip(reconstructed, 0, 1).permute(1, 2, 0).to(torch.float64).numpy()


def compress_dct_patches(image, compression_ratio, patch_size=8):
    """Compress the image using DCT on patches."""
    image = torch.tensor(image, dtype=torch.float32).permute(-1, 0, 1)

    *_, H, W = image.shape

    # Rearrange image to form 8x8 patches
    patches = rearrange(
        image, "c (h p1) (w p2) -> c (h w) p1 p2", p1=patch_size, p2=patch_size
    )

    # Apply DCT to each patch
    dct_patches = dct.dct_2d(patches)

    # Keep only a certain number of low-frequency components
    R = math.floor(math.sqrt(patch_size * patch_size / compression_ratio))
    mask = torch.zeros_like(dct_patches)
    mask[:, :, :R, :R] = 1  # Keep top-left corner according to R
    compressed_dct_patches = dct_patches * mask

    # Apply IDCT to reconstruct the patches
    reconstructed_patches = dct.idct_2d(compressed_dct_patches)

    # Rearrange compressed patches back to image format
    reconstructed_image = rearrange(
        reconstructed_patches,
        "c (h w) p1 p2 -> c (h p1) (w p2)",
        h=H // patch_size,
        w=W // patch_size,
    )
    return (
        torch.clip(reconstructed_image, 0, 1).permute(1, 2, 0).to(torch.float64).numpy()
    )


def compress_svd(image, compression_ratio):
    """Compress the image using SVD."""
    image = torch.tensor(image, dtype=torch.float32).permute(-1, 0, 1)
    M, N = image.shape[-2:]
    R = math.floor(M * N // (compression_ratio * (M + N)))
    U, S, Vt = torch.linalg.svd(image, full_matrices=False)
    reconstructed = U[:, :, :R] @ torch.diag_embed(S[:, :R]) @ Vt[:, :R, :]
    return torch.clip(reconstructed, 0, 1).permute(1, 2, 0).to(torch.float64).numpy()


def compress_svd_patches(image, compression_ratio, patch_size=8):
    """Compress the image using SVD on patches."""
    image = torch.tensor(image, dtype=torch.float32).permute(-1, 0, 1)

    # Rearrange image to form columns of flattened patches
    patches = rearrange(
        image, "c (h p1) (w p2) -> (h w) (c p1 p2)", p1=patch_size, p2=patch_size
    )

    M, N = patches.shape[-2:]
    R = math.floor(M * N // (compression_ratio * (M + N)))

    U, S, Vt = torch.linalg.svd(patches, full_matrices=False)
    reconstructed_patches = U[:, :R] @ torch.diag_embed(S[:R]) @ Vt[:R, :]

    # Rearrange compressed patches back to image format
    reconstructed_image = rearrange(
        reconstructed_patches,
        "(h w) (c p1 p2) -> c (h p1) (w p2)",
        p1=patch_size,
        p2=patch_size,
        h=image.shape[1] // patch_size,
    )
    return (
        torch.clip(reconstructed_image, 0, 1).permute(1, 2, 0).to(torch.float64).numpy()
    )


# Load the astronaut image
image = data.astronaut()

# Convert the image to float and resize
image = img_as_float(image)
image = resize(image, (224, 224), preserve_range=True)

plt.imshow(image)
plt.axis("off")
plt.title("Astronaut Image")
plt.show()


# Compression ratios to be used
compression_ratios = np.arange(1, 20.5, 1.5)

# Store MAE and compressed images for each method and compression ratio
err_values = {
    "Rescale": [],
    "DCT": [],
    "DCT Patches": [],
    "SVD": [],
    "SVD Patches": [],
}
compressed_images = {
    "Rescale": [],
    "DCT": [],
    "DCT Patches": [],
    "SVD": [],
    "SVD Patches": [],
}

# Calculate MAE and compressed images for each method and compression ratio
for ratio in compression_ratios:
    # Rescale
    compressed_rescale = compress_rescale(image, ratio)
    err_values["Rescale"].append(mae(image, compressed_rescale))
    compressed_images["Rescale"].append(compressed_rescale)

    # DCT
    compressed_dct = compress_dct(image, ratio)
    err_values["DCT"].append(mae(image, compressed_dct))
    compressed_images["DCT"].append(compressed_dct)

    # DCT Patches
    compressed_dct_patches = compress_dct_patches(image, ratio)
    err_values["DCT Patches"].append(mae(image, compressed_dct_patches))
    compressed_images["DCT Patches"].append(compressed_dct_patches)

    # SVD
    compressed_svd = compress_svd(image, ratio)
    err_values["SVD"].append(mae(image, compressed_svd))
    compressed_images["SVD"].append(compressed_svd)

    # SVD Patches
    compressed_svd_patches = compress_svd_patches(image, ratio)
    err_values["SVD Patches"].append(mae(image, compressed_svd_patches))
    compressed_images["SVD Patches"].append(compressed_svd_patches)


# Plotting the results
plt.figure(figsize=(10, 7))
for method, err in err_values.items():
    plt.plot(compression_ratios, err, marker="o", label=method)

plt.xlabel("Compression Ratio")
plt.ylabel("MAE")
plt.title("Comprison of Different Compression Methods")
plt.xticks(np.arange(compression_ratios.min(), compression_ratios.max() + 1))
plt.legend()
plt.grid()
plt.savefig("experiments/comparison_of_compression_methods.pdf", format="pdf", dpi=600)
plt.show()


# Plotting the compressed images for each method and compression ratio
fig, axs = plt.subplots(
    len(compression_ratios),
    len(err_values),
    figsize=(2 * len(err_values), 2 * len(compression_ratios)),
)

# Setting titles for columns
for ax, method in zip(axs[0], err_values.keys()):
    ax.set_title(method)

# Setting labels for rows
for ax, ratio in zip(axs[:, 0], compression_ratios):
    ax.set_ylabel(f"Ratio {ratio}", rotation=90, size="large")

for i, ratio in enumerate(compression_ratios):
    for j, method in enumerate(err_values.keys()):
        compressed_image = compressed_images[method][i]
        axs[i, j].imshow(compressed_image)
        axs[i, j].axis("off")

plt.tight_layout()
plt.show()
