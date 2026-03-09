import chromadb
import fitz
import os
from ai_service import get_embedding

client = chromadb.PersistentClient(path="./database/db_arsip")
collection = client.get_or_create_collection(name="docs")

def chunk_text(text, chunk_size=1000, overlap=200):
    chunks, start = [], 0
    
    while start < len(text):
        chunks.append(text[start:start + chunk_size])
        start += chunk_size - overlap
    return chunks

def init_db(folder_path="arsip"):
    """Fungsi yang akan dijalankan saat server FastAPI pertama kali menyala."""
    if collection.count() == 0:
        print("Database kosong. Memulai embedding PDF...")
        documents, file_names = [], []
        
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(".pdf"):
                    file_path = os.path.join(folder_path, filename)
                    
                    with fitz.open(file_path) as pdf_doc:
                        full_text = "".join([page.get_text() for page in pdf_doc])
                        
                    if full_text.strip():
                        text_chunks = chunk_text(full_text)
                        for i, chunk in enumerate(text_chunks):
                            documents.append(chunk)
                            file_names.append(f"{filename}_part_{i+1}")
                            
            for i, d in enumerate(documents):
                embeddings = get_embedding(d)
                collection.add(
                    ids=[file_names[i]],
                    embeddings=embeddings,
                    documents=[d]
                )
            print("embedding selesai!")
            
        else:
            print(f"Folder '{folder_path}' tidak ditemukan. Lewati embedding.")
            
def search_documents(query_embedding, limit):
    """Fungsi pembantu untuk mencari dokumen di database."""
    return collection.query(query_embeddings=query_embedding, n_results=limit)

def process_single_pdf(file_path, filename):
    """Fungsi untuk memproses dan embedding 1 file PDF."""
    print(f"\n[Auto-Detect] Menemukan file baru: {filename}")
    
    # fitz
    try:
        with fitz.open(file_path) as pdf_doc:
            full_text = "".join([page.get_text() for page in pdf_doc])
            
        if full_text.strip():
            text_chunks = chunk_text(full_text)
            documents, file_names = [], []
            
            for i, chunk in enumerate(text_chunks):
                documents.append(chunk)
                file_names.append(f"{filename}_part_{i+1}")
                
            for i, d in enumerate(documents):
                embeddings = get_embedding(d)
                collection.add(
                    ids=[file_names[i]],
                    embeddings=embeddings,
                    documents=[d]
                )
            print(f"[Auto-Detect] Selesai embedding: {filename} ({len(text_chunks)} chunks masuk ke database)")
        else:
            print(f"[Auto-Detect] Gagal: File {filename} kosong atau berupa gambar scan.")
    except Exception as e:
        print(f"[Auto-Detect] Error membaca PDF: {str(e)}")