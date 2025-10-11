from crewai import Crew, Process
from .agents import ClaimTriageAgents
from .tasks import ClaimTriageTasks

class ClaimTriageCrew:
    """
    Defines the crew for triaging insurance claims.
    """

    def __init__(self, claim_file_path: str):
        self.claim_file_path = claim_file_path
        self.agents = ClaimTriageAgents()
        self.tasks = ClaimTriageTasks()

    def run(self) -> str:
        """
        Initializes and runs the claim triage crew.
        """
        # Instantiate agents
        intake_agent = self.agents.claim_intake_agent()
        investigator_agent = self.agents.fraud_investigator_agent()
        analyst_agent = self.agents.triage_analyst_agent()

        # Instantiate tasks
        intake_task = self.tasks.intake_and_parse_claim(
            agent=intake_agent, claim_file_path=self.claim_file_path
        )
        investigation_task = self.tasks.investigate_for_fraud(
            agent=investigator_agent, context=[intake_task]
        )
        analysis_task = self.tasks.analyze_and_classify(
            agent=analyst_agent, context=[investigation_task]
        )

        # Form the crew
        crew = Crew(
            agents=[intake_agent, investigator_agent, analyst_agent],
            tasks=[intake_task, investigation_task, analysis_task],
            process=Process.sequential,
            verbose=2,
        )

        result = crew.kickoff()
        return result
