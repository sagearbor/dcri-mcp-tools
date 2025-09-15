"""
Tests for Schedule Converter Tool
"""

import pytest
import json
import os
import sqlite3
from unittest.mock import Mock, patch
from tools.schedule_converter import (
    ScheduleConverter, PatternMatcher, FuzzyMatcher,
    LLMAnalyzer, LLMJudge, MappingCache, run
)


class TestScheduleConverter:
    """Test the main ScheduleConverter class"""

    def test_convert_csv_to_cdisc_sdtm(self):
        """Test converting CSV to CDISC SDTM format"""
        converter = ScheduleConverter()

        csv_content = """Visit Name,Study Day,Procedures
Screening,-14,Informed Consent
Baseline,0,Vital Signs
Week 1,7,Blood Draw
Week 2,14,ECG"""

        result = converter.convert(
            file_content=csv_content,
            file_type="csv",
            target_format="CDISC_SDTM",
            organization_id="test_org"
        )

        assert result["success"] is True
        assert "data" in result
        assert "TV" in result["data"]
        assert "PR" in result["data"]
        assert len(result["data"]["TV"]) == 4
        assert len(result["data"]["PR"]) == 4
        assert result["confidence"] > 0

    def test_convert_to_fhir_r4(self):
        """Test converting to FHIR R4 format"""
        converter = ScheduleConverter()

        csv_content = """Visit,Day,Assessment
Screening,-14,Consent
Baseline,0,Physical Exam"""

        result = converter.convert(
            file_content=csv_content,
            file_type="csv",
            target_format="FHIR_R4"
        )

        assert result["success"] is True
        assert "data" in result
        fhir_data = result["data"]
        assert fhir_data["resourceType"] == "CarePlan"
        assert fhir_data["status"] == "active"
        assert len(fhir_data["activity"]) == 2

    def test_convert_to_omop_cdm(self):
        """Test converting to OMOP CDM format"""
        converter = ScheduleConverter()

        csv_content = """Visit,Day
Visit 1,1
Visit 2,7"""

        result = converter.convert(
            file_content=csv_content,
            file_type="csv",
            target_format="OMOP_CDM"
        )

        assert result["success"] is True
        assert "data" in result
        assert "visit_occurrence" in result["data"]
        assert len(result["data"]["visit_occurrence"]) == 2

    def test_analyze_structure(self):
        """Test structure analysis without conversion"""
        converter = ScheduleConverter()

        csv_content = """Visit Name,Study Day,Procedures
Screening,-14,Consent"""

        result = converter.analyze_structure(
            file_content=csv_content,
            file_type="csv"
        )

        assert "columns" in result
        assert "Visit Name" in result["columns"]
        assert "Study Day" in result["columns"]
        assert "Procedures" in result["columns"]
        assert result["row_count"] == 1

    def test_validate_cdisc_output(self):
        """Test CDISC SDTM validation"""
        converter = ScheduleConverter()

        valid_data = {
            "TV": [
                {"VISITNUM": 1, "VISIT": "Screening"},
                {"VISITNUM": 2, "VISIT": "Baseline"}
            ],
            "PR": []
        }

        result = converter.validate_output(valid_data, "CDISC_SDTM")
        assert result["valid"] is True
        assert len(result["issues"]) == 0

        # Test invalid data
        invalid_data = {"PR": []}  # Missing TV domain
        result = converter.validate_output(invalid_data, "CDISC_SDTM")
        assert result["valid"] is False
        assert len(result["issues"]) > 0

    def test_json_input(self):
        """Test JSON input parsing"""
        converter = ScheduleConverter()

        json_content = json.dumps([
            {"visit": "Screening", "day": -14, "procedure": "Consent"},
            {"visit": "Baseline", "day": 0, "procedure": "Labs"}
        ])

        result = converter.convert(
            file_content=json_content,
            file_type="json",
            target_format="CDISC_SDTM"
        )

        assert result["success"] is True
        assert result["row_count"] == 2

    def test_base64_input(self):
        """Test base64 encoded input"""
        import base64

        converter = ScheduleConverter()
        csv_content = "Visit,Day\nScreening,-14"
        encoded = base64.b64encode(csv_content.encode()).decode()

        result = converter.convert(
            file_content=encoded,
            file_type="csv",
            target_format="CDISC_SDTM"
        )

        assert result["success"] is True


class TestPatternMatcher:
    """Test the PatternMatcher class"""

    def test_match_columns(self):
        """Test pattern matching for columns"""
        matcher = PatternMatcher()

        parsed_data = {
            "columns": ["Visit Name", "Study Day", "Procedures"],
            "rows": []
        }

        result = matcher.match(parsed_data)

        assert "mappings" in result
        assert result["confidence"] > 0
        assert "Visit Name" in result["mappings"]
        assert result["mappings"]["Visit Name"] == "visit_name"

    def test_detect_patterns(self):
        """Test pattern detection"""
        matcher = PatternMatcher()

        parsed_data = {
            "columns": ["Visit Date", "Assessment Type"],
            "rows": []
        }

        patterns = matcher.detect_patterns(parsed_data)
        assert len(patterns) > 0
        assert any("Date pattern" in p for p in patterns)

    def test_suggest_mappings(self):
        """Test mapping suggestions"""
        matcher = PatternMatcher()

        parsed_data = {
            "columns": ["Visit", "Day", "Procedure"],
            "rows": []
        }

        suggestions = matcher.suggest_mappings(parsed_data)
        assert "Visit" in suggestions
        assert "Day" in suggestions
        assert "Procedure" in suggestions


class TestFuzzyMatcher:
    """Test the FuzzyMatcher class"""

    def test_validate_mappings(self):
        """Test fuzzy validation of mappings"""
        fuzzy = FuzzyMatcher()

        llm_result = {
            "mappings": {"Visit": "visit_name"},
            "confidence": 80
        }

        parsed_data = {
            "columns": ["Visit", "Day"],
            "rows": []
        }

        result = fuzzy.validate(llm_result, parsed_data)

        assert "mappings" in result
        assert result["confidence"] >= 0
        assert result["method"] == "fuzzy_logic"

    def test_similarity_calculation(self):
        """Test string similarity calculation"""
        fuzzy = FuzzyMatcher()

        # Exact substring match
        score = fuzzy._calculate_similarity("visit", "visit")
        assert score == 1.0

        # Substring match
        score = fuzzy._calculate_similarity("visits", "visit")
        assert score > 0.5

        # No match
        score = fuzzy._calculate_similarity("abc", "xyz")
        assert score < 0.5


class TestLLMAnalyzer:
    """Test the LLM Analyzer (simulated)"""

    def test_analyze_structure(self):
        """Test LLM structure analysis"""
        analyzer = LLMAnalyzer()

        parsed_data = {
            "columns": ["Visit Name", "Study Day", "Procedures"],
            "rows": []
        }

        result = analyzer.analyze_structure(parsed_data)

        assert "mappings" in result
        assert result["confidence"] > 0
        assert result["method"] == "llm_analysis"
        assert "Visit Name" in result["mappings"]


class TestLLMJudge:
    """Test the LLM Judge arbitration"""

    def test_arbitrate_disagreement(self):
        """Test arbitration between disagreeing systems"""
        judge = LLMJudge()

        llm_result = {
            "mappings": {"Visit": "visit_name"},
            "confidence": 75
        }

        fuzzy_result = {
            "mappings": {"Visit": "visit_day"},
            "confidence": 85
        }

        parsed_data = {"columns": ["Visit"], "rows": []}

        decision = judge.arbitrate(llm_result, fuzzy_result, parsed_data)

        assert "mappings" in decision
        assert "confidence" in decision
        assert "reasoning" in decision
        assert decision["arbitrated"] is True
        assert decision["confidence"] > 85  # Should be boosted


class TestMappingCache:
    """Test the MappingCache class"""

    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create a temporary database"""
        db_path = tmp_path / "test_mappings.db"
        return str(db_path)

    def test_store_and_retrieve_mapping(self, temp_db):
        """Test storing and retrieving mappings"""
        cache = MappingCache(db_path=temp_db)

        # Store a mapping
        result = {
            "mappings": {"Visit": "visit_name"},
            "confidence": 90,
            "fingerprint": "visit|day"
        }
        cache.store_mapping("org1", result)

        # Retrieve the mapping
        retrieved = cache.get_org_mappings("org1", "visit|day")
        assert retrieved is not None
        assert retrieved["confidence"] == 90
        assert "Visit" in retrieved["mappings"]

    def test_get_all_mappings(self, temp_db):
        """Test retrieving all mappings for an organization"""
        cache = MappingCache(db_path=temp_db)

        # Store multiple mappings
        cache.store_mapping("org1", {
            "mappings": {"Visit": "visit_name"},
            "confidence": 90,
            "fingerprint": "fp1"
        })
        cache.store_mapping("org1", {
            "mappings": {"Day": "visit_day"},
            "confidence": 85,
            "fingerprint": "fp2"
        })

        all_mappings = cache.get_all_mappings("org1")
        assert len(all_mappings) == 2

    def test_clear_cache(self, temp_db):
        """Test clearing cache"""
        cache = MappingCache(db_path=temp_db)

        # Store and then clear
        cache.store_mapping("org1", {
            "mappings": {},
            "confidence": 90,
            "fingerprint": "fp1"
        })

        count = cache.clear("org1")
        assert count == 1

        # Verify it's cleared
        all_mappings = cache.get_all_mappings("org1")
        assert len(all_mappings) == 0

    def test_get_statistics(self, temp_db):
        """Test getting statistics"""
        cache = MappingCache(db_path=temp_db)

        # Store some mappings
        cache.store_mapping("org1", {
            "mappings": {},
            "confidence": 90,
            "fingerprint": "fp1"
        })
        cache.store_mapping("org1", {
            "mappings": {},
            "confidence": 80,
            "fingerprint": "fp2"
        })

        stats = cache.get_statistics("org1")
        assert stats["total_mappings"] == 2
        assert stats["average_confidence"] == 85.0


class TestRunFunction:
    """Test the main run function"""

    def test_run_with_csv(self):
        """Test the run function with CSV input"""
        input_data = {
            "file_content": "Visit,Day\nScreening,-14\nBaseline,0",
            "file_type": "csv",
            "target_format": "CDISC_SDTM"
        }

        result = run(input_data)

        assert result["success"] is True
        assert "data" in result
        assert result["confidence"] > 0

    def test_run_with_missing_params(self):
        """Test run function with missing parameters"""
        input_data = {}

        result = run(input_data)

        # Should still work with defaults
        assert "success" in result

    def test_run_with_invalid_format(self):
        """Test run function with invalid target format"""
        input_data = {
            "file_content": "test",
            "file_type": "text",
            "target_format": "INVALID_FORMAT"
        }

        # Should raise an error or handle gracefully
        try:
            result = run(input_data)
            assert result["success"] is False or "error" in result
        except ValueError:
            pass  # Expected error

    def test_run_with_organization_cache(self):
        """Test run function with organization caching"""
        input_data = {
            "file_content": "Visit,Day\nScreening,-14",
            "file_type": "csv",
            "target_format": "CDISC_SDTM",
            "organization_id": "test_org_cache"
        }

        # First run - should create cache
        result1 = run(input_data)
        assert result1["success"] is True

        # Second run - might use cache
        result2 = run(input_data)
        assert result2["success"] is True


@pytest.mark.integration
class TestIntegration:
    """Integration tests for the complete conversion flow"""

    def test_complex_conversion_with_arbitration(self):
        """Test complex conversion that triggers arbitration"""
        converter = ScheduleConverter()

        # Complex CSV that might trigger disagreement
        csv_content = """TimePoint,Day Number,Assessments and Procedures
Pre-Study Visit,-21,Screening Labs|Consent Form
Study Start,1,Physical Exam|Baseline Measurements
Treatment Period 1,8,Drug Administration|Safety Labs"""

        result = converter.convert(
            file_content=csv_content,
            file_type="csv",
            target_format="CDISC_SDTM",
            confidence_threshold=95  # High threshold to potentially trigger arbitration
        )

        assert result["success"] is True
        assert "data" in result
        # Check if arbitration was used
        if result.get("arbitration_used"):
            assert "judge_reasoning" in result

    def test_all_target_formats(self):
        """Test conversion to all supported formats"""
        converter = ScheduleConverter()

        csv_content = """Visit,Day,Procedure
V1,1,Test1
V2,7,Test2"""

        formats = ["CDISC_SDTM", "FHIR_R4", "OMOP_CDM"]

        for target_format in formats:
            result = converter.convert(
                file_content=csv_content,
                file_type="csv",
                target_format=target_format
            )
            assert result["success"] is True, f"Failed for format: {target_format}"
            assert "data" in result
            # Verify the format is correctly applied
            if target_format == "CDISC_SDTM":
                assert "TV" in result["data"] and "PR" in result["data"]
            elif target_format == "FHIR_R4":
                assert result["data"].get("resourceType") == "CarePlan"
            elif target_format == "OMOP_CDM":
                assert "visit_occurrence" in result["data"]