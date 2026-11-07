
from src.copilot import run_copilot


def main():

    while True:

        print("\n" + "=" * 55)
        print("SWIGGY INSTAMART CUSTOMER INTELLIGENCE")
        print("SUPPORT CO-PILOT")
        print("=" * 55)

        print("\n1. Run Customer Intelligence Co-Pilot")
        print("2. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":

            try:
                print("\nENTER CUSTOMER DETAILS")
                print("-" * 35)

                frequency = float(input("Enter delivered orders: "))
                monetary = float(input("Enter total spending (Rs): "))

                if frequency < 0 or monetary < 0:
                    print("Please enter non-negative values.")
                    continue

                complaint = input("\nEnter customer complaint: ")
                question = input("Enter customer policy question: ")

                run_copilot(
                    frequency=frequency,
                    monetary=monetary,
                    complaint=complaint,
                    question=question
                )

            except ValueError:
                print("Invalid number. Please enter valid numeric values.")

            except Exception as error:
                print("An error occurred:", error)

        elif choice == "2":

            print("\nThank you for using the Customer Intelligence Co-Pilot!")
            break

        else:
            print("\nInvalid choice. Please select 1 or 2.")


if __name__ == "__main__":
    main()
