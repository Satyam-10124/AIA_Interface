from crewai import Agent, LLM
from crewai_tools import FileReadTool, SerperDevTool

from .tools.booking_tools import (
    check_availability_tool,
    create_booking_tool,
    draft_response_email_tool,
)

# Initialize tools
file_read_tool = FileReadTool()
serper_tool = SerperDevTool()

class RestaurantBookingAgents:
    """A class to define the agents for the restaurant booking crew."""

    def request_parser_agent(self) -> Agent:
        """
        Parses customer emails to extract booking details.
        """
        return Agent(
            role="Request Parser",
            goal="Accurately extract all booking details from a customer's email request. "
                 "These details include name, contact info, party size, desired date, and time.",
            backstory="You are a meticulous assistant, highly skilled in understanding "
                      "natural language and identifying key information within unstructured text. "
                      "Your primary function is to read customer emails and organize their "
                      "requests into a structured format for the booking system.",
            tools=[file_read_tool, serper_tool],
            llm=LLM(model="gemini/gemini-2.5-pro"),
            verbose=True,
            allow_delegation=False,
        )

    def availability_checker_agent(self) -> Agent:
        """
        Checks for table availability and creates bookings.
        """
        return Agent(
            role="Availability Checker",
            goal="Check for table availability using the booking calendar tool based on the parsed request. "
                 "If the slot is available, create a new reservation in the system. "
                 "If not, identify and propose alternative available times.",
            backstory="You are the guardian of the restaurant's reservation calendar. "
                      "With direct access to the booking system, you efficiently verify "
                      "table availability, secure slots for customers, and find viable "
                      "alternatives when the requested time is unavailable. You are precise and fast.",
            tools=[check_availability_tool, create_booking_tool],
            llm=LLM(model="gemini/gemini-2.5-pro"),
            verbose=True,
            allow_delegation=False,
        )

    def communication_agent(self) -> Agent:
        """
        Drafts clear and professional email responses to customers.
        """
        return Agent(
            role="Communication Specialist",
            goal="Draft clear, professional, and friendly email responses to customers. "
                 "This includes sending booking confirmations with all the details, "
                 "or suggesting alternative times if the original request couldn't be met.",
            backstory="You are the voice of the restaurant. Your communication is always "
                      "courteous, clear, and helpful. You craft perfect email responses "
                      "that make customers feel valued, whether you're confirming their "
                      "booking or helping them find a different time to dine.",
            tools=[draft_response_email_tool],
            llm=LLM(model="gemini/gemini-2.5-pro"),
            verbose=True,
            allow_delegation=False,
        )
