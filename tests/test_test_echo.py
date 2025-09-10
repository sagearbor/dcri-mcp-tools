import pytest
from tools.test_echo import run

def test_echo_basic():
    """Test basic echo functionality."""
    input_data = {"text": "Hello DCRI"}
    result = run(input_data)
    assert result["output"] == "Hello DCRI"

def test_echo_empty():
    """Test echo with empty input."""
    input_data = {}
    result = run(input_data)
    assert result["output"] == "No text provided"

def test_echo_complex_message():
    """Test echo with complex clinical research message."""
    input_data = {"text": "Clinical trial DCR-2024-001 patient enrollment status: 125/200 subjects randomized"}
    result = run(input_data)
    assert result["output"] == "Clinical trial DCR-2024-001 patient enrollment status: 125/200 subjects randomized"

def test_echo_special_characters():
    """Test echo with special characters common in clinical data."""
    input_data = {"text": "Patient ID: P-001@SITE_01, AE: Grade 3/4 neutropenia (>99% confidence)"}
    result = run(input_data)
    assert result["output"] == "Patient ID: P-001@SITE_01, AE: Grade 3/4 neutropenia (>99% confidence)"