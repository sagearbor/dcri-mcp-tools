import pytest
from tools.patient_retention_predictor import run


def test_patient_retention_predictor_basic():
    """Test basic patient retention prediction."""
    input_data = {
        "patients": [
            {
                "patient_id": "P001",
                "age": 45,
                "gender": "female",
                "baseline_visit_date": "2024-01-15",
                "distance_to_site": 25.5,
                "prior_studies": 0,
                "comorbidities": ["diabetes"],
                "visit_adherence": 0.95
            },
            {
                "patient_id": "P002", 
                "age": 72,
                "gender": "male",
                "baseline_visit_date": "2024-01-20",
                "distance_to_site": 45.2,
                "prior_studies": 2,
                "comorbidities": ["hypertension", "heart_disease"],
                "visit_adherence": 0.80
            }
        ],
        "study_duration_months": 12
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["patient_predictions"]) == 2
    assert result["model_summary"]["total_patients_analyzed"] == 2
    assert all(0 <= pred["dropout_probability"] <= 1 for pred in result["patient_predictions"])


def test_patient_retention_predictor_risk_factors():
    """Test risk factor analysis."""
    input_data = {
        "patients": [
            {
                "patient_id": "P001",
                "age": 35,
                "distance_to_site": 15.0,
                "visit_adherence": 0.95,
                "adverse_events": 1
            },
            {
                "patient_id": "P002",
                "age": 75,
                "distance_to_site": 60.0,
                "visit_adherence": 0.70,
                "adverse_events": 5
            }
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    
    # Higher risk patient should have higher dropout probability
    p1_risk = next(p for p in result["patient_predictions"] if p["patient_id"] == "P001")
    p2_risk = next(p for p in result["patient_predictions"] if p["patient_id"] == "P002")
    
    assert p2_risk["dropout_probability"] > p1_risk["dropout_probability"]
    assert p2_risk["risk_category"] in ["medium", "high"]


def test_patient_retention_predictor_intervention_recommendations():
    """Test intervention recommendations."""
    input_data = {
        "patients": [
            {
                "patient_id": "P003",
                "age": 65,
                "distance_to_site": 50.0,
                "visit_adherence": 0.75,
                "missed_visits": 3,
                "side_effects_severity": "moderate",
                "socioeconomic_status": "low"
            }
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    patient_pred = result["patient_predictions"][0]
    assert "intervention_recommendations" in patient_pred
    
    recommendations = patient_pred["intervention_recommendations"]
    assert len(recommendations) > 0
    assert any("transportation" in rec.lower() for rec in recommendations)


def test_patient_retention_predictor_high_risk_patients():
    """Test identification of high-risk patients."""
    input_data = {
        "patients": [
            {
                "patient_id": "P004",
                "age": 80,
                "distance_to_site": 75.0,
                "visit_adherence": 0.60,
                "missed_visits": 5,
                "adverse_events": 8,
                "treatment_satisfaction": "low",
                "caregiver_support": False
            }
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    patient_pred = result["patient_predictions"][0]
    assert patient_pred["risk_category"] == "high"
    assert patient_pred["dropout_probability"] > 0.6
    assert "high-risk" in result["retention_summary"]["risk_distribution"]


def test_patient_retention_predictor_demographic_analysis():
    """Test demographic factor analysis."""
    input_data = {
        "patients": [
            {"patient_id": "P005", "age": 25, "gender": "female", "education": "college"},
            {"patient_id": "P006", "age": 30, "gender": "male", "education": "high_school"},
            {"patient_id": "P007", "age": 70, "gender": "female", "education": "elementary"},
            {"patient_id": "P008", "age": 75, "gender": "male", "education": "college"}
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "risk_factor_analysis" in result
    risk_factors = result["risk_factor_analysis"]
    assert "demographic_factors" in risk_factors
    assert "age_risk_correlation" in risk_factors["demographic_factors"]


def test_patient_retention_predictor_temporal_patterns():
    """Test temporal dropout risk patterns."""
    input_data = {
        "patients": [
            {
                "patient_id": "P009",
                "baseline_visit_date": "2024-01-01",
                "months_in_study": 3,
                "visit_adherence": 0.90,
                "recent_visit_adherence": 0.70  # Declining
            },
            {
                "patient_id": "P010",
                "baseline_visit_date": "2024-01-01", 
                "months_in_study": 8,
                "visit_adherence": 0.85,
                "recent_visit_adherence": 0.85  # Stable
            }
        ],
        "analyze_temporal_patterns": True
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "temporal_analysis" in result
    temporal = result["temporal_analysis"]
    assert "dropout_risk_by_month" in temporal
    assert "adherence_trends" in temporal


def test_patient_retention_predictor_study_factors():
    """Test study-specific factor analysis."""
    input_data = {
        "patients": [
            {
                "patient_id": "P011",
                "treatment_arm": "experimental",
                "protocol_complexity": "high",
                "visit_frequency": "weekly",
                "study_burden_score": 8.5
            },
            {
                "patient_id": "P012",
                "treatment_arm": "control",
                "protocol_complexity": "low", 
                "visit_frequency": "monthly",
                "study_burden_score": 4.2
            }
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    
    # Patient with higher burden should have higher dropout risk
    p11_risk = next(p for p in result["patient_predictions"] if p["patient_id"] == "P011")
    p12_risk = next(p for p in result["patient_predictions"] if p["patient_id"] == "P012")
    
    assert p11_risk["dropout_probability"] >= p12_risk["dropout_probability"]


def test_patient_retention_predictor_safety_factors():
    """Test safety-related dropout risk factors."""
    input_data = {
        "patients": [
            {
                "patient_id": "P013",
                "adverse_events": 2,
                "serious_adverse_events": 0,
                "side_effects_severity": "mild",
                "treatment_satisfaction": "high"
            },
            {
                "patient_id": "P014",
                "adverse_events": 12,
                "serious_adverse_events": 3,
                "side_effects_severity": "severe",
                "treatment_satisfaction": "low"
            }
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    
    # Patient with more AEs should have higher dropout risk
    p13_risk = next(p for p in result["patient_predictions"] if p["patient_id"] == "P013")
    p14_risk = next(p for p in result["patient_predictions"] if p["patient_id"] == "P014")
    
    assert p14_risk["dropout_probability"] > p13_risk["dropout_probability"]
    assert p14_risk["risk_category"] in ["medium", "high"]


def test_patient_retention_predictor_site_factors():
    """Test site-related factors in retention."""
    input_data = {
        "patients": [
            {"patient_id": "P015", "site_id": "Site001", "site_retention_rate": 0.95},
            {"patient_id": "P016", "site_id": "Site002", "site_retention_rate": 0.70},
            {"patient_id": "P017", "site_id": "Site003", "site_retention_rate": 0.85}
        ],
        "include_site_factors": True
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "site_analysis" in result
    site_analysis = result["site_analysis"]
    assert "site_retention_rates" in site_analysis
    assert "site_risk_factors" in site_analysis


def test_patient_retention_predictor_model_validation():
    """Test model validation metrics."""
    # Create a larger dataset for model validation
    patients = []
    for i in range(50):
        patients.append({
            "patient_id": f"P{i+1:03d}",
            "age": 30 + (i % 50),
            "distance_to_site": 10 + (i % 40),
            "visit_adherence": 0.6 + (i % 40) * 0.01,
            "prior_studies": i % 3,
            "comorbidities_count": i % 5
        })
    
    input_data = {
        "patients": patients,
        "validate_model": True,
        "validation_split": 0.2
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "model_validation" in result
    validation = result["model_validation"]
    assert "accuracy_metrics" in validation
    assert "feature_importance" in validation


def test_patient_retention_predictor_early_dropout():
    """Test early dropout risk prediction."""
    input_data = {
        "patients": [
            {
                "patient_id": "P018",
                "months_in_study": 1,
                "baseline_enthusiasm": "low",
                "informed_consent_concerns": True,
                "family_support": False
            }
        ],
        "predict_early_dropout": True,
        "early_dropout_threshold_months": 3
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    patient_pred = result["patient_predictions"][0]
    assert "early_dropout_risk" in patient_pred
    assert patient_pred["early_dropout_risk"] > 0.5


def test_patient_retention_predictor_empty_patients():
    """Test handling of empty patient list."""
    input_data = {
        "patients": []
    }
    
    result = run(input_data)
    
    assert result["success"] == False
    assert "No patient data provided" in result["error"]


def test_patient_retention_predictor_missing_patient_id():
    """Test handling of missing patient ID."""
    input_data = {
        "patients": [
            {
                "age": 45,
                "gender": "female"
            }
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == False
    assert "Patient ID missing" in result["error"]


def test_patient_retention_predictor_feature_engineering():
    """Test feature engineering capabilities."""
    input_data = {
        "patients": [
            {
                "patient_id": "P019",
                "age": 55,
                "baseline_visit_date": "2024-01-01",
                "visit_dates": ["2024-01-01", "2024-02-01", "2024-03-15"],  # Irregular spacing
                "lab_values": [{"date": "2024-01-01", "value": 120}, {"date": "2024-02-01", "value": 125}],
                "symptom_scores": [3, 4, 2]
            }
        ],
        "engineer_features": True
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "feature_engineering" in result
    features = result["feature_engineering"]
    assert "engineered_features" in features
    assert "feature_correlations" in features


def test_patient_retention_predictor_longitudinal_data():
    """Test longitudinal data analysis."""
    input_data = {
        "patients": [
            {
                "patient_id": "P020",
                "longitudinal_data": {
                    "visit_adherence_history": [1.0, 0.9, 0.8, 0.7, 0.6],
                    "satisfaction_scores": [9, 8, 7, 6, 5],
                    "ae_counts": [0, 1, 2, 3, 2],
                    "months": [1, 2, 3, 4, 5]
                }
            }
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    patient_pred = result["patient_predictions"][0]
    assert "longitudinal_trends" in patient_pred
    trends = patient_pred["longitudinal_trends"]
    assert "adherence_trend" in trends
    assert trends["adherence_trend"] == "decreasing"


def test_patient_retention_predictor_subgroup_analysis():
    """Test subgroup-specific retention analysis."""
    input_data = {
        "patients": [
            {"patient_id": "P021", "age": 25, "gender": "female", "disease_severity": "mild"},
            {"patient_id": "P022", "age": 30, "gender": "female", "disease_severity": "severe"},
            {"patient_id": "P023", "age": 65, "gender": "male", "disease_severity": "mild"},
            {"patient_id": "P024", "age": 70, "gender": "male", "disease_severity": "severe"}
        ],
        "subgroup_analysis": ["age_group", "gender", "disease_severity"]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "subgroup_analysis" in result
    subgroups = result["subgroup_analysis"]
    assert "age_group" in subgroups
    assert "gender" in subgroups
    assert "disease_severity" in subgroups


def test_patient_retention_predictor_intervention_effectiveness():
    """Test intervention effectiveness prediction."""
    input_data = {
        "patients": [
            {
                "patient_id": "P025",
                "dropout_probability": 0.8,
                "risk_factors": ["distance", "age"],
                "previous_interventions": []
            }
        ],
        "potential_interventions": [
            {"type": "transportation_assistance", "cost": 500, "effectiveness": 0.3},
            {"type": "telemedicine", "cost": 200, "effectiveness": 0.25},
            {"type": "patient_navigator", "cost": 1000, "effectiveness": 0.4}
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    patient_pred = result["patient_predictions"][0]
    assert "intervention_analysis" in patient_pred
    interventions = patient_pred["intervention_analysis"]
    assert "recommended_interventions" in interventions
    assert "cost_effectiveness" in interventions


def test_patient_retention_predictor_real_time_scoring():
    """Test real-time risk scoring."""
    input_data = {
        "patients": [
            {
                "patient_id": "P026",
                "age": 55,
                "recent_events": [
                    {"type": "missed_visit", "date": "2024-01-15"},
                    {"type": "adverse_event", "date": "2024-01-20", "severity": "moderate"},
                    {"type": "satisfaction_survey", "date": "2024-01-25", "score": 4}
                ]
            }
        ],
        "real_time_scoring": True
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    patient_pred = result["patient_predictions"][0]
    assert "real_time_score" in patient_pred
    assert "score_change_history" in patient_pred
    assert patient_pred["real_time_score"]["current_risk"] > 0


def test_patient_retention_predictor_retention_strategies():
    """Test retention strategy recommendations."""
    input_data = {
        "patients": [
            {
                "patient_id": "P027",
                "risk_category": "high",
                "primary_risk_factors": ["distance", "age", "side_effects"],
                "patient_profile": {
                    "age": 75,
                    "technology_comfort": "low",
                    "caregiver_support": True,
                    "financial_status": "limited"
                }
            }
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    patient_pred = result["patient_predictions"][0]
    assert "retention_strategies" in patient_pred
    strategies = patient_pred["retention_strategies"]
    assert "personalized_recommendations" in strategies
    assert "implementation_timeline" in strategies


def test_patient_retention_predictor_cohort_analysis():
    """Test cohort-based retention analysis."""
    # Create different enrollment cohorts
    patients = []
    for month in range(1, 13):  # 12 months of enrollment
        for patient_num in range(5):  # 5 patients per month
            patients.append({
                "patient_id": f"P{month:02d}_{patient_num:02d}",
                "enrollment_month": month,
                "enrollment_date": f"2024-{month:02d}-15",
                "age": 40 + month,
                "visit_adherence": 0.9 - (month * 0.02)  # Declining over time
            })
    
    input_data = {
        "patients": patients,
        "cohort_analysis": True,
        "cohort_variable": "enrollment_month"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "cohort_analysis" in result
    cohort_analysis = result["cohort_analysis"]
    assert "retention_by_cohort" in cohort_analysis
    assert "cohort_risk_trends" in cohort_analysis


def test_patient_retention_predictor_machine_learning_metrics():
    """Test machine learning model performance metrics."""
    # Create a substantial dataset for ML evaluation
    patients = []
    for i in range(100):
        dropout_occurred = i % 4 == 0  # 25% dropout rate
        patients.append({
            "patient_id": f"P{i+1:03d}",
            "age": 30 + (i % 50),
            "distance_to_site": 10 + (i % 60),
            "visit_adherence": 0.5 + (i % 50) * 0.01,
            "adverse_events": i % 10,
            "actual_dropout": dropout_occurred  # Ground truth for validation
        })
    
    input_data = {
        "patients": patients,
        "include_ml_metrics": True,
        "model_type": "ensemble"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "ml_performance" in result
    ml_metrics = result["ml_performance"]
    assert "model_accuracy" in ml_metrics
    assert "precision" in ml_metrics
    assert "recall" in ml_metrics
    assert "auc_score" in ml_metrics