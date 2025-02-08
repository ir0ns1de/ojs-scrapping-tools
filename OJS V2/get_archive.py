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

    # Menemukan semua <div> dengan id yang diinginkan
    issues = soup.find_all("div", id=lambda x: x and x.startswith("issue"))

    # Membuat folder 'archive' jika belum ada
    os.makedirs('archive', exist_ok=True)

    # Menyusun path file dengan nama yang diberikan oleh pengguna
    filename = os.path.join("archive", f"{filename_input}.txt")

    # Menulis hasil ke dalam file
    with open(filename, 'w') as file:
        for issue in issues:
            title_tag = issue.find("h4").find("a")  # Mencari <a> dalam <h4>
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag["href"]
                file.write(f"Judul: {title}\n")
                file.write(f"Link: {link}\n")
                file.write("-" * 50 + "\n")

    print(f"Data berhasil disimpan dalam file {filename}")

else:
    print("Gagal mengakses halaman.")
