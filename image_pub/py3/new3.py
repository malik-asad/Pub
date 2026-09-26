from paillier_gmpy2 import *
import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import pandas as pd

img_file= '/home/asad/image_pub/py3/lena512.bmp'
img = cv2.imread(img_file,0)
# Check if image loaded correctly
if img is None:
    print("Error: Image not loaded.")
    exit(1)
height, width = img.shape

def split_into_n_shares(value, n):
    shares = [np.random.randint(0, value+1) for _ in range(n-1)]
    final_share = value - sum(shares)
    shares.append(final_share)
    return shares


priv, pub=generate_keypair(128)
all_enc = np.zeros([height,width], dtype=object)
all_dec = np.zeros([height,width])
for x in range(height):
    for y in range(width):
        cpixel = img[x, y]
        all_enc[x,y]=encrypt(pub, int(cpixel))

# Split each pixel in all_enc into n shares
n = 4  # Number of shares
all_enc_shares = np.empty((height, width, n), dtype=object)

for x in range(height):
    for y in range(width):
        try:
            pixel_val = int(all_enc[x, y])
        except Exception as e:
            print(f"Error converting all_enc[{x},{y}] to int: {e}")
            pixel_val = 0
        # Ensure pixel_val is non-negative for random splitting
        pixel_val = abs(pixel_val)
        shares = split_into_n_shares(pixel_val, n)
        for i in range(n):
            all_enc_shares[x, y, i] = shares[i]

# Usage:
shares = split_into_n_shares(int(all_enc[x, y]), 4)
# shares[0], shares[1], shares[2], shares[3] are your 4 sub-values for pixel (x, y)





