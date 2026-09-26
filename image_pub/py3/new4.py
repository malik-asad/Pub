from paillier_gmpy2 import *
import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import pandas as pd
import random

img_file= '/home/asad/image_pub/py3/lena512.bmp'
img = cv2.imread(img_file,0)
# Check if image loaded correctly
if img is None:
    print("Error: Image not loaded.")
    exit(1)
N, M = img.shape
key=128  # Key size for encryption
# Generate keypair
priv, pub=generate_keypair(key)
height, width = img.shape
all_enc = np.zeros([height,width], dtype=object)
all_dec = np.zeros([height,width])


def nth_bits(enc_array, x, y, n, m):
    """
    Extract the n-th LSB and m-th MSB of the encrypted pixel at (x, y).
    n: 1 means LSB, 2 means 2nd LSB, etc.
    m: 1 means MSB, 2 means 2nd MSB, etc.
    """
    val = int(enc_array[x, y])
    nth_lsb = (val >> (n - 1)) & 1 
    mth_lsb = (val >> (m - 1)) & 1 
    binary_val = bin(val)[2:]
    combined = (nth_lsb << 1) | mth_lsb
    return {
        'x': x, 'y': y,
        f'{n}th_LSB': nth_lsb,
        f'{m}th_MSB': mth_lsb,
        'combined': combined,
        #'Value': val,
        'Binary': binary_val
    }



bit_info_list = []
for x in range(N):
    for y in range(M):
        cpixel = img[x, y]
        all_enc[x, y] = encrypt(pub, int(cpixel))
        # Generate random n and m for each pixel
        val = int(all_enc[x, y])
        n = 1
        m = 2
        bit_info = nth_bits(all_enc, x, y, n, m)

        bit_info_list.append(bit_info)

# Save to Excel file
df = pd.DataFrame(bit_info_list)
df.to_excel('/home/asad/image_pub/py3/encrypted_bits_info_nth.xlsx', index=False)

def check_function(P_E, S_k, S_k1):
    # Example: embed two bits in the two LSBs of the encrypted value
    val = int(P_E)
    lsb1 = val & 1
    lsb2 = (val >> 1) & 1
    return (lsb1 == S_k) and (lsb2 == S_k1)

def embed_secret_bits(I_E, pub, S, T):
    k = 0
    I_E_emb = I_E.copy()
    while T != 0 and k + 1 < len(S):
        for i in range(N):
            for j in range(M):
                P_E = I_E_emb[i, j]
                if check_function(P_E, S[k], S[k+1]):
                    k += 2
                    break  # Bit is embedded
                else:
                    # Modify encrypted value: Pe(i) <- Pe(i) * g^0 * r^N mod N^2
                    # g^0 = 1, so just multiply by r^N mod N^2
                     z1 = encrypt(pub, 1)
                     Te_new = Te * z1  # Homomorphic addition of 1
                    # Continue to next j
        T -= 1
    return I_E_emb

# Example usage:
# S = np.random.randint(0, 2, size=2000)  # Secret bits
# T = 1  # Number of embedding rounds
# all_enc_embedded = embed_secret_bits(all_enc, pub, S, T)







