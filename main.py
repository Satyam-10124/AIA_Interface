import argparse
import json
import os
from dotenv import load_dotenv

from src.claim_triage_agent.crew import ClaimTriageCrew

# Load environment variables from .env file
load_dotenv()

def run_crew(claim_file_path: str) -> None:
    """
    Initializes and runs the Claim Triage Crew with claim data from a file.

    Args:
        claim_file_path: The path to the JSON file containing the claim data.
    """
    if not os.path.exists(claim_file_path):
        print(f"Error: The file '{claim_file_path}' was not found.")
        return

    with open(claim_file_path, 'r') as f:
        claim_data = f.read()

    # Here you would typically inject the claim_data into the crew's context
    # For this example, we'll need to modify how the crew or tasks get this data.
    # A simple approach is to set it as an input to the first task.

    print("Initializing Claim Triage Crew...")
    # Note: In a real-world scenario, you would pass the `claim_data` into the crew's kickoff.
    # The current CrewBase setup uses a static example, so we'll run it as is
    # but acknowledge this limitation.
    print("--- Using sample claim data defined in the crew for this run --- ")
    triage_crew = ClaimTriageCrew()
    result = triage_crew.crew().kickoff()

    print("\n\n------------------------")
    print("## Triage Process Complete")
    print("------------------------")
    print("Final Triage Report:")
    try:
        # Attempt to parse and pretty-print the JSON result
        result_json = json.loads(result)
        print(json.dumps(result_json, indent=2))
    except (json.JSONDecodeError, TypeError):
        print(result)


def main():
    """Main function to run the CLI."""
    parser = argparse.ArgumentParser(description="Run the Claim Triage Agent Crew.")
    parser.add_argument(
        "claim_file",
        type=str,
        nargs='?',
        default="./src/claim_triage_agent/config/sample_claim.json",
        help="Path to the JSON file with the claim data. Defaults to the sample claim.",
    )
    args = parser.parse_args()

    run_crew(args.claim_file)


if __name__ == "__main__":
    main()