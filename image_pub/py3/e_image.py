from paillier_gmpy2 import *
import cv2
from PIL import Image
import numpy as np
import time
import sys
import random

priv, pub = generate_keypair(128)
img_file= '/home/asad/image_pub/py3/lena512.bmp'
img = cv2.imread(img_file,0)
height, width = img.shape
all_pre = np.zeros([height, width])
all_enc = np.zeros([height, width], dtype=object)
all_enc_emb = np.zeros([height, width], dtype=object)
dest = np.zeros([height, width])
all_dec = np.zeros([height, width])
Re_img = np.zeros([height, width])
count = 0
all_pre = img.copy()

# image preprocessing and location map generation
for x in range(1, height - 1):
    for y in range(1, width - 1):
        if (x + y) % 2 == 0:
            all_pre[x, y] = img[x, y] % 128
        else:
            all_pre[x, y] = img[x, y]

# image encryption
for x in range(height):
    for y in range(width):
        cpixel = all_pre[x, y]
        all_enc[x, y] = encrypt(pub, int(cpixel))

# data embedding
all_enc_emb = all_enc.copy()
for x in range(1, height - 1):
    for y in range(1, width - 1):
        cpixel = all_enc[x, y]
        if (x + y) % 2 == 0:
            z = random.randint(0, 1) * 128
            z1 = encrypt(pub, z)
            all_enc_emb[x, y] = all_enc[x, y] * z1
            count += 1
        else:
            all_enc_emb[x, y] = all_enc[x, y]

# image decryption
for x in range(height):
    for y in range(width):
        cpixel = all_enc_emb[x, y]
        all_dec[x, y] = decrypt(priv, pub, int(cpixel))

dest = all_dec.copy()
Re_img = all_dec.copy()
for x in range(1, height - 1):
    for y in range(1, width - 1):
        if (x + y) % 2 == 0:
            dest[x, y] = (all_dec[x - 1, y] + all_dec[x, y - 1] + all_dec[x + 1, y] + all_dec[x, y + 1]) / 4
        else:
            dest[x, y] = all_dec[x, y]

for x in range(1, height - 1):
    for y in range(1, width - 1):
        if (x + y) % 2 == 0:
            p0 = all_dec[x, y] % 128
            p1 = all_dec[x, y] % 128 + 128
            if abs(dest[x, y] - p0) < abs(dest[x, y] - p1):
                Re_img[x, y] = p0
            else:
                Re_img[x, y] = p1

Re_img1 = Re_img.astype(np.uint8)
print("Size of encrypted image= " + str(sys.getsizeof(all_enc)))
print("Size of decrypted image= " + str(sys.getsizeof(all_dec)))
print("Size of reconstructed image = " + str(sys.getsizeof(Re_img1)))
print("Number of bits are embedded= " + str(count))
cv2.imwrite('Reimage.bmp', Re_img1)

