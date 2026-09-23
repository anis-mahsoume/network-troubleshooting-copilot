from openai import OpenAI
import pymupdf as fitz
import os
import json
import re

client = OpenAI()

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def chunk_text(text, marker="### "):
    parts = re.split(re.escape(marker), text)
    chunks = [p.strip() for p in parts if p.strip()]
    return chunks


def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def load_existing_chunks(output_file):
    if not os.path.exists(output_file):
        return [], set()
    
    with open(output_file, "r", encoding="utf-8") as f:
        existing_chunks = json.load(f)
    
    processed_files = set(chunk["source"] for chunk in existing_chunks)
    return existing_chunks, processed_files


def process_folder(pdf_folder, existing_chunks, processed_files):
    all_chunks = list(existing_chunks)  # start with what we already have
    chunk_counter = len(all_chunks)      # continue numbering from where we left off

    pdf_paths = []
    for root, _, filenames in os.walk(pdf_folder):
        for filename in filenames:
            if filename.lower().endswith(".pdf"):
                pdf_paths.append(os.path.join(root, filename))
    pdf_paths.sort()

    for pdf_path in pdf_paths:
        filename = os.path.basename(pdf_path)

        rel_path = os.path.relpath(pdf_path, pdf_folder)

        if filename in processed_files:
            print(f"⏭️  {rel_path}: already processed, skipping")
            continue

        
        category = os.path.dirname(rel_path).replace(os.sep, "/") or "general"

        text = extract_text(pdf_path)

        word_count = len(text.split())
        if word_count < 200:
            print(f"⚠️  {rel_path}: only {word_count} words extracted — check this file")
        else:
            print(f"✅ {rel_path}: {word_count} words extracted")

        chunks = chunk_text(text)
        for chunk in chunks:
            embedding = get_embedding(chunk)
            all_chunks.append({
                "text": chunk,
                "source": filename,
                "category": category,
                "chunk_id": chunk_counter,
                "embedding": embedding
            })
            chunk_counter += 1

    return all_chunks


if __name__ == "__main__":
    PDF_FOLDER = "./data/raw"
    OUTPUT_FILE = "./data/processed/chunks.json"

    existing_chunks, processed_files = load_existing_chunks(OUTPUT_FILE)
    chunks = process_folder(PDF_FOLDER, existing_chunks, processed_files)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"\nDone. {len(chunks)} total chunks from {len(set(c['source'] for c in chunks))} docs saved to {OUTPUT_FILE}")