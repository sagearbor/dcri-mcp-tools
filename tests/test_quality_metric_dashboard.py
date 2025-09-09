import pytest
from tools.quality_metric_dashboard import run

def test_quality_metric_dashboard():
    input_data = {
        "metrics_data": {
            "enrollment": {"actual": 80, "target": 100},
            "data_quality": {"queries": 10, "data_points": 1000}
        }
    }
    result = run(input_data)
    assert "error" not in result
    assert "kpis" in result
