from fastapi import APIRouter, HTTPException, UploadFile, File
import json
import shutil
import os
from models import SearchRequest
from database import search_documents, process_single_pdf
from ai_service import get_embedding, generate_json_summary

router = APIRouter()

@router.post("/search")
def search_arsip(request: SearchRequest):
    if not request.intensi.strip():
        raise HTTPException(status_code=400, detail="Intensi pencarian tidak boleh kosong.")
    
    query_embedding = get_embedding(request.intensi)
    
    results = search_documents(query_embedding, request.limit)
    
    if not results['documents'] or len(results['documents'][0]) == 0:
        return {"data": [], "message": "Tidak ada arsip yang relevan."}
    
    konteks_dokumen = ""
    for idx, (doc, raw_id) in enumerate(zip(results['documents'][0], results['ids'][0])):
        nama_file = raw_id.split('_part_')[0]
        konteks_dokumen += f"--- Arsip {idx + 1} ---\nNama File: {nama_file}\nIsi Dokumen: {doc}\n\n"
        
    prompt_json = f"""
    Anda adalah sistem pencari arsip pintar. 
    User sedang mencari: "{request.intensi}"
    
    Berikut adalah beberapa potongan dokumen yang relevan: 
    {konteks_dokumen}
    
    Tugas Anda: Buat deskripsi singkat (1-2 kalimat) untuk MASING-MASING dokumen.
    Keluarkan jawaban HANYA dalam format Array of JSON:
    [
      {{
        "id": 1,
        "nama": "nama_file.pdf",
        "deskripsi": "..."
      }}
    ]
    """
    
    output_string = generate_json_summary(prompt_json)
    
    try:
        data_json = json.loads(output_string)
        return {"data": data_json, "message": "Pencarian berhasil"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Gagal memformat hasil dari AI.")
    
# Router untuk process pdf
@router.post("/process-pdf")
async def process_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File harus berupa PDF.")
    
    folder_path = "arsip"
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan file: {str(e)}")
    
    try:
        process_single_pdf(file_path, file.filename)
        return {"status": "success", "message": f"File {file.filename} berhasil diproses ke vektor."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses embedding: {str(e)}")