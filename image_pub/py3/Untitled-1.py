img_file= '/home/asad/image_pub/py3/lena512.bmp'
img = cv2.imread(img_file,0)
# Check if image loaded correctly
if img is None:
    print("Error: Image not loaded.")
    exit(1)
height, width = img.shape
print("Original Image size.", img.shape)
priv, pub=generate_keypair(128)
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


# Calculate the mean value of all_enc_emb
#total = 0
#count = height * width
#for x in range(height):
#    for y in range(width):
#        total += int(all_enc_emb[x, y])
#mean_value = total // count  # Use integer division for modulus

#print("Mean value of all_enc_emb:", mean_value)
# Calculate the median value of all_enc_emb
#all_enc_emb_int = np.array([[int(all_enc_emb[x, y]) for y in range(width)] for x in range(height)])
#median_value = int(np.median(all_enc_emb_int))
#print("Median value of all_enc_emb:", median_value)

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




print("The bit at location [5,5] in all_enc_emb:", all_enc[5,5])
print("Total length of bits in all_enc_emb:", all_enc[5,5].bit_length())
print("The bit at location [5,5] in mod_array:", mod_array[1,5])
print("Total length of bits in mod_array:", mod_array[1,5].bit_length())
print("The bit at location [5,5] in quot_array:", quot_array[1,5])
print("Total length of bits in quot_array:", quot_array[1,5].bit_length())








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
        cpixel = all_enc[x, y]
        all_dec[x, y] = decrypt(priv, pub, cpixel)

Re_img_emb = np.clip(all_dec, 0, 255).astype(np.uint8)
print("Reconstructed Image from Embedded Data size.", Re_img_emb.shape)

MAX_I = 255.0
# Calculate PSNR between original and reconstructed image with embedded data
mse_emb = np.mean((img.astype(np.float32) - Re_img_emb.astype(np.float32)) ** 2)
if mse_emb == 0:
    psnr_emb = float('inf')
else:
    psnr_emb = 10 * np.log10((MAX_I ** 2) / mse_emb)
print("PSNR with embedded data (manual calculation):", psnr_emb)

# Save the reconstructed image with embedded data to disk
cv2.imwrite('/home/asad/image_pub/py3/reimage_embedded.bmp', Re_img_emb)

# Calculate total number of bits used by all_enc
total_bits = 0
for x in range(height):
    for y in range(width):
        total_bits += all_enc[x, y].bit_length()
print("Total number of bits in all_enc:", total_bits)


def get_total_size(arr):
    # For object arrays, sum the size of each element plus the array container
    return sys.getsizeof(arr) + sum(sys.getsizeof(item) for item in arr.flat)

size_all_enc_emb = get_total_size(all_enc_emb)
size_mod_array = get_total_size(mod_array)
size_quot_array = get_total_size(quot_array)

print("Total storage size of all_enc_emb (bytes):", size_all_enc_emb)
print("Total storage size of mod_array (bytes):", size_mod_array)
print("Total storage size of quot_array (bytes):", size_quot_array)