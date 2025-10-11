from textwrap import dedent
from crewai import Agent
from crewai_tools import FileReadTool, SerperDevTool

class ClaimTriageAgents:
    """
    A class to instantiate the agents for the claim triage crew.
    """

    def __init__(self):
        self.search_tool = SerperDevTool()
        self.file_read_tool = FileReadTool()

    def claim_intake_agent(self) -> Agent:
        """
        Agent responsible for reading and parsing the initial claim data.
        """
        return Agent(
            role="Insurance Claim Intake Specialist",
            goal=dedent("""
                Read an insurance claim file, parse its contents, and extract
                key details such as claimant information, policy number, incident
                description, and claimed amount.
            """),
            backstory=dedent("""
                As a meticulous and detail-oriented specialist, your primary function
                is to be the first point of contact for all incoming insurance claims.
                You ensure that all necessary information is accurately extracted from
                the provided file, laying a clean foundation for the rest of the
                triage process.
            """),
            tools=[self.file_read_tool],
            allow_delegation=False,
            verbose=True,
        )

    def fraud_investigator_agent(self) -> Agent:
        """
        Agent that investigates the claim for potential fraud using web searches.
        """
        return Agent(
            role="Fraud Investigator",
            goal=dedent("""
                Investigate the details of an insurance claim to identify any
                potential red flags or inconsistencies that might indicate fraud.
                Verify facts using external web searches.
            """),
            backstory=dedent("""
                With a background in forensic analysis and a keen eye for deceit,
                you specialize in uncovering the truth. You use your web search
                prowess to cross-reference claim details against public records,
                news reports, and weather data to validate the claimant's story.
                Your work is crucial in protecting the company from fraudulent activities.
            """),
            tools=[self.search_tool],
            allow_delegation=False,
            verbose=True,
        )

    def triage_analyst_agent(self) -> Agent:
        """
        Agent that analyzes all findings and makes a final triage decision.
        """
        return Agent(
            role="Senior Triage Analyst",
            goal=dedent("""
                Synthesize all gathered information and investigative findings to
                classify an insurance claim as 'Standard', 'Complex', or
                'Potential Fraud'. Produce a final summary report.
            """),
            backstory=dedent("""
                You are the final decision-maker in the automated triage process.
                With years of experience in claims processing, you can weigh
                evidence, assess complexity, and identify subtle indicators of fraud.
                You take the structured data from the Intake Specialist and the
                investigative report from the Fraud Investigator to produce a clear,
                concise, and actionable triage recommendation.
            """),
            allow_delegation=False,
            verbose=True,
        )