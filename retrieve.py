from openai import OpenAI
import json
import numpy as np

client = OpenAI()


def load_chunks(path="data/processed/chunks.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_query_embedding(query):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    return response.data[0].embedding


def cosine_similarity(query_vec, chunk_vecs):
    query_vec = np.array(query_vec)
    chunk_vecs = np.array(chunk_vecs)
    return chunk_vecs @ query_vec / (
        np.linalg.norm(chunk_vecs, axis=1) * np.linalg.norm(query_vec)
    )


def top_k(query, chunks, k=3):
    query_vec = get_query_embedding(query)
    chunk_vecs = [c["embedding"] for c in chunks]
    scores = cosine_similarity(query_vec, chunk_vecs)
    top_idx = np.argsort(scores)[::-1][:k]

    results = []
    for i in top_idx:
        results.append({
            "text": chunks[i]["text"],
            "source": chunks[i]["source"],
            "category": chunks[i]["category"],
            "score": float(scores[i])
        })
    return results

if __name__ == "__main__":
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks\n")

    test_queries = [
        "My VPN connects fine but Outlook keeps hanging when the tunnel is up",
        "A device that got moved to a new switch port still has its old IP address",
        "DNS is returning SERVFAIL for one domain but everything else resolves fine",
        "Our HA firewall pair both think they're active at the same time",
        "Traceroute stops responding at one hop but the app itself seems to still work through a different port",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {query}")
        print('='*60)
        results = top_k(query, chunks, k=3)
        for r in results:
            print(f"\n[{r['score']:.3f}] {r['source']} ({r['category']})")
            print(f"  {r['text'][:200]}...")