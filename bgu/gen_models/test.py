import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from torch.nn import functional as F
import os

# --- Configuration and Hyperparameters ---
EPOCHS = 10
BATCH_SIZE = 128
LEARNING_RATE = 1e-4
LATENT_DIM = 128
IMAGE_SIZE = 32
CHANNELS = 3
BETA = 1.0 # Weight for KL divergence (Beta-VAE concept, 1.0 is standard VAE)

# Determine the device to use (GPU if available, otherwise CPU)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")

# --- VAE Model Definition ---

class VAE(nn.Module):
    def __init__(self, latent_dim=LATENT_DIM):
        super(VAE, self).__init__()
        self.latent_dim = latent_dim
        
        # 1. Encoder (P(z|x)) - Maps image to latent distribution parameters (mu and log_var)
        self.encoder = nn.Sequential(
            # Input: 3 x 32 x 32 (CIFAR-10)
            nn.Conv2d(CHANNELS, 32, kernel_size=4, stride=2, padding=1), # 32 x 16 x 16
            nn.BatchNorm2d(32),
            nn.LeakyReLU(0.2),

            nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=1), # 64 x 8 x 8
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2),

            nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1), # 128 x 4 x 4
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2),
            
            # Flatten to vector
            nn.Flatten()
        )
        
        # Calculate the size after convolution (128 * 4 * 4 = 2048)
        self.flat_size = 128 * (IMAGE_SIZE // 8) * (IMAGE_SIZE // 8) # 2048 for 32x32
        
        # Latent variables layers
        self.fc_mu = nn.Linear(self.flat_size, latent_dim)
        self.fc_logvar = nn.Linear(self.flat_size, latent_dim)

        # 2. Decoder (P(x|z)) - Maps latent vector to image
        self.fc_decode = nn.Linear(latent_dim, self.flat_size)
        
        self.decoder = nn.Sequential(
            # Reshape: 128 x 4 x 4
            
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1), # 64 x 8 x 8
            nn.BatchNorm2d(64),
            nn.ReLU(),
            
            nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1), # 32 x 16 x 16
            nn.BatchNorm2d(32),
            nn.ReLU(),
            
            # Output: 3 x 32 x 32 (Sigmoid activation for pixel values [0, 1])
            nn.ConvTranspose2d(32, CHANNELS, kernel_size=4, stride=2, padding=1), # 3 x 32 x 32
            nn.Sigmoid() # To output pixel values between 0 and 1
        )

    def reparameterize(self, mu, logvar):
        """
        Reparameterization trick: z = mu + std * epsilon, where epsilon ~ N(0, I)
        """
        # Calculate standard deviation (std = exp(0.5 * logvar))
        std = torch.exp(0.5 * logvar)
        # Sample epsilon from standard normal distribution
        eps = torch.randn_like(std)
        # Return the latent sample z
        return mu + eps * std

    def forward(self, x):
        # 1. Encode
        encoded = self.encoder(x)
        mu = self.fc_mu(encoded)
        logvar = self.fc_logvar(encoded)
        
        # 2. Reparameterize (sample z)
        z = self.reparameterize(mu, logvar)
        
        # 3. Decode
        decoded = self.fc_decode(z)
        # Reshape to 4x4 feature map
        decoded = decoded.view(-1, 128, IMAGE_SIZE // 8, IMAGE_SIZE // 8)
        reconstruction = self.decoder(decoded)
        
        return reconstruction, mu, logvar
    
    @torch.no_grad()
    def generate_samples(self, num_samples=1, z=None):
        """
        Generates images by decoding latent vectors.
        
        Args:
            num_samples (int): The number of images to generate (ignored if z is provided).
            z (torch.Tensor, optional): A batch of latent vectors (shape [N, LATENT_DIM]).
            If None, vectors are sampled from the standard Gaussian prior P(z).
        
        Returns:
            torch.Tensor: A batch of generated images (shape [N, C, H, W]).
        """
        
        # Use the same device as the model parameters
        model_device = next(self.parameters()).device
        
        if z is None:
            # Generate random latent vectors if none are provided
            z = torch.randn(num_samples, self.latent_dim).to(model_device)
        else:
            # Ensure the input latent vector is on the correct device
            z = z.to(model_device)
        
        # Decode the latent vector(s)
        decoded = self.fc_decode(z)
        
        # Reshape to 4x4 feature map. The first dimension is batch size
        decoded = decoded.view(-1, 128, IMAGE_SIZE // 8, IMAGE_SIZE // 8)
        
        # Pass through the convolutional decoder layers
        generated_images = self.decoder(decoded)
        
        return generated_images

    def load_weights(self, filepath):
        """
        Loads the model parameters from a PyTorch checkpoint file (.pth) or attempts to handle .npz.
        
        Args:
            filepath (str): Path to the saved model file.
        """
        model_device = next(self.parameters()).device
        
        if filepath.endswith('.pth'):
            try:
                # Load the state dictionary, mapping storage to the current device
                state_dict = torch.load(filepath, map_location=model_device)
                self.load_state_dict(state_dict)
                print(f"Successfully loaded VAE weights from {filepath} onto {model_device}.")
            except FileNotFoundError:
                print(f"Error: Checkpoint file not found at {filepath}.")
            except Exception as e:
                print(f"Error loading PyTorch state dict: {e}")
        elif filepath.endswith('.npz'):
            print("Note: Loading from a raw .npz file is non-standard for PyTorch model weights.")
            print("This requires manual loading of NumPy arrays and mapping them to PyTorch layers, which is highly specific.")
            print("Please use a PyTorch `.pth` checkpoint file for reliable parameter loading.")
        else:
            print(f"Unsupported file format for loading weights: {filepath}. Please use a .pth file.")


# --- VAE Loss Function (ELBO) ---

def vae_loss(recon_x, x, mu, logvar):
    """
    Calculates the Evidence Lower Bound (ELBO) loss.
    ELBO = Reconstruction Loss + KL Divergence Loss
    """
    # 1. Reconstruction Loss (E_q(z|x) [log P(x|z)])
    # Use Binary Cross-Entropy (BCE) for image reconstruction loss, 
    # which is common for VAEs with Sigmoid output. 
    
    # Flatten the image for BCE calculation
    BCE = F.binary_cross_entropy(recon_x.view(-1, CHANNELS * IMAGE_SIZE * IMAGE_SIZE), 
                                 x.view(-1, CHANNELS * IMAGE_SIZE * IMAGE_SIZE), 
                                 reduction='sum')

    # 2. KL Divergence Loss (D_KL(Q(z|x) || P(z)))
    # Analytic KL divergence between N(mu, exp(logvar)) and N(0, 1)
    # Formula: 0.5 * sum(1 + logvar - mu^2 - exp(logvar))
    KL_Divergence = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    
    # Total loss (Negative ELBO)
    # We use 'sum' reduction for both, so we divide by batch size for averaging
    return (BCE + BETA * KL_Divergence) / x.size(0)

# --- Data Loading and Preprocessing ---

def get_data_loaders():
    # Define transformations: Convert to tensor and normalize to [0, 1] for VAE
    transform = transforms.Compose([
        transforms.ToTensor(), # Converts image to Tensor, scales to [0.0, 1.0]
        # CIFAR-10 is 32x32. No need for resize.
    ])
    
    # Download and load the CIFAR-10 training dataset
    train_dataset = datasets.EMNIST(
        root='./data', 
        train=True, 
        download=True, 
        transform=transform
    )
    
    # # Download and load the CIFAR-10 training dataset
    # train_dataset = datasets.CIFAR10(
    #     root='./data', 
    #     train=True, 
    #     download=True, 
    #     transform=transform
    # )
    
    # Create the data loader
    train_loader = DataLoader(
        train_dataset, 
        batch_size=BATCH_SIZE, 
        shuffle=True, 
        num_workers=os.cpu_count() // 2 if os.cpu_count() else 0, # Use half cores for loading
        pin_memory=True
    )
    
    return train_loader

# --- Training Function ---

def train(model, data_loader, optimizer, epoch):
    model.train()
    total_loss = 0
    
    for batch_idx, (data, _) in enumerate(data_loader):
        # Move data to the specified device
        data = data.to(DEVICE)
        
        # Zero gradients
        optimizer.zero_grad()
        
        # Forward pass
        recon_batch, mu, logvar = model(data)
        
        # Calculate loss
        loss = vae_loss(recon_batch, data, mu, logvar)
        
        # Backward pass and optimization
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()

        if batch_idx % 100 == 0:
            print(f'Train Epoch: {epoch} [{batch_idx * len(data)}/{len(data_loader.dataset)} '
                  f'({100. * batch_idx / len(data_loader):.0f}%)]\tLoss: {loss.item():.6f}')
            
    avg_loss = total_loss / BATCH_SIZE
    print(f'====> Epoch: {epoch} Average loss: {avg_loss:.4f}')

# --- Main Execution ---

if __name__ == '__main__':
    # Initialize model, optimizer, and data
    vae_model = VAE(latent_dim=LATENT_DIM).to(DEVICE)
    vae_optimizer = optim.Adam(vae_model.parameters(), lr=LEARNING_RATE)
    cifar_loader = get_data_loaders()
    
    print("\nStarting training...\n")

    for epoch in range(1, EPOCHS + 1):
        train(vae_model, cifar_loader, vae_optimizer, epoch)
    
    print("\nTraining complete.")
    print(f"Model trained for {EPOCHS} epochs on CIFAR-10.")
    
    # --- Example of saving and loading model weights ---
    # NOTE: Since this is a single, isolated run environment, the save/load
    # logic below is for demonstration and will only work if the file exists.
    
    CHECKPOINT_PATH = 'vae_cifar_checkpoint.pth'
    
    # 1. Save (Demonstration logic)
    # torch.save(vae_model.state_dict(), CHECKPOINT_PATH)
    # print(f"\nModel state dictionary saved to {CHECKPOINT_PATH} (commented out in script).")
    
    # 2. Load (Demonstration logic)
    # If a checkpoint existed, you could load it like this:
    # vae_model_new = VAE(latent_dim=LATENT_DIM).to(DEVICE)
    # vae_model_new.load_weights(CHECKPOINT_PATH) 
    # Example of unsupported format:
    # vae_model.load_weights('model_weights.npz')


    # --- Simple Sampling Example using the new method ---
    
    vae_model.eval()
    with torch.no_grad():
        num_samples_to_generate = 64
        
        # Use the new generate_samples method
        generated_images = vae_model.generate_samples(num_samples=num_samples_to_generate).cpu()
        
        # For demonstration, we'll just print the shape and min/max values.
        print("\n--- Generation Example ---")
        print(f"Generated batch shape: {generated_images.shape}")
        print(f"Generated pixel range (min/max): {generated_images.min():.4f} / {generated_images.max():.4f}")
        print(f"Successfully generated {num_samples_to_generate} images from the latent space.")