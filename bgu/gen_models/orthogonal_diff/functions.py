import google.generativeai as genai
from PIL import Image
import random
import os
import time
import sys
import torch
import objaverse
import trimesh
import numpy as np
import cv2
import glob
from pytorch3d.io import load_objs_as_meshes
from pytorch3d.structures import Meshes
from pytorch3d.renderer import (
    FoVPerspectiveCameras, 
    look_at_view_transform,
    RasterizationSettings, 
    MeshRenderer, 
    MeshRasterizer,
    SoftPhongShader, 
    TexturesVertex, 
    PointLights
)
from diffusers import AutoencoderKL, UNet2DConditionModel, DDPMScheduler
from transformers import CLIPTextModel, CLIPTokenizer
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from torch.cuda.amp import autocast

# Global variable - device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ===============================================================================
#                                   OLD FUNCTIONS
# ===============================================================================
def generate_toy_prompt_from_image(image_path):
  """
  Takes an image file path, sends it to Gemini, and returns a simple
  text prompt describing the object (specifically tailored for toys).

  Args:
      image_path (str): The path to the image file in Colab.

  Returns:
      str: The generated text prompt.
  """

  model = genai.GenerativeModel('gemini-2.5-flash')

  # 3. Load the Image
  try:
    img = Image.open(image_path)
  except FileNotFoundError:
    return f"Error: Image not found at path: {image_path}"

  # 4. Define the Instruction for Gemini
  # We guide Gemini to be concise and focus on the visual description
  # which matches your goal of training on specific toy descriptions.
  system_instruction = (
      "Analyze this image. "
      "Provide a simple, concise text prompt that describes this object visually. "
      "Focus on shape, color, and material (e.g., 'a wooden toy car with red wheels'). "
      "Do not include background details or filler words."
  )

  # 5. Generate Content
  try:
    response = model.generate_content([system_instruction, img])
    return response.text.strip()
  except Exception as e:
    return f"Error communicating with Gemini: {e}"
  
# generate images

def get_toy_objects(limit=5):
    """
    Fetches a list of UIDs from Objaverse that are likely toys
    using LVIS annotations.
    """
    lvis_annotations = objaverse.load_lvis_annotations()
    
    # Categories that fit your "Toy" project
    toy_categories = ['car', 'truck', 'airplane', 'boat', 'motorcycle', 'ball', 'teddy bear']
    
    selected_uids = []
    for cat in toy_categories:
        if cat in lvis_annotations:
            # Add some objects from this category
            selected_uids.extend(lvis_annotations[cat][:limit])
            
    # Remove duplicates and shuffle
    selected_uids = list(set(selected_uids))
    return selected_uids[:limit]

def render_views_old(mesh_path, output_folder, object_name):
    """
    Loads a mesh, renders 4 views, and saves them.
    STRICT MODE: Skips any object that does not have a texture.
    """

    # 1. Convert GLB to OBJ
    temp_obj_path = f"temp_{object_name}.obj"
    
    try:
        mesh = trimesh.load(mesh_path, force='mesh')
        
        # Center and Scale
        mesh.apply_translation(-mesh.centroid)
        scale = 1.0 / np.max(mesh.extents)
        mesh.apply_scale(scale)
        
        # Export
        mesh.export(temp_obj_path)
    except Exception as e:
        print(f"   Skipping {object_name}: Conversion error. {e}")
        return

    # 2. Load into PyTorch3D
    try:
        pytorch_mesh = load_objs_as_meshes([temp_obj_path], device=device)
    except Exception as e:
        print(f"   Skipping {object_name}: PyTorch3D load error. {e}")
        # Cleanup even if load fails
        if os.path.exists(temp_obj_path): os.remove(temp_obj_path)
        return 

    # --- STRICT CHECK: Skip if no texture ---
    if pytorch_mesh.textures is None:
        print(f"   -> Skipping {object_name}: Object has no texture.")
        # Cleanup
        if os.path.exists(temp_obj_path): os.remove(temp_obj_path)
        return
    # ----------------------------------------

    # 3. Setup Renderer
    dist = 2.5 
    elev = 30.0
    azim_angles = [0, 90, 180, 270]
    
    R, T = look_at_view_transform(dist=dist, elev=elev, azim=azim_angles)
    cameras = FoVPerspectiveCameras(device=device, R=R, T=T)
    
    raster_settings = RasterizationSettings(
        image_size=512, 
        blur_radius=0.0, 
        faces_per_pixel=1
    )
    
    lights = PointLights(device=device, location=[[0.0, 0.0, -3.0]])

    renderer = MeshRenderer(
        rasterizer=MeshRasterizer(cameras=cameras, raster_settings=raster_settings),
        shader=SoftPhongShader(device=device, cameras=cameras, lights=lights)
    )

    # 4. Render
    try:
        images = renderer(pytorch_mesh.extend(4)) # Batch of 4
        
        # 5. Save Images

        # Convert to numpy and standard RGB
        images_np = images.cpu().numpy()
        images_rgb = (images_np[..., :3] * 255).astype(np.uint8)

        # --- GRID LOGIC ---
        # 1. Create Top Row (View 0 + View 1)
        row_top = np.concatenate([images_rgb[0], images_rgb[1]], axis=1)
        
        # 2. Create Bottom Row (View 2 + View 3)
        row_bottom = np.concatenate([images_rgb[2], images_rgb[3]], axis=1)
        
        # 3. Stack Top on top of Bottom
        square_image = np.concatenate([row_top, row_bottom], axis=0)

        save_name = f"{object_name}_combined.jpg"
        cv2.imwrite(os.path.join(output_folder, save_name), cv2.cvtColor(square_image, cv2.COLOR_RGB2BGR))
        
        print(f"   Saved 4 views for {object_name}")
        
    except Exception as e:
        print(f"   Rendering failed for {object_name}: {e}")

    # Final Cleanup
    if os.path.exists(temp_obj_path):
        os.remove(temp_obj_path)
    if os.path.exists(temp_obj_path.replace(".obj", ".mtl")):
        os.remove(temp_obj_path.replace(".obj", ".mtl"))

def combine_images_grid(input_dir, output_dir):
    """
    Reads 4 views of an object and stitches them into a 2x2 Grid.
    Layout:
    [ View 0 ] [ View 1 ]
    [ View 2 ] [ View 3 ]
    """
    
    # 1. Identify Unique Objects
    if not os.path.exists(input_dir):
        print(f"Error: Input folder not found: {input_dir}")
        return

    # Filter for 'view0' to find the unique object names
    all_files = os.listdir(input_dir)
    object_names = [f.split('_view')[0] for f in all_files if '_view0.jpg' in f]
    
    print(f"Found {len(object_names)} objects to combine.")

    # 2. Process Each Object
    for obj_name in object_names:
        images = []
        
        # Load the 4 views
        try:
            for i in range(4):
                img_path = os.path.join(input_dir, f"{obj_name}_view{i}.jpg")
                if os.path.exists(img_path):
                    images.append(Image.open(img_path))
                else:
                    print(f"   Warning: Missing view {i} for {obj_name}")
                    images.append(None)
            
            # Check if we have the first image to determine size
            if images[0] is None:
                continue

            # Get dimensions of one single view
            w, h = images[0].size
            
            # Create a blank canvas (2x width, 2x height)
            combined_image = Image.new('RGB', (w * 2, h * 2))
            
            # Paste images into the 2x2 grid
            # Top-Left
            if images[0]: combined_image.paste(images[0], (0, 0))
            # Top-Right
            if images[1]: combined_image.paste(images[1], (w, 0))
            # Bottom-Left
            if images[2]: combined_image.paste(images[2], (0, h))
            # Bottom-Right
            if images[3]: combined_image.paste(images[3], (w, h))
            
            # Save the result
            save_path = os.path.join(output_dir, f"{obj_name}_combined.jpg")
            combined_image.save(save_path)
            
        except Exception as e:
            print(f"   Error combining {obj_name}: {e}")

    print(f"Done! Combined images saved to: {output_dir}")
# ===============================================================================
# ===============================================================================

# ===============================================================================
#                           Model Management System
# ===============================================================================
def load_stable_diffusion_model():
    model_id = "runwayml/stable-diffusion-v1-5"
    print(f"⏳ Loading SD v1.5 from {model_id}...")
    vae = AutoencoderKL.from_pretrained(model_id, subfolder="vae").to(device)
    tokenizer = CLIPTokenizer.from_pretrained(model_id, subfolder="tokenizer")
    text_encoder = CLIPTextModel.from_pretrained(model_id, subfolder="text_encoder").to(device)
    unet = UNet2DConditionModel.from_pretrained(model_id, subfolder="unet").to(device)
    noise_scheduler = DDPMScheduler.from_pretrained(model_id, subfolder="scheduler")

    vae.requires_grad_(False)
    text_encoder.requires_grad_(False)
    #unet.enable_gradient_checkpointing()
    return vae, tokenizer, text_encoder, unet, noise_scheduler

def save_sd_checkpoint(unet, optimizer, epoch, loss, folder_path, filename="sd_finetune.pth"):
    os.makedirs(folder_path, exist_ok=True)
    full_path = os.path.join(folder_path, filename)
    checkpoint = {
        'epoch': epoch,
        'unet_state_dict': unet.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
    }
    torch.save(checkpoint, full_path)
    print(f"✅ SD Checkpoint saved: {full_path}")

def load_sd_checkpoint(unet, optimizer, folder_path, filename="sd_finetune.pth"):
    full_path = os.path.join(folder_path, filename)
    if os.path.exists(full_path):
        print(f"🔄 Found checkpoint at {full_path}. Loading...")
        checkpoint = torch.load(full_path, map_location=device)
        unet.load_state_dict(checkpoint['unet_state_dict'])
        try:
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        except:
            print("⚠️ Warning: Optimizer state mismatch. Starting fresh optimizer.")
        return checkpoint['epoch'] + 1, checkpoint['loss']
    else:
        print(f"🆕 No checkpoint found. Starting fresh.")
        return 0, None

# --- 2. DATA GENERATION ---
def get_diverse_objects(limit=50):
    lvis_annotations = objaverse.load_lvis_annotations()
    
    # Expanded Category List for Diversity
    categories = [
        'car', 'truck', 'airplane', 'boat', 'motorcycle', # Vehicles
        'chair', 'table', 'sofa', 'bed', 'lamp',          # Furniture
        'bottle', 'cup', 'bowl', 'vase', 'clock',         # Household
        'dog', 'cat', 'horse', 'bird', 'teddy bear',      # Animals/Toys
        'computer', 'keyboard', 'phone', 'camera',        # Tech
        'bag', 'shoe', 'hat', 'helmet'                    # Accessories
    ]
    
    selected_uids = []
    for cat in categories:
        if cat in lvis_annotations:
            # Grab a few from each category
            subset = lvis_annotations[cat]
            random.shuffle(subset) # Shuffle to get variety
            selected_uids.extend(subset[:10]) # Take top 10 from each
            
    # Shuffle the final mix
    random.shuffle(selected_uids)
    return selected_uids[:limit]

def generate_prompt_from_image(image_path):
    # Relies on global genai.configure() in notebook
    model = genai.GenerativeModel('gemini-2.5-flash')
    try:
        img = Image.open(image_path)
    except:
        return "error loading image"

    # Instruction ensures we get a description of the OBJECT, not the 2x2 grid layout
    system_instruction = (
        "This is a 2x2 grid showing 4 views of a single 3D object. "
        "Describe the object itself (shape, color, material, style). "
        "Do NOT mention the grid, the views, or the background. "
        "Start directly with the description (e.g., 'A red vintage race car...')."
    )

    try:
        response = model.generate_content([system_instruction, img], request_options={'timeout': 30})
        return response.text.strip()
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "a 3d object"

def render_views(mesh_path, output_folder, object_name):
    # 1. Convert
    temp_obj_path = f"temp_{object_name}.obj"
    try:
        mesh = trimesh.load(mesh_path, force='mesh')
        mesh.apply_translation(-mesh.centroid)
        scale = 1.0 / np.max(mesh.extents)
        mesh.apply_scale(scale)
        mesh.export(temp_obj_path)
    except:
        return False

    # 2. Load
    try:
        pytorch_mesh = load_objs_as_meshes([temp_obj_path], device=device)
    except:
        if os.path.exists(temp_obj_path): os.remove(temp_obj_path)
        return False

    # 3. Check Texture
    if pytorch_mesh.textures is None:
        if os.path.exists(temp_obj_path): os.remove(temp_obj_path)
        return False

    # 4. Render Setup
    dist = 2.5; elev = 30.0; azim_angles = [0, 90, 180, 270]
    R, T = look_at_view_transform(dist=dist, elev=elev, azim=azim_angles)
    cameras = FoVPerspectiveCameras(device=device, R=R, T=T)
    raster_settings = RasterizationSettings(image_size=512, blur_radius=0.0, faces_per_pixel=1)
    lights = PointLights(device=device, location=[[0.0, 0.0, -3.0]])
    renderer = MeshRenderer(
        rasterizer=MeshRasterizer(cameras=cameras, raster_settings=raster_settings),
        shader=SoftPhongShader(device=device, cameras=cameras, lights=lights)
    )

    # 5. Render & Combine
    try:
        images = renderer(pytorch_mesh.extend(4))
        images_np = images.cpu().numpy()
        images_rgb = (images_np[..., :3] * 255).astype(np.uint8)

        # 2x2 Grid Logic
        row_top = np.concatenate([images_rgb[0], images_rgb[1]], axis=1)
        row_bottom = np.concatenate([images_rgb[2], images_rgb[3]], axis=1)
        square_image = np.concatenate([row_top, row_bottom], axis=0)

        save_name = f"{object_name}_combined.jpg"
        cv2.imwrite(os.path.join(output_folder, save_name), cv2.cvtColor(square_image, cv2.COLOR_RGB2BGR))
    except:
        if os.path.exists(temp_obj_path): os.remove(temp_obj_path)
        return False

    if os.path.exists(temp_obj_path): os.remove(temp_obj_path)
    if os.path.exists(temp_obj_path.replace(".obj", ".mtl")): os.remove(temp_obj_path.replace(".obj", ".mtl"))
    return True

# --- 3. TRAINING ---
# Dataset class
class MultiViewDataset(Dataset):
    def __init__(self, image_paths, prompts, tokenizer):
        self.image_paths = image_paths
        self.prompts = prompts
        self.tokenizer = tokenizer
        
        self.transform = transforms.Compose([
            transforms.Resize((512, 512)), 
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5]) 
        ])

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img = Image.open(self.image_paths[idx]).convert("RGB")
        pixel_values = self.transform(img)

        prompt = self.prompts[idx]
        tokens = self.tokenizer(
            prompt, padding="max_length", truncation=True, max_length=self.tokenizer.model_max_length, return_tensors="pt"
        ).input_ids[0]

        return {"pixel_values": pixel_values, "input_ids": tokens}

# Train step function
def train_batch(batch, unet, vae, text_encoder, noise_scheduler, optimizer):
    unet.train()
    
    # Use global 'device' defined at top of this file
    pixel_values = batch["pixel_values"].to(device)
    input_ids = batch["input_ids"].to(device)
    
    # --- MEMORY OPTIMIZATION START ---
    # We use 'autocast' to run the heavy math in 16-bit precision
    #with autocast(dtype=torch.float16):
        
    # 1. Encode Image to Latents (VAE)
    with torch.no_grad():
        latents = vae.encode(pixel_values).latent_dist.sample()
        latents = latents * 0.18215

    # 2. Encode Text to Embeddings (CLIP)
    with torch.no_grad():
        encoder_hidden_states = text_encoder(input_ids)[0]

    # 3. Add Noise
    noise = torch.randn_like(latents)
    bsz = latents.shape[0]
    timesteps = torch.randint(0, noise_scheduler.config.num_train_timesteps, (bsz,), device=device).long()
    
    noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

    # 4. Predict the Noise
    noise_pred = unet(noisy_latents, timesteps, encoder_hidden_states).sample

    # 5. Calculate Loss
    loss = torch.nn.functional.mse_loss(noise_pred, noise)
    # --- MEMORY OPTIMIZATION END ---

    optimizer.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(unet.parameters(), 1.0)
    optimizer.step()

    return loss.item()
