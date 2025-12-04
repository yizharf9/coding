import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from IPython.display import HTML
import os

class game_of_life_simulator():
    
    def __init__(
        self,
        init_board = None, 
        activation_function = None,
        length=100,
        width=100,
        kernel = None
        ):
        if init_board is None : 
            self.board = np.random.rand(int(length),int(width)) <= 0.5
        else :
            self.board = init_board
            
        if kernel is None:
            self.kernel = np.array(
                [
                    [1,1,1],
                    [1,0,1],
                    [1,1,1],
                ]
            )
        
        if activation_function is None:
            def act(activation,current_state):
                if current_state and activation == 2 or activation == 3 :
                    return True
                elif not current_state and activation == 3 :
                    return True
                else:
                    return False
                
            self.activation_function = act
        else :
            self.activation_function = activation_function
    
    def get_next_state(self,current_pixel):
        x,y = current_pixel
        current_state = self.board[x,y]
        l,h = self.kernel.shape
        padded_board = np.pad(self.board,(l//2,h//2))
        x_start = x-l//2+1
        x_end = x+l-l//2+1
        y_start = y-h//2+1
        y_end = y+h-h//2+1
        # print(x_start,x_end)
        # print(y_start,y_end)
        # print(padded_board)
        # print(self.board)
        # print(padded_board[x_start:x_end,y_start:y_end])
        activation = np.sum (padded_board[x_start:x_end,y_start:y_end] * self.kernel)
        return self.activation_function(activation,current_state)
    
    def get_next_board_state(self):
        next_board = np.zeros_like(self.board)
        N,M = self.board.shape
        
        for i in range(N): 
            for j in range(M):
                
                next_pixel_state = self.get_next_state((i,j))
                next_board[i,j] = next_pixel_state
        self.board = next_board 
    
    def show_board(self):
        plt.imshow(self.board,cmap="binary")
        plt.show()

    def create_life_sequence(self, iterations = 100):
        images_path = "game_of_life_images"
        if not os.path.exists(images_path):
            os.makedirs(images_path)
        
        # Clear existing images
        for file in os.listdir(images_path):
            if file.endswith(".png"):
                os.remove(os.path.join(images_path, file))
        
        for i in range(iterations):
            # Save current state
            plt.imsave(
                os.path.join(images_path, f'frame_{i:03d}.png'), 
                self.board,
                cmap='binary'
            )
            # Update board for next iteration
            self.get_next_board_state()
    
    def animate_picture_array(self,images_folder_dir,image_titles=None, interval=50, repeat_delay=1000):
        if not images_folder_dir:
            print("Warning: The image list is empty. No animation will be created.")
            return None
        
        images_dirs = []
        images_folder_dir = os.path.abspath(images_folder_dir)
        for image_dir in os.listdir(images_folder_dir):
            if image_dir.endswith(".png"):
                images_dirs.append(image_dir)
        images_dirs.sort()

        if image_titles is None:
            image_titles = [i for i in range(len(images_dirs))]

        images = [plt.imshow(plt.imread(os.path.join(images_folder_dir,images_dir))) for images_dir in images_dirs]
        plt.close()

        fig = images[0].figure

        artist_list = [[img] for img in images]

        anim = animation.ArtistAnimation(
                                            fig,
                                            artist_list,
                                            interval=interval,
                                            repeat_delay=repeat_delay,
                                            blit=True
                                        )

        plt.close(fig)

        return HTML(anim.to_jshtml())
    
    def play_animation(self,images_folder_dir, interval=300, save_path=None, repeat_delay=1000, dpi=200):
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


init_board = np.array(
    [
        [0,0,0,0,0],
        [0,1,1,1,0],
        [0,0,1,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
    ]
)
iterations = 30
G = game_of_life_simulator()
G.create_life_sequence(iterations=iterations)
# G.animate_picture_array("game_of_life_images")
G.play_animation("./game_of_life_images",interval=100)