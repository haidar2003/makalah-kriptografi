# 18221134
# Muhammad Rafi Haidar

import cv2
import numpy as np
import os

from Crypto.PublicKey import RSA
from secrets import token_bytes

key = RSA.generate(2048)
private_key = key
public_key = key.public_key()
print("Kunci pribadi baru:", private_key.export_key().decode())
print("Kunci publik baru:", public_key.export_key().decode())

def embed_watermark(original_image, watermark):
    global private_key

    selected_image = cv2.imread(os.path.join('source_image', original_image), cv2.IMREAD_COLOR)
    selected_watermark = cv2.imread(os.path.join('watermark', watermark), cv2.IMREAD_COLOR)

    # Mengecek apakah ukuran watermark lebih kecil (watermark harus selalu lebih kecil )
    if (selected_watermark.shape[0] > selected_image.shape[0] or selected_watermark.shape[1] > selected_image.shape[1]):
        print('Error')
        return
    else:
        selected_watermark_flattened = selected_watermark.flatten()

    # Kunci -> Seed
    private_key_bytes = private_key.export_key(format='DER')
    seed = int.from_bytes(token_bytes(32) + private_key_bytes, 'big')
    rng = np.random.default_rng(seed)

    # Proses Penyematan
    indices = rng.choice(len(selected_image.flatten()), len(selected_watermark_flattened), replace=True)
    for i, idx in enumerate(indices):
        selected_image.flat[idx] = (selected_image.flat[idx] & ~1) | (selected_watermark_flattened[i] & 1)

    return selected_image

# GAGAL
def extract_watermark(stego_image):
    global public_key

    stego = cv2.imread(os.path.join('stego_image', stego_image), cv2.IMREAD_COLOR)

    # Kunci -> Seed
    public_key_bytes = public_key.export_key(format='DER')
    seed = int.from_bytes(public_key_bytes, byteorder='big')
    rng = np.random.default_rng(seed)

    # Proses Ekstraksi
    indices = rng.choice(len(stego.flatten()), len(stego.flatten()) // 3, replace=False)
    selected_watermark_flattened = np.zeros(len(indices), dtype=np.uint8)
    for i, idx in enumerate(indices):
        selected_watermark_flattened[i] = stego.flat[idx] & 1

    # Proses Rekonstruksi Watermark
    selected_watermark_shape = (selected_watermark_flattened.size // 3, 1, 3)
    selected_watermark = np.reshape(selected_watermark_flattened, selected_watermark_shape).squeeze()

    return selected_watermark

def main():
    global private_key, public_key 

    while True:
        print("Pilih opsi:")
        print("1. Bangkitkan kunci")
        print("2. Sematkan Watermark")
        print("3. Ekstrak Watermark")
        print("4. Keluar dari program")
        choice = input("Masukkan pilihan: ")

        if choice == "1":
            key = RSA.generate(2048)
            private_key = key
            public_key = key.public_key()
            print("Kunci pribadi baru:", private_key.export_key().decode())
            print("Kunci publik baru:", public_key.export_key().decode())
        elif choice == "2":
            original_image = input("Masukkan nama berkas Gambar Asli: ")
            watermark = input("Masukkan nama berkas Watermark: ")
            stego_image_name = input("Masukkan nama berkas output untuk Gambar Stego: ")
            stego_image = embed_watermark(original_image, watermark)
            cv2.imwrite(os.path.join('stego_image', stego_image_name), stego_image)
            print(f"Gambar stego disimpan sebagai {stego_image_name}")
        elif choice == "3":
            stego_image = input("Masukkan nama berkas gambar stego: ")
            extracted_image = extract_watermark(stego_image)
            cv2.imwrite(os.path.join('extracted_watermark', 'extracted_watermark.png'), extracted_image)
            print("Watermark diekstrak dan disimpan sebagai extracted_watermark.png")
        elif choice == "4":
            return
        else:
            print("Pilihan tidak valid")

if __name__ == "__main__":
    main()