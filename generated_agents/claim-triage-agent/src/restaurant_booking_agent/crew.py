from crewai import Crew, Process
from .agents import RestaurantBookingAgents
from .tasks import RestaurantBookingTasks

class RestaurantBookingCrew:
    """
    Defines the crew responsible for handling restaurant booking requests.
    """

    def __init__(self, email_file_path: str):
        self.email_file_path = email_file_path
        self.agents = RestaurantBookingAgents()
        self.tasks = RestaurantBookingTasks()

    def run(self) -> str:
        """
        Initializes and runs the booking crew.
        """
        # Define Agents
        request_parser = self.agents.request_parser_agent()
        availability_checker = self.agents.availability_checker_agent()
        communication_specialist = self.agents.communication_agent()

        # Define Tasks
        parse_task = self.tasks.parse_request_task(
            agent=request_parser,
            email_file_path=self.email_file_path
        )

        check_and_book_task = self.tasks.check_and_book_task(
            agent=availability_checker,
            context=[parse_task]
        )

        draft_response_task = self.tasks.draft_response_task(
            agent=communication_specialist,
            context=[check_and_book_task, parse_task]
        )

        # Assemble Crew
        crew = Crew(
            agents=[request_parser, availability_checker, communication_specialist],
            tasks=[parse_task, check_and_book_task, draft_response_task],
            process=Process.sequential,
            verbose=2,
        )

        # Kick off the crew's work
        result = crew.kickoff()
        return result
