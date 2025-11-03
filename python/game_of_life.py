import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from IPython.display import HTML
import os
            

def pixel_state(pixel,board):
    total_neighbors_alive = 0
    x,y = pixel
    for i in range(-1,2):
        for j in range(-1,2):
            if i == 0 and j == 0 : 
                continue
            # print(x+i,y+j)
            if board[x+i,y+j] == 1 :
                total_neighbors_alive +=1
                # print("hit")
    
    if total_neighbors_alive == 2 or total_neighbors_alive == 3  :
        return True
    return False

def remamp_board(board):
    N,M = board.shape
    padded_board = np.pad(board,1)
    for i in range(N):
        for j in range(M):
            new_state = pixel_state((i+1,j+1),padded_board)
            board[i,j] = 1 if new_state else 0
    return board

def animate_picture_array(images_folder_dir,image_titles=None, interval=50, repeat_delay=1000):

    """Creates an animation from a list of Matplotlib image artists.
    This function is designed to be used in a Jupyter/IPython notebook
    environment to display the animation inline.

    Args:
        images: A list of Matplotlib image artists (e.g., the objects
                returned by `hci.imshow_field` or `plt.imshow`).
        interval: Delay between frames in milliseconds.
        repeat_delay: Delay in milliseconds before repeating the animation.

    Returns:
        An IPython.display.HTML object for displaying the animation.
    """

    if not images_folder_dir:
        print("Warning: The image list is empty. No animation will be created.")
        return None

    images_dirs = []
    for image_dir in os.listdir(images_folder_dir):
        if image_dir.endswith(".png"):
            images_dirs.append(image_dir)
    images_dirs.sort()

    if image_titles is None:
        image_titles = [i for i in range(len(images_dirs))]

    images = [plt.imshow(plt.imread(os.path.join(images_folder_dir,images_dir))) for images_dir in images_dirs]
    plt.close()

    # Get the figure from the first image artist in the list
    fig = images[0].figure

    # ArtistAnimation requires a list of lists, where each inner list is a frame.
    # We'll wrap each of our images in its own list to create the frames.
    artist_list = [[img] for img in images]

    # Create the animation
    anim = animation.ArtistAnimation(
                                        fig,
                                        artist_list,
                                        interval=interval,
                                        repeat_delay=repeat_delay,
                                        blit=True
                                    )

    # Close the static figure to prevent it from displaying
    plt.close(fig)

    # Return the animation as an HTML5 video
    return HTML(anim.to_jshtml())

def create_life_sequence(board = np.random.rand()>0.5, iterations = 100):
    images_path = "game_of_life_images"
    if not os.path.exists(images_path):
        os.makedirs(images_path)
    
    # Clear existing images
    for file in os.listdir(images_path):
        if file.endswith(".png"):
            os.remove(os.path.join(images_path, file))
    
    current_board = board.copy()
    for i in range(iterations):
        # Save current state
        plt.imsave(
            os.path.join(images_path, f'frame_{i:03d}.png'), 
            current_board,
            cmap='binary'
        )
        # Update board for next iteration
        current_board = remamp_board(current_board.copy())

def play_animation(images_folder_dir, interval=300, save_path=None, repeat_delay=1000, dpi=200):
    """Play an animation from saved PNG frames in a regular Python script.

    If `save_path` is provided (e.g. 'anim.mp4'), the function will try to
    save the animation to that file (requires ffmpeg or another writer).
    Otherwise it will open a matplotlib window and play the animation.
    """
    images_dirs = sorted([f for f in os.listdir(images_folder_dir) if f.endswith('.png')])
    if not images_dirs:
        print(f"No PNG frames found in '{images_folder_dir}'")
        return None

    fig = plt.figure()
    plt.axis('off')
    frames = []
    for img_name in images_dirs:
        img = plt.imread(os.path.join(images_folder_dir, img_name))
        im = plt.imshow(img, animated=True, cmap='binary')
        frames.append([im])

    anim = animation.ArtistAnimation(
        fig,
        frames,
        interval=interval,
        repeat_delay=repeat_delay,
        blit=True,
    )

    if save_path:
        try:
            anim.save(save_path, dpi=dpi)
            print(f"Saved animation to {save_path}")
        except Exception as e:
            print("Failed to save animation:", e)
            print("You may need ffmpeg installed and available on PATH to save MP4 files.")
    else:
        plt.show()


N = 100
p = 0.005
iterations = 50
# np.random.seed(42)
init_board = np.random.rand(N,N) 
init_board = (init_board<p)

create_life_sequence(init_board,iterations=iterations)

play_animation("./game_of_life_images", interval=100)
