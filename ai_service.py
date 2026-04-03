import ollama

def get_embedding(text: str):
    """Menghasilkan vektor embedding dari teks."""
    response = ollama.embed(model="nomic-embed-text-v2-moe", input=text)
    return response["embeddings"]

def generate_json_summary(prompt_json: str):
    """Meminta llama merangkum dokumen dengan format JSON."""
    print("\n[AI Service] Mengirim prompt ke Llama 3.1...")
    print("\n[AI Service] Llama 3.1 sedang menganalisis dokumen...")
    output = ollama.generate(
        model="llama3.1",
        prompt=prompt_json,
        format="json"
    )
    print("\n[AI Service] Llama 3.1 selesai merespons.")
    return output['response']