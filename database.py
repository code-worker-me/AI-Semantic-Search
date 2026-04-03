import chromadb
import fitz
import os
import pytesseract
from pdf2image import convert_from_path
from ai_service import get_embedding

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'C:\poppler-25.12.0\Library\bin' 

client = chromadb.PersistentClient(path="./database/db_arsip")
collection = client.get_or_create_collection(name="docs")

def chunk_text(text, chunk_size=1000, overlap=200):
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + chunk_size])
        start += chunk_size - overlap
    return chunks

def extract_text_from_pdf(file_path: str, filename: str) -> str:
    print(f"\n[Ekstract] 1. Reading file: {filename}")
    full_text= ""
    
    try:
        with fitz.open(file_path) as pdf_doc:
            full_text = "".join([page.get_text() for page in pdf_doc])
        print(f"2. Result: Find {len(full_text.strip())} character.")
    except Exception as e:
        print(f"❌ Failed: {e}")
        
    if len(full_text.strip()) < 50:
        print(f"[OCR] Pdf image content")
        print(f"[OCR] 3. Prepare poppler..")
        full_text = ""
        
        try:
            images = convert_from_path(file_path, poppler_path=POPPLER_PATH)
            print(f"[OCR] 4. Memproses {len(images)} halaman dengan Tesseract OCR...")
            
            for i, image in enumerate(images):
                print(f"[OCR]    -> Menerjemahkan halaman {i + 1}...")
                page_text = pytesseract.image_to_string(image, lang='ind+eng')
                full_text += f"\n{page_text}\n"
                
            print(f"[OCR] 5. Selesai! Berhasil mengekstrak {len(full_text.strip())} karakter.")
        except Exception as e:
            print(f"[OCR] ❌ Gagal melakukan proses OCR: {e}")
    return full_text

def insert_to_chromadb(full_text: str, filename: str):
    text_chunks = chunk_text(full_text)
    total_chunks = len(text_chunks)
    
    print(f"[EMBEDDING] 1. Memecah teks menjadi {total_chunks} bagian (chunks).")
    print(f"[EMBEDDING] 2. Memulai proses konversi vektor dengan mxbai-embed-large...")
    
    for i, chunk in enumerate(text_chunks):
        doc_id = f"{filename}_part_{i+1}"
        embeddings = get_embedding(chunk)
        
        collection.add(
            ids=[doc_id],
            embeddings=embeddings,
            documents=[chunk]
        )
        print(f"[EMBEDDING]    -> Chunk {i+1}/{total_chunks} berhasil disimpan.", end="\r")
    print(f"\n[EMBEDDING] 3. Selesai! Data {filename} tersimpan di ChromaDB.")

def init_db(folder_path="arsip"):
    """Dijalankan saat server FastAPI pertama kali menyala."""
    if collection.count() == 0:
        print("\n[INIT] Database kosong. Memulai inisialisasi awal...")
        if os.path.exists(folder_path):
            files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
            print(f"[INIT] Ditemukan {len(files)} file PDF di folder '{folder_path}'.")
            
            for filename in files:
                file_path = os.path.join(folder_path, filename)
                full_text = extract_text_from_pdf(file_path, filename)
                
                if full_text.strip():
                    insert_to_chromadb(full_text, filename)
                else:
                    print(f"[INIT] ❌ File {filename} kosong atau gagal diekstrak sepenuhnya.")
                    
            print("\n[INIT] Seluruh proses inisialisasi database selesai!")
        else:
            print(f"[INIT] Folder '{folder_path}' tidak ditemukan. Lewati embedding.")
    else:
        print(f"\n[INIT] Database siap. Terdapat {collection.count()} chunks tersimpan.")
            
def search_documents(query_embedding, limit):
    """Fungsi pembantu untuk mencari dokumen di database."""
    print(f"\n[PENCARIAN] Melakukan pencarian di ChromaDB (Limit: {limit})...")
    return collection.query(query_embeddings=query_embedding, n_results=limit)

def process_single_pdf(file_path, filename):
    """Memproses 1 file PDF (Dipanggil saat ada unggahan baru dari Laravel)."""
    print(f"\n{'='*50}")
    print(f"[AUTO-DETECT] Menerima dokumen baru: {filename}")
    print(f"{'='*50}")
    
    full_text = extract_text_from_pdf(file_path, filename)
    
    if full_text.strip():
        insert_to_chromadb(full_text, filename)
    else:
        print(f"[AUTO-DETECT] ❌ Gagal: File {filename} tidak memiliki teks yang bisa dibaca.")
           
def remove_single_pdf(filename):
    """Menghapus data dokumen dari database ChromaDB."""
    print(f"\n[AUTO-DETECT] Menerima perintah penghapusan untuk: {filename}")
    
    try:
        all_data = collection.get()
        ids_to_delete = [doc_id for doc_id in all_data['ids'] if doc_id.startswith(f"{filename}_part_")]
        
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            print(f"[AUTO-DETECT] Berhasil menghapus {len(ids_to_delete)} chunks milik {filename}.")
        else:
            print(f"[AUTO-DETECT] Peringatan: Data {filename} tidak ditemukan di database.")
    except Exception as e:
        print(f"[AUTO-DETECT] ❌ Error menghapus data: {str(e)}")