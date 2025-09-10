"""
Project Timeline Generator

Creates project timelines with milestones and dependencies.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate comprehensive project timelines with milestones and dependencies
    
    Example:
        Input: Study parameters with start date, phases, and key activities
        Output: Detailed timeline with milestones, critical path, and Gantt chart data
    
    Parameters:
        start_date : str
            Project start date in YYYY-MM-DD format
        project_phases : list
            List of project phases with durations and dependencies
        study_type : str
            Type of clinical study affecting timeline complexity
        regulatory_requirements : list
            Regulatory milestones and submission deadlines
        resource_constraints : dict
            Resource availability and capacity constraints
    """
    
    start_date = input_data.get('start_date', datetime.now().strftime('%Y-%m-%d'))
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    
    # Generate timeline phases
    phases = _generate_phases(input_data, start_date)
    
    # Calculate milestones
    milestones = _calculate_milestones(phases, input_data)
    
    # Identify critical path
    critical_path = _identify_critical_path(phases)
    
    # Calculate total duration
    total_duration = _calculate_total_duration(phases)
    
    # Generate Gantt chart data
    gantt_data = _generate_gantt_data(phases)
    
    return {
        'phases': phases,
        'milestones': milestones,
        'critical_path': critical_path,
        'total_duration_days': total_duration,
        'total_duration_months': round(total_duration / 30, 1),
        'gantt_chart_data': gantt_data,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'projected_end_date': (start_date + timedelta(days=total_duration)).strftime('%Y-%m-%d'),
        'risk_factors': _identify_timeline_risks(input_data)
    }


def _generate_phases(data: Dict, start_date: datetime) -> List[Dict]:
    """Generate project phases."""
    phases = []
    current_date = start_date
    
    # Define standard clinical trial phases with durations
    phase_templates = [
        {
            'name': 'Study Startup',
            'duration_days': data.get('startup_duration', 90),
            'activities': [
                'Protocol finalization',
                'Regulatory submissions',
                'Site selection',
                'Contract negotiations'
            ]
        },
        {
            'name': 'Site Initiation',
            'duration_days': data.get('initiation_duration', 60),
            'activities': [
                'Site training',
                'Supply distribution',
                'System setup',
                'First site activated'
            ]
        },
        {
            'name': 'Recruitment',
            'duration_days': _calculate_recruitment_duration(data),
            'activities': [
                'Patient screening',
                'Enrollment',
                'Randomization'
            ]
        },
        {
            'name': 'Treatment',
            'duration_days': data.get('treatment_duration_days', 180),
            'activities': [
                'Dosing',
                'Safety monitoring',
                'Protocol compliance'
            ]
        },
        {
            'name': 'Follow-up',
            'duration_days': data.get('followup_duration_days', 90),
            'activities': [
                'Post-treatment assessments',
                'Safety follow-up',
                'Data completion'
            ]
        },
        {
            'name': 'Closeout',
            'duration_days': data.get('closeout_duration', 60),
            'activities': [
                'Database lock',
                'Statistical analysis',
                'Report writing',
                'Regulatory submission'
            ]
        }
    ]
    
    for template in phase_templates:
        phase = {
            'name': template['name'],
            'start_date': current_date.strftime('%Y-%m-%d'),
            'duration_days': template['duration_days'],
            'end_date': (current_date + timedelta(days=template['duration_days'])).strftime('%Y-%m-%d'),
            'activities': template['activities'],
            'status': _determine_phase_status(current_date, template['duration_days']),
            'dependencies': _get_phase_dependencies(template['name'])
        }
        phases.append(phase)
        current_date += timedelta(days=template['duration_days'])
    
    return phases


def _calculate_recruitment_duration(data: Dict) -> int:
    """Calculate recruitment duration based on enrollment rate."""
    n_subjects = data.get('n_subjects', 100)
    n_sites = data.get('n_sites', 10)
    enrollment_rate_per_site = data.get('enrollment_rate_per_site_per_month', 2)
    
    if n_sites > 0 and enrollment_rate_per_site > 0:
        months_needed = n_subjects / (n_sites * enrollment_rate_per_site)
        # Add ramp-up time
        months_needed += 2
        return int(months_needed * 30)
    
    return 180  # Default 6 months


def _calculate_milestones(phases: List[Dict], data: Dict) -> List[Dict]:
    """Calculate key milestones."""
    milestones = []
    
    # Extract key dates from phases
    for phase in phases:
        if phase['name'] == 'Study Startup':
            milestones.append({
                'name': 'Study Start',
                'date': phase['start_date'],
                'type': 'start',
                'phase': phase['name']
            })
        elif phase['name'] == 'Site Initiation':
            milestones.append({
                'name': 'First Site Activated',
                'date': phase['end_date'],
                'type': 'regulatory',
                'phase': phase['name']
            })
        elif phase['name'] == 'Recruitment':
            # First patient in
            fpi_date = datetime.strptime(phase['start_date'], '%Y-%m-%d') + timedelta(days=14)
            milestones.append({
                'name': 'First Patient In',
                'date': fpi_date.strftime('%Y-%m-%d'),
                'type': 'enrollment',
                'phase': phase['name']
            })
            # Last patient in
            milestones.append({
                'name': 'Last Patient In',
                'date': phase['end_date'],
                'type': 'enrollment',
                'phase': phase['name']
            })
        elif phase['name'] == 'Follow-up':
            milestones.append({
                'name': 'Last Patient Out',
                'date': phase['end_date'],
                'type': 'completion',
                'phase': phase['name']
            })
        elif phase['name'] == 'Closeout':
            # Database lock
            db_lock = datetime.strptime(phase['start_date'], '%Y-%m-%d') + timedelta(days=14)
            milestones.append({
                'name': 'Database Lock',
                'date': db_lock.strftime('%Y-%m-%d'),
                'type': 'data',
                'phase': phase['name']
            })
            # Study completion
            milestones.append({
                'name': 'Study Completion',
                'date': phase['end_date'],
                'type': 'completion',
                'phase': phase['name']
            })
    
    # Add custom milestones if provided
    custom_milestones = data.get('custom_milestones', [])
    milestones.extend(custom_milestones)
    
    return sorted(milestones, key=lambda x: x['date'])


def _identify_critical_path(phases: List[Dict]) -> List[str]:
    """Identify critical path activities."""
    critical_path = []
    
    # In a clinical trial, these are typically critical path
    critical_phases = [
        'Study Startup',
        'Site Initiation',
        'Recruitment',
        'Treatment',
        'Follow-up',
        'Closeout'
    ]
    
    for phase in phases:
        if phase['name'] in critical_phases:
            critical_path.append(phase['name'])
    
    return critical_path


def _calculate_total_duration(phases: List[Dict]) -> int:
    """Calculate total project duration."""
    return sum(phase['duration_days'] for phase in phases)


def _generate_gantt_data(phases: List[Dict]) -> List[Dict]:
    """Generate data for Gantt chart visualization."""
    gantt_data = []
    
    for i, phase in enumerate(phases):
        gantt_entry = {
            'task_id': i + 1,
            'task_name': phase['name'],
            'start': phase['start_date'],
            'end': phase['end_date'],
            'duration': phase['duration_days'],
            'progress': _estimate_progress(phase),
            'dependencies': phase['dependencies']
        }
        
        # Add activities as subtasks
        subtasks = []
        for j, activity in enumerate(phase['activities']):
            subtasks.append({
                'subtask_id': f"{i+1}.{j+1}",
                'subtask_name': activity,
                'parent_task': phase['name']
            })
        
        gantt_entry['subtasks'] = subtasks
        gantt_data.append(gantt_entry)
    
    return gantt_data


def _determine_phase_status(start_date: datetime, duration: int) -> str:
    """Determine current status of phase."""
    today = datetime.now()
    end_date = start_date + timedelta(days=duration)
    
    if today < start_date:
        return 'Not Started'
    elif today > end_date:
        return 'Completed'
    else:
        progress = (today - start_date).days / duration * 100
        return f'In Progress ({progress:.0f}%)'


def _get_phase_dependencies(phase_name: str) -> List[str]:
    """Get phase dependencies."""
    dependencies = {
        'Study Startup': [],
        'Site Initiation': ['Study Startup'],
        'Recruitment': ['Site Initiation'],
        'Treatment': ['Recruitment'],
        'Follow-up': ['Treatment'],
        'Closeout': ['Follow-up']
    }
    return dependencies.get(phase_name, [])


def _estimate_progress(phase: Dict) -> float:
    """Estimate phase progress."""
    status = phase['status']
    if status == 'Completed':
        return 100.0
    elif status == 'Not Started':
        return 0.0
    elif 'In Progress' in status:
        # Extract percentage from status
        import re
        match = re.search(r'(\d+)%', status)
        if match:
            return float(match.group(1))
    return 0.0


def _identify_timeline_risks(data: Dict) -> List[Dict]:
    """Identify potential timeline risks."""
    risks = []
    
    # Check enrollment rate
    enrollment_rate = data.get('enrollment_rate_per_site_per_month', 2)
    if enrollment_rate < 1:
        risks.append({
            'risk': 'Low enrollment rate',
            'impact': 'Timeline extension',
            'mitigation': 'Consider additional sites or recruitment strategies'
        })
    
    # Check number of sites
    n_sites = data.get('n_sites', 10)
    if n_sites < 5:
        risks.append({
            'risk': 'Limited number of sites',
            'impact': 'Recruitment delays',
            'mitigation': 'Plan for site expansion if needed'
        })
    
    # Check complexity
    if data.get('complex_protocol', False):
        risks.append({
            'risk': 'Complex protocol',
            'impact': 'Extended site training and startup',
            'mitigation': 'Allow extra time for site preparation'
        })
    
    return risks
