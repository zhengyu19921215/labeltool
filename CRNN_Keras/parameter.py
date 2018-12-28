
import os
f1 = open(os.path.abspath(os.path.dirname(__file__))+"/1.txt","r")
character = f1.readlines()
character=''.join(character)
characters=character.replace("\n", "")
letters=str(characters)+' '
num_classes = len(letters) + 1
img_w, img_h = 256, 32

# Network parameters
batch_size =256
val_batch_size = 16

downsample_factor = 4
max_text_len =16