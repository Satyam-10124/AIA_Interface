import pytest
from src.claim_triage_agent.crew import ClaimTriageCrew

def test_crew_initialization():
    """
    Test that the ClaimTriageCrew can be initialized without errors.
    """
    # A dummy file path is sufficient for initialization testing
    claim_file_path = "dummy_claim.json"

    try:
        crew_instance = ClaimTriageCrew(claim_file_path=claim_file_path)
        # Assert that the main components are not None
        assert crew_instance is not None
        assert crew_instance.agents is not None
        assert crew_instance.tasks is not None
        assert crew_instance.claim_file_path == claim_file_path
    except Exception as e:
        pytest.fail(f"Crew initialization failed with an exception: {e}")
