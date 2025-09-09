from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes audit trail data to identify patterns and potential issues.
    
    Args:
        input_data: Dictionary containing:
            - audit_entries: List of audit trail entries with:
                - timestamp: Event timestamp
                - user: User who performed action
                - action: Action performed
                - entity: Entity affected (e.g., "CRF", "Query")
                - entity_id: Specific entity identifier
                - old_value: Previous value (if applicable)
                - new_value: New value (if applicable)
                - reason: Reason for change
            - analysis_period: Time period to analyze (days)
            - alert_thresholds: Thresholds for alerts:
                - unusual_activity_multiplier: Factor for unusual activity
                - after_hours_threshold: % of after-hours activity
                - rapid_changes_window: Minutes for rapid change detection
    
    Returns:
        Dictionary containing:
            - summary: Overall audit trail summary
            - user_activity: Activity breakdown by user
            - suspicious_patterns: Identified suspicious patterns
            - compliance_issues: Potential compliance issues
            - recommendations: Recommended actions
            - visualizations: Data for charts
    """
    try:
        audit_entries = input_data.get("audit_entries", [])
        if not audit_entries:
            return {
                "error": "No audit entries provided",
                "summary": {},
                "user_activity": {},
                "suspicious_patterns": [],
                "compliance_issues": [],
                "recommendations": [],
                "visualizations": {}
            }
        
        analysis_period = input_data.get("analysis_period", 30)
        thresholds = input_data.get("alert_thresholds", {
            "unusual_activity_multiplier": 3,
            "after_hours_threshold": 20,
            "rapid_changes_window": 5
        })
        
        # Analyze audit trail
        summary = generate_summary(audit_entries, analysis_period)
        user_activity = analyze_user_activity(audit_entries)
        suspicious_patterns = detect_suspicious_patterns(audit_entries, thresholds)
        compliance_issues = check_compliance_issues(audit_entries)
        recommendations = generate_recommendations(suspicious_patterns, compliance_issues)
        visualizations = prepare_visualizations(audit_entries, user_activity)
        
        return {
            "summary": summary,
            "user_activity": user_activity,
            "suspicious_patterns": suspicious_patterns,
            "compliance_issues": compliance_issues,
            "recommendations": recommendations,
            "visualizations": visualizations
        }
        
    except Exception as e:
        return {
            "error": f"Error analyzing audit trail: {str(e)}",
            "summary": {},
            "user_activity": {},
            "suspicious_patterns": [],
            "compliance_issues": [],
            "recommendations": [],
            "visualizations": {}
        }


def generate_summary(audit_entries: List[Dict], analysis_period: int) -> Dict:
    """Generate overall audit trail summary."""
    cutoff_date = datetime.now() - timedelta(days=analysis_period)
    recent_entries = [e for e in audit_entries if 
                     datetime.fromisoformat(e.get("timestamp", "2000-01-01")) > cutoff_date]
    
    action_counts = defaultdict(int)
    entity_counts = defaultdict(int)
    
    for entry in recent_entries:
        action_counts[entry.get("action", "unknown")] += 1
        entity_counts[entry.get("entity", "unknown")] += 1
    
    return {
        "total_entries": len(recent_entries),
        "analysis_period_days": analysis_period,
        "unique_users": len(set(e.get("user") for e in recent_entries)),
        "action_breakdown": dict(action_counts),
        "entity_breakdown": dict(entity_counts),
        "daily_average": len(recent_entries) / analysis_period if analysis_period > 0 else 0
    }


def analyze_user_activity(audit_entries: List[Dict]) -> Dict:
    """Analyze activity patterns by user."""
    user_stats = defaultdict(lambda: {
        "total_actions": 0,
        "actions_by_type": defaultdict(int),
        "entities_modified": set(),
        "after_hours_actions": 0,
        "weekend_actions": 0
    })
    
    for entry in audit_entries:
        user = entry.get("user", "unknown")
        action = entry.get("action", "unknown")
        entity = entry.get("entity", "unknown")
        timestamp = datetime.fromisoformat(entry.get("timestamp", "2000-01-01"))
        
        user_stats[user]["total_actions"] += 1
        user_stats[user]["actions_by_type"][action] += 1
        user_stats[user]["entities_modified"].add(entity)
        
        # Check after-hours (before 8am or after 6pm)
        if timestamp.hour < 8 or timestamp.hour >= 18:
            user_stats[user]["after_hours_actions"] += 1
        
        # Check weekend
        if timestamp.weekday() >= 5:
            user_stats[user]["weekend_actions"] += 1
    
    # Convert sets to lists for JSON serialization
    for user in user_stats:
        user_stats[user]["entities_modified"] = list(user_stats[user]["entities_modified"])
        user_stats[user]["actions_by_type"] = dict(user_stats[user]["actions_by_type"])
    
    return dict(user_stats)


def detect_suspicious_patterns(audit_entries: List[Dict], thresholds: Dict) -> List[Dict]:
    """Detect potentially suspicious patterns in audit trail."""
    patterns = []
    
    # Pattern 1: Rapid successive changes
    rapid_changes = detect_rapid_changes(audit_entries, thresholds["rapid_changes_window"])
    if rapid_changes:
        patterns.extend(rapid_changes)
    
    # Pattern 2: Unusual activity volume
    volume_anomalies = detect_volume_anomalies(audit_entries, thresholds["unusual_activity_multiplier"])
    if volume_anomalies:
        patterns.extend(volume_anomalies)
    
    # Pattern 3: After-hours activity
    after_hours = detect_after_hours_activity(audit_entries, thresholds["after_hours_threshold"])
    if after_hours:
        patterns.extend(after_hours)
    
    # Pattern 4: Bulk deletions
    bulk_deletions = detect_bulk_deletions(audit_entries)
    if bulk_deletions:
        patterns.extend(bulk_deletions)
    
    return patterns


def detect_rapid_changes(entries: List[Dict], window_minutes: int) -> List[Dict]:
    """Detect rapid successive changes to same entity."""
    patterns = []
    entity_changes = defaultdict(list)
    
    for entry in entries:
        entity_id = entry.get("entity_id")
        if entity_id:
            entity_changes[entity_id].append(entry)
    
    for entity_id, changes in entity_changes.items():
        if len(changes) < 3:
            continue
        
        changes.sort(key=lambda x: x.get("timestamp", ""))
        
        for i in range(len(changes) - 2):
            time1 = datetime.fromisoformat(changes[i]["timestamp"])
            time2 = datetime.fromisoformat(changes[i + 2]["timestamp"])
            
            if (time2 - time1).total_seconds() < window_minutes * 60:
                patterns.append({
                    "type": "rapid_changes",
                    "severity": "medium",
                    "entity_id": entity_id,
                    "user": changes[i]["user"],
                    "description": f"3+ changes within {window_minutes} minutes",
                    "timestamp": changes[i]["timestamp"]
                })
                break
    
    return patterns


def detect_volume_anomalies(entries: List[Dict], multiplier: float) -> List[Dict]:
    """Detect unusual activity volume by user."""
    patterns = []
    user_daily_counts = defaultdict(lambda: defaultdict(int))
    
    for entry in entries:
        user = entry.get("user")
        date = datetime.fromisoformat(entry.get("timestamp", "2000-01-01")).date()
        user_daily_counts[user][date] += 1
    
    for user, daily_counts in user_daily_counts.items():
        if len(daily_counts) < 5:
            continue
        
        counts = list(daily_counts.values())
        avg_count = sum(counts) / len(counts)
        max_count = max(counts)
        
        if max_count > avg_count * multiplier:
            patterns.append({
                "type": "volume_anomaly",
                "severity": "low",
                "user": user,
                "description": f"Peak activity {max_count} vs average {avg_count:.1f}",
                "max_count": max_count,
                "average_count": avg_count
            })
    
    return patterns


def detect_after_hours_activity(entries: List[Dict], threshold_percent: float) -> List[Dict]:
    """Detect excessive after-hours activity."""
    patterns = []
    user_hours = defaultdict(lambda: {"total": 0, "after_hours": 0})
    
    for entry in entries:
        user = entry.get("user")
        timestamp = datetime.fromisoformat(entry.get("timestamp", "2000-01-01"))
        
        user_hours[user]["total"] += 1
        if timestamp.hour < 8 or timestamp.hour >= 18 or timestamp.weekday() >= 5:
            user_hours[user]["after_hours"] += 1
    
    for user, hours in user_hours.items():
        if hours["total"] < 10:
            continue
        
        after_hours_percent = (hours["after_hours"] / hours["total"]) * 100
        
        if after_hours_percent > threshold_percent:
            patterns.append({
                "type": "after_hours_activity",
                "severity": "low",
                "user": user,
                "description": f"{after_hours_percent:.1f}% of activity after hours",
                "after_hours_count": hours["after_hours"],
                "total_count": hours["total"]
            })
    
    return patterns


def detect_bulk_deletions(entries: List[Dict]) -> List[Dict]:
    """Detect bulk deletion patterns."""
    patterns = []
    user_daily_deletions = defaultdict(lambda: defaultdict(int))
    
    for entry in entries:
        if "delete" in entry.get("action", "").lower():
            user = entry.get("user")
            date = datetime.fromisoformat(entry.get("timestamp", "2000-01-01")).date()
            user_daily_deletions[user][date] += 1
    
    for user, daily_deletions in user_daily_deletions.items():
        for date, count in daily_deletions.items():
            if count >= 10:
                patterns.append({
                    "type": "bulk_deletion",
                    "severity": "high",
                    "user": user,
                    "date": str(date),
                    "description": f"{count} deletions in one day",
                    "deletion_count": count
                })
    
    return patterns


def check_compliance_issues(audit_entries: List[Dict]) -> List[Dict]:
    """Check for potential compliance issues."""
    issues = []
    
    # Check for missing reasons for changes
    missing_reasons = 0
    for entry in audit_entries:
        if entry.get("action") in ["update", "delete"] and not entry.get("reason"):
            missing_reasons += 1
    
    if missing_reasons > 0:
        issues.append({
            "type": "missing_change_reasons",
            "severity": "medium",
            "count": missing_reasons,
            "description": f"{missing_reasons} changes without documented reasons",
            "recommendation": "Ensure all data changes include reason for change"
        })
    
    # Check for unauthorized access patterns
    unauthorized_patterns = check_unauthorized_access(audit_entries)
    issues.extend(unauthorized_patterns)
    
    # Check for data integrity issues
    integrity_issues = check_data_integrity(audit_entries)
    issues.extend(integrity_issues)
    
    return issues


def check_unauthorized_access(entries: List[Dict]) -> List[Dict]:
    """Check for potential unauthorized access patterns."""
    issues = []
    
    # Check for access to sensitive entities outside normal hours
    sensitive_entities = ["patient_data", "randomization", "unblinding"]
    after_hours_sensitive = 0
    
    for entry in entries:
        if entry.get("entity", "").lower() in sensitive_entities:
            timestamp = datetime.fromisoformat(entry.get("timestamp", "2000-01-01"))
            if timestamp.hour < 6 or timestamp.hour >= 22:
                after_hours_sensitive += 1
    
    if after_hours_sensitive > 0:
        issues.append({
            "type": "after_hours_sensitive_access",
            "severity": "high",
            "count": after_hours_sensitive,
            "description": "Access to sensitive data outside business hours"
        })
    
    return issues


def check_data_integrity(entries: List[Dict]) -> List[Dict]:
    """Check for data integrity issues."""
    issues = []
    
    # Check for backdated entries
    backdated = 0
    for i, entry in enumerate(entries):
        if i > 0:
            current_time = datetime.fromisoformat(entry.get("timestamp", "2000-01-01"))
            prev_time = datetime.fromisoformat(entries[i-1].get("timestamp", "2000-01-01"))
            
            if current_time < prev_time - timedelta(minutes=1):
                backdated += 1
    
    if backdated > 0:
        issues.append({
            "type": "backdated_entries",
            "severity": "high",
            "count": backdated,
            "description": "Potential backdated audit trail entries"
        })
    
    return issues


def generate_recommendations(suspicious_patterns: List[Dict], 
                            compliance_issues: List[Dict]) -> List[Dict]:
    """Generate recommendations based on findings."""
    recommendations = []
    
    # High severity issues
    high_severity = [p for p in suspicious_patterns if p.get("severity") == "high"]
    high_severity.extend([i for i in compliance_issues if i.get("severity") == "high"])
    
    if high_severity:
        recommendations.append({
            "priority": "CRITICAL",
            "action": "Immediate review required",
            "description": f"Found {len(high_severity)} high-severity issues requiring immediate attention",
            "issues": high_severity
        })
    
    # User training recommendations
    if any(i["type"] == "missing_change_reasons" for i in compliance_issues):
        recommendations.append({
            "priority": "HIGH",
            "action": "User training on audit trail requirements",
            "description": "Multiple instances of missing change reasons detected"
        })
    
    # System configuration recommendations
    if any(p["type"] == "after_hours_activity" for p in suspicious_patterns):
        recommendations.append({
            "priority": "MEDIUM",
            "action": "Review system access controls",
            "description": "Consider implementing time-based access restrictions"
        })
    
    return recommendations


def prepare_visualizations(audit_entries: List[Dict], user_activity: Dict) -> Dict:
    """Prepare data for visualization."""
    # Activity timeline
    timeline_data = defaultdict(int)
    for entry in audit_entries:
        date = datetime.fromisoformat(entry.get("timestamp", "2000-01-01")).date()
        timeline_data[str(date)] += 1
    
    # User activity distribution
    user_distribution = {
        user: stats["total_actions"] 
        for user, stats in user_activity.items()
    }
    
    # Action type distribution
    action_distribution = defaultdict(int)
    for entry in audit_entries:
        action_distribution[entry.get("action", "unknown")] += 1
    
    return {
        "timeline": dict(timeline_data),
        "user_distribution": user_distribution,
        "action_distribution": dict(action_distribution),
        "hourly_pattern": generate_hourly_pattern(audit_entries)
    }


def generate_hourly_pattern(entries: List[Dict]) -> Dict:
    """Generate hourly activity pattern."""
    hourly_counts = defaultdict(int)
    
    for entry in entries:
        hour = datetime.fromisoformat(entry.get("timestamp", "2000-01-01")).hour
        hourly_counts[hour] += 1
    
    return {str(h): hourly_counts[h] for h in range(24)}