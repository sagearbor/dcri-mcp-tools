"""
Patient Retention Predictor Tool
AI-powered prediction of patient dropout risk in clinical trials
"""

from typing import Dict, List, Any, Tuple
import re
from datetime import datetime, timedelta
from collections import Counter
import math

def run(input_data: Dict) -> Dict:
    """
    Predict patient dropout risk using AI-powered analysis of engagement patterns
    
    Example:
        Input: Patient demographic data, visit attendance, compliance metrics, and study characteristics
        Output: Risk scores, high-risk patient identification, and targeted retention intervention recommendations
    
    Parameters:
        patient_data : list
            Individual patient demographics and baseline characteristics
        engagement_data : list
            Patient engagement metrics (visits, compliance, communication)
        study_parameters : dict
            Study design parameters affecting retention rates
        historical_dropout_data : list
            Historical dropout patterns from similar studies
        intervention_history : list
            Previous retention interventions and effectiveness
        prediction_timeframe : int
            Timeframe for dropout predictions in days
    """
    try:
        patient_data = input_data.get('patient_data', [])
        engagement_data = input_data.get('engagement_data', [])
        study_parameters = input_data.get('study_parameters', {})
        historical_dropout_data = input_data.get('historical_dropout_data', [])
        intervention_history = input_data.get('intervention_history', [])
        prediction_timeframe = input_data.get('prediction_timeframe', 30)  # days
        
        if not patient_data:
            return {
                'success': False,
                'error': 'No patient data provided for retention prediction'
            }
        
        # Process and validate input data
        processed_patients = process_patient_data(patient_data, engagement_data)
        
        # Build risk prediction model
        risk_model = build_dropout_risk_model(
            processed_patients, historical_dropout_data, study_parameters
        )
        
        # Generate risk predictions for each patient
        patient_predictions = generate_patient_predictions(
            processed_patients, risk_model, prediction_timeframe
        )
        
        # Identify high-risk patients
        high_risk_patients = identify_high_risk_patients(patient_predictions)
        
        # Analyze risk factors
        risk_factor_analysis = analyze_risk_factors(
            processed_patients, patient_predictions, study_parameters
        )
        
        # Generate intervention recommendations
        intervention_recommendations = generate_intervention_recommendations(
            patient_predictions, risk_factor_analysis, intervention_history
        )
        
        # Create retention strategies
        retention_strategies = create_retention_strategies(
            high_risk_patients, risk_factor_analysis, study_parameters
        )
        
        # Calculate study-level retention metrics
        study_retention_metrics = calculate_study_retention_metrics(
            processed_patients, patient_predictions, study_parameters
        )
        
        # Generate trend analysis
        retention_trends = analyze_retention_trends(
            processed_patients, historical_dropout_data
        )
        
        return {
            'success': True,
            'prediction_summary': {
                'total_patients_analyzed': len(processed_patients),
                'high_risk_patients_count': len(high_risk_patients),
                'overall_predicted_retention_rate': study_retention_metrics['predicted_retention_rates']['predicted_retention_rate'],
                'prediction_timeframe_days': prediction_timeframe,
                'model_confidence_score': risk_model['model_confidence'],
                'analysis_date': datetime.now().isoformat()
            },
            'patient_predictions': patient_predictions,
            'high_risk_patients': high_risk_patients,
            'risk_factor_analysis': risk_factor_analysis,
            'intervention_recommendations': intervention_recommendations,
            'retention_strategies': retention_strategies,
            'study_retention_metrics': study_retention_metrics,
            'retention_trends': retention_trends,
            'model_insights': {
                'key_predictive_factors': risk_model['key_factors'],
                'model_performance_metrics': risk_model['performance_metrics'],
                'risk_thresholds': risk_model['risk_thresholds']
            },
            'monitoring_recommendations': generate_monitoring_recommendations(
                patient_predictions, high_risk_patients
            )
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error predicting patient retention: {str(e)}'
        }

def process_patient_data(patient_data: List[Dict], engagement_data: List[Dict]) -> List[Dict]:
    """Process and combine patient demographic and engagement data."""
    processed_patients = []
    
    # Create engagement data lookup
    engagement_lookup = {}
    for engagement in engagement_data:
        patient_id = str(engagement.get('patient_id', ''))
        if patient_id not in engagement_lookup:
            engagement_lookup[patient_id] = []
        engagement_lookup[patient_id].append(engagement)
    
    for patient in patient_data:
        if not isinstance(patient, dict):
            continue
        
        patient_id = str(patient.get('patient_id', ''))
        patient_engagement = engagement_lookup.get(patient_id, [])
        
        processed_patient = {
            'patient_id': patient_id,
            
            # Demographics
            'age': validate_numeric(patient.get('age'), 0, 120),
            'gender': patient.get('gender', 'unknown').lower(),
            'race_ethnicity': patient.get('race_ethnicity', 'unknown').lower(),
            'education_level': patient.get('education_level', 'unknown').lower(),
            'employment_status': patient.get('employment_status', 'unknown').lower(),
            'marital_status': patient.get('marital_status', 'unknown').lower(),
            'income_level': patient.get('income_level', 'unknown').lower(),
            
            # Geographic and logistical factors
            'distance_to_site_miles': validate_numeric(patient.get('distance_to_site_miles'), 0, 1000),
            'transportation_method': patient.get('transportation_method', 'unknown').lower(),
            'caregiver_support': patient.get('caregiver_support', False),
            'insurance_status': patient.get('insurance_status', 'unknown').lower(),
            
            # Medical history and baseline characteristics
            'primary_diagnosis': patient.get('primary_diagnosis', '').lower(),
            'disease_duration_months': validate_numeric(patient.get('disease_duration_months'), 0, 600),
            'disease_severity': patient.get('disease_severity', 'unknown').lower(),
            'comorbidity_count': validate_numeric(patient.get('comorbidity_count'), 0, 20),
            'previous_trial_participation': patient.get('previous_trial_participation', False),
            'medication_count': validate_numeric(patient.get('medication_count'), 0, 50),
            
            # Study-specific factors
            'enrollment_date': parse_date(patient.get('enrollment_date')),
            'randomization_arm': patient.get('randomization_arm', 'unknown').lower(),
            'site_id': patient.get('site_id', 'unknown'),
            'recruitment_source': patient.get('recruitment_source', 'unknown').lower(),
            
            # Baseline attitudes and expectations
            'baseline_motivation_score': validate_numeric(patient.get('baseline_motivation_score'), 0, 10),
            'baseline_expectation_score': validate_numeric(patient.get('baseline_expectation_score'), 0, 10),
            'baseline_burden_perception': validate_numeric(patient.get('baseline_burden_perception'), 0, 10),
            
            # Current status
            'current_status': patient.get('current_status', 'active').lower(),
            'dropout_date': parse_date(patient.get('dropout_date')),
            'dropout_reason': patient.get('dropout_reason', '').lower(),
            
            # Engagement metrics (calculated from engagement_data)
            'engagement_metrics': calculate_engagement_metrics(patient_engagement),
            
            # Risk indicators
            'risk_indicators': extract_risk_indicators(patient, patient_engagement),
            
            # Original data for reference
            'original_patient_data': patient,
            'original_engagement_data': patient_engagement
        }
        
        # Calculate derived metrics
        processed_patient['study_duration_days'] = calculate_study_duration(processed_patient)
        processed_patient['engagement_trend'] = calculate_engagement_trend(patient_engagement)
        processed_patient['compliance_score'] = calculate_compliance_score(patient_engagement)
        processed_patient['visit_adherence_rate'] = calculate_visit_adherence(patient_engagement)
        
        processed_patients.append(processed_patient)
    
    return processed_patients

def validate_numeric(value: Any, min_val: float = None, max_val: float = None) -> float:
    """Validate and convert numeric values."""
    try:
        num_val = float(value) if value is not None else 0.0
        if min_val is not None and num_val < min_val:
            num_val = min_val
        if max_val is not None and num_val > max_val:
            num_val = max_val
        return num_val
    except (ValueError, TypeError):
        return 0.0

def parse_date(date_input: Any) -> datetime:
    """Parse date input into datetime object."""
    if isinstance(date_input, datetime):
        return date_input
    elif isinstance(date_input, str) and date_input.strip():
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y', '%Y-%m-%d %H:%M:%S']:
            try:
                return datetime.strptime(date_input.strip(), fmt)
            except ValueError:
                continue
    return None

def calculate_engagement_metrics(engagement_data: List[Dict]) -> Dict:
    """Calculate engagement metrics from patient engagement data."""
    if not engagement_data:
        return {
            'total_interactions': 0,
            'avg_response_time_hours': 0,
            'missed_visits_count': 0,
            'compliance_rate': 0,
            'last_interaction_days_ago': 999,
            'engagement_frequency_score': 0
        }
    
    total_interactions = len(engagement_data)
    response_times = [e.get('response_time_hours', 0) for e in engagement_data if e.get('response_time_hours', 0) > 0]
    missed_visits = sum(1 for e in engagement_data if e.get('visit_status') == 'missed')
    completed_activities = sum(1 for e in engagement_data if e.get('activity_status') == 'completed')
    
    # Calculate last interaction
    last_interaction = None
    current_date = datetime.now()
    for engagement in engagement_data:
        interaction_date = parse_date(engagement.get('interaction_date'))
        if interaction_date and (last_interaction is None or interaction_date > last_interaction):
            last_interaction = interaction_date
    
    last_interaction_days = (current_date - last_interaction).days if last_interaction else 999
    
    return {
        'total_interactions': total_interactions,
        'avg_response_time_hours': sum(response_times) / len(response_times) if response_times else 0,
        'missed_visits_count': missed_visits,
        'compliance_rate': (completed_activities / total_interactions) * 100 if total_interactions > 0 else 0,
        'last_interaction_days_ago': last_interaction_days,
        'engagement_frequency_score': min(10, total_interactions / 10)  # Scale to 0-10
    }

def extract_risk_indicators(patient: Dict, engagement_data: List[Dict]) -> List[str]:
    """Extract risk indicators from patient and engagement data."""
    indicators = []
    
    # Demographic risk factors
    age = patient.get('age', 0)
    if age < 25 or age > 75:
        indicators.append('extreme_age')
    
    if patient.get('distance_to_site_miles', 0) > 50:
        indicators.append('long_distance_to_site')
    
    if not patient.get('caregiver_support', False):
        indicators.append('lack_of_caregiver_support')
    
    if patient.get('comorbidity_count', 0) > 5:
        indicators.append('high_comorbidity_burden')
    
    # Engagement risk factors
    if not engagement_data:
        indicators.append('no_engagement_data')
    else:
        missed_visits = sum(1 for e in engagement_data if e.get('visit_status') == 'missed')
        if missed_visits > len(engagement_data) * 0.3:  # >30% missed
            indicators.append('high_missed_visit_rate')
        
        avg_response_time = sum(e.get('response_time_hours', 0) for e in engagement_data) / len(engagement_data)
        if avg_response_time > 48:  # >2 days average response
            indicators.append('slow_response_to_communications')
    
    # Study-specific risk factors
    if patient.get('baseline_motivation_score', 5) < 3:
        indicators.append('low_baseline_motivation')
    
    if patient.get('baseline_burden_perception', 5) > 7:
        indicators.append('high_perceived_burden')
    
    return indicators

def calculate_study_duration(patient: Dict) -> int:
    """Calculate how long patient has been in study."""
    enrollment_date = patient.get('enrollment_date')
    if enrollment_date:
        return (datetime.now() - enrollment_date).days
    return 0

def calculate_engagement_trend(engagement_data: List[Dict]) -> str:
    """Calculate trend in patient engagement over time."""
    if len(engagement_data) < 3:
        return 'insufficient_data'
    
    # Sort by date
    sorted_data = sorted(
        [e for e in engagement_data if parse_date(e.get('interaction_date'))],
        key=lambda x: parse_date(x['interaction_date'])
    )
    
    if len(sorted_data) < 3:
        return 'insufficient_data'
    
    # Calculate engagement scores for first third and last third
    third_size = len(sorted_data) // 3
    early_data = sorted_data[:third_size]
    recent_data = sorted_data[-third_size:]
    
    early_score = sum(1 for e in early_data if e.get('activity_status') == 'completed') / len(early_data)
    recent_score = sum(1 for e in recent_data if e.get('activity_status') == 'completed') / len(recent_data)
    
    if recent_score > early_score + 0.1:
        return 'improving'
    elif recent_score < early_score - 0.1:
        return 'declining'
    else:
        return 'stable'

def calculate_compliance_score(engagement_data: List[Dict]) -> float:
    """Calculate overall compliance score."""
    if not engagement_data:
        return 0.0
    
    completed_activities = sum(1 for e in engagement_data if e.get('activity_status') == 'completed')
    total_activities = len(engagement_data)
    
    base_score = (completed_activities / total_activities) * 100
    
    # Adjust for timeliness
    timely_activities = sum(1 for e in engagement_data if e.get('response_time_hours', 999) <= 24)
    timeliness_bonus = (timely_activities / total_activities) * 10
    
    return min(100, base_score + timeliness_bonus)

def calculate_visit_adherence(engagement_data: List[Dict]) -> float:
    """Calculate visit adherence rate."""
    visits = [e for e in engagement_data if e.get('activity_type') == 'visit']
    if not visits:
        return 100.0  # No visits scheduled
    
    attended_visits = sum(1 for v in visits if v.get('visit_status') in ['completed', 'attended'])
    return (attended_visits / len(visits)) * 100

def build_dropout_risk_model(processed_patients: List[Dict], historical_data: List[Dict], 
                           study_parameters: Dict) -> Dict:
    """Build a dropout risk prediction model."""
    model = {
        'key_factors': [],
        'risk_weights': {},
        'risk_thresholds': {
            'low': 0.2,
            'moderate': 0.5,
            'high': 0.75,
            'very_high': 0.9
        },
        'model_confidence': 0.75,  # Default confidence
        'performance_metrics': {}
    }
    
    # Analyze historical dropout patterns
    if historical_data:
        historical_analysis = analyze_historical_dropouts(historical_data)
        model['key_factors'] = historical_analysis['key_risk_factors']
        model['risk_weights'] = historical_analysis['risk_weights']
    else:
        # Use evidence-based risk factors from literature
        model['key_factors'] = [
            'age_extremes', 'distance_to_site', 'comorbidity_burden',
            'missed_visits', 'low_motivation', 'poor_compliance',
            'lack_of_support', 'adverse_events', 'treatment_burden'
        ]
        model['risk_weights'] = {
            'age_extremes': 0.15,
            'distance_to_site': 0.12,
            'comorbidity_burden': 0.10,
            'missed_visits': 0.20,
            'low_motivation': 0.15,
            'poor_compliance': 0.18,
            'lack_of_support': 0.08,
            'treatment_burden': 0.02
        }
    
    # Adjust model based on study parameters
    model = adjust_model_for_study_parameters(model, study_parameters)
    
    # Validate model with current patient data
    if len(processed_patients) > 10:
        validation_metrics = validate_model_with_current_data(model, processed_patients)
        model['performance_metrics'] = validation_metrics
        model['model_confidence'] = validation_metrics.get('confidence_score', 0.75)
    
    return model

def analyze_historical_dropouts(historical_data: List[Dict]) -> Dict:
    """Analyze historical dropout data to identify key risk factors."""
    analysis = {
        'key_risk_factors': [],
        'risk_weights': {},
        'dropout_patterns': {}
    }
    
    # Simple analysis of common factors in dropouts
    dropout_factors = []
    retention_factors = []
    
    for record in historical_data:
        if record.get('dropped_out', False):
            dropout_factors.extend(record.get('risk_factors', []))
        else:
            retention_factors.extend(record.get('risk_factors', []))
    
    # Count factor frequencies
    dropout_counter = Counter(dropout_factors)
    retention_counter = Counter(retention_factors)
    
    # Calculate risk weights based on differential frequency
    all_factors = set(dropout_factors + retention_factors)
    risk_weights = {}
    
    for factor in all_factors:
        dropout_freq = dropout_counter.get(factor, 0)
        retention_freq = retention_counter.get(factor, 0)
        total_dropout = len([r for r in historical_data if r.get('dropped_out', False)])
        total_retention = len(historical_data) - total_dropout
        
        if total_dropout > 0 and total_retention > 0:
            dropout_rate = dropout_freq / total_dropout
            retention_rate = retention_freq / total_retention
            risk_weight = dropout_rate / max(retention_rate, 0.01)  # Avoid division by zero
            risk_weights[factor] = min(risk_weight / 10, 0.3)  # Normalize and cap
    
    # Select top risk factors
    top_factors = sorted(risk_weights.items(), key=lambda x: x[1], reverse=True)[:10]
    
    analysis['key_risk_factors'] = [factor for factor, weight in top_factors]
    analysis['risk_weights'] = dict(top_factors)
    
    return analysis

def adjust_model_for_study_parameters(model: Dict, study_parameters: Dict) -> Dict:
    """Adjust risk model based on specific study parameters."""
    # Study duration impact
    study_duration_weeks = study_parameters.get('planned_duration_weeks', 52)
    if study_duration_weeks > 104:  # >2 years
        model['risk_weights']['long_study_duration'] = 0.1
        model['key_factors'].append('long_study_duration')
    
    # Visit frequency impact
    visit_frequency_weeks = study_parameters.get('visit_frequency_weeks', 4)
    if visit_frequency_weeks > 8:  # Infrequent visits
        model['risk_weights']['infrequent_visits'] = 0.05
    elif visit_frequency_weeks < 2:  # Very frequent visits
        model['risk_weights']['frequent_visits'] = 0.08
        model['key_factors'].append('frequent_visits')
    
    # Treatment complexity
    treatment_complexity = study_parameters.get('treatment_complexity', 'low')
    if treatment_complexity == 'high':
        model['risk_weights']['high_treatment_complexity'] = 0.12
        model['key_factors'].append('high_treatment_complexity')
    
    # Study phase impact
    study_phase = study_parameters.get('phase', 'III')
    if study_phase in ['I', 'II']:
        model['risk_weights']['early_phase_uncertainty'] = 0.08
        model['key_factors'].append('early_phase_uncertainty')
    
    return model

def validate_model_with_current_data(model: Dict, processed_patients: List[Dict]) -> Dict:
    """Validate model performance with current patient data."""
    validation_metrics = {
        'patients_evaluated': len(processed_patients),
        'risk_distribution': {'low': 0, 'moderate': 0, 'high': 0, 'very_high': 0},
        'confidence_score': 0.75
    }
    
    # Calculate risk scores for current patients
    risk_scores = []
    for patient in processed_patients:
        risk_score = calculate_patient_risk_score(patient, model)
        risk_scores.append(risk_score)
        
        # Categorize risk
        if risk_score < model['risk_thresholds']['low']:
            validation_metrics['risk_distribution']['low'] += 1
        elif risk_score < model['risk_thresholds']['moderate']:
            validation_metrics['risk_distribution']['moderate'] += 1
        elif risk_score < model['risk_thresholds']['high']:
            validation_metrics['risk_distribution']['high'] += 1
        else:
            validation_metrics['risk_distribution']['very_high'] += 1
    
    # Calculate confidence based on risk distribution reasonableness
    high_risk_percent = (validation_metrics['risk_distribution']['high'] + 
                        validation_metrics['risk_distribution']['very_high']) / len(processed_patients)
    
    # Expect 10-30% high risk in typical studies
    if 0.1 <= high_risk_percent <= 0.3:
        validation_metrics['confidence_score'] = 0.85
    elif 0.05 <= high_risk_percent <= 0.4:
        validation_metrics['confidence_score'] = 0.75
    else:
        validation_metrics['confidence_score'] = 0.65
    
    validation_metrics['average_risk_score'] = sum(risk_scores) / len(risk_scores)
    validation_metrics['risk_score_std'] = calculate_standard_deviation(risk_scores)
    
    return validation_metrics

def calculate_standard_deviation(values: List[float]) -> float:
    """Calculate standard deviation of values."""
    if len(values) < 2:
        return 0.0
    
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)

def generate_patient_predictions(processed_patients: List[Dict], risk_model: Dict, 
                               prediction_timeframe: int) -> List[Dict]:
    """Generate dropout risk predictions for each patient."""
    predictions = []
    
    for patient in processed_patients:
        # Calculate base risk score
        risk_score = calculate_patient_risk_score(patient, risk_model)
        
        # Determine risk category
        risk_category = categorize_risk_level(risk_score, risk_model['risk_thresholds'])
        
        # Calculate time-specific dropout probability
        dropout_probability = calculate_dropout_probability(
            risk_score, prediction_timeframe, patient
        )
        
        # Identify specific risk factors for this patient
        patient_risk_factors = identify_patient_risk_factors(patient, risk_model)
        
        # Generate recommendations
        patient_recommendations = generate_patient_specific_recommendations(
            patient, risk_category, patient_risk_factors
        )
        
        prediction = {
            'patient_id': patient['patient_id'],
            'risk_score': round(risk_score, 3),
            'risk_category': risk_category,
            'dropout_probability': round(dropout_probability, 3),
            'prediction_timeframe_days': prediction_timeframe,
            'confidence_level': calculate_prediction_confidence(patient, risk_model),
            'key_risk_factors': patient_risk_factors,
            'protective_factors': identify_protective_factors(patient),
            'recommendations': patient_recommendations,
            'intervention_urgency': determine_intervention_urgency(risk_category, patient_risk_factors),
            'monitoring_frequency': determine_monitoring_frequency(risk_category),
            'predicted_dropout_date': calculate_predicted_dropout_date(
                patient, dropout_probability, prediction_timeframe
            )
        }
        
        predictions.append(prediction)
    
    # Sort by risk score (highest first)
    predictions.sort(key=lambda x: x['risk_score'], reverse=True)
    
    return predictions

def calculate_patient_risk_score(patient: Dict, risk_model: Dict) -> float:
    """Calculate risk score for individual patient."""
    risk_score = 0.0
    
    # Age factor
    age = patient.get('age', 0)
    if age < 25:
        risk_score += risk_model['risk_weights'].get('age_extremes', 0.1) * 1.5
    elif age > 75:
        risk_score += risk_model['risk_weights'].get('age_extremes', 0.1) * 1.2
    
    # Distance factor
    distance = patient.get('distance_to_site_miles', 0)
    if distance > 50:
        distance_factor = min(distance / 100, 2.0)  # Cap at 2x
        risk_score += risk_model['risk_weights'].get('distance_to_site', 0.1) * distance_factor
    
    # Comorbidity factor
    comorbidities = patient.get('comorbidity_count', 0)
    if comorbidities > 3:
        comorbidity_factor = min(comorbidities / 5, 2.0)
        risk_score += risk_model['risk_weights'].get('comorbidity_burden', 0.08) * comorbidity_factor
    
    # Engagement factors
    engagement_metrics = patient.get('engagement_metrics', {})
    missed_visits = engagement_metrics.get('missed_visits_count', 0)
    total_interactions = engagement_metrics.get('total_interactions', 1)
    
    if total_interactions > 0 and missed_visits / total_interactions > 0.2:
        miss_rate = missed_visits / total_interactions
        risk_score += risk_model['risk_weights'].get('missed_visits', 0.15) * miss_rate * 2
    
    # Compliance factor
    compliance_rate = patient.get('compliance_score', 100) / 100
    if compliance_rate < 0.8:
        compliance_factor = (0.8 - compliance_rate) * 2
        risk_score += risk_model['risk_weights'].get('poor_compliance', 0.15) * compliance_factor
    
    # Motivation and support factors
    if patient.get('baseline_motivation_score', 5) < 4:
        motivation_factor = (4 - patient.get('baseline_motivation_score', 5)) / 4
        risk_score += risk_model['risk_weights'].get('low_motivation', 0.12) * motivation_factor
    
    if not patient.get('caregiver_support', False):
        risk_score += risk_model['risk_weights'].get('lack_of_support', 0.08)
    
    # Risk indicators
    risk_indicators = patient.get('risk_indicators', [])
    for indicator in risk_indicators:
        indicator_weight = risk_model['risk_weights'].get(indicator, 0.05)
        risk_score += indicator_weight
    
    # Engagement trend factor
    engagement_trend = patient.get('engagement_trend', 'stable')
    if engagement_trend == 'declining':
        risk_score += 0.1
    elif engagement_trend == 'improving':
        risk_score -= 0.05
    
    # Time in study factor (longer time can reduce risk due to commitment)
    study_duration_days = patient.get('study_duration_days', 0)
    if study_duration_days > 90:  # After 3 months, some stabilization
        time_factor = min(study_duration_days / 365, 1.0) * 0.05
        risk_score -= time_factor
    
    return max(0.0, min(1.0, risk_score))  # Ensure score is between 0 and 1

def categorize_risk_level(risk_score: float, thresholds: Dict) -> str:
    """Categorize risk level based on score and thresholds."""
    if risk_score >= thresholds['very_high']:
        return 'very_high'
    elif risk_score >= thresholds['high']:
        return 'high'
    elif risk_score >= thresholds['moderate']:
        return 'moderate'
    else:
        return 'low'

def calculate_dropout_probability(risk_score: float, timeframe_days: int, patient: Dict) -> float:
    """Calculate probability of dropout within specified timeframe."""
    # Base probability from risk score
    base_probability = risk_score
    
    # Adjust for timeframe (longer timeframe = higher probability)
    time_factor = min(timeframe_days / 365, 2.0)  # Max 2x for very long timeframes
    time_adjusted_probability = base_probability * (0.5 + time_factor * 0.5)
    
    # Adjust for patient-specific factors
    study_duration = patient.get('study_duration_days', 0)
    
    # Survival curve adjustment (risk changes over time)
    if study_duration < 30:  # Early high-risk period
        survival_factor = 1.2
    elif study_duration < 90:  # Stabilizing period
        survival_factor = 1.0
    else:  # Later period - commitment established
        survival_factor = 0.8
    
    final_probability = time_adjusted_probability * survival_factor
    
    return max(0.0, min(1.0, final_probability))

def identify_patient_risk_factors(patient: Dict, risk_model: Dict) -> List[Dict]:
    """Identify specific risk factors for individual patient."""
    risk_factors = []
    
    # Check each potential risk factor
    age = patient.get('age', 0)
    if age < 25 or age > 75:
        risk_factors.append({
            'factor': 'Age extremes',
            'value': age,
            'risk_level': 'high' if age < 20 or age > 80 else 'moderate',
            'description': f"Patient age {age} is associated with higher dropout risk"
        })
    
    distance = patient.get('distance_to_site_miles', 0)
    if distance > 30:
        risk_factors.append({
            'factor': 'Distance to site',
            'value': distance,
            'risk_level': 'high' if distance > 75 else 'moderate',
            'description': f"Distance of {distance} miles may create logistical barriers"
        })
    
    comorbidities = patient.get('comorbidity_count', 0)
    if comorbidities > 3:
        risk_factors.append({
            'factor': 'High comorbidity burden',
            'value': comorbidities,
            'risk_level': 'high' if comorbidities > 6 else 'moderate',
            'description': f"{comorbidities} comorbidities may complicate study participation"
        })
    
    # Engagement-based risk factors
    engagement_metrics = patient.get('engagement_metrics', {})
    compliance_rate = engagement_metrics.get('compliance_rate', 100)
    if compliance_rate < 80:
        risk_factors.append({
            'factor': 'Poor compliance',
            'value': compliance_rate,
            'risk_level': 'high' if compliance_rate < 60 else 'moderate',
            'description': f"Compliance rate of {compliance_rate:.1f}% indicates engagement issues"
        })
    
    missed_visits = engagement_metrics.get('missed_visits_count', 0)
    total_interactions = engagement_metrics.get('total_interactions', 1)
    if total_interactions > 0 and missed_visits / total_interactions > 0.2:
        miss_rate = (missed_visits / total_interactions) * 100
        risk_factors.append({
            'factor': 'High missed visit rate',
            'value': miss_rate,
            'risk_level': 'high' if miss_rate > 40 else 'moderate',
            'description': f"{miss_rate:.1f}% missed visit rate suggests attendance issues"
        })
    
    # Motivation and support factors
    motivation = patient.get('baseline_motivation_score', 5)
    if motivation < 4:
        risk_factors.append({
            'factor': 'Low baseline motivation',
            'value': motivation,
            'risk_level': 'high' if motivation < 3 else 'moderate',
            'description': f"Low motivation score of {motivation} may affect participation"
        })
    
    if not patient.get('caregiver_support', False):
        risk_factors.append({
            'factor': 'Lack of caregiver support',
            'value': False,
            'risk_level': 'moderate',
            'description': "No caregiver support may make participation more difficult"
        })
    
    # Sort by risk level
    risk_level_order = {'high': 3, 'moderate': 2, 'low': 1}
    risk_factors.sort(key=lambda x: risk_level_order.get(x['risk_level'], 0), reverse=True)
    
    return risk_factors

def identify_protective_factors(patient: Dict) -> List[Dict]:
    """Identify factors that may protect against dropout."""
    protective_factors = []
    
    # Strong engagement
    compliance_score = patient.get('compliance_score', 0)
    if compliance_score > 90:
        protective_factors.append({
            'factor': 'High compliance',
            'value': compliance_score,
            'protection_level': 'high',
            'description': f"Excellent compliance rate of {compliance_score:.1f}%"
        })
    
    # Good motivation
    motivation = patient.get('baseline_motivation_score', 5)
    if motivation > 7:
        protective_factors.append({
            'factor': 'High motivation',
            'value': motivation,
            'protection_level': 'high',
            'description': f"High motivation score of {motivation}"
        })
    
    # Support system
    if patient.get('caregiver_support', False):
        protective_factors.append({
            'factor': 'Caregiver support',
            'value': True,
            'protection_level': 'moderate',
            'description': "Has caregiver support system"
        })
    
    # Previous trial experience
    if patient.get('previous_trial_participation', False):
        protective_factors.append({
            'factor': 'Previous trial experience',
            'value': True,
            'protection_level': 'moderate',
            'description': "Previous clinical trial participation"
        })
    
    # Close to site
    distance = patient.get('distance_to_site_miles', 999)
    if distance < 15:
        protective_factors.append({
            'factor': 'Close proximity to site',
            'value': distance,
            'protection_level': 'moderate',
            'description': f"Lives only {distance} miles from site"
        })
    
    # Engagement trend
    if patient.get('engagement_trend') == 'improving':
        protective_factors.append({
            'factor': 'Improving engagement',
            'value': 'improving',
            'protection_level': 'high',
            'description': "Engagement has been improving over time"
        })
    
    return protective_factors

def generate_patient_specific_recommendations(patient: Dict, risk_category: str, 
                                           risk_factors: List[Dict]) -> List[str]:
    """Generate specific recommendations for individual patient."""
    recommendations = []
    
    # Risk category-based recommendations
    if risk_category in ['high', 'very_high']:
        recommendations.append("Immediate intervention required - contact patient within 24 hours")
        recommendations.append("Schedule one-on-one discussion to understand barriers")
        recommendations.append("Consider personalized retention strategy")
    
    # Factor-specific recommendations
    for factor in risk_factors:
        factor_name = factor['factor'].lower()
        
        if 'distance' in factor_name:
            recommendations.append("Offer transportation assistance or telemedicine options")
            recommendations.append("Consider flexible scheduling for visits")
        
        elif 'compliance' in factor_name or 'missed visit' in factor_name:
            recommendations.append("Implement enhanced reminder system")
            recommendations.append("Investigate barriers to visit attendance")
            recommendations.append("Provide additional patient education on study importance")
        
        elif 'motivation' in factor_name:
            recommendations.append("Provide motivational counseling")
            recommendations.append("Share personalized study progress reports")
            recommendations.append("Connect with study peer support group")
        
        elif 'support' in factor_name:
            recommendations.append("Identify and engage caregiver or family member")
            recommendations.append("Provide family education materials")
        
        elif 'comorbidity' in factor_name:
            recommendations.append("Coordinate with patient's other healthcare providers")
            recommendations.append("Simplify study procedures where possible")
            recommendations.append("Monitor for competing health priorities")
    
    # Remove duplicates while preserving order
    unique_recommendations = []
    for rec in recommendations:
        if rec not in unique_recommendations:
            unique_recommendations.append(rec)
    
    return unique_recommendations[:5]  # Return top 5 recommendations

def determine_intervention_urgency(risk_category: str, risk_factors: List[Dict]) -> str:
    """Determine urgency level for intervention."""
    if risk_category == 'very_high':
        return 'immediate'
    elif risk_category == 'high':
        return 'urgent'
    elif risk_category == 'moderate' and any(f['risk_level'] == 'high' for f in risk_factors):
        return 'soon'
    elif risk_category == 'moderate':
        return 'routine'
    else:
        return 'monitoring'

def determine_monitoring_frequency(risk_category: str) -> str:
    """Determine appropriate monitoring frequency based on risk."""
    frequency_map = {
        'very_high': 'daily',
        'high': 'weekly',
        'moderate': 'bi-weekly',
        'low': 'monthly'
    }
    
    return frequency_map.get(risk_category, 'monthly')

def calculate_predicted_dropout_date(patient: Dict, dropout_probability: float, 
                                   timeframe_days: int) -> str:
    """Calculate predicted dropout date if risk factors persist."""
    if dropout_probability < 0.3:
        return None  # Low probability, no specific date predicted
    
    enrollment_date = patient.get('enrollment_date')
    if not enrollment_date:
        return None
    
    # Estimate dropout timing based on probability and typical patterns
    # Higher probability = earlier dropout within timeframe
    days_until_dropout = int(timeframe_days * (1 - dropout_probability))
    predicted_date = enrollment_date + timedelta(days=days_until_dropout)
    
    return predicted_date.strftime('%Y-%m-%d')

def calculate_prediction_confidence(patient: Dict, risk_model: Dict) -> float:
    """Calculate confidence level for individual prediction."""
    base_confidence = risk_model.get('model_confidence', 0.75)
    
    # Adjust based on data completeness
    data_completeness = 0
    key_fields = ['age', 'distance_to_site_miles', 'enrollment_date', 'baseline_motivation_score']
    
    for field in key_fields:
        if patient.get(field) is not None:
            data_completeness += 1
    
    data_factor = data_completeness / len(key_fields)
    
    # Adjust based on engagement data availability
    engagement_metrics = patient.get('engagement_metrics', {})
    engagement_data_quality = 0
    
    if engagement_metrics.get('total_interactions', 0) > 5:
        engagement_data_quality = 0.8
    elif engagement_metrics.get('total_interactions', 0) > 2:
        engagement_data_quality = 0.6
    else:
        engagement_data_quality = 0.3
    
    # Calculate final confidence
    adjusted_confidence = base_confidence * (0.5 * data_factor + 0.5 * engagement_data_quality)
    
    return round(adjusted_confidence, 2)

def identify_high_risk_patients(patient_predictions: List[Dict]) -> List[Dict]:
    """Identify patients with high dropout risk requiring immediate attention."""
    high_risk_patients = []
    
    for prediction in patient_predictions:
        if prediction['risk_category'] in ['high', 'very_high']:
            high_risk_patient = {
                'patient_id': prediction['patient_id'],
                'risk_score': prediction['risk_score'],
                'risk_category': prediction['risk_category'],
                'dropout_probability': prediction['dropout_probability'],
                'intervention_urgency': prediction['intervention_urgency'],
                'top_risk_factors': prediction['key_risk_factors'][:3],
                'immediate_actions': prediction['recommendations'][:3],
                'monitoring_frequency': prediction['monitoring_frequency'],
                'contact_priority': 1 if prediction['risk_category'] == 'very_high' else 2
            }
            high_risk_patients.append(high_risk_patient)
    
    # Sort by risk score (highest first)
    high_risk_patients.sort(key=lambda x: x['risk_score'], reverse=True)
    
    return high_risk_patients

def analyze_risk_factors(processed_patients: List[Dict], patient_predictions: List[Dict], 
                       study_parameters: Dict) -> Dict:
    """Analyze risk factors across the patient population."""
    analysis = {
        'most_common_risk_factors': {},
        'risk_factor_impact': {},
        'demographic_risk_patterns': {},
        'modifiable_vs_nonmodifiable': {},
        'risk_factor_combinations': {}
    }
    
    # Aggregate all risk factors
    all_risk_factors = []
    factor_impact_scores = {}
    
    for prediction in patient_predictions:
        patient_risk_factors = prediction.get('key_risk_factors', [])
        all_risk_factors.extend([f['factor'] for f in patient_risk_factors])
        
        # Track impact of each factor on risk score
        for factor in patient_risk_factors:
            factor_name = factor['factor']
            if factor_name not in factor_impact_scores:
                factor_impact_scores[factor_name] = []
            factor_impact_scores[factor_name].append(prediction['risk_score'])
    
    # Most common risk factors
    factor_counts = Counter(all_risk_factors)
    analysis['most_common_risk_factors'] = dict(factor_counts.most_common(10))
    
    # Risk factor impact analysis
    for factor_name, risk_scores in factor_impact_scores.items():
        if risk_scores:
            analysis['risk_factor_impact'][factor_name] = {
                'average_risk_score': round(sum(risk_scores) / len(risk_scores), 3),
                'patient_count': len(risk_scores),
                'impact_level': 'high' if sum(risk_scores) / len(risk_scores) > 0.6 else 'moderate'
            }
    
    # Demographic patterns
    analysis['demographic_risk_patterns'] = analyze_demographic_risk_patterns(
        processed_patients, patient_predictions
    )
    
    # Categorize modifiable vs non-modifiable factors
    analysis['modifiable_vs_nonmodifiable'] = categorize_risk_factors_modifiability(
        analysis['most_common_risk_factors']
    )
    
    return analysis

def analyze_demographic_risk_patterns(processed_patients: List[Dict], 
                                    patient_predictions: List[Dict]) -> Dict:
    """Analyze risk patterns by demographic groups."""
    patterns = {
        'age_groups': {},
        'gender': {},
        'distance_categories': {},
        'support_status': {}
    }
    
    # Create prediction lookup
    prediction_lookup = {p['patient_id']: p for p in patient_predictions}
    
    # Age group analysis
    age_groups = {'<30': [], '30-50': [], '50-65': [], '>65': []}
    for patient in processed_patients:
        age = patient.get('age', 0)
        prediction = prediction_lookup.get(patient['patient_id'])
        if prediction:
            risk_score = prediction['risk_score']
            
            if age < 30:
                age_groups['<30'].append(risk_score)
            elif age < 50:
                age_groups['30-50'].append(risk_score)
            elif age < 65:
                age_groups['50-65'].append(risk_score)
            else:
                age_groups['>65'].append(risk_score)
    
    for age_group, scores in age_groups.items():
        if scores:
            patterns['age_groups'][age_group] = {
                'average_risk': round(sum(scores) / len(scores), 3),
                'high_risk_count': len([s for s in scores if s > 0.6]),
                'patient_count': len(scores)
            }
    
    # Gender analysis
    gender_groups = {'male': [], 'female': [], 'other': []}
    for patient in processed_patients:
        gender = patient.get('gender', 'unknown').lower()
        prediction = prediction_lookup.get(patient['patient_id'])
        if prediction and gender in gender_groups:
            gender_groups[gender].append(prediction['risk_score'])
    
    for gender, scores in gender_groups.items():
        if scores:
            patterns['gender'][gender] = {
                'average_risk': round(sum(scores) / len(scores), 3),
                'high_risk_count': len([s for s in scores if s > 0.6]),
                'patient_count': len(scores)
            }
    
    return patterns

def categorize_risk_factors_modifiability(risk_factors: Dict) -> Dict:
    """Categorize risk factors by whether they can be modified through interventions."""
    modifiable_factors = [
        'Poor compliance', 'High missed visit rate', 'Low baseline motivation',
        'Lack of caregiver support', 'Poor engagement', 'Transportation issues'
    ]
    
    non_modifiable_factors = [
        'Age extremes', 'Distance to site', 'High comorbidity burden',
        'Disease severity', 'Gender', 'Education level'
    ]
    
    categorized = {
        'modifiable': {},
        'non_modifiable': {},
        'partially_modifiable': {}
    }
    
    for factor, count in risk_factors.items():
        if any(mod_factor.lower() in factor.lower() for mod_factor in modifiable_factors):
            categorized['modifiable'][factor] = count
        elif any(non_mod_factor.lower() in factor.lower() for non_mod_factor in non_modifiable_factors):
            categorized['non_modifiable'][factor] = count
        else:
            categorized['partially_modifiable'][factor] = count
    
    return categorized

def generate_intervention_recommendations(patient_predictions: List[Dict], 
                                        risk_factor_analysis: Dict, 
                                        intervention_history: List[Dict]) -> List[Dict]:
    """Generate intervention recommendations based on analysis results."""
    recommendations = []
    
    # High-level intervention strategies
    high_risk_count = len([p for p in patient_predictions if p['risk_category'] in ['high', 'very_high']])
    if high_risk_count > 0:
        recommendations.append({
            'category': 'immediate_action',
            'intervention': 'High-Risk Patient Outreach',
            'description': f'Immediate contact required for {high_risk_count} high-risk patients',
            'priority': 'urgent',
            'target_patients': high_risk_count,
            'implementation_timeline': '24-48 hours',
            'expected_impact': 'Prevent 30-50% of predicted dropouts',
            'resources_required': ['Study coordinator time', 'Patient contact protocols']
        })
    
    # Address most common modifiable risk factors
    modifiable_factors = risk_factor_analysis.get('modifiable_vs_nonmodifiable', {}).get('modifiable', {})
    for factor, count in list(modifiable_factors.items())[:3]:  # Top 3 modifiable factors
        if 'compliance' in factor.lower() or 'missed visit' in factor.lower():
            recommendations.append({
                'category': 'compliance_improvement',
                'intervention': 'Enhanced Compliance Support Program',
                'description': f'Address compliance issues affecting {count} patients',
                'priority': 'high',
                'target_patients': count,
                'implementation_timeline': '1-2 weeks',
                'expected_impact': 'Improve compliance rates by 25-40%',
                'resources_required': ['Patient education materials', 'Reminder system enhancement']
            })
        
        elif 'motivation' in factor.lower():
            recommendations.append({
                'category': 'motivation_enhancement',
                'intervention': 'Motivational Support Program',
                'description': f'Enhance motivation for {count} patients with low engagement',
                'priority': 'medium',
                'target_patients': count,
                'implementation_timeline': '2-3 weeks',
                'expected_impact': 'Increase engagement scores by 20-35%',
                'resources_required': ['Motivational interviewing training', 'Peer support groups']
            })
    
    # Technology-based interventions
    total_patients = len(patient_predictions)
    if total_patients > 20:  # For larger studies
        recommendations.append({
            'category': 'technology',
            'intervention': 'Predictive Monitoring System',
            'description': 'Implement automated risk monitoring and early warning system',
            'priority': 'medium',
            'target_patients': total_patients,
            'implementation_timeline': '4-6 weeks',
            'expected_impact': 'Identify at-risk patients 2-3 weeks earlier',
            'resources_required': ['Monitoring software', 'Staff training', 'Data integration']
        })
    
    # Personalized intervention strategies
    very_high_risk = len([p for p in patient_predictions if p['risk_category'] == 'very_high'])
    if very_high_risk > 0:
        recommendations.append({
            'category': 'personalized',
            'intervention': 'Individualized Retention Plans',
            'description': f'Develop personalized retention strategies for {very_high_risk} very high-risk patients',
            'priority': 'urgent',
            'target_patients': very_high_risk,
            'implementation_timeline': '1 week',
            'expected_impact': 'Prevent 60-80% of very high-risk dropouts',
            'resources_required': ['Case management', 'Flexible study procedures', 'Additional support services']
        })
    
    return recommendations

def create_retention_strategies(high_risk_patients: List[Dict], risk_factor_analysis: Dict, 
                              study_parameters: Dict) -> Dict:
    """Create specific retention strategies based on risk analysis."""
    strategies = {
        'immediate_actions': [],
        'short_term_strategies': [],
        'long_term_strategies': [],
        'resource_requirements': {},
        'success_metrics': {}
    }
    
    # Immediate actions for very high-risk patients
    very_high_risk = [p for p in high_risk_patients if p['risk_category'] == 'very_high']
    if very_high_risk:
        strategies['immediate_actions'] = [
            {
                'action': 'Emergency retention calls',
                'description': f'Contact all {len(very_high_risk)} very high-risk patients within 24 hours',
                'target_patients': [p['patient_id'] for p in very_high_risk],
                'timeline': '24 hours',
                'responsible_role': 'Study coordinator'
            },
            {
                'action': 'Barrier assessment',
                'description': 'Conduct detailed assessment of participation barriers',
                'target_patients': [p['patient_id'] for p in very_high_risk],
                'timeline': '48 hours',
                'responsible_role': 'Clinical research associate'
            }
        ]
    
    # Short-term strategies (1-4 weeks)
    common_factors = risk_factor_analysis.get('most_common_risk_factors', {})
    for factor, count in list(common_factors.items())[:5]:
        if 'distance' in factor.lower():
            strategies['short_term_strategies'].append({
                'strategy': 'Transportation assistance program',
                'description': f'Provide transportation support for {count} patients with distance barriers',
                'timeline': '2-3 weeks',
                'expected_impact': f'Reduce dropout risk for {count} patients by 40%'
            })
        
        elif 'compliance' in factor.lower():
            strategies['short_term_strategies'].append({
                'strategy': 'Enhanced reminder system',
                'description': f'Implement personalized reminder system for {count} patients with compliance issues',
                'timeline': '1-2 weeks',
                'expected_impact': f'Improve compliance rates by 30% for {count} patients'
            })
    
    # Long-term strategies (>1 month)
    total_high_risk = len(high_risk_patients)
    if total_high_risk > len(high_risk_patients) * 0.15:  # >15% high risk
        strategies['long_term_strategies'] = [
            {
                'strategy': 'Study design modifications',
                'description': 'Consider protocol amendments to reduce participant burden',
                'timeline': '2-3 months',
                'expected_impact': 'Reduce overall dropout risk by 20-25%'
            },
            {
                'strategy': 'Enhanced patient support services',
                'description': 'Implement comprehensive patient support program',
                'timeline': '1-2 months',
                'expected_impact': 'Improve overall retention by 15-20%'
            }
        ]
    
    # Resource requirements
    strategies['resource_requirements'] = {
        'personnel': [
            'Additional study coordinator time (20-40 hours/week)',
            'Patient support specialist (0.5-1.0 FTE)',
            'Transportation coordinator (part-time)'
        ],
        'technology': [
            'Enhanced reminder system',
            'Patient portal enhancements',
            'Risk monitoring dashboard'
        ],
        'financial': [
            'Transportation assistance fund',
            'Patient incentive program',
            'Additional support services'
        ]
    }
    
    # Success metrics
    strategies['success_metrics'] = {
        'primary_metrics': [
            'Dropout rate reduction (target: 25-40%)',
            'High-risk patient retention (target: 70-80%)',
            'Overall study completion rate (target: 85%+)'
        ],
        'secondary_metrics': [
            'Patient satisfaction scores',
            'Compliance rate improvements',
            'Time to intervention implementation'
        ],
        'monitoring_frequency': 'Weekly for high-risk patients, monthly for overall metrics'
    }
    
    return strategies

def calculate_study_retention_metrics(processed_patients: List[Dict], 
                                    patient_predictions: List[Dict], 
                                    study_parameters: Dict) -> Dict:
    """Calculate study-level retention metrics and projections."""
    metrics = {
        'current_retention_status': {},
        'predicted_retention_rates': {},
        'risk_distribution': {},
        'comparative_benchmarks': {},
        'study_performance_indicators': {}
    }
    
    total_patients = len(processed_patients)
    if total_patients == 0:
        return metrics
    
    # Current retention status
    active_patients = len([p for p in processed_patients if p.get('current_status', 'active') == 'active'])
    dropout_patients = total_patients - active_patients
    
    metrics['current_retention_status'] = {
        'total_enrolled': total_patients,
        'currently_active': active_patients,
        'dropout_count': dropout_patients,
        'current_retention_rate': round((active_patients / total_patients) * 100, 2)
    }
    
    # Predicted retention rates
    risk_categories = {'low': 0, 'moderate': 0, 'high': 0, 'very_high': 0}
    total_dropout_probability = 0
    
    for prediction in patient_predictions:
        risk_categories[prediction['risk_category']] += 1
        total_dropout_probability += prediction['dropout_probability']
    
    predicted_dropout_rate = (total_dropout_probability / len(patient_predictions)) * 100 if patient_predictions else 0
    predicted_retention_rate = 100 - predicted_dropout_rate
    
    metrics['predicted_retention_rates'] = {
        'predicted_retention_rate': round(predicted_retention_rate, 2),
        'predicted_dropout_rate': round(predicted_dropout_rate, 2),
        'confidence_interval': f"±{round(predicted_dropout_rate * 0.15, 1)}%"  # Simplified CI
    }
    
    # Risk distribution
    metrics['risk_distribution'] = {
        'low_risk_patients': risk_categories['low'],
        'moderate_risk_patients': risk_categories['moderate'],
        'high_risk_patients': risk_categories['high'] + risk_categories['very_high'],
        'high_risk_percentage': round(((risk_categories['high'] + risk_categories['very_high']) / total_patients) * 100, 2)
    }
    
    # Comparative benchmarks (based on literature/industry standards)
    study_type = study_parameters.get('study_type', 'interventional').lower()
    study_duration_weeks = study_parameters.get('planned_duration_weeks', 52)
    
    benchmark_retention_rate = get_benchmark_retention_rate(study_type, study_duration_weeks)
    metrics['comparative_benchmarks'] = {
        'industry_benchmark': benchmark_retention_rate,
        'performance_vs_benchmark': round(predicted_retention_rate - benchmark_retention_rate, 2),
        'benchmark_category': 'above' if predicted_retention_rate > benchmark_retention_rate else 'below'
    }
    
    # Study performance indicators
    metrics['study_performance_indicators'] = {
        'retention_risk_level': determine_study_retention_risk_level(metrics),
        'intervention_priority': determine_study_intervention_priority(metrics),
        'predicted_study_completion_rate': calculate_study_completion_rate(metrics, study_parameters),
        'enrollment_impact': assess_enrollment_impact(metrics)
    }
    
    return metrics

def get_benchmark_retention_rate(study_type: str, duration_weeks: int) -> float:
    """Get benchmark retention rate based on study characteristics."""
    # Simplified benchmark data based on literature
    base_rates = {
        'interventional': 85,
        'observational': 90,
        'device': 80,
        'behavioral': 75
    }
    
    base_rate = base_rates.get(study_type, 85)
    
    # Adjust for duration
    if duration_weeks > 104:  # >2 years
        base_rate -= 10
    elif duration_weeks > 52:  # 1-2 years
        base_rate -= 5
    elif duration_weeks < 12:  # <3 months
        base_rate += 5
    
    return max(60, min(95, base_rate))

def determine_study_retention_risk_level(metrics: Dict) -> str:
    """Determine overall retention risk level for the study."""
    predicted_retention = metrics['predicted_retention_rates']['predicted_retention_rate']
    high_risk_percentage = metrics['risk_distribution']['high_risk_percentage']
    
    if predicted_retention < 70 or high_risk_percentage > 30:
        return 'high'
    elif predicted_retention < 80 or high_risk_percentage > 20:
        return 'moderate'
    else:
        return 'low'

def determine_study_intervention_priority(metrics: Dict) -> str:
    """Determine intervention priority for the study."""
    risk_level = determine_study_retention_risk_level(metrics)
    
    if risk_level == 'high':
        return 'immediate'
    elif risk_level == 'moderate':
        return 'urgent'
    else:
        return 'routine'

def calculate_study_completion_rate(metrics: Dict, study_parameters: Dict) -> float:
    """Calculate predicted study completion rate."""
    predicted_retention = metrics['predicted_retention_rates']['predicted_retention_rate']
    
    # Adjust for study-specific factors
    adjustment_factors = 0
    
    # Duration adjustment
    duration_weeks = study_parameters.get('planned_duration_weeks', 52)
    if duration_weeks > 104:
        adjustment_factors -= 5
    elif duration_weeks > 52:
        adjustment_factors -= 2
    
    # Complexity adjustment
    complexity = study_parameters.get('treatment_complexity', 'low')
    if complexity == 'high':
        adjustment_factors -= 3
    elif complexity == 'medium':
        adjustment_factors -= 1
    
    final_completion_rate = predicted_retention + adjustment_factors
    return max(50, min(95, final_completion_rate))

def assess_enrollment_impact(metrics: Dict) -> Dict:
    """Assess impact of retention issues on enrollment strategy."""
    high_risk_percentage = metrics['risk_distribution']['high_risk_percentage']
    
    impact_assessment = {
        'enrollment_adjustment_needed': high_risk_percentage > 25,
        'recommended_over_enrollment_percentage': max(0, high_risk_percentage - 15),
        'screening_intensification_needed': high_risk_percentage > 20,
        'site_performance_review_needed': high_risk_percentage > 30
    }
    
    return impact_assessment

def analyze_retention_trends(processed_patients: List[Dict], historical_data: List[Dict]) -> Dict:
    """Analyze retention trends over time."""
    trends = {
        'historical_comparison': {},
        'temporal_patterns': {},
        'predictive_trends': {},
        'seasonal_effects': {}
    }
    
    # Historical comparison
    if historical_data:
        historical_retention_rates = [record.get('retention_rate', 0) for record in historical_data if record.get('retention_rate')]
        if historical_retention_rates:
            trends['historical_comparison'] = {
                'average_historical_retention': round(sum(historical_retention_rates) / len(historical_retention_rates), 2),
                'best_historical_retention': max(historical_retention_rates),
                'worst_historical_retention': min(historical_retention_rates),
                'trend_direction': 'stable'  # Simplified
            }
    
    # Temporal patterns in current study
    enrollment_dates = [p.get('enrollment_date') for p in processed_patients if p.get('enrollment_date')]
    if len(enrollment_dates) > 5:
        # Group by enrollment month
        monthly_enrollments = {}
        for date in enrollment_dates:
            month_key = date.strftime('%Y-%m')
            if month_key not in monthly_enrollments:
                monthly_enrollments[month_key] = 0
            monthly_enrollments[month_key] += 1
        
        trends['temporal_patterns'] = {
            'enrollment_by_month': monthly_enrollments,
            'peak_enrollment_month': max(monthly_enrollments.items(), key=lambda x: x[1])[0] if monthly_enrollments else None,
            'enrollment_trend': 'increasing' if len(monthly_enrollments) > 1 else 'stable'
        }
    
    return trends

def generate_monitoring_recommendations(patient_predictions: List[Dict], 
                                      high_risk_patients: List[Dict]) -> List[Dict]:
    """Generate recommendations for ongoing monitoring."""
    recommendations = []
    
    # High-risk patient monitoring
    if high_risk_patients:
        recommendations.append({
            'monitoring_type': 'high_risk_patient_tracking',
            'description': f'Daily monitoring of {len(high_risk_patients)} high-risk patients',
            'frequency': 'daily',
            'metrics_to_track': [
                'Contact attempts and responses',
                'Visit attendance',
                'Compliance rates',
                'Barrier resolution progress'
            ],
            'alert_triggers': [
                'Missed contact attempts (>2 consecutive)',
                'Missed visits',
                'Declining compliance scores',
                'New risk factors identified'
            ],
            'responsible_roles': ['Study coordinator', 'Principal investigator']
        })
    
    # Overall study monitoring
    recommendations.append({
        'monitoring_type': 'study_retention_dashboard',
        'description': 'Comprehensive retention metrics tracking',
        'frequency': 'weekly',
        'metrics_to_track': [
            'Overall retention rate',
            'Risk category distribution',
            'Intervention effectiveness',
            'Predictive model accuracy'
        ],
        'alert_triggers': [
            'Retention rate drops below 80%',
            'High-risk patient percentage exceeds 25%',
            'Prediction accuracy drops below 70%'
        ],
        'responsible_roles': ['Study manager', 'Data manager']
    })
    
    # Predictive model monitoring
    recommendations.append({
        'monitoring_type': 'model_performance_tracking',
        'description': 'Monitor and update retention prediction model',
        'frequency': 'monthly',
        'metrics_to_track': [
            'Prediction accuracy',
            'Model calibration',
            'New risk factor emergence',
            'Intervention response rates'
        ],
        'alert_triggers': [
            'Prediction accuracy <70%',
            'Significant model drift detected',
            'New risk patterns identified'
        ],
        'responsible_roles': ['Data scientist', 'Study statistician']
    })
    
    return recommendations