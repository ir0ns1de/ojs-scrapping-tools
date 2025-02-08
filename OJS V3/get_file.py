import requests
from bs4 import BeautifulSoup
import os
import re

# Fungsi untuk membersihkan nama file dari karakter unik
def clean_filename(title):
    return re.sub(r'[\\/*?:"<>|]', '', title)

# Fungsi untuk membaca file yang berisi URL
def read_links_from_file(file_path):
    links = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('Link:'):
                links.append(line.split('Link:')[1].strip())
    return links

# Fungsi untuk membaca log dan mendapatkan URL yang sudah di-scrape
def read_scraped_urls(log_file):
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            return set(line.strip() for line in f.readlines())
    return set()

# Fungsi untuk menambahkan URL yang sudah di-scrape ke log
def append_to_log(log_file, url):
    with open(log_file, 'a') as f:
        f.write(url + '\n')

# Meminta input nama file dan folder output dari pengguna
file_name = input("Masukkan nama file yang ingin di-scrape (terletak di folder 'archive'): ")
output_folder = input("Masukkan nama folder untuk menyimpan hasil (akan dibuat jika belum ada): ")

# Cek apakah folder pdf sudah ada, jika belum maka buat
pdf_main_folder = 'pdf'
if not os.path.exists(pdf_main_folder):
    os.makedirs(pdf_main_folder)

# Membuat folder sesuai nama input pengguna di dalam folder pdf
output_folder_path = os.path.join(pdf_main_folder, output_folder)
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

# File log untuk menyimpan URL yang sudah di-scrape
log_file = 'scraping_log.txt'

# Membaca URL yang sudah di-scrape dari log
scraped_urls = read_scraped_urls(log_file)

# Path file yang berisi URL
file_path = os.path.join('archive', file_name)

# Membaca URL dari file
if os.path.exists(file_path):
    links = read_links_from_file(file_path)

    # Loop melalui semua URL yang ditemukan di file
    for url in links:
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Mencari semua artikel di dalam <div class="obj_article_summary">
            articles = soup.find_all('div', class_='obj_article_summary')

            for article in articles:
                # Mengambil judul artikel
                title_tag = article.find('h3', class_='title')
                title = title_tag.get_text(strip=True) if title_tag else "No Title"

                # Mengambil daftar penulis
                author_tag = article.find('div', class_='authors')
                authors = author_tag.get_text(strip=True) if author_tag else "No Authors"

                # Mengambil link PDF
                pdf_link_tag = article.find('a', class_='obj_galley_link pdf')
                if pdf_link_tag:
                    pdf_url = pdf_link_tag['href']
                    pdf_url = pdf_url.replace('/view/', '/download/')  # Ubah /view/ menjadi /download/

                    # Cek apakah PDF sudah pernah di-scrape
                    if pdf_url in scraped_urls:
                        print(f"PDF {pdf_url} sudah di-scrape sebelumnya, melewati...")
                        continue

                    # Bersihkan judul untuk dijadikan nama file
                    clean_title = clean_filename(title)
                    pdf_name = f"{clean_title}.pdf"
                    pdf_path = os.path.join(output_folder_path, pdf_name)

                    # Download file PDF
                    pdf_response = requests.get(pdf_url)
                    if pdf_response.status_code == 200:
                        with open(pdf_path, 'wb') as f:
                            f.write(pdf_response.content)
                        print(f'File "{title}" oleh {authors} berhasil di-download sebagai {pdf_name}')

                        # Tambahkan ke log
                        append_to_log(log_file, pdf_url)
                    else:
                        print(f'Gagal mendownload file untuk artikel "{title}"')
                else:
                    print(f'Tidak ditemukan link download untuk artikel "{title}", melewati...')
        else:
            print(f'Halaman {url} tidak ditemukan atau gagal diakses.')
else:
    print(f'File {file_name} tidak ditemukan di folder "archive".')
