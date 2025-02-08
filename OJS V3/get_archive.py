import os
import requests
from bs4 import BeautifulSoup

# Meminta pengguna untuk memasukkan URL halaman
url = input("Masukkan URL halaman untuk scraping: ")

# Meminta pengguna untuk memasukkan nama file yang diinginkan
filename_input = input("Masukkan nama file yang diinginkan (tanpa ekstensi .txt): ")

# Mengambil konten halaman
response = requests.get(url)

# Memeriksa status code, 200 berarti sukses
if response.status_code == 200:
    # Menggunakan BeautifulSoup untuk parsing HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Menemukan semua <h2> dengan <a> yang memiliki kelas "title"
    titles = soup.find_all("a", class_="title")

    # Membuat folder 'archive' jika belum ada
    os.makedirs('archive', exist_ok=True)

    # Menyusun path file dengan nama yang diberikan oleh pengguna
    filename = os.path.join("archive", f"{filename_input}.txt")

    # Menulis hasil ke dalam file
    with open(filename, 'w') as file:
        for title_tag in titles:
            link = title_tag["href"]
            file.write(f"Link: {link}\n")
            file.write("-" * 50 + "\n")

    print(f"Data berhasil disimpan dalam file {filename}")

else:
    print("Gagal mengakses halaman.")
