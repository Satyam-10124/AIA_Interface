from textwrap import dedent
from crewai import Task
from crewai.agent import Agent

class ClaimTriageTasks:
    """
    A class to define the tasks for the claim triage crew.
    """

    def intake_and_parse_claim(self, agent: Agent, claim_file_path: str) -> Task:
        """
        Task to read a claim file and extract its contents.
        """
        return Task(
            description=dedent(f"""
                Read the insurance claim from the file at the path: {claim_file_path}.
                Use your tool to open and read the contents of the file.
                Extract all relevant information, including claimant details,
                policy information, incident description, and claimed amount.
                Present the extracted data in a clear, structured format.
            """),
            expected_output=dedent("""
                A structured summary of the insurance claim's contents, including
                all key data points.
            """),
            agent=agent,
        )

    def investigate_for_fraud(self, agent: Agent, context: list[Task]) -> Task:
        """
        Task to investigate the claim for red flags and inconsistencies.
        """
        return Task(
            description=dedent("""
                Based on the provided claim details, conduct a thorough investigation
                to identify any potential signs of fraud. Use your search tool to:
                1. Verify the weather conditions at the location and date of the incident.
                2. Check for news reports or public records of the incident.
                3. Look for common fraud indicators (e.g., inconsistencies in the
                   narrative, recent policy changes, multiple similar claims).
                Compile a report of your findings, highlighting any suspicious details.
            """),
            expected_output=dedent("""
                An investigative report detailing the findings. The report should
                list all checks performed and explicitly state whether any red flags
                were found. If red flags are found, explain them clearly.
            """),
            agent=agent,
            context=context,
        )

    def analyze_and_classify(self, agent: Agent, context: list[Task]) -> Task:
        """
        Task to synthesize all information and produce a final triage report.
        """
        return Task(
            description=dedent("""
                Review the initial claim data and the fraud investigation report.
                Based on all available information, make a final triage decision.
                Categorize the claim into one of three categories:
                - 'Standard': No complexities or red flags.
                - 'Complex': The claim is legitimate but requires special handling
                  due to its nature (e.g., high value, unusual circumstances).
                - 'Potential Fraud': Red flags or significant inconsistencies were found.

                Generate a final JSON object with your analysis.
            """),
            expected_output=dedent("""
                A JSON object containing the final triage analysis. The JSON must
                include the following keys:
                - 'claim_id': The original claim ID (if available, otherwise use a placeholder).
                - 'category': One of 'Standard', 'Complex', or 'Potential Fraud'.
                - 'fraud_confidence_score': A float between 0.0 and 1.0.
                - 'summary': A concise text summary explaining the classification decision
                  and referencing key findings from the investigation.

                Example Output:
                {
                  "claim_id": "CL-12345",
                  "category": "Potential Fraud",
                  "fraud_confidence_score": 0.85,
                  "summary": "Claim flagged for potential fraud due to inconsistencies in the incident description. Web search found no news reports of the alleged event, and weather data contradicts the stated conditions."
                }
            """),
            agent=agent,
            context=context,
        )