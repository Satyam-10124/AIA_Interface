import json
from pathlib import Path
from typing import Dict, List, Any

# --- Mock Database Interaction ---
def get_mock_db_path() -> Path:
    """Returns the path to the mock bookings JSON file."""
    # Assumes the script is run from the project root
    return Path("data/mock_bookings.json")


def read_bookings() -> List[Dict[str, Any]]:
    """Reads all bookings from the mock JSON database."""
    db_path = get_mock_db_path()
    if not db_path.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(db_path, "w") as f:
            json.dump([], f)
        return []
    with open(db_path, "r") as f:
        return json.load(f)


def write_bookings(bookings: List[Dict[str, Any]]) -> None:
    """Writes a list of bookings to the mock JSON database."""
    with open(get_mock_db_path(), "w") as f:
        json.dump(bookings, f, indent=2)


class BookingTools:
    """A suite of tools for managing restaurant bookings."""

    @staticmethod
    def check_availability(date: str, time: str) -> str:
        """
        Checks if a table is available for a given date and time.
        Returns a confirmation message if available, or a list of alternative times if not.
        """
        bookings = read_bookings()
        
        # Check for direct conflict
        conflict = any(
            booking["date"] == date and booking["time"] == time for booking in bookings
        )

        if not conflict:
            return f"Success: The time slot {time} on {date} is available."
        else:
            # Simple logic to suggest alternative times
            alternatives = ["18:00", "18:30", "21:00", "21:30"]
            available_alternatives = [alt for alt in alternatives if not any(
                b["date"] == date and b["time"] == alt for b in bookings
            )]
            if available_alternatives:
                return f"Conflict: The requested time {time} on {date} is booked. Suggest these alternative times: {', '.join(available_alternatives)}."
            else:
                return f"Conflict: The requested time {time} on {date} is booked, and no other times are available on that day."

    @staticmethod
    def create_booking(date: str, time: str, party_size: int, customer_name: str, customer_contact: str) -> str:
        """
        Creates a new booking in the system for a given date, time, party size, and customer details.
        """
        bookings = read_bookings()
        new_booking = {
            "name": customer_name,
            "contact": customer_contact,
            "party_size": party_size,
            "date": date,
            "time": time,
        }
        bookings.append(new_booking)
        write_bookings(bookings)
        return f"Success: Booking confirmed for {customer_name} for {party_size} people on {date} at {time}."


class EmailTools:
    """A suite of tools for drafting emails."""

    @staticmethod
    def draft_response_email(recipient_name: str, subject: str, body: str, output_filename: str = "drafted_email.out") -> str:
        """Saves a drafted email to a local file."""
        draft_content = f"Recipient Name: {recipient_name}\n"
        draft_content += f"Subject: {subject}\n"
        draft_content += "---\n"
        draft_content += body

        try:
            with open(output_filename, "w") as f:
                f.write(draft_content)
            return f"Successfully drafted email for {recipient_name} and saved to '{output_filename}'."
        except IOError as e:
            return f"Error: Failed to write email draft to file. {e}"
