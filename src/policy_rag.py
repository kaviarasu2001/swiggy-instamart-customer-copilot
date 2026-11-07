from pathlib import Path
import sys

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_DIR = Path(__file__).resolve().parents[1]
POLICY_DIR = PROJECT_DIR / "data" / "policies"

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import mock_llm

CHUNK_SIZE = 40
CHUNK_OVERLAP = 10


def load_policies():
    documents = []

    for filepath in sorted(POLICY_DIR.glob("*.txt")):
        with open(filepath, "r", encoding="utf-8") as file:
            documents.append({
                "source": filepath.name,
                "content": file.read().strip()
            })

    return documents


def create_chunks(documents):
    chunks = []
    step = CHUNK_SIZE - CHUNK_OVERLAP

    for document in documents:
        words = document["content"].split()
        start = 0

        while start < len(words):
            chunk_words = words[start:start + CHUNK_SIZE]

            chunks.append({
                "source": document["source"],
                "content": " ".join(chunk_words),
                "word_count": len(chunk_words)
            })

            if start + CHUNK_SIZE >= len(words):
                break

            start += step

    return chunks


documents = load_policies()
policy_chunks = create_chunks(documents)

if len(documents) != 5:
    raise ValueError("Expected 5 policy documents")

expected_chunks = 15

if len(policy_chunks) != expected_chunks:
    raise ValueError(
        f"Expected {expected_chunks} chunks, found {len(policy_chunks)}"
    )

vectorizer = TfidfVectorizer(stop_words="english")
policy_vectors = vectorizer.fit_transform(
    [chunk["content"] for chunk in policy_chunks]
)


def retrieve_policy(query, top_k=3):
    query_vector = vectorizer.transform([query])

    similarities = cosine_similarity(
        query_vector, policy_vectors
    )[0]

    top_indices = similarities.argsort()[::-1][:top_k]

    results = []

    for index in top_indices:
        if similarities[index] > 0:
            results.append({
                "source": policy_chunks[index]["source"],
                "content": policy_chunks[index]["content"],
                "similarity": round(float(similarities[index]), 4)
            })

    return results


def generate_answer(query):
    results = retrieve_policy(query)

    if not results:
        return {
            "answer": "No relevant policy found. Please contact human support.",
            "sources": [],
            "escalation": True
        }

    context = "\n\n".join(
        f"[{item['source']}] {item['content']}"
        for item in results
    )

    messages = [
        {
            "role": "system",
            "content": (
                "POLICY ASSISTANT\n"
                "Answer using only the supplied policy context. "
                "Never invent policy rules. "
                "If the context does not support an answer, "
                "recommend human support."
            )
        },
        {
            "role": "user",
            "content": (
                f"CONTEXT:\n{context}\n"
                f"QUESTION:\n{query}"
            )
        }
    ]

    response = mock_llm.chat(messages)
    answer = response.choices[0].message.content

    not_found = (
        "could not find" in answer.lower()
        or "no relevant policy" in answer.lower()
    )

    return {
        "answer": answer,
        "sources": list(dict.fromkeys(
            item["source"] for item in results
        )),
        "escalation": not_found
    }



def retrieve(query, k=3):
    results = retrieve_policy(query, top_k=k)

    return [
        {
            "source": item["source"],
            "score": item["similarity"],
            "text": item["content"]
        }
        for item in results
    ]
