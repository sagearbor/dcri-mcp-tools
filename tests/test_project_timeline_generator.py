"""Tests for Project Timeline Generator"""
import pytest
from tools.project_timeline_generator import run
from datetime import datetime

def test_timeline_generation():
    result = run({
        'start_date': '2024-01-01',
        'n_subjects': 100,
        'n_sites': 10,
        'treatment_duration_days': 180
    })
    assert 'phases' in result
    assert len(result['phases']) > 0
    assert 'milestones' in result
    assert 'total_duration_days' in result

def test_milestone_calculation():
    result = run({
        'start_date': '2024-01-01',
        'n_subjects': 50
    })
    milestone_names = [m['name'] for m in result['milestones']]
    assert 'First Patient In' in milestone_names
    assert 'Last Patient Out' in milestone_names
    assert 'Database Lock' in milestone_names

def test_gantt_data():
    result = run({'start_date': '2024-01-01'})
    assert 'gantt_chart_data' in result
    assert len(result['gantt_chart_data']) > 0
