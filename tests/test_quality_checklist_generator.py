import pytest
from tools.quality_checklist_generator import run

def test_quality_checklist_generator():
    input_data = {
        "review_type": "monitoring_visit",
        "study_phase": "ongoing"
    }
    result = run(input_data)
    assert "error" not in result
    assert "checklist" in result
    assert len(result["checklist"]) > 0
