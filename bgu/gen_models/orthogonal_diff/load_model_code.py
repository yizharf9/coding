import os
import shutil
import torch
from diffusers import StableDiffusionPipeline

# 1. Detect the best available hardware
if torch.cuda.is_available():
    device = "cuda"
    dtype = torch.float16  # GPU handles float16 well
    print("Using Hardware: NVIDIA GPU (CUDA)")
elif torch.backends.mps.is_available():
    device = "mps"
    dtype = torch.float32  # Mac Metal (MPS) is most stable with float32
    print("Using Hardware: Apple Silicon (MPS)")
else:
    device = "cpu"
    dtype = torch.float32  # CPU requires float32 (float16 is extremely slow or breaks)
    print("Using Hardware: Standard CPU")

# Change cache path to a local temporary directory for more stable downloads
my_cache_path = "/tmp/models_cache"

# Remove corrupted cache if it exists to force a clean download
if os.path.exists(my_cache_path):
    print(f"Removing corrupted cache directory: {my_cache_path}")
    shutil.rmtree(my_cache_path)

# 2. Load the pipeline with the correct precision
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=dtype,        # <--- Dynamic precision (float16 or float32)
    cache_dir=my_cache_path,
    local_files_only=False
)

# 3. Move to the detected device
pipe = pipe.to(device)

# Optional: Enable memory efficiency if on Mac/CPU to prevent crashing
if device != "cuda":
    pipe.enable_attention_slicing()

print(f"Ready to generate images on {device}!")