
from src.churn_prediction import predict_churn
from src.triage import process_ticket
from src.policy_rag import generate_answer


def analyze_customer(frequency, monetary):

    return predict_churn(frequency, monetary)


def analyze_ticket(description, priority="Medium", status="Open"):

    return process_ticket(
        description=description,
        priority=priority,
        status=status
    )


def answer_customer_query(question):

    return generate_answer(question)


def run_copilot(frequency, monetary, complaint, question):

    print("\nSWIGGY INSTAMART CUSTOMER INTELLIGENCE")
    print("=" * 55)

    # Part 1: Churn prediction
    print("\n1. CUSTOMER CHURN ANALYSIS")
    churn = analyze_customer(frequency, monetary)

    print("Prediction:", churn["prediction"])
    print("Churn probability:", churn["churn_probability"], "%")

    # Part 2: Ticket classification and routing
    print("\n2. SUPPORT TICKET TRIAGE")
    ticket = analyze_ticket(complaint)

    print("Category:", ticket["category"])
    print("Priority:", ticket["priority"])
    print("Assigned team:", ticket["team"])
    print("Status:", ticket["status"])

    # Part 3: Policy retrieval and response
    print("\n3. POLICY-BASED CUSTOMER SUPPORT")
    response = answer_customer_query(question)

    print("Customer question:", question)
    print("\nAssistant response:")
    print(response["answer"])

    print("\nPolicy sources:", response["sources"])
    print("Escalation required:", response["escalation"])

    return {
        "churn": churn,
        "ticket": ticket,
        "support": response
    }


if __name__ == "__main__":

    print("CUSTOMER INTELLIGENCE SUPPORT CO-PILOT")
    print("=" * 50)

    frequency = float(input("Enter delivered orders: "))
    monetary = float(input("Enter total spending (Rs): "))
    complaint = input("Enter customer complaint: ")
    question = input("Enter customer policy question: ")

    run_copilot(
        frequency,
        monetary,
        complaint,
        question
    )
