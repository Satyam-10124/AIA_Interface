import argparse
from dotenv import load_dotenv
from pathlib import Path
import os

# Load environment variables from .env file
load_dotenv()

# It's recommended to import crew components after loading the .env
from src.restaurant_booking_agent.crew import RestaurantBookingCrew


def run_crew(email_file: str) -> None:
    """
    Runs the restaurant booking crew with the given email file.

    Args:
        email_file (str): The path to the email file containing the booking request.
    """
    email_path = Path(email_file)
    if not email_path.exists():
        print(f"Error: Email file not found at '{email_file}'")
        return

    print(f"🚀 Starting the crew for email: {email_file}...")

    # The SERPER_API_KEY is loaded by load_dotenv() and used by SerperDevTool internally
    # No need to pass it explicitly if it's in the .env file.
    if not os.getenv("SERPER_API_KEY"):
        print("Warning: SERPER_API_KEY is not set. The agent's search capabilities will be limited.")

    try:
        crew = RestaurantBookingCrew(email_file_path=str(email_path))
        result = crew.run()
        print("\n✅ Crew execution finished successfully!")
        print("\nCrew Final Result:")
        print("==================")
        print(result)
        print("\n📄 You can find the drafted email response in 'drafted_email.out'.")
    except Exception as e:
        print(f"\n❌ An error occurred during crew execution: {e}")


def main():
    """
    Main function to parse command-line arguments and run the crew.
    """
    parser = argparse.ArgumentParser(description="Run the Restaurant Booking Agent Crew.")
    parser.add_argument(
        "--email-file",
        type=str,
        required=True,
        help="The path to the .txt file containing the email reservation request.",
    )
    args = parser.parse_args()
    run_crew(args.email_file)


if __name__ == "__main__":
    main()
