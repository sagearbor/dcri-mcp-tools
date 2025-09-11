"""
Comprehensive tests for the Compliance Knowledge Base tool.
Tests various scenarios including different schemas, rule types, and edge cases.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.compliance_knowledge_base import run


class TestComplianceKnowledgeBase:
    """Test suite for compliance knowledge base tool."""
    
    def test_basic_valid_schedule(self):
        """Test with a completely valid schedule."""
        input_data = {
            "schedule_data": {
                "study_id": "TEST-001",
                "visits": [
                    {
                        "id": "V1",
                        "day": 0,
                        "date": "2024-02-05",  # Monday
                        "type": "Screening",
                        "site": "SITE-001",
                        "procedures": ["informed_consent", "blood_draw"]
                    },
                    {
                        "id": "V2",
                        "day": 7,
                        "date": "2024-02-12",  # Monday
                        "type": "Baseline",
                        "site": "SITE-001",
                        "procedures": ["blood_draw", "ecg"]
                    }
                ]
            },
            "schema_type": "generic"
        }
        
        result = run(input_data)
        
        assert result["status"] == "success"
        assert result["compliance_status"] in ["PASS", "WARNING"]
        assert "summary" in result
        assert result["summary"]["visits_analyzed"] == 2
    
    def test_weekend_visit_violation(self):
        """Test detection of weekend visit violations."""
        input_data = {
            "schedule_data": {
                "visits": [
                    {
                        "id": "V1",
                        "day": 0,
                        "date": "2024-02-03",  # Saturday
                        "type": "Screening",
                        "site": "SITE-001",
                        "procedures": ["blood_draw"]
                    }
                ]
            },
            "schema_type": "generic"
        }
        
        result = run(input_data)
        
        assert result["status"] == "success"
        assert result["compliance_status"] == "FAIL"
        assert result["summary"]["errors"] > 0
        
        # Check that weekend violation was detected
        findings = result["findings"]
        weekend_findings = [f for f in findings if "weekend" in f["description"].lower()]
        assert len(weekend_findings) > 0
    
    def test_equipment_capability_violation(self):
        """Test detection of site equipment capability violations."""
        input_data = {
            "schedule_data": {
                "visits": [
                    {
                        "id": "V1",
                        "day": 7,
                        "date": "2024-02-05",
                        "type": "Treatment",
                        "site": "SITE-001",
                        "procedures": ["MRI"]  # SITE-001 doesn't have MRI
                    }
                ]
            },
            "schema_type": "generic"
        }
        
        result = run(input_data)
        
        assert result["status"] == "success"
        assert result["compliance_status"] == "FAIL"
        
        # Check for equipment violation
        findings = result["findings"]
        equipment_findings = [f for f in findings if "RES-001" in f.get("rule_id", "")]
        assert len(equipment_findings) > 0
    
    def test_safety_followup_missing(self):
        """Test detection of missing safety follow-up visits."""
        input_data = {
            "schedule_data": {
                "visits": [
                    {
                        "id": "V1",
                        "day": 0,
                        "date": "2024-02-05",
                        "type": "Screening",
                        "site": "SITE-002",
                        "procedures": ["biopsy"]  # Requires safety follow-up
                    },
                    {
                        "id": "V2",
                        "day": 21,
                        "date": "2024-02-26",  # More than 7 days later
                        "type": "Treatment",
                        "site": "SITE-002",
                        "procedures": ["blood_draw"]
                    }
                ]
            },
            "schema_type": "generic"
        }
        
        result = run(input_data)
        
        assert result["status"] == "success"
        
        # Check for safety follow-up violation
        findings = result["findings"]
        safety_findings = [f for f in findings if "REG-001" in f.get("rule_id", "")]
        assert len(safety_findings) > 0
    
    def test_visit_order_violation(self):
        """Test detection of visits out of chronological order."""
        input_data = {
            "schedule_data": {
                "visits": [
                    {
                        "id": "V1",
                        "day": 0,
                        "date": "2024-02-10",
                        "type": "Screening",
                        "site": "SITE-001",
                        "procedures": ["blood_draw"]
                    },
                    {
                        "id": "V2",
                        "day": 7,
                        "date": "2024-02-08",  # Earlier date than day 0
                        "type": "Baseline",
                        "site": "SITE-001",
                        "procedures": ["blood_draw"]
                    }
                ]
            },
            "schema_type": "generic"
        }
        
        result = run(input_data)
        
        assert result["status"] == "success"
        
        # Check for sequence violation
        findings = result["findings"]
        sequence_findings = [f for f in findings if "SEQ-001" in f.get("rule_id", "")]
        assert len(sequence_findings) > 0
    
    def test_rule_category_filtering(self):
        """Test filtering rules by category."""
        schedule_with_issues = {
            "visits": [
                {
                    "id": "V1",
                    "day": 0,
                    "date": "2024-02-03",  # Saturday - logistics issue
                    "type": "Screening",
                    "site": "SITE-001",
                    "procedures": ["MRI"]  # Equipment issue
                }
            ]
        }
        
        # Test with only logistics rules
        result = run({
            "schedule_data": schedule_with_issues,
            "schema_type": "generic",
            "rule_categories": ["logistics"]
        })
        
        assert result["status"] == "success"
        findings = result["findings"]
        
        # Should only have logistics findings
        for finding in findings:
            rule_id = finding.get("rule_id", "")
            assert rule_id.startswith("SITE") or rule_id.startswith("SEQ")
    
    def test_warning_filtering(self):
        """Test filtering of warning-level findings."""
        input_data = {
            "schedule_data": {
                "visits": [
                    {
                        "id": "V1",
                        "day": 0,
                        "date": "2024-02-05",
                        "type": "Screening",
                        "site": "SITE-001",
                        "procedures": ["blood_draw"]
                    }
                ]
            },
            "schema_type": "generic",
            "include_warnings": False
        }
        
        result = run(input_data)
        
        assert result["status"] == "success"
        
        # Check that warnings are filtered out
        findings = result["findings"]
        warning_findings = [f for f in findings if f.get("severity") == "warning"]
        assert len(warning_findings) == 0
    
    def test_cdisc_like_schema(self):
        """Test with CDISC-like data schema."""
        input_data = {
            "schedule_data": {
                "SV": [
                    {
                        "VISITNUM": 1,
                        "SVSTDTC": "2024-02-05",
                        "VISITDY": 0,
                        "SITEID": "001",
                        "USUBJID": "SUBJ001",
                        "PROC": ["blood_draw", "ecg"],
                        "VISIT": "Screening"
                    }
                ],
                "DM": [
                    {"USUBJID": "SUBJ001", "SITEID": "001"}
                ]
            },
            "schema_type": "cdisc_like"
        }
        
        result = run(input_data)
        
        assert result["status"] == "success"
        assert result["metadata"]["schema_type"] == "cdisc_like"
        assert result["summary"]["visits_analyzed"] > 0
    
    def test_missing_required_parameter(self):
        """Test error handling for missing required parameters."""
        result = run({})
        
        assert result["status"] == "error"
        assert "schedule_data" in result["message"]
    
    def test_invalid_date_format(self):
        """Test handling of invalid date formats."""
        input_data = {
            "schedule_data": {
                "visits": [
                    {
                        "id": "V1",
                        "day": 0,
                        "date": "invalid-date",
                        "type": "Screening",
                        "site": "SITE-001",
                        "procedures": ["blood_draw"]
                    }
                ]
            },
            "schema_type": "generic"
        }
        
        result = run(input_data)
        
        # Should still return success but may have date-related findings
        assert result["status"] == "success"
    
    def test_complex_multi_site_schedule(self):
        """Test a complex schedule with multiple sites and procedures."""
        input_data = {
            "schedule_data": {
                "study_id": "COMPLEX-001",
                "visits": [
                    {
                        "id": "V1",
                        "day": -7,
                        "date": "2024-01-29",
                        "type": "Pre-screening",
                        "site": "SITE-003",
                        "procedures": ["phone_screen"]
                    },
                    {
                        "id": "V2",
                        "day": 0,
                        "date": "2024-02-05",
                        "type": "Screening",
                        "site": "SITE-004",
                        "procedures": ["informed_consent", "blood_draw", "ecg", "MRI"]
                    },
                    {
                        "id": "V3",
                        "day": 7,
                        "date": "2024-02-12",
                        "type": "Baseline",
                        "site": "SITE-004",
                        "procedures": ["blood_draw", "PET Scan"]
                    },
                    {
                        "id": "V4",
                        "day": 14,
                        "date": "2024-02-19",
                        "type": "Treatment",
                        "site": "SITE-002",
                        "procedures": ["surgery"]
                    },
                    {
                        "id": "V5",
                        "day": 15,
                        "date": "2024-02-20",
                        "type": "Safety",
                        "site": "SITE-002",
                        "procedures": ["blood_draw", "ecg"]
                    }
                ]
            },
            "schema_type": "generic",
            "study_start_date": "2024-02-05"
        }
        
        result = run(input_data)
        
        assert result["status"] == "success"
        assert result["summary"]["visits_analyzed"] == 5
        
        # Check findings are categorized
        assert "findings_by_category" in result
    
    def test_washout_period_violation(self):
        """Test detection of inadequate washout periods."""
        input_data = {
            "schedule_data": {
                "visits": [
                    {
                        "id": "V1",
                        "day": 0,
                        "date": "2024-02-05",
                        "type": "Baseline",
                        "site": "SITE-002",
                        "procedures": ["contrast_imaging"]
                    },
                    {
                        "id": "V2",
                        "day": 7,
                        "date": "2024-02-12",
                        "type": "Treatment",
                        "site": "SITE-002",
                        "procedures": ["contrast_imaging"]  # Too soon after first
                    }
                ]
            },
            "schema_type": "generic"
        }
        
        result = run(input_data)
        
        assert result["status"] == "success"
        
        # Check for washout violation
        findings = result["findings"]
        washout_findings = [f for f in findings if "WASH" in f.get("rule_id", "")]
        assert len(washout_findings) > 0
    
    def test_metadata_information(self):
        """Test that metadata is properly included in response."""
        input_data = {
            "schedule_data": {
                "visits": []
            },
            "schema_type": "generic",
            "rule_categories": ["logistics", "safety"]
        }
        
        result = run(input_data)
        
        assert result["status"] == "success"
        assert "metadata" in result
        assert result["metadata"]["schema_type"] == "generic"
        assert result["metadata"]["rule_categories"] == ["logistics", "safety"]
        assert "available_schemas" in result["metadata"]
        assert "generic" in result["metadata"]["available_schemas"]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])