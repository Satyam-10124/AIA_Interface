import argparse
from dotenv import load_dotenv
from .crew import ClaimTriageCrew

def main():
    """
    Main function to run the claim triage crew from the command line.
    """
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run the Claim Triage Agent Crew.")
    parser.add_argument(
        "--claim-file",
        type=str,
        required=True,
        help="The path to the JSON file containing the claim details.",
    )
    args = parser.parse_args()

    try:
        crew = ClaimTriageCrew(claim_file_path=args.claim_file)
        result = crew.run()
        print("\n--- Triage Analysis Complete ---")
        print(result)
        print("---------------------------------")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
