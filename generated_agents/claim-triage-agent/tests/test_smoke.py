import pytest
from src.restaurant_booking_agent.crew import RestaurantBookingCrew

def test_crew_initialization():
    """
    Test that the RestaurantBookingCrew can be initialized without errors.
    """
    # Define a dummy file path for initialization
    dummy_email_file = "data/sample_email.txt"
    
    try:
        crew_instance = RestaurantBookingCrew(email_file_path=dummy_email_file)
        assert crew_instance is not None
        assert crew_instance.email_file_path == dummy_email_file
        # Check if agents and tasks are initialized (simple check)
        assert hasattr(crew_instance, 'agents')
        assert hasattr(crew_instance, 'tasks')
    except Exception as e:
        pytest.fail(f"Crew initialization failed with an exception: {e}")
