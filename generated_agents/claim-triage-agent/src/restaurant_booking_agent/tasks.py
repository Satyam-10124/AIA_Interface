from crewai import Task
from crewai.agent import Agent
from typing import Dict, Any

class RestaurantBookingTasks:
    """A class to define the tasks for the restaurant booking crew."""

    def parse_request_task(self, agent: Agent, email_file_path: str) -> Task:
        """
        Task to parse the customer's email request.
        """
        return Task(
            description=f"Read and parse the customer's email from the file: '{email_file_path}'. "
                        "Extract the customer's name, contact information, desired date, time, and party size. "
                        "Return these details in a structured JSON format.",
            expected_output="A JSON object containing the extracted booking details: "
                            "{'customer_name': '...', 'customer_contact': '...', 'date': 'YYYY-MM-DD', "
                            "'time': 'HH:MM', 'party_size': ...}.",
            agent=agent,
        )

    def check_and_book_task(self, agent: Agent, context: list[Task]) -> Task:
        """
        Task to check availability and book a table if possible.
        """
        return Task(
            description="Based on the parsed booking details, first check for table availability. "
                        "If the requested slot is available, proceed to create the booking with all customer details. "
                        "If the slot is not available, report back with suggested alternative times.",
            expected_output="If booking is successful, a confirmation message with all booking details. "
                            "If the slot is unavailable, a message detailing the conflict and listing alternative times.",
            agent=agent,
            context=context,
        )

    def draft_response_task(self, agent: Agent, context: list[Task]) -> Task:
        """
        Task to draft an email response to the customer.
        """
        return Task(
            description="Draft an email response to the customer based on the outcome of the booking attempt. "
                        "If the booking was successful, draft a confirmation email. "
                        "If the booking failed, draft a polite email suggesting the alternative times provided.",
            expected_output="The full text of the drafted email, saved to a local file. The output of the tool call will confirm the filename.",
            agent=agent,
            context=context,
        )
