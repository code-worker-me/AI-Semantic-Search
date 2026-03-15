import os
import pytesseract
from pdf2image import convert_from_path
import fitz  # PyMuPDF

# --- KONFIGURASI PATH (SESUAIKAN DENGAN KOMPUTER ANDA) ---
# 1. Lokasi file tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 2. Lokasi folder bin dari Poppler
# Ubah path ini sesuai dengan tempat Anda mengekstrak folder Poppler
POPPLER_PATH = r'C:\poppler-25.12.0\Library\bin' 

def extract_text_from_pdf(pdf_path: str) -> str:
    print(f"Memulai proses pembacaan file: {pdf_path}")
    teks_dokumen = ""
    
    # LANGKAH 1: Percobaan ekstraksi teks digital (Normal)
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            teks_dokumen += page.get_text()
        print(f"Hasil ekstraksi normal: {len(teks_dokumen)} karakter ditemukan.")
    except Exception as e:
        print(f"Peringatan: Gagal membaca PDF secara normal: {e}")

    # LANGKAH 2: Evaluasi (Jika teks kurang dari 50 karakter, anggap sebagai gambar)
    if len(teks_dokumen.strip()) < 50:
        print("Teks terlalu sedikit. Dokumen terdeteksi sebagai gambar/scan. Memulai proses OCR...")
        teks_dokumen = "" 
        
        try:
            # Ubah PDF menjadi deretan gambar
            print("1. Mengubah PDF menjadi gambar (menggunakan Poppler)...")
            images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH) 
            
            # Ekstrak teks dari gambar
            print("2. Membaca teks dari gambar (menggunakan Tesseract OCR)...")
            for i, image in enumerate(images):
                print(f"   -> Memproses halaman {i + 1}...")
                page_text = pytesseract.image_to_string(image, lang='ind+eng')
                teks_dokumen += f"\n--- Halaman {i + 1} ---\n{page_text}\n"
                
            print("Proses OCR selesai dengan sukses!")
        except Exception as e:
            print(f"❌ Gagal melakukan proses OCR: {e}")
            return ""
            
    return teks_dokumen

# --- EKSEKUSI PENGUJIAN ---
if __name__ == "__main__":
    file_uji = "dummy.pdf"
    
    if not os.path.exists(file_uji):
        print(f"File {file_uji} tidak ditemukan! Pastikan file sudah ada di folder ini.")
    else:
        hasil_teks = extract_text_from_pdf(file_uji)
        
        print("\n" + "="*50)
        print("HASIL AKHIR EKSTRAKSI TEKS:")
        print("="*50)
        print(hasil_teks)
        print("="*50)