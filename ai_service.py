import ollama

def get_embedding(text: str):
    """Menghasilkan vektor embedding dari teks."""
    response = ollama.embed(model="mxbai-embed-large", input=text)
    return response["embeddings"]

def generate_json_summary(prompt_json: str):
    """Meminta llama merangkum dokumen dengan format JSON."""
    output = ollama.generate(
        model="gemma3",
        prompt=prompt_json,
        format="json"
    )
    return output['response']