import pytest
from tools.patient_diary_checker import run


def test_patient_diary_checker_basic():
    """Test basic diary compliance checking."""
    input_data = {
        "patient_id": "P001",
        "diary_entries": [
            {
                "date": "2024-01-01",
                "entry_time": "09:00",
                "symptoms": {"pain": 3, "fatigue": 2},
                "medications_taken": True,
                "side_effects": None
            },
            {
                "date": "2024-01-02", 
                "entry_time": "09:15",
                "symptoms": {"pain": 4, "fatigue": 3},
                "medications_taken": True,
                "side_effects": "mild nausea"
            }
        ],
        "expected_frequency": "daily",
        "monitoring_period_days": 7
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["patient_id"] == "P001"
    assert result["compliance_summary"]["overall_compliance_rate"] >= 0
    assert len(result["compliance_analysis"]["daily_entries"]) > 0
    assert "compliance_alerts" in result


def test_patient_diary_checker_missed_entries():
    """Test detection of missed diary entries."""
    input_data = {
        "patient_id": "P002",
        "diary_entries": [
            {"date": "2024-01-01", "entry_time": "09:00", "symptoms": {"pain": 2}},
            {"date": "2024-01-03", "entry_time": "09:30", "symptoms": {"pain": 3}},
            {"date": "2024-01-06", "entry_time": "10:00", "symptoms": {"pain": 1}}
        ],
        "expected_frequency": "daily",
        "monitoring_period_days": 7,
        "study_start_date": "2024-01-01"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["compliance_summary"]["missed_entries"] > 0
    assert len(result["compliance_alerts"]) > 0
    
    # Should identify specific missed days
    missed_days = result["compliance_analysis"]["missed_days"]
    assert len(missed_days) > 0
    assert "2024-01-02" in missed_days


def test_patient_diary_checker_timing_analysis():
    """Test entry timing analysis."""
    input_data = {
        "patient_id": "P003",
        "diary_entries": [
            {"date": "2024-01-01", "entry_time": "09:00", "symptoms": {"pain": 2}},
            {"date": "2024-01-02", "entry_time": "14:30", "symptoms": {"pain": 3}},
            {"date": "2024-01-03", "entry_time": "21:45", "symptoms": {"pain": 2}},
            {"date": "2024-01-04", "entry_time": "08:15", "symptoms": {"pain": 1}}
        ],
        "expected_entry_time": "09:00",
        "time_window_hours": 2
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "timing_analysis" in result
    timing = result["timing_analysis"]
    assert "on_time_entries" in timing
    assert "late_entries" in timing
    assert timing["average_entry_time"] is not None


def test_patient_diary_checker_symptom_tracking():
    """Test symptom score tracking and trends."""
    input_data = {
        "patient_id": "P004",
        "diary_entries": [
            {"date": "2024-01-01", "symptoms": {"pain": 5, "nausea": 2, "fatigue": 4}},
            {"date": "2024-01-02", "symptoms": {"pain": 4, "nausea": 3, "fatigue": 3}},
            {"date": "2024-01-03", "symptoms": {"pain": 6, "nausea": 1, "fatigue": 5}},
            {"date": "2024-01-04", "symptoms": {"pain": 3, "nausea": 0, "fatigue": 2}},
            {"date": "2024-01-05", "symptoms": {"pain": 7, "nausea": 4, "fatigue": 6}}
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "symptom_analysis" in result
    symptom_analysis = result["symptom_analysis"]
    assert "symptom_trends" in symptom_analysis
    assert "severity_patterns" in symptom_analysis
    
    # Should detect pain increase trend
    pain_trend = symptom_analysis["symptom_trends"]["pain"]
    assert pain_trend["trend_direction"] in ["increasing", "decreasing", "stable", "variable"]


def test_patient_diary_checker_medication_compliance():
    """Test medication compliance tracking."""
    input_data = {
        "patient_id": "P005",
        "diary_entries": [
            {"date": "2024-01-01", "medications_taken": True, "missed_doses": 0},
            {"date": "2024-01-02", "medications_taken": True, "missed_doses": 0},
            {"date": "2024-01-03", "medications_taken": False, "missed_doses": 1},
            {"date": "2024-01-04", "medications_taken": True, "missed_doses": 0},
            {"date": "2024-01-05", "medications_taken": True, "missed_doses": 0}
        ],
        "expected_frequency": "daily"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "medication_compliance" in result
    med_compliance = result["medication_compliance"]
    assert "compliance_rate" in med_compliance
    assert med_compliance["missed_doses_count"] == 1
    assert len(med_compliance["missed_dose_dates"]) == 1


def test_patient_diary_checker_side_effects_monitoring():
    """Test side effects monitoring."""
    input_data = {
        "patient_id": "P006",
        "diary_entries": [
            {"date": "2024-01-01", "side_effects": None},
            {"date": "2024-01-02", "side_effects": "mild headache"},
            {"date": "2024-01-03", "side_effects": "nausea, dizziness"},
            {"date": "2024-01-04", "side_effects": "severe headache"},
            {"date": "2024-01-05", "side_effects": None}
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "side_effects_analysis" in result
    side_effects = result["side_effects_analysis"]
    assert "common_side_effects" in side_effects
    assert "severity_distribution" in side_effects
    
    # Should identify headache as common side effect
    common_effects = side_effects["common_side_effects"]
    headache_found = any("headache" in effect["effect"].lower() for effect in common_effects)
    assert headache_found


def test_patient_diary_checker_quality_scores():
    """Test diary entry quality scoring."""
    input_data = {
        "patient_id": "P007",
        "diary_entries": [
            {
                "date": "2024-01-01",
                "entry_time": "09:00",
                "symptoms": {"pain": 3, "fatigue": 2},
                "medications_taken": True,
                "side_effects": "mild nausea",
                "additional_notes": "Feeling better today"
            },
            {
                "date": "2024-01-02",
                "symptoms": {"pain": 4},
                "medications_taken": True
                # Missing some fields
            }
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "quality_assessment" in result
    quality = result["quality_assessment"]
    assert "average_completeness_score" in quality
    assert "data_quality_issues" in quality
    assert quality["average_completeness_score"] >= 0


def test_patient_diary_checker_compliance_patterns():
    """Test compliance pattern analysis."""
    input_data = {
        "patient_id": "P008",
        "diary_entries": [
            {"date": "2024-01-01", "entry_time": "09:00"},  # Monday
            {"date": "2024-01-02", "entry_time": "09:15"},  # Tuesday
            # Missing Wednesday
            {"date": "2024-01-04", "entry_time": "14:30"},  # Thursday (late)
            {"date": "2024-01-05", "entry_time": "09:00"},  # Friday
            # Missing Weekend
            {"date": "2024-01-08", "entry_time": "09:30"},  # Monday
        ],
        "expected_frequency": "daily",
        "monitoring_period_days": 14
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "compliance_patterns" in result
    patterns = result["compliance_patterns"]
    assert "day_of_week_compliance" in patterns
    assert "time_patterns" in patterns
    
    # Should identify weekend compliance issues
    dow_compliance = patterns["day_of_week_compliance"]
    assert "patterns_identified" in patterns


def test_patient_diary_checker_alerts_generation():
    """Test compliance alerts generation."""
    input_data = {
        "patient_id": "P009",
        "diary_entries": [
            {"date": "2024-01-01", "symptoms": {"pain": 8}},  # High pain score
            {"date": "2024-01-04", "symptoms": {"pain": 3}},  # 3-day gap
            {"date": "2024-01-05", "medications_taken": False},  # Missed meds
            {"date": "2024-01-06", "side_effects": "severe headache, vomiting"}  # Severe AE
        ],
        "alert_thresholds": {
            "max_missed_days": 2,
            "high_symptom_threshold": 7,
            "severe_side_effects": ["severe", "vomiting"]
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["compliance_alerts"]) > 0
    
    # Check for specific alert types
    alert_types = [alert["type"] for alert in result["compliance_alerts"]]
    assert "missed_entries" in alert_types
    assert "high_symptom_score" in alert_types or "severe_side_effect" in alert_types


def test_patient_diary_checker_intervention_recommendations():
    """Test intervention recommendations."""
    input_data = {
        "patient_id": "P010",
        "diary_entries": [
            {"date": "2024-01-01", "symptoms": {"pain": 2}},
            {"date": "2024-01-04", "symptoms": {"pain": 3}},
            {"date": "2024-01-07", "symptoms": {"pain": 2}},
        ],
        "expected_frequency": "daily",
        "monitoring_period_days": 14,
        "compliance_threshold": 0.8
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "intervention_recommendations" in result
    recommendations = result["intervention_recommendations"]
    assert "recommended_actions" in recommendations
    assert "priority_level" in recommendations
    assert len(recommendations["recommended_actions"]) > 0


def test_patient_diary_checker_weekly_frequency():
    """Test weekly diary frequency."""
    input_data = {
        "patient_id": "P011",
        "diary_entries": [
            {"date": "2024-01-01", "symptoms": {"pain": 2}},  # Week 1
            {"date": "2024-01-08", "symptoms": {"pain": 3}},  # Week 2
            {"date": "2024-01-15", "symptoms": {"pain": 1}},  # Week 3
            {"date": "2024-01-22", "symptoms": {"pain": 4}},  # Week 4
        ],
        "expected_frequency": "weekly",
        "monitoring_period_days": 28
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["compliance_summary"]["overall_compliance_rate"] == 100.0
    assert result["compliance_summary"]["missed_entries"] == 0


def test_patient_diary_checker_twice_daily_frequency():
    """Test twice daily diary frequency."""
    input_data = {
        "patient_id": "P012",
        "diary_entries": [
            {"date": "2024-01-01", "entry_time": "08:00", "symptoms": {"pain": 2}},
            {"date": "2024-01-01", "entry_time": "20:00", "symptoms": {"pain": 3}},
            {"date": "2024-01-02", "entry_time": "08:30", "symptoms": {"pain": 2}},
            # Missing evening entry for Jan 2
        ],
        "expected_frequency": "twice_daily",
        "monitoring_period_days": 2
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["compliance_summary"]["missed_entries"] == 1
    assert result["compliance_summary"]["overall_compliance_rate"] < 100.0


def test_patient_diary_checker_empty_entries():
    """Test handling of empty diary entries."""
    input_data = {
        "patient_id": "P013",
        "diary_entries": [],
        "expected_frequency": "daily",
        "monitoring_period_days": 7
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["compliance_summary"]["overall_compliance_rate"] == 0.0
    assert result["compliance_summary"]["missed_entries"] == 7
    assert len(result["compliance_alerts"]) > 0


def test_patient_diary_checker_no_patient_id():
    """Test handling of missing patient ID."""
    input_data = {
        "diary_entries": [
            {"date": "2024-01-01", "symptoms": {"pain": 2}}
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == False
    assert "No patient ID provided" in result["error"]


def test_patient_diary_checker_trend_analysis():
    """Test symptom trend analysis."""
    input_data = {
        "patient_id": "P014",
        "diary_entries": [
            {"date": "2024-01-01", "symptoms": {"pain": 1, "fatigue": 2}},
            {"date": "2024-01-02", "symptoms": {"pain": 2, "fatigue": 2}},
            {"date": "2024-01-03", "symptoms": {"pain": 3, "fatigue": 3}},
            {"date": "2024-01-04", "symptoms": {"pain": 4, "fatigue": 3}},
            {"date": "2024-01-05", "symptoms": {"pain": 5, "fatigue": 4}},
            {"date": "2024-01-06", "symptoms": {"pain": 6, "fatigue": 4}},
            {"date": "2024-01-07", "symptoms": {"pain": 7, "fatigue": 5}}
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "symptom_analysis" in result
    trends = result["symptom_analysis"]["symptom_trends"]
    
    # Should detect increasing pain trend
    assert trends["pain"]["trend_direction"] == "increasing"
    assert trends["pain"]["slope"] > 0


def test_patient_diary_checker_data_completeness():
    """Test data completeness assessment."""
    input_data = {
        "patient_id": "P015",
        "diary_entries": [
            {
                "date": "2024-01-01",
                "entry_time": "09:00",
                "symptoms": {"pain": 3, "fatigue": 2, "nausea": 1},
                "medications_taken": True,
                "side_effects": None,
                "mood": "good",
                "sleep_quality": 7
            },
            {
                "date": "2024-01-02",
                "symptoms": {"pain": 4},
                "medications_taken": True
                # Missing several fields
            }
        ],
        "required_fields": ["symptoms", "medications_taken", "side_effects", "mood"]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "quality_assessment" in result
    quality = result["quality_assessment"]
    assert "field_completeness" in quality
    assert quality["average_completeness_score"] < 100.0


def test_patient_diary_checker_adherence_prediction():
    """Test adherence prediction functionality."""
    input_data = {
        "patient_id": "P016",
        "diary_entries": [
            {"date": "2024-01-01", "entry_time": "09:00"},
            {"date": "2024-01-02", "entry_time": "09:15"},
            {"date": "2024-01-04", "entry_time": "14:30"},  # Late entry
            {"date": "2024-01-06", "entry_time": "09:00"},
            # Recent pattern showing declining compliance
        ],
        "monitoring_period_days": 14,
        "predict_future_compliance": True
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "compliance_prediction" in result
    prediction = result["compliance_prediction"]
    assert "predicted_compliance_rate" in prediction
    assert "risk_level" in prediction
    assert prediction["risk_level"] in ["low", "medium", "high"]


def test_patient_diary_checker_multiple_symptoms():
    """Test handling of multiple symptom types."""
    input_data = {
        "patient_id": "P017",
        "diary_entries": [
            {
                "date": "2024-01-01",
                "symptoms": {
                    "pain": 3, "fatigue": 2, "nausea": 1, "headache": 0,
                    "dizziness": 2, "appetite_loss": 1, "insomnia": 3
                }
            },
            {
                "date": "2024-01-02", 
                "symptoms": {
                    "pain": 4, "fatigue": 3, "nausea": 2, "headache": 1,
                    "dizziness": 1, "appetite_loss": 2, "insomnia": 2
                }
            }
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "symptom_analysis" in result
    symptom_analysis = result["symptom_analysis"]
    assert len(symptom_analysis["symptom_trends"]) >= 7
    assert "severity_patterns" in symptom_analysis


def test_patient_diary_checker_longitudinal_analysis():
    """Test longitudinal analysis over extended period."""
    # Generate 30 days of diary entries with varying compliance
    diary_entries = []
    for day in range(1, 31):
        if day % 7 != 0:  # Skip Sundays (weekly pattern)
            date = f"2024-01-{day:02d}"
            entry_time = "09:00" if day < 20 else "14:00"  # Later entries in second half
            diary_entries.append({
                "date": date,
                "entry_time": entry_time,
                "symptoms": {"pain": (day % 5) + 1, "fatigue": (day % 4) + 1},
                "medications_taken": day % 10 != 0  # Miss every 10th day
            })
    
    input_data = {
        "patient_id": "P018",
        "diary_entries": diary_entries,
        "expected_frequency": "daily",
        "monitoring_period_days": 30
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["compliance_summary"]["overall_compliance_rate"] < 90.0  # Due to Sunday skips
    assert "compliance_patterns" in result
    patterns = result["compliance_patterns"]
    assert "temporal_trends" in patterns


def test_patient_diary_checker_custom_scoring():
    """Test custom compliance scoring algorithm."""
    input_data = {
        "patient_id": "P019",
        "diary_entries": [
            {"date": "2024-01-01", "entry_time": "09:00", "quality_score": 100},
            {"date": "2024-01-02", "entry_time": "12:00", "quality_score": 75},
            {"date": "2024-01-04", "entry_time": "09:00", "quality_score": 90},  # 1 day gap
        ],
        "scoring_weights": {
            "timeliness": 0.3,
            "completeness": 0.4, 
            "consistency": 0.3
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "compliance_summary" in result
    assert "weighted_compliance_score" in result["compliance_summary"]
    assert result["compliance_summary"]["weighted_compliance_score"] <= 100.0