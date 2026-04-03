import ollama

def get_embedding(text: str):
    response = ollama.embed(model="mxbai-embed-large", input=text)
    return response["embeddings"]

def generate_json_summary(prompt_json: str):
    print("\n[AI Service] Mengirim prompt ke LLM...")
    print("\n[AI Service] LLM sedang menganalisis dokumen...")
    output = ollama.generate(
        model="qwen3:1.7b",
        prompt=prompt_json,
        format="json"
    )
    print("\n[AI Service] LLM selesai merespons.")
    return output['response']