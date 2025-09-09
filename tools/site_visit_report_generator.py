"""
Site Visit Report Generator Tool
Generate monitoring visit reports for clinical trial sites
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta

def run(input_data: Dict) -> Dict:
    """
    Generate comprehensive monitoring visit reports
    
    Args:
        input_data: Dictionary containing:
            - visit_details: Visit information and logistics
            - findings: List of findings and observations
            - site_metrics: Site performance metrics
            - previous_visit_findings: Prior visit findings for follow-up
            - report_template: Optional template configuration
    
    Returns:
        Dictionary with generated visit report content and structure
    """
    try:
        visit_details = input_data.get('visit_details', {})
        findings = input_data.get('findings', [])
        site_metrics = input_data.get('site_metrics', {})
        previous_findings = input_data.get('previous_visit_findings', [])
        report_template = input_data.get('report_template', {})
        
        if not visit_details:
            return {
                'success': False,
                'error': 'Visit details are required'
            }
        
        current_date = datetime.now()
        
        # Extract visit information
        site_id = visit_details.get('site_id')
        site_name = visit_details.get('site_name', f'Site {site_id}')
        visit_date = datetime.fromisoformat(visit_details.get('visit_date', current_date.isoformat()))
        visit_type = visit_details.get('visit_type', 'Routine Monitoring')
        monitor_name = visit_details.get('monitor_name', 'Unknown Monitor')
        study_id = visit_details.get('study_id', 'Unknown Study')
        
        # Initialize report structure
        report_data = {
            'report_header': {
                'study_id': study_id,
                'site_id': site_id,
                'site_name': site_name,
                'visit_type': visit_type,
                'visit_date': visit_date.isoformat(),
                'monitor_name': monitor_name,
                'report_generated': current_date.isoformat(),
                'visit_duration_hours': visit_details.get('duration_hours', 0)
            },
            'executive_summary': {},
            'site_performance': {},
            'findings_summary': {},
            'previous_findings_follow_up': {},
            'recommendations': [],
            'action_items': [],
            'next_visit_planning': {}
        }
        
        # Process findings by category
        findings_by_category = {}
        findings_by_severity = {'critical': 0, 'major': 0, 'minor': 0, 'observation': 0}
        
        for finding in findings:
            category = finding.get('category', 'General')
            severity = finding.get('severity', 'observation').lower()
            
            if category not in findings_by_category:
                findings_by_category[category] = []
            
            finding_data = {
                'finding_id': finding.get('finding_id', f"F{len(findings_by_category[category]) + 1}"),
                'description': finding.get('description', ''),
                'severity': severity,
                'subject_id': finding.get('subject_id'),
                'visit_id': finding.get('visit_id'),
                'corrective_action': finding.get('corrective_action', 'To be determined'),
                'due_date': finding.get('due_date'),
                'responsible_person': finding.get('responsible_person', 'Site staff'),
                'regulatory_impact': finding.get('regulatory_impact', False),
                'root_cause': finding.get('root_cause', ''),
                'preventive_action': finding.get('preventive_action', '')
            }
            
            findings_by_category[category].append(finding_data)
            
            if severity in findings_by_severity:
                findings_by_severity[severity] += 1
        
        # Generate executive summary
        total_findings = len(findings)
        critical_findings = findings_by_severity['critical']
        major_findings = findings_by_severity['major']
        
        summary_text = f"Monitoring visit conducted at {site_name} on {visit_date.strftime('%B %d, %Y')}. "
        summary_text += f"Total of {total_findings} findings identified"
        
        if critical_findings > 0:
            summary_text += f", including {critical_findings} critical finding{'s' if critical_findings != 1 else ''}"
        
        if major_findings > 0:
            summary_text += f" and {major_findings} major finding{'s' if major_findings != 1 else ''}"
        
        summary_text += ". "
        
        # Overall assessment
        if critical_findings > 0:
            overall_assessment = "Significant concerns identified - immediate action required"
            risk_level = "High"
        elif major_findings > 2:
            overall_assessment = "Multiple issues noted - corrective action needed"
            risk_level = "Medium"
        elif total_findings > 10:
            overall_assessment = "Multiple minor issues - process improvement recommended"
            risk_level = "Low-Medium"
        else:
            overall_assessment = "Generally acceptable performance"
            risk_level = "Low"
        
        report_data['executive_summary'] = {
            'summary_text': summary_text,
            'overall_assessment': overall_assessment,
            'risk_level': risk_level,
            'total_findings': total_findings,
            'findings_breakdown': findings_by_severity,
            'visit_outcome': visit_details.get('visit_outcome', 'Completed successfully')
        }
        
        # Site performance analysis
        enrollment_data = site_metrics.get('enrollment', {})
        quality_data = site_metrics.get('quality', {})
        
        performance_highlights = []
        performance_concerns = []
        
        # Enrollment performance
        enrolled = enrollment_data.get('current_enrolled', 0)
        target = enrollment_data.get('target', 0)
        enrollment_rate = enrollment_data.get('monthly_rate', 0)
        
        if target > 0:
            enrollment_progress = (enrolled / target) * 100
            if enrollment_progress >= 90:
                performance_highlights.append(f"Excellent enrollment progress: {enrollment_progress:.0f}% of target")
            elif enrollment_progress < 50:
                performance_concerns.append(f"Low enrollment: only {enrollment_progress:.0f}% of target achieved")
        
        # Quality metrics
        deviation_rate = quality_data.get('protocol_deviation_rate', 0)
        query_rate = quality_data.get('query_rate', 0)
        
        if deviation_rate > 0.1:  # > 10%
            performance_concerns.append(f"High protocol deviation rate: {deviation_rate:.1%}")
        elif deviation_rate < 0.05:  # < 5%
            performance_highlights.append(f"Low protocol deviation rate: {deviation_rate:.1%}")
        
        if query_rate > 0.2:  # > 20%
            performance_concerns.append(f"High data query rate: {query_rate:.1%}")
        elif query_rate < 0.1:  # < 10%
            performance_highlights.append(f"Low data query rate: {query_rate:.1%}")
        
        report_data['site_performance'] = {
            'enrollment_metrics': {
                'current_enrolled': enrolled,
                'target_enrollment': target,
                'enrollment_progress_percent': round((enrolled / max(target, 1)) * 100, 1),
                'monthly_enrollment_rate': enrollment_rate
            },
            'quality_metrics': {
                'protocol_deviation_rate': deviation_rate,
                'data_query_rate': query_rate,
                'sdv_completion_rate': quality_data.get('sdv_completion_rate', 0)
            },
            'performance_highlights': performance_highlights,
            'performance_concerns': performance_concerns
        }
        
        # Process previous findings follow-up
        previous_findings_status = []
        open_previous_findings = 0
        
        for prev_finding in previous_findings:
            status = prev_finding.get('status', 'open')
            follow_up_item = {
                'finding_id': prev_finding.get('finding_id'),
                'description': prev_finding.get('description', ''),
                'original_date': prev_finding.get('finding_date'),
                'status': status,
                'resolution_notes': prev_finding.get('resolution_notes', ''),
                'verification_date': prev_finding.get('verification_date')
            }
            
            if status.lower() in ['open', 'pending']:
                open_previous_findings += 1
            
            previous_findings_status.append(follow_up_item)
        
        report_data['previous_findings_follow_up'] = {
            'total_previous_findings': len(previous_findings),
            'open_previous_findings': open_previous_findings,
            'closure_rate': round(((len(previous_findings) - open_previous_findings) / max(len(previous_findings), 1)) * 100, 1),
            'findings_status': previous_findings_status
        }
        
        # Generate recommendations
        recommendations = []
        
        if critical_findings > 0:
            recommendations.append("Immediate implementation of corrective actions for critical findings")
            recommendations.append("Enhanced monitoring frequency until critical issues resolved")
        
        if major_findings > 3:
            recommendations.append("Review site processes and provide additional training")
        
        if open_previous_findings > 5:
            recommendations.append("Focus on closure of outstanding previous findings")
        
        if enrollment_rate < 2 and target > 0:  # Low enrollment
            recommendations.append("Implement enrollment enhancement strategies")
        
        if deviation_rate > 0.15:
            recommendations.append("Protocol compliance training for site staff")
        
        # Source document verification recommendations
        if 'source_verification' in site_metrics:
            sdv_rate = site_metrics['source_verification'].get('completion_rate', 0)
            if sdv_rate < 0.8:
                recommendations.append("Increase source document verification completion")
        
        report_data['recommendations'] = recommendations
        
        # Generate action items with priorities and due dates
        action_items = []
        
        # Critical findings become immediate action items
        for category, category_findings in findings_by_category.items():
            for finding in category_findings:
                if finding['severity'] == 'critical':
                    action_items.append({
                        'priority': 'Immediate',
                        'action': f"Address critical finding: {finding['description'][:100]}...",
                        'responsible': finding['responsible_person'],
                        'due_date': (current_date + timedelta(days=3)).isoformat(),
                        'finding_reference': finding['finding_id']
                    })
        
        # Major findings become high priority actions
        for category, category_findings in findings_by_category.items():
            for finding in category_findings:
                if finding['severity'] == 'major':
                    action_items.append({
                        'priority': 'High',
                        'action': f"Resolve major finding: {finding['description'][:100]}...",
                        'responsible': finding['responsible_person'],
                        'due_date': (current_date + timedelta(days=14)).isoformat(),
                        'finding_reference': finding['finding_id']
                    })
        
        # Performance-based action items
        if enrollment_rate < 2:
            action_items.append({
                'priority': 'Medium',
                'action': 'Develop and implement enrollment improvement plan',
                'responsible': 'Principal Investigator',
                'due_date': (current_date + timedelta(days=21)).isoformat(),
                'finding_reference': 'Performance'
            })
        
        report_data['action_items'] = action_items
        
        # Next visit planning
        next_visit_interval = 90  # Default 3 months
        
        if critical_findings > 0:
            next_visit_interval = 30  # 1 month for critical issues
        elif major_findings > 2:
            next_visit_interval = 60  # 2 months for multiple major issues
        
        next_visit_date = current_date + timedelta(days=next_visit_interval)
        
        report_data['next_visit_planning'] = {
            'recommended_next_visit_date': next_visit_date.isoformat(),
            'visit_interval_days': next_visit_interval,
            'visit_type': 'Follow-up' if critical_findings > 0 else 'Routine',
            'focus_areas': self._determine_focus_areas(findings_by_category, performance_concerns),
            'estimated_duration_hours': 6 if critical_findings > 0 else 4
        }
        
        # Generate detailed findings report
        detailed_findings = {}
        for category, category_findings in findings_by_category.items():
            detailed_findings[category] = {
                'findings_count': len(category_findings),
                'severity_breakdown': {},
                'findings': category_findings
            }
            
            # Calculate severity breakdown for category
            for finding in category_findings:
                severity = finding['severity']
                if severity not in detailed_findings[category]['severity_breakdown']:
                    detailed_findings[category]['severity_breakdown'][severity] = 0
                detailed_findings[category]['severity_breakdown'][severity] += 1
        
        report_data['findings_summary'] = {
            'findings_by_category': detailed_findings,
            'regulatory_reportable_findings': len([f for f in findings if f.get('regulatory_impact', False)]),
            'findings_requiring_capa': len([f for f in findings if f.get('severity') in ['critical', 'major']])
        }
        
        return {
            'success': True,
            'report_data': report_data,
            'report_metadata': {
                'template_version': report_template.get('version', '1.0'),
                'generated_by': 'Site Visit Report Generator',
                'generation_timestamp': current_date.isoformat()
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error generating site visit report: {str(e)}'
        }

def _determine_focus_areas(findings_by_category: Dict, performance_concerns: List) -> List[str]:
    """Determine focus areas for next visit based on findings and concerns"""
    focus_areas = []
    
    # Categories with most findings become focus areas
    sorted_categories = sorted(
        findings_by_category.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )
    
    for category, findings in sorted_categories[:3]:  # Top 3 categories
        if len(findings) > 0:
            focus_areas.append(category)
    
    # Add performance-based focus areas
    if any('enrollment' in concern.lower() for concern in performance_concerns):
        focus_areas.append('Enrollment Performance')
    
    if any('deviation' in concern.lower() for concern in performance_concerns):
        focus_areas.append('Protocol Compliance')
    
    if any('query' in concern.lower() for concern in performance_concerns):
        focus_areas.append('Data Quality')
    
    return list(set(focus_areas))  # Remove duplicates