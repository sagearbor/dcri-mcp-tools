"""
Study Budget Calculator

Estimates clinical trial costs across various categories.
"""

from typing import Dict, Any, List


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate study budget based on various cost components.
    
    Args:
        input_data: Dictionary containing:
            - n_subjects: int
            - n_sites: int
            - study_duration_months: int
            - visits_per_subject: int
            - cost_per_subject: float
            - site_startup_cost: float
            - monitoring_visits_per_site: int
            - staff_costs: dict
    
    Returns:
        Dictionary with budget breakdown
    """
    
    n_subjects = input_data.get('n_subjects', 100)
    n_sites = input_data.get('n_sites', 10)
    duration = input_data.get('study_duration_months', 24)
    visits = input_data.get('visits_per_subject', 8)
    
    # Calculate major cost categories
    subject_costs = _calculate_subject_costs(input_data)
    site_costs = _calculate_site_costs(input_data)
    staff_costs = _calculate_staff_costs(input_data)
    operational_costs = _calculate_operational_costs(input_data)
    
    total_budget = sum([
        subject_costs['total'],
        site_costs['total'],
        staff_costs['total'],
        operational_costs['total']
    ])
    
    # Add contingency
    contingency = total_budget * 0.1
    total_with_contingency = total_budget + contingency
    
    return {
        'subject_costs': subject_costs,
        'site_costs': site_costs,
        'staff_costs': staff_costs,
        'operational_costs': operational_costs,
        'subtotal': total_budget,
        'contingency': contingency,
        'total_budget': total_with_contingency,
        'cost_per_subject': total_with_contingency / n_subjects if n_subjects > 0 else 0,
        'monthly_burn_rate': total_with_contingency / duration if duration > 0 else 0
    }


def _calculate_subject_costs(input_data: Dict) -> Dict:
    """Calculate subject-related costs."""
    n_subjects = input_data.get('n_subjects', 100)
    visits = input_data.get('visits_per_subject', 8)
    
    # Default costs if not provided
    visit_cost = input_data.get('cost_per_visit', 500)
    screening_cost = input_data.get('screening_cost', 1000)
    completion_bonus = input_data.get('completion_bonus', 200)
    
    screening_total = n_subjects * 1.3 * screening_cost  # 30% screen failure
    visit_total = n_subjects * visits * visit_cost
    bonus_total = n_subjects * 0.8 * completion_bonus  # 80% completion
    
    return {
        'screening': screening_total,
        'visits': visit_total,
        'completion_bonuses': bonus_total,
        'total': screening_total + visit_total + bonus_total
    }


def _calculate_site_costs(input_data: Dict) -> Dict:
    """Calculate site-related costs."""
    n_sites = input_data.get('n_sites', 10)
    
    startup_cost = input_data.get('site_startup_cost', 15000)
    maintenance_cost = input_data.get('site_maintenance_monthly', 2000)
    duration = input_data.get('study_duration_months', 24)
    close_out_cost = input_data.get('site_closeout_cost', 5000)
    
    startup_total = n_sites * startup_cost
    maintenance_total = n_sites * maintenance_cost * duration
    closeout_total = n_sites * close_out_cost
    
    return {
        'startup': startup_total,
        'maintenance': maintenance_total,
        'closeout': closeout_total,
        'total': startup_total + maintenance_total + closeout_total
    }


def _calculate_staff_costs(input_data: Dict) -> Dict:
    """Calculate staff/personnel costs."""
    duration = input_data.get('study_duration_months', 24)
    
    # Default FTE allocations
    staff = input_data.get('staff_costs', {
        'project_manager': {'fte': 1.0, 'monthly_cost': 10000},
        'clinical_coordinator': {'fte': 2.0, 'monthly_cost': 7500},
        'data_manager': {'fte': 1.0, 'monthly_cost': 8000},
        'statistician': {'fte': 0.5, 'monthly_cost': 12000},
        'medical_monitor': {'fte': 0.3, 'monthly_cost': 15000}
    })
    
    total_monthly = sum(
        role['fte'] * role['monthly_cost']
        for role in staff.values()
    )
    
    return {
        'monthly_total': total_monthly,
        'total': total_monthly * duration,
        'breakdown': staff
    }


def _calculate_operational_costs(input_data: Dict) -> Dict:
    """Calculate operational costs."""
    n_sites = input_data.get('n_sites', 10)
    duration = input_data.get('study_duration_months', 24)
    
    # Monitoring costs
    monitoring_visits = input_data.get('monitoring_visits_per_site', 8)
    monitoring_cost_per_visit = input_data.get('monitoring_cost_per_visit', 3000)
    monitoring_total = n_sites * monitoring_visits * monitoring_cost_per_visit
    
    # Other operational costs
    database_setup = input_data.get('database_setup_cost', 50000)
    database_maintenance = input_data.get('database_monthly', 2000) * duration
    
    lab_costs = input_data.get('lab_costs_total', 100000)
    drug_supply = input_data.get('drug_supply_cost', 200000)
    
    regulatory = input_data.get('regulatory_costs', 75000)
    
    return {
        'monitoring': monitoring_total,
        'database': database_setup + database_maintenance,
        'laboratory': lab_costs,
        'drug_supply': drug_supply,
        'regulatory': regulatory,
        'total': monitoring_total + database_setup + database_maintenance + 
                lab_costs + drug_supply + regulatory
    }
