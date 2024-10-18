# create_dataset.py
import os
from PIL import Image
import numpy as np

def create_dataset():
    for split in ['train', 'test']:
        for cls in ['class1', 'class2']:
            dir_path = f'/data/dataset/{split}/{cls}'
            os.makedirs(dir_path, exist_ok=True)
            for i in range(1, 3):
                img = Image.fromarray(np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8), 'RGB')
                img.save(f'{dir_path}/image{i}.jpg')

if __name__ == '__main__':
    create_dataset()
