
def generate_response(question, retrieved_chunks):

    if not retrieved_chunks:
        return (
            "I could not find a relevant policy for your question. "
            "Please contact a human support agent."
        )

    # Collect unique policy information
    unique_lines = []

    for chunk in retrieved_chunks:

        lines = chunk["content"].splitlines()

        for line in lines:

            line = line.strip()

            if line and line not in unique_lines:
                unique_lines.append(line)

    # Build a concise mock response
    context = "\n".join(unique_lines)

    answer = (
        "Based on the simulated project policy:\n\n"
        + context
        + "\n\nRecommended next step:\n"
        "The support team should review the relevant details "
        "and follow the applicable policy. "
        "Unresolved cases should be escalated to a human support agent."
    )

    return answer
