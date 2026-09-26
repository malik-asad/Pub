from paillier_gmpy2 import *
import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
import pandas as pd

img_file= '/home/asad/image_pub/py3/lake.tif'
img = cv2.imread(img_file,0)
img = cv2.resize(img, (256, 256))
# Check if image loaded correctly
if img is None:
    print("Error: Image not loaded.")
    exit(1)
height, width = img.shape

# Key generation timing
start_keygen = time.time()
priv, pub = generate_keypair(512)  # Generate keys with 512 bits
end_keygen = time.time()

# Image encryption timing
start_enc = time.time()
all_enc = np.zeros([height,width], dtype=object)
for x in range(height):
    for y in range(width):
        cpixel = img[x, y]
        all_enc[x,y]=encrypt(pub, int(cpixel))
end_enc = time.time()
# Example secret bit sequence S
L = 512*512*2+1  # Length of secret bits, must be even
S = np.random.randint(0, 2, size=L)
k = 0  # Index for secret bits

def check_function(P_E, S_k, S_k1):
    val = int(P_E)
    lsb1 = val & 1
    lsb2 = (val >> 1) & 1
    if (lsb1 == S_k) and (lsb2 == S_k1):
        return True
    else:
        return False


def embed_secret_bits(I_E, pub, S, T):
    height, width = I_E.shape
    all_enc_emb = I_E.copy()
    k = 0
    connt = 0  # Count of successful embeddings
    for i in range(height):
        for j in range(width):
            attempts = 0
            while attempts < T and k + 1 < len(S):
                P_E = all_enc_emb[i, j]
                if check_function(P_E, S[k], S[k+1]):
                    # Data embedded at (i, j)
                    k += 1
                    connt += 2
                    break
                else:
                    # Modify pixel homomorphically
                    va=0
                    z1 = encrypt(pub, va)
                    P_E = e_add(pub,P_E, z1)  # Homomorphic addition of 1
                    all_enc_emb[i, j] = P_E
                    attempts += 1
                    continue
    return all_enc_emb, connt

# Data hiding timing
results = []
def decrypt_image(enc_img, priv, pub):
    height, width = enc_img.shape
    dec_img = np.zeros((height, width), dtype=np.uint8)
    for x in range(height):
        for y in range(width):
            dec_img[x, y] = decrypt(priv, pub, enc_img[x, y])
    return dec_img

# Calculate PSNR
def calculate_psnr(original, reconstructed):
    mse = np.mean((original.astype(np.float32) - reconstructed.astype(np.float32)) ** 2)
    if mse == 0:
        return float('inf')
    max_pixel = 255.0
    psnr = 10 * np.log10((max_pixel ** 2) / mse)
    return psnr

for T in [4]:
    start_hide = time.time()
    all_enc_emb, connt = embed_secret_bits(all_enc, pub, S, T)
    end_hide = time.time()
    hide_time = end_hide - start_hide

    start_decrypt = time.time()
    decrypted_img = decrypt_image(all_enc_emb, priv, pub)
    end_decrypt = time.time()
    decrypt_time = end_decrypt - start_decrypt

    psnr_value = calculate_psnr(img, decrypted_img)
    mismatch_count = np.sum(img != decrypted_img)

    results.append({
        'T': T,
        'Key generation time (s)': format(end_keygen - start_keygen, '.10f'),
        'Encryption time (s)': format(end_enc - start_enc, '.10f'),
        'Data hiding time (s)': format(hide_time, '.10f'),
        'Decryption time (s)': format(decrypt_time, '.10f'),
        'PSNR (dB)': psnr_value,
        'Mismatched pixels': mismatch_count,
        'Successful embeddings': connt,
        'embading rate(bpp)': connt / (height * width)
    })

df = pd.DataFrame(results)
df.to_excel('embedding_results.xlsx', index=False)
print("Results saved to embedding_results.xlsx")

# Extract T and embedding rate from the results
T_values = [entry['T'] for entry in results]
embedding_rates = [entry['embading rate(bpp)'] for entry in results]

plt.figure()
plt.plot(T_values, embedding_rates, marker='o')
plt.xlabel('T value')
plt.ylabel('Embedding rate (bpp)')
plt.title('Embedding Rate vs T')
plt.grid(True)
plt.savefig('embedding_rate_vs_T.png')
plt.close()
print("Plot saved as embedding_rate_vs_T.png")

