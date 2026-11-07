
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).resolve().parent.parent

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from mock_llm import generate_response

POLICY_DIR = PROJECT_DIR / "policies"


def load_policies():

    documents = []

    for filepath in POLICY_DIR.glob("*.txt"):

        with open(filepath, "r", encoding="utf-8") as file:
            documents.append({
                "source": filepath.name,
                "content": file.read()
            })

    return documents


def create_chunks(documents):

    chunks = []

    for doc in documents:

        lines = [
            line.strip()
            for line in doc["content"].splitlines()
            if line.strip()
        ]

        if not lines:
            continue

        title = lines[0]
        rules = lines[1:]

        for i in range(0, len(rules), 2):

            chunks.append({
                "source": doc["source"],
                "content": title + "\n" + "\n".join(rules[i:i + 2])
            })

    return chunks


documents = load_policies()
policy_chunks = create_chunks(documents)

if not policy_chunks:
    raise ValueError("No policy documents found.")

vectorizer = TfidfVectorizer(stop_words="english")

policy_vectors = vectorizer.fit_transform(
    [chunk["content"] for chunk in policy_chunks]
)


def retrieve_policy(query, top_k=3):

    query_vector = vectorizer.transform([query])

    similarities = cosine_similarity(
        query_vector,
        policy_vectors
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
            "answer": (
                "I could not find a relevant policy. "
                "Please contact a human support agent."
            ),
            "sources": [],
            "escalation": True
        }

    answer = generate_response(query, results)

    return {
        "answer": answer,
        "sources": list(dict.fromkeys(
            result["source"] for result in results
        )),
        "escalation": False
    }


if __name__ == "__main__":

    question = input("Ask a customer support question: ")

    response = generate_answer(question)

    print("\nRAG SUPPORT ASSISTANT")
    print("=" * 45)
    print(response["answer"])
    print("\nSources:", response["sources"])
    print("Escalation required:", response["escalation"])
