from paillier_gmpy2 import *
import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import pandas as pd

# Directory containing BOWS2 images
bows2_dir = '/home/asad/BOWS2OrigEp3'
priv, pub=generate_keypair(128)
# Get list of image files and take only first 10
image_files = [f for f in os.listdir(bows2_dir) if f.endswith(('.pgm', '.bmp', '.png'))][:10]

results = []  # To store results for each image

# Process each image in the directory
for image_name in image_files:
    img_path = os.path.join(bows2_dir, image_name)
    print(f"Processing {image_name}...")
    
    # Read and process image
    img = cv2.imread(img_path, 0)
    if img is None:
        print(f"Error: Could not load {image_name}")
        continue
    
    height, width = img.shape
    all_enc = np.zeros([height,width], dtype=object)
    all_dec = np.zeros([height,width])
    for x in range(height):
        for y in range(width):
            cpixel = img[x, y]
            all_enc[x,y]=encrypt(pub, int(cpixel))

    # Example secret bit sequence S
    L = 512*512  # Number of bits to embed (adjust as needed)
    S = np.random.randint(0, 2, size=L)  # Random bits for demonstration

    all_enc_emb = all_enc.copy()
    k = 0  # Index for secret bits

    for x in range(height):
        for y in range(width):
            if k >= L:
                break
            Te = all_enc[x, y]
            if S[k] == 0:
                if int(Te) % 2 == 0:
                    all_enc_emb[x, y] = Te
                    k += 1
                else:
                    # Modify encrypted value to make it even
                    while int(Te) % 2 == 0:
                        z1 = encrypt(pub, 1)
                        Te_new = Te * z1  # Homomorphic addition of 1
                        if int(Te_new) % 2 == 0 and Te_new > 0:
                            all_enc_emb[x, y] = Te_new
                            k += 1
                            break
                        else:
                            Te = Te_new  # Try again with the new value
            else:  # S[k] == 1
                if int(Te) % 2 == 1:
                    all_enc_emb[x, y] = Te
                    k += 1
                else:
                    # Modify encrypted value to make it odd
                    while int(Te) % 2 == 1:
                        z1 = encrypt(pub, 1)
                        Te_new = Te * z1  # Homomorphic addition of 1
                        if int(Te_new) % 2 == 1 and Te_new > 0:
                            all_enc_emb[x, y] = Te_new
                            k += 1
                            break
                        else:
                            Te = Te_new  # Try again with the new value


    # Calculate the minimum value of all_enc_emb
    all_enc_emb_int = np.array([[int(all_enc_emb[x, y]) for y in range(width)] for x in range(height)])
    min_value = int(np.min(all_enc_emb_int))
    print("Minimum value of all_enc_emb:", min_value)

    # Apply modulo operation and reverse it for all_enc_emb
    modulus = min_value  # Paillier modulus

    mod_array = np.zeros((height, width), dtype=object)
    quot_array = np.zeros((height, width), dtype=object)
    reversed_array = np.zeros((height, width), dtype=object)

    for x in range(height):
        for y in range(width):
            val = int(all_enc_emb[x, y])
            mod_array[x, y] = val % modulus
            quot_array[x, y] = val // modulus
            # Reverse operation
            reversed_array[x, y] = mod_array[x, y] + modulus * quot_array[x, y]
   
    # Check if reversed_array matches original all_enc_emb
    is_equal = True
    for x in range(height):
        for y in range(width):
            if int(all_enc_emb[x, y]) != reversed_array[x, y]:
                is_equal = False
                print(f"Mismatch at ({x},{y})")
                break
    print("Reverse operation successful for all pixels:", is_equal)

    # Use reversed_array for decryption phase
    for x in range(height):
        for y in range(width):
            cpixel = reversed_array[x, y]
            all_dec[x, y] = decrypt(priv, pub, cpixel)

    Re_img_emb = np.clip(all_dec, 0, 255).astype(np.uint8)
    MAX_I = 255.0
    # Calculate PSNR between original and reconstructed image with embedded data
    mse_emb = np.mean((img.astype(np.float32) - all_dec.astype(np.float32)) ** 2)
    if mse_emb == 0:
        psnr_emb = float('inf')
    else:
        psnr_emb = 10 * np.log10((MAX_I ** 2) / mse_emb)
    

    # Calculate total number of bits used by all_enc
    total_bits_e = 0

    for x in range(height):
        for y in range(width):
            total_bits_e += all_enc[x, y].bit_length()
            
    print("Total number of bits in all_enc:", total_bits_e)
    def get_total_size(arr):
        # For object arrays, sum the size of each element plus the array container
        return sys.getsizeof(arr) + sum(sys.getsizeof(item) for item in arr.flat)
    
    size_all_enc = get_total_size(all_enc)
    size_all_enc_emb = get_total_size(all_enc_emb)
    size_mod_array = get_total_size(mod_array)
    size_quot_array = get_total_size(quot_array)
    
   
    # Store results for this image
    results.append({
        'Image': image_name,
        'PSNR': psnr_emb,
        'TotalBits_all_enc': total_bits_e,
        'Size_all_enc_bytes': size_all_enc,
        'Size_all_enc_emb_bytes': size_all_enc_emb,
        'Size_mod_array_bytes': size_mod_array,
        'Size_quot_array_bytes': size_quot_array
    })

# Create DataFrame and save to Excel
df = pd.DataFrame(results)
excel_path = '/home/asad/image_pub/py3/results_10images.xlsx'
df.to_excel(excel_path, index=False)
print(f"Results saved to {excel_path}")