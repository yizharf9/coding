import os
import glob
import torch
import numpy as np
import matplotlib.pyplot as plt
from test import VAE, LATENT_DIM, DEVICE, get_data_loaders

# Find and load the latest checkpoint
ckpt_dir = './checkpoints'
latest_ckpt = max(glob.glob(os.path.join(ckpt_dir, '*.pth')), key=os.path.getmtime) if os.path.isdir(ckpt_dir) else None

# Instantiate and load model
model = VAE(latent_dim=LATENT_DIM).to(DEVICE)
# model.load_weights("./checkpoints/best_vae_epoch10_loss14.2459.pth")
model.load_weights("./checkpoints/best_vae_epoch10_params.npz")
gen_images = model.generate_samples()
for gen_image in gen_images:
    gen_image = np.array(gen_image*255,dtype=int).transpose((1,2,0))
    # print(gen_image)
    # print(gen_image.shape)
    plt.imshow(gen_image)
    plt.show()
