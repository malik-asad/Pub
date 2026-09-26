def process_image(img_file):
    img = cv2.imread(img_file, 0)
    if img is None:
        print(f"Error: Image not loaded for {img_file}")
        return None
    height, width = img.shape
    priv, pub = generate_keypair(128)
    all_enc = np.zeros([height, width], dtype=object)
    all_dec = np.zeros([height, width])
    for x in range(height):
        for y in range(width):
            cpixel = img[x, y]
            all_enc[x, y] = encrypt(pub, int(cpixel))

    # Example secret bit sequence S
    L = height * width
    S = np.random.randint(0, 2, size=L)
    all_enc_emb = all_enc.copy()
    k = 0
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
                    while int(Te) % 2 == 0:
                        z1 = encrypt(pub, 1)
                        Te_new = Te * z1
                        if int(Te_new) % 2 == 0 and Te_new > 0:
                            all_enc_emb[x, y] = Te_new
                            k += 1
                            break
                        else:
                            Te = Te_new
            else:
                if int(Te) % 2 == 1:
                    all_enc_emb[x, y] = Te
                    k += 1
                else:
                    while int(Te) % 2 == 1:
                        z1 = encrypt(pub, 1)
                        Te_new = Te * z1
                        if int(Te_new) % 2 == 1 and Te_new > 0:
                            all_enc_emb[x, y] = Te_new
                            k += 1
                            break
                        else:
                            Te = Te_new

    all_enc_emb_int = np.array([[int(all_enc_emb[x, y]) for y in range(width)] for x in range(height)])
    min_value = int(np.min(all_enc_emb_int))
    modulus = min_value

    mod_array = np.zeros((height, width), dtype=object)
    quot_array = np.zeros((height, width), dtype=object)
    for x in range(height):
        for y in range(width):
            val = int(all_enc_emb[x, y])
            mod_array[x, y] = val % modulus
            quot_array[x, y] = val // modulus

    def get_total_size(arr):
        import sys
        return sys.getsizeof(arr) + sum(sys.getsizeof(item) for item in arr.flat)

    size_all_enc_emb = get_total_size(all_enc_emb)
    size_mod_array = get_total_size(mod_array)
    size_quot_array = get_total_size(quot_array)

    return {
        "image": img_file,
        "all_enc_emb_size": size_all_enc_emb,
        "mod_array_size": size_mod_array,
        "quot_array_size": size_quot_array
    }

# List of image files to process
image_files = [
    '/home/asad/image_pub/py3/lena512.bmp',
    '/home/asad/image_pub/py3/another_image.bmp',
    # Add more image paths here
]

results = []
for img_file in image_files:
    result = process_image(img_file)
    if result:
        results.append(result)

# Print comparison
for res in results:
    print(f"Image: {res['image']}")
    print(f"  all_enc_emb size: {res['all_enc_emb_size']} bytes")
    print(f"  mod_array size:   {res['mod_array_size']} bytes")
    print(f"  quot_array size:  {res['quot_array_size']} bytes")
    print("-" * 40)