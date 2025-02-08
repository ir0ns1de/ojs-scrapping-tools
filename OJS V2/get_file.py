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
        lines = file.readlines()
        for i in range(len(lines)):
            if lines[i].startswith('Link:'):
                links.append(lines[i].split('Link:')[1].strip())
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
        # Mengirim permintaan HTTP untuk mengambil halaman
        response = requests.get(url)
        
        # Memastikan halaman berhasil diambil
        if response.status_code == 200:
            # Parsing halaman menggunakan BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Mencari semua judul artikel dalam tag <div class="tocTitle">
            titles = soup.find_all('div', class_='tocTitle')
            
            # Mencari semua link download PDF dalam tag <div class="tocGalleys">
            file_links = soup.find_all('div', class_='tocGalleys')
            
            # Membaca URL yang sudah di-scrape dari log
            for title, link in zip(titles, file_links):
                # Mendapatkan URL artikel, dengan pengecekan jika elemen 'a' tidak ada
                a_tag = link.find('a', class_='file')
                if a_tag:
                    article_url = a_tag['href']
                    
                    # Cek apakah URL sudah pernah di-scrape
                    if article_url in scraped_urls:
                        print(f"Artikel dengan URL {article_url} sudah di-scrape sebelumnya, melewati...")
                        continue
                    
                    # Mendapatkan judul artikel dan membersihkan nama file
                    article_title = title.get_text(strip=True)
                    clean_title = clean_filename(article_title)
                    
                    # Mendapatkan link PDF (mengganti '/view/' dengan '/download/')
                    pdf_url = article_url.replace('/view/', '/download/')
                    
                    # Menyimpan file PDF
                    pdf_response = requests.get(pdf_url)
                    
                    # Memastikan file berhasil di-download
                    if pdf_response.status_code == 200:
                        pdf_name = f'{clean_title}.pdf'
                        pdf_path = os.path.join(output_folder_path, pdf_name)
                        with open(pdf_path, 'wb') as f:
                            f.write(pdf_response.content)
                        print(f'File "{article_title}" berhasil di-download sebagai {pdf_name}j')
                        
                        # Menambahkan URL yang sudah di-scrape ke log
                        append_to_log(log_file, article_url)
                    else:
                        print(f'Gagal mendownload file untuk artikel "{article_title}"')
                else:
                    print(f'Tidak ditemukan link download untuk artikel "{title.get_text(strip=True)}", melewati...')
        else:
            print(f'Halaman {url} tidak ditemukan atau gagal diakses.')
else:
    print(f'File {file_name} tidak ditemukan di folder "archive".')
