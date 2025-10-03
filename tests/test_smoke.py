import pytest
from src.claim_triage_agent.crew import ClaimTriageCrew


def test_crew_initialization():
    """
    Tests that the ClaimTriageCrew can be initialized without errors.
    """
    try:
        crew_instance = ClaimTriageCrew()
        assert crew_instance is not None, "Crew instance should not be None"
        assert crew_instance.crew() is not None, "Crew object should be created"
    except Exception as e:
        pytest.fail(f"Crew initialization failed with an exception: {e}")