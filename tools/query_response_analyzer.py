from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tracks and analyzes query response time metrics.
    
    Args:
        input_data: Dictionary containing:
            - queries: List of query records with:
                - query_id: Unique query identifier
                - subject_id: Subject identifier
                - site_id: Site identifier
                - query_type: Type of query (e.g., "data_clarification", "missing_data")
                - severity: Query severity ("low", "medium", "high")
                - issued_date: Date query was issued
                - response_date: Date response received (if any)
                - closed_date: Date query was closed (if any)
                - status: Current status ("open", "answered", "closed")
            - targets: Response time targets by severity (days)
            - analysis_period: Period to analyze (days)
    
    Returns:
        Dictionary containing:
            - summary: Overall query metrics
            - site_performance: Performance metrics by site
            - query_aging: Query aging analysis
            - response_times: Response time statistics
            - compliance_metrics: Target compliance metrics
            - recommendations: Performance recommendations
    """
    try:
        queries = input_data.get("queries", [])
        if not queries:
            return {
                "error": "No queries provided",
                "summary": {},
                "site_performance": {},
                "query_aging": {},
                "response_times": {},
                "compliance_metrics": {},
                "recommendations": []
            }
        
        targets = input_data.get("targets", {
            "high": 2,
            "medium": 5,
            "low": 10
        })
        analysis_period = input_data.get("analysis_period", 30)
        
        # Calculate metrics
        summary = calculate_summary_metrics(queries, analysis_period)
        site_performance = analyze_site_performance(queries, targets)
        query_aging = analyze_query_aging(queries)
        response_times = calculate_response_times(queries)
        compliance_metrics = calculate_compliance_metrics(queries, targets)
        recommendations = generate_recommendations(site_performance, compliance_metrics, query_aging)
        
        return {
            "summary": summary,
            "site_performance": site_performance,
            "query_aging": query_aging,
            "response_times": response_times,
            "compliance_metrics": compliance_metrics,
            "recommendations": recommendations
        }
        
    except Exception as e:
        return {
            "error": f"Error analyzing query response times: {str(e)}",
            "summary": {},
            "site_performance": {},
            "query_aging": {},
            "response_times": {},
            "compliance_metrics": {},
            "recommendations": []
        }


def calculate_summary_metrics(queries: List[Dict], analysis_period: int) -> Dict:
    """Calculate overall query summary metrics."""
    cutoff_date = datetime.now() - timedelta(days=analysis_period)
    recent_queries = [q for q in queries if 
                     datetime.fromisoformat(q.get("issued_date", "2000-01-01")) > cutoff_date]
    
    open_queries = [q for q in queries if q.get("status") == "open"]
    answered_queries = [q for q in queries if q.get("status") == "answered"]
    closed_queries = [q for q in queries if q.get("status") == "closed"]
    
    # Calculate response rates
    total_requiring_response = len([q for q in queries if q.get("status") in ["answered", "closed"]])
    
    return {
        "total_queries": len(queries),
        "recent_queries": len(recent_queries),
        "open_queries": len(open_queries),
        "answered_queries": len(answered_queries),
        "closed_queries": len(closed_queries),
        "response_rate": (len(answered_queries) + len(closed_queries)) / len(queries) * 100 if queries else 0,
        "closure_rate": len(closed_queries) / len(queries) * 100 if queries else 0,
        "queries_by_type": count_by_field(queries, "query_type"),
        "queries_by_severity": count_by_field(queries, "severity")
    }


def count_by_field(items: List[Dict], field: str) -> Dict:
    """Count items by a specific field."""
    counts = defaultdict(int)
    for item in items:
        value = item.get(field, "unknown")
        counts[value] += 1
    return dict(counts)


def analyze_site_performance(queries: List[Dict], targets: Dict) -> Dict:
    """Analyze query response performance by site."""
    site_metrics = defaultdict(lambda: {
        "total_queries": 0,
        "open_queries": 0,
        "response_times": [],
        "overdue_queries": 0,
        "compliance_rate": 0
    })
    
    for query in queries:
        site_id = query.get("site_id", "unknown")
        site_metrics[site_id]["total_queries"] += 1
        
        if query.get("status") == "open":
            site_metrics[site_id]["open_queries"] += 1
            
            # Check if overdue
            if is_query_overdue(query, targets):
                site_metrics[site_id]["overdue_queries"] += 1
        
        # Calculate response time
        response_time = calculate_query_response_time(query)
        if response_time is not None:
            site_metrics[site_id]["response_times"].append(response_time)
    
    # Calculate aggregated metrics
    for site_id, metrics in site_metrics.items():
        response_times = metrics["response_times"]
        if response_times:
            metrics["avg_response_time"] = statistics.mean(response_times)
            metrics["median_response_time"] = statistics.median(response_times)
            
            # Calculate compliance rate
            severity_targets = [targets.get(q.get("severity", "low"), 10) 
                               for q in queries if q.get("site_id") == site_id]
            compliant = sum(1 for i, rt in enumerate(response_times) 
                          if i < len(severity_targets) and rt <= severity_targets[i])
            metrics["compliance_rate"] = compliant / len(response_times) * 100 if response_times else 0
        else:
            metrics["avg_response_time"] = None
            metrics["median_response_time"] = None
        
        # Clean up response_times list for output
        del metrics["response_times"]
    
    return dict(site_metrics)


def is_query_overdue(query: Dict, targets: Dict) -> bool:
    """Check if a query is overdue based on targets."""
    if query.get("status") != "open":
        return False
    
    issued_date = datetime.fromisoformat(query.get("issued_date", "2000-01-01"))
    days_open = (datetime.now() - issued_date).days
    target_days = targets.get(query.get("severity", "low"), 10)
    
    return days_open > target_days


def calculate_query_response_time(query: Dict) -> Optional[float]:
    """Calculate response time for a query in days."""
    if not query.get("response_date"):
        return None
    
    try:
        issued = datetime.fromisoformat(query["issued_date"])
        responded = datetime.fromisoformat(query["response_date"])
        return (responded - issued).days
    except (KeyError, ValueError):
        return None


def analyze_query_aging(queries: List[Dict]) -> Dict:
    """Analyze aging of open queries."""
    open_queries = [q for q in queries if q.get("status") == "open"]
    
    if not open_queries:
        return {
            "open_query_count": 0,
            "aging_brackets": {},
            "oldest_query_days": 0,
            "critical_aged_queries": []
        }
    
    aging_brackets = {
        "0-3_days": 0,
        "4-7_days": 0,
        "8-14_days": 0,
        "15-30_days": 0,
        "over_30_days": 0
    }
    
    query_ages = []
    critical_aged = []
    
    for query in open_queries:
        try:
            issued = datetime.fromisoformat(query["issued_date"])
            age_days = (datetime.now() - issued).days
            query_ages.append(age_days)
            
            # Categorize into brackets
            if age_days <= 3:
                aging_brackets["0-3_days"] += 1
            elif age_days <= 7:
                aging_brackets["4-7_days"] += 1
            elif age_days <= 14:
                aging_brackets["8-14_days"] += 1
            elif age_days <= 30:
                aging_brackets["15-30_days"] += 1
            else:
                aging_brackets["over_30_days"] += 1
            
            # Track critical aged queries
            if query.get("severity") == "high" and age_days > 7:
                critical_aged.append({
                    "query_id": query["query_id"],
                    "subject_id": query.get("subject_id"),
                    "site_id": query.get("site_id"),
                    "days_open": age_days
                })
        except (KeyError, ValueError):
            continue
    
    return {
        "open_query_count": len(open_queries),
        "aging_brackets": aging_brackets,
        "oldest_query_days": max(query_ages) if query_ages else 0,
        "average_age_days": statistics.mean(query_ages) if query_ages else 0,
        "critical_aged_queries": critical_aged
    }


def calculate_response_times(queries: List[Dict]) -> Dict:
    """Calculate detailed response time statistics."""
    response_times_by_severity = defaultdict(list)
    response_times_by_type = defaultdict(list)
    all_response_times = []
    
    for query in queries:
        response_time = calculate_query_response_time(query)
        if response_time is not None:
            all_response_times.append(response_time)
            response_times_by_severity[query.get("severity", "unknown")].append(response_time)
            response_times_by_type[query.get("query_type", "unknown")].append(response_time)
    
    # Calculate statistics
    stats = {}
    
    if all_response_times:
        stats["overall"] = {
            "mean": statistics.mean(all_response_times),
            "median": statistics.median(all_response_times),
            "min": min(all_response_times),
            "max": max(all_response_times),
            "stdev": statistics.stdev(all_response_times) if len(all_response_times) > 1 else 0
        }
    
    # By severity
    stats["by_severity"] = {}
    for severity, times in response_times_by_severity.items():
        if times:
            stats["by_severity"][severity] = {
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "count": len(times)
            }
    
    # By type
    stats["by_type"] = {}
    for query_type, times in response_times_by_type.items():
        if times:
            stats["by_type"][query_type] = {
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "count": len(times)
            }
    
    return stats


def calculate_compliance_metrics(queries: List[Dict], targets: Dict) -> Dict:
    """Calculate target compliance metrics."""
    compliance_by_severity = defaultdict(lambda: {"compliant": 0, "total": 0})
    overall_compliant = 0
    overall_total = 0
    
    for query in queries:
        response_time = calculate_query_response_time(query)
        if response_time is not None:
            severity = query.get("severity", "low")
            target = targets.get(severity, 10)
            
            is_compliant = response_time <= target
            
            compliance_by_severity[severity]["total"] += 1
            overall_total += 1
            
            if is_compliant:
                compliance_by_severity[severity]["compliant"] += 1
                overall_compliant += 1
    
    # Calculate rates
    metrics = {
        "overall_compliance_rate": overall_compliant / overall_total * 100 if overall_total else 0,
        "by_severity": {}
    }
    
    for severity, counts in compliance_by_severity.items():
        if counts["total"] > 0:
            metrics["by_severity"][severity] = {
                "compliance_rate": counts["compliant"] / counts["total"] * 100,
                "compliant_count": counts["compliant"],
                "total_count": counts["total"],
                "target_days": targets.get(severity, 10)
            }
    
    return metrics


def generate_recommendations(site_performance: Dict, compliance_metrics: Dict, 
                            query_aging: Dict) -> List[Dict]:
    """Generate recommendations based on analysis."""
    recommendations = []
    
    # Low compliance sites
    low_compliance_sites = [
        site for site, metrics in site_performance.items()
        if metrics.get("compliance_rate", 100) < 80
    ]
    
    if low_compliance_sites:
        recommendations.append({
            "priority": "HIGH",
            "category": "Site Performance",
            "action": "Site training on query response",
            "description": f"{len(low_compliance_sites)} sites below 80% compliance",
            "affected_sites": low_compliance_sites[:5]  # Top 5
        })
    
    # High overdue count
    total_overdue = sum(m.get("overdue_queries", 0) for m in site_performance.values())
    if total_overdue > 10:
        recommendations.append({
            "priority": "CRITICAL",
            "category": "Overdue Queries",
            "action": "Escalate overdue queries",
            "description": f"{total_overdue} queries are overdue",
            "focus_sites": [s for s, m in site_performance.items() 
                          if m.get("overdue_queries", 0) > 2]
        })
    
    # Aged critical queries
    if query_aging.get("critical_aged_queries"):
        recommendations.append({
            "priority": "CRITICAL",
            "category": "Critical Queries",
            "action": "Immediate attention required",
            "description": f"{len(query_aging['critical_aged_queries'])} critical queries open >7 days",
            "queries": query_aging["critical_aged_queries"][:10]  # Top 10
        })
    
    # Overall compliance
    if compliance_metrics.get("overall_compliance_rate", 100) < 90:
        recommendations.append({
            "priority": "MEDIUM",
            "category": "Overall Compliance",
            "action": "Review query management process",
            "description": f"Overall compliance at {compliance_metrics['overall_compliance_rate']:.1f}%",
            "improvement_areas": identify_improvement_areas(compliance_metrics)
        })
    
    return recommendations


def identify_improvement_areas(compliance_metrics: Dict) -> List[str]:
    """Identify specific areas for improvement."""
    areas = []
    
    for severity, metrics in compliance_metrics.get("by_severity", {}).items():
        if metrics["compliance_rate"] < 80:
            areas.append(f"{severity} severity queries ({metrics['compliance_rate']:.1f}% compliance)")
    
    return areas