import pytest
from tools.gcp_training_analyzer import run

def test_gcp_training_analyzer():
    input_data = {
        "training_records": [
            {"staff_id": "ST001", "completed_trainings": ["GCP", "Protocol"]}
        ],
        "staff_roles": {"ST001": "CRC"},
        "training_requirements": {"CRC": ["GCP", "Protocol", "Safety"]}
    }
    result = run(input_data)
    assert "error" not in result
    assert "training_gaps" in result
