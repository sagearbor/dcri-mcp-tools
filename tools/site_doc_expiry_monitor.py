"""
Site Document Expiry Monitor Tool
Alert on expiring site documents for clinical trials
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta

def run(input_data: Dict) -> Dict:
    """
    Monitor and alert on expiring site documents
    
    Args:
        input_data: Dictionary containing:
            - site_documents: List of site documents with expiry dates
            - document_types: Required document types and their renewal periods
            - alert_thresholds: Days before expiry for different alert levels
            - sites: Site information for context
    
    Returns:
        Dictionary with document expiry alerts and renewal tracking
    """
    try:
        site_documents = input_data.get('site_documents', [])
        document_types = input_data.get('document_types', {})
        alert_thresholds = input_data.get('alert_thresholds', {
            'critical': 7,   # 7 days before expiry
            'urgent': 30,    # 30 days before expiry
            'warning': 60,   # 60 days before expiry
            'notice': 90     # 90 days before expiry
        })
        sites = input_data.get('sites', [])
        
        if not site_documents:
            return {
                'success': False,
                'error': 'No site documents provided'
            }
        
        current_date = datetime.now()
        
        # Create site lookup
        site_lookup = {site.get('site_id'): site for site in sites}
        
        # Process document types with default configurations
        default_doc_types = {
            'IRB_APPROVAL': {'name': 'IRB Approval', 'renewal_period_days': 365, 'critical': True},
            'CV': {'name': 'Curriculum Vitae', 'renewal_period_days': 730, 'critical': False},
            'LICENSE': {'name': 'Medical License', 'renewal_period_days': 730, 'critical': True},
            'GCP_CERTIFICATE': {'name': 'GCP Certificate', 'renewal_period_days': 1095, 'critical': True},
            'FINANCIAL_DISCLOSURE': {'name': 'Financial Disclosure', 'renewal_period_days': 365, 'critical': True},
            'REGULATORY_APPROVAL': {'name': 'Regulatory Approval', 'renewal_period_days': 365, 'critical': True},
            'LABORATORY_CERTIFICATION': {'name': 'Lab Certification', 'renewal_period_days': 365, 'critical': True},
            'SITE_AGREEMENT': {'name': 'Site Agreement', 'renewal_period_days': 1095, 'critical': True}
        }
        
        # Merge with provided document types
        for doc_type_id, doc_config in document_types.items():
            default_doc_types[doc_type_id] = doc_config
        
        # Analyze each document
        expiry_alerts = []
        document_status = []
        site_compliance = {}
        
        for document in site_documents:
            site_id = document.get('site_id')
            doc_type_id = document.get('document_type_id')
            doc_name = document.get('document_name', 'Unknown Document')
            expiry_date_str = document.get('expiry_date')
            submission_date_str = document.get('submission_date')
            status = document.get('status', 'active')
            
            if not expiry_date_str or status != 'active':
                continue
            
            try:
                expiry_date = datetime.fromisoformat(expiry_date_str)
                days_until_expiry = (expiry_date - current_date).days
                
                # Get document type configuration
                doc_config = default_doc_types.get(doc_type_id, {
                    'name': doc_name,
                    'renewal_period_days': 365,
                    'critical': False
                })
                
                # Determine alert level
                alert_level = None
                if days_until_expiry <= alert_thresholds['critical']:
                    alert_level = 'critical'
                elif days_until_expiry <= alert_thresholds['urgent']:
                    alert_level = 'urgent'
                elif days_until_expiry <= alert_thresholds['warning']:
                    alert_level = 'warning'
                elif days_until_expiry <= alert_thresholds['notice']:
                    alert_level = 'notice'
                
                # Document status
                if days_until_expiry < 0:
                    doc_status = 'expired'
                elif alert_level:
                    doc_status = f'expiring_{alert_level}'
                else:
                    doc_status = 'valid'
                
                site_info = site_lookup.get(site_id, {})
                site_name = site_info.get('site_name', f'Site {site_id}')
                
                doc_analysis = {
                    'document_id': document.get('document_id'),
                    'site_id': site_id,
                    'site_name': site_name,
                    'document_type_id': doc_type_id,
                    'document_type_name': doc_config['name'],
                    'document_name': doc_name,
                    'expiry_date': expiry_date.isoformat(),
                    'days_until_expiry': days_until_expiry,
                    'status': doc_status,
                    'alert_level': alert_level,
                    'is_critical': doc_config.get('critical', False),
                    'renewal_period_days': doc_config.get('renewal_period_days', 365),
                    'submission_date': submission_date_str,
                    'responsible_person': document.get('responsible_person')
                }
                
                document_status.append(doc_analysis)
                
                # Create alerts for documents needing attention
                if alert_level or days_until_expiry < 0:
                    alert_priority = 'high' if doc_config.get('critical') else 'medium'
                    if days_until_expiry < 0:
                        alert_priority = 'critical'
                    
                    expiry_alerts.append({
                        'alert_id': f"{site_id}_{doc_type_id}_{document.get('document_id', 'unknown')}",
                        'priority': alert_priority,
                        'alert_level': alert_level if days_until_expiry >= 0 else 'expired',
                        'site_id': site_id,
                        'site_name': site_name,
                        'document_type': doc_config['name'],
                        'document_name': doc_name,
                        'expiry_date': expiry_date.isoformat(),
                        'days_until_expiry': days_until_expiry,
                        'action_required': _get_action_required(days_until_expiry, doc_config),
                        'responsible_person': document.get('responsible_person'),
                        'created_at': current_date.isoformat()
                    })
                
                # Track site compliance
                if site_id not in site_compliance:
                    site_compliance[site_id] = {
                        'site_name': site_name,
                        'total_documents': 0,
                        'valid_documents': 0,
                        'expiring_documents': 0,
                        'expired_documents': 0,
                        'critical_issues': 0
                    }
                
                site_compliance[site_id]['total_documents'] += 1
                
                if doc_status == 'valid':
                    site_compliance[site_id]['valid_documents'] += 1
                elif doc_status == 'expired':
                    site_compliance[site_id]['expired_documents'] += 1
                    if doc_config.get('critical'):
                        site_compliance[site_id]['critical_issues'] += 1
                elif 'expiring' in doc_status:
                    site_compliance[site_id]['expiring_documents'] += 1
                    if alert_level in ['critical', 'urgent'] and doc_config.get('critical'):
                        site_compliance[site_id]['critical_issues'] += 1
                        
            except ValueError as e:
                # Skip documents with invalid date formats
                continue
        
        # Calculate compliance percentages
        for site_data in site_compliance.values():
            if site_data['total_documents'] > 0:
                site_data['compliance_percentage'] = round(
                    (site_data['valid_documents'] / site_data['total_documents']) * 100, 1
                )
            else:
                site_data['compliance_percentage'] = 100
        
        # Sort alerts by priority and expiry date
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        expiry_alerts.sort(key=lambda x: (
            priority_order.get(x['priority'], 99),
            x['days_until_expiry']
        ))
        
        # Generate summary statistics
        summary_stats = {
            'total_documents': len(document_status),
            'valid_documents': len([d for d in document_status if d['status'] == 'valid']),
            'expiring_documents': len([d for d in document_status if 'expiring' in d['status']]),
            'expired_documents': len([d for d in document_status if d['status'] == 'expired']),
            'critical_alerts': len([a for a in expiry_alerts if a['priority'] == 'critical']),
            'high_priority_alerts': len([a for a in expiry_alerts if a['priority'] == 'high']),
            'sites_monitored': len(site_compliance)
        }
        
        # Generate recommendations
        recommendations = []
        
        if summary_stats['expired_documents'] > 0:
            recommendations.append(f"{summary_stats['expired_documents']} documents have expired - immediate renewal required")
        
        if summary_stats['critical_alerts'] > 0:
            recommendations.append(f"{summary_stats['critical_alerts']} critical documents expire within 7 days")
        
        sites_with_critical_issues = len([s for s in site_compliance.values() if s['critical_issues'] > 0])
        if sites_with_critical_issues > 0:
            recommendations.append(f"{sites_with_critical_issues} sites have critical document compliance issues")
        
        # Document type specific recommendations
        doc_type_issues = {}
        for doc in document_status:
            if doc['status'] != 'valid':
                doc_type = doc['document_type_name']
                if doc_type not in doc_type_issues:
                    doc_type_issues[doc_type] = 0
                doc_type_issues[doc_type] += 1
        
        for doc_type, count in doc_type_issues.items():
            if count >= 3:
                recommendations.append(f"Multiple {doc_type} documents need attention - consider bulk renewal process")
        
        # Renewal schedule suggestions
        upcoming_renewals = {}
        for doc in document_status:
            if 0 <= doc['days_until_expiry'] <= 180:  # Next 6 months
                month = (current_date + timedelta(days=doc['days_until_expiry'])).strftime('%Y-%m')
                if month not in upcoming_renewals:
                    upcoming_renewals[month] = []
                upcoming_renewals[month].append({
                    'site_name': doc['site_name'],
                    'document_type': doc['document_type_name'],
                    'expiry_date': doc['expiry_date']
                })
        
        return {
            'success': True,
            'monitoring_data': {
                'generated_at': current_date.isoformat(),
                'alert_thresholds': alert_thresholds,
                'summary_statistics': summary_stats,
                'expiry_alerts': expiry_alerts[:50],  # Limit to top 50 alerts
                'document_status': document_status,
                'site_compliance': site_compliance,
                'upcoming_renewals_by_month': dict(sorted(upcoming_renewals.items())[:6]),
                'recommendations': recommendations
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error monitoring document expiry: {str(e)}'
        }

def _get_action_required(days_until_expiry: int, doc_config: Dict) -> str:
    """Generate action required text based on expiry timeline"""
    if days_until_expiry < 0:
        return f"Document expired {abs(days_until_expiry)} days ago - renew immediately"
    elif days_until_expiry <= 7:
        return "Renew within 1 week - critical priority"
    elif days_until_expiry <= 30:
        return "Schedule renewal within 30 days"
    elif days_until_expiry <= 60:
        return "Plan renewal process - contact responsible parties"
    else:
        return "Monitor for upcoming renewal timeline"