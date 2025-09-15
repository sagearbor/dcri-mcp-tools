"""
Clinical Trial Schedule Converter Tool
Autonomous conversion with dual validation (LLM + Fuzzy Logic)
"""

import json
import base64
import csv
import io
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import sqlite3
import os

# For the mock implementation, we'll simulate LLM responses
# In production, these would be replaced with actual Azure OpenAI calls

logger = logging.getLogger(__name__)


class ScheduleConverter:
    """Main converter class with autonomous arbitration"""

    def __init__(self):
        self.pattern_matcher = PatternMatcher()
        self.fuzzy_matcher = FuzzyMatcher()
        self.mapping_cache = MappingCache()
        self.llm_analyzer = LLMAnalyzer()
        self.llm_judge = LLMJudge()
        self.format_converters = {
            "CDISC_SDTM": self.to_cdisc_sdtm,
            "FHIR_R4": self.to_fhir_r4,
            "OMOP_CDM": self.to_omop_cdm
        }

    def convert(self, file_content: str, file_type: str, target_format: str,
                organization_id: Optional[str] = None,
                confidence_threshold: float = 85) -> Dict[str, Any]:
        """
        Main conversion method with autonomous arbitration

        Example:
            Input: CSV file with columns "Visit Name", "Day", "Procedures"
            Output: CDISC SDTM formatted data with TV and PR domains

        Parameters:
            file_content : str
                Base64 encoded or raw text content
            file_type : str
                Type of file (csv, xlsx, json, etc.)
            target_format : str
                Target format (CDISC_SDTM, FHIR_R4, OMOP_CDM)
            organization_id : str, optional
                Organization ID for cached mappings
            confidence_threshold : float, optional
                Minimum confidence for autonomous conversion (default: 85)
        """
        # Parse the input file
        parsed_data = self._parse_input(file_content, file_type)

        # Step 1: Check cache for organization mappings
        if organization_id:
            cached_result = self.mapping_cache.get_org_mappings(
                organization_id, parsed_data.get("fingerprint")
            )
            if cached_result and cached_result["confidence"] > 90:
                logger.info(f"Using cached mapping with confidence {cached_result['confidence']}")
                return self._apply_conversion(parsed_data, cached_result["mappings"], target_format)

        # Step 2: Try pattern matching (fast path)
        pattern_result = self.pattern_matcher.match(parsed_data)
        if pattern_result["confidence"] > confidence_threshold:
            logger.info(f"Pattern matching succeeded with confidence {pattern_result['confidence']}")
            self.mapping_cache.store_mapping(organization_id, pattern_result)
            return self._apply_conversion(parsed_data, pattern_result["mappings"], target_format)

        # Step 3: LLM analysis (simulated for now)
        llm_result = self.llm_analyzer.analyze_structure(parsed_data)

        # Step 4: Fuzzy logic validation
        fuzzy_result = self.fuzzy_matcher.validate(llm_result, parsed_data)

        # Step 5: Check agreement
        agreement = self._calculate_agreement(llm_result, fuzzy_result)
        if agreement > confidence_threshold:
            logger.info(f"LLM and Fuzzy agree with confidence {agreement}")
            final_result = self._merge_results(llm_result, fuzzy_result)
            self.mapping_cache.store_mapping(organization_id, final_result)
            return self._apply_conversion(parsed_data, final_result["mappings"], target_format)

        # Step 6: Autonomous arbitration - Judge decides
        logger.info("Disagreement detected, invoking LLM judge for arbitration")
        judge_decision = self.llm_judge.arbitrate(llm_result, fuzzy_result, parsed_data)

        # Store decision for learning
        self.mapping_cache.store_mapping(organization_id, judge_decision)

        result = self._apply_conversion(parsed_data, judge_decision["mappings"], target_format)
        result["arbitration_used"] = True
        result["judge_reasoning"] = judge_decision.get("reasoning", "")

        return result

    def analyze_structure(self, file_content: str, file_type: str) -> Dict[str, Any]:
        """Analyze file structure without converting"""
        parsed_data = self._parse_input(file_content, file_type)

        return {
            "columns": parsed_data.get("columns", []),
            "row_count": parsed_data.get("row_count", 0),
            "detected_patterns": self.pattern_matcher.detect_patterns(parsed_data),
            "suggested_mappings": self.pattern_matcher.suggest_mappings(parsed_data),
            "file_type": file_type
        }

    def validate_output(self, data: Dict[str, Any], target_format: str) -> Dict[str, Any]:
        """Validate converted data against standard requirements"""
        validators = {
            "CDISC_SDTM": self._validate_cdisc_sdtm,
            "FHIR_R4": self._validate_fhir_r4,
            "OMOP_CDM": self._validate_omop_cdm
        }

        if target_format not in validators:
            return {"valid": False, "issues": ["Unknown target format"]}

        return validators[target_format](data)

    def get_cached_mappings(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get cached mappings for an organization"""
        return self.mapping_cache.get_all_mappings(organization_id)

    def clear_cache(self, organization_id: str) -> int:
        """Clear cached mappings"""
        return self.mapping_cache.clear(organization_id)

    def get_statistics(self, organization_id: Optional[str] = None) -> Dict[str, Any]:
        """Get conversion statistics"""
        return self.mapping_cache.get_statistics(organization_id)

    def _parse_input(self, file_content: str, file_type: str) -> Dict[str, Any]:
        """Parse input file based on type"""
        parsers = {
            "csv": self._parse_csv,
            "json": self._parse_json,
            "text": self._parse_text
        }

        if file_type not in parsers:
            raise ValueError(f"Unsupported file type: {file_type}")

        # Try to decode base64 if needed
        try:
            decoded = base64.b64decode(file_content)
            file_content = decoded.decode('utf-8')
        except:
            # Not base64 encoded, use as is
            pass

        return parsers[file_type](file_content)

    def _parse_csv(self, content: str) -> Dict[str, Any]:
        """Parse CSV content"""
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)

        return {
            "columns": reader.fieldnames or [],
            "rows": rows,
            "row_count": len(rows),
            "fingerprint": self._generate_fingerprint(reader.fieldnames or [])
        }

    def _parse_json(self, content: str) -> Dict[str, Any]:
        """Parse JSON content"""
        data = json.loads(content)

        # Extract structure
        if isinstance(data, list) and data:
            columns = list(data[0].keys()) if isinstance(data[0], dict) else []
            return {
                "columns": columns,
                "rows": data,
                "row_count": len(data),
                "fingerprint": self._generate_fingerprint(columns)
            }
        else:
            return {
                "columns": [],
                "rows": [data] if not isinstance(data, list) else data,
                "row_count": 1,
                "fingerprint": ""
            }

    def _parse_text(self, content: str) -> Dict[str, Any]:
        """Parse plain text content"""
        lines = content.strip().split('\n')
        return {
            "columns": ["text"],
            "rows": [{"text": line} for line in lines],
            "row_count": len(lines),
            "fingerprint": self._generate_fingerprint(["text"])
        }

    def _generate_fingerprint(self, columns: List[str]) -> str:
        """Generate a fingerprint for the file structure"""
        return "|".join(sorted(columns)).lower()

    def _calculate_agreement(self, llm_result: Dict, fuzzy_result: Dict) -> float:
        """Calculate agreement between LLM and fuzzy results"""
        llm_mappings = llm_result.get("mappings", {})
        fuzzy_mappings = fuzzy_result.get("mappings", {})

        if not llm_mappings or not fuzzy_mappings:
            return 0

        matches = sum(1 for k, v in llm_mappings.items()
                     if k in fuzzy_mappings and fuzzy_mappings[k] == v)
        total = max(len(llm_mappings), len(fuzzy_mappings))

        agreement_score = (matches / total * 100) if total > 0 else 0

        # Boost score if confidences are both high
        if llm_result.get("confidence", 0) > 80 and fuzzy_result.get("confidence", 0) > 80:
            agreement_score = min(agreement_score + 10, 100)

        return agreement_score

    def _merge_results(self, llm_result: Dict, fuzzy_result: Dict) -> Dict[str, Any]:
        """Merge LLM and fuzzy results when they agree"""
        merged_mappings = {}

        # Take mappings that both agree on
        llm_mappings = llm_result.get("mappings", {})
        fuzzy_mappings = fuzzy_result.get("mappings", {})

        for key in set(llm_mappings.keys()) | set(fuzzy_mappings.keys()):
            if key in llm_mappings and key in fuzzy_mappings:
                if llm_mappings[key] == fuzzy_mappings[key]:
                    merged_mappings[key] = llm_mappings[key]
                else:
                    # Use the one with higher confidence
                    if llm_result.get("confidence", 0) > fuzzy_result.get("confidence", 0):
                        merged_mappings[key] = llm_mappings[key]
                    else:
                        merged_mappings[key] = fuzzy_mappings[key]
            elif key in llm_mappings:
                merged_mappings[key] = llm_mappings[key]
            else:
                merged_mappings[key] = fuzzy_mappings[key]

        avg_confidence = (llm_result.get("confidence", 0) + fuzzy_result.get("confidence", 0)) / 2

        return {
            "mappings": merged_mappings,
            "confidence": avg_confidence,
            "method": "merged"
        }

    def _apply_conversion(self, parsed_data: Dict, mappings: Dict, target_format: str) -> Dict[str, Any]:
        """Apply mappings to convert to target format"""
        if target_format not in self.format_converters:
            raise ValueError(f"Unknown target format: {target_format}")

        converter = self.format_converters[target_format]
        converted_data = converter(parsed_data, mappings)

        return {
            "success": True,
            "data": converted_data,
            "confidence": mappings.get("confidence", 85),
            "mappings_used": mappings,
            "row_count": parsed_data.get("row_count", 0)
        }

    def to_cdisc_sdtm(self, parsed_data: Dict, mappings: Dict) -> Dict[str, Any]:
        """Convert to CDISC SDTM format"""
        tv_domain = []  # Trial Visits
        pr_domain = []  # Procedures

        rows = parsed_data.get("rows", [])
        for idx, row in enumerate(rows):
            # Map visit information
            tv_record = {
                "STUDYID": "STUDY001",  # Default study ID
                "DOMAIN": "TV",
                "VISITNUM": idx + 1,
                "VISIT": self._get_mapped_value(row, mappings, "visit_name"),
                "VISITDY": self._get_mapped_value(row, mappings, "visit_day"),
            }
            tv_domain.append(tv_record)

            # Map procedures if present
            procedures = self._get_mapped_value(row, mappings, "procedures")
            if procedures:
                proc_list = procedures.split(",") if isinstance(procedures, str) else [procedures]
                for proc in proc_list:
                    pr_record = {
                        "STUDYID": "STUDY001",
                        "DOMAIN": "PR",
                        "VISITNUM": idx + 1,
                        "PRTRT": proc.strip()
                    }
                    pr_domain.append(pr_record)

        return {
            "TV": tv_domain,
            "PR": pr_domain,
            "format": "CDISC_SDTM",
            "version": "3.3"
        }

    def to_fhir_r4(self, parsed_data: Dict, mappings: Dict) -> Dict[str, Any]:
        """Convert to FHIR R4 format"""
        care_plan = {
            "resourceType": "CarePlan",
            "status": "active",
            "intent": "plan",
            "title": "Clinical Trial Schedule",
            "activity": []
        }

        rows = parsed_data.get("rows", [])
        for row in rows:
            activity = {
                "detail": {
                    "kind": "Appointment",
                    "code": {
                        "text": self._get_mapped_value(row, mappings, "visit_name")
                    },
                    "scheduledString": f"Day {self._get_mapped_value(row, mappings, 'visit_day')}"
                }
            }
            care_plan["activity"].append(activity)

        return care_plan

    def to_omop_cdm(self, parsed_data: Dict, mappings: Dict) -> Dict[str, Any]:
        """Convert to OMOP CDM format"""
        visit_occurrences = []

        rows = parsed_data.get("rows", [])
        for idx, row in enumerate(rows):
            visit = {
                "visit_occurrence_id": idx + 1,
                "visit_concept_id": 32810,  # Clinical trial visit
                "visit_start_date": self._get_mapped_value(row, mappings, "visit_day"),
                "visit_type_concept_id": 32810
            }
            visit_occurrences.append(visit)

        return {
            "visit_occurrence": visit_occurrences,
            "format": "OMOP_CDM",
            "version": "5.3"
        }

    def _get_mapped_value(self, row: Dict, mappings: Dict, target_field: str) -> Any:
        """Get value from row using mappings"""
        mapping_dict = mappings.get("mappings", mappings)

        # Find source column for target field
        for source, target in mapping_dict.items():
            if target == target_field:
                return row.get(source, "")

        # Try direct field access
        return row.get(target_field, "")

    def _validate_cdisc_sdtm(self, data: Dict) -> Dict[str, Any]:
        """Validate CDISC SDTM data"""
        issues = []
        warnings = []

        # Check for required domains
        if "TV" not in data:
            issues.append("Missing TV (Trial Visits) domain")
        else:
            # Validate TV records
            for record in data["TV"]:
                if "VISITNUM" not in record:
                    issues.append("TV record missing VISITNUM")
                if "VISIT" not in record:
                    warnings.append("TV record missing VISIT name")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }

    def _validate_fhir_r4(self, data: Dict) -> Dict[str, Any]:
        """Validate FHIR R4 data"""
        issues = []
        warnings = []

        if "resourceType" not in data:
            issues.append("Missing resourceType")
        elif data["resourceType"] != "CarePlan":
            warnings.append(f"Unexpected resourceType: {data['resourceType']}")

        if "status" not in data:
            issues.append("Missing status field")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }

    def _validate_omop_cdm(self, data: Dict) -> Dict[str, Any]:
        """Validate OMOP CDM data"""
        issues = []
        warnings = []

        if "visit_occurrence" not in data:
            issues.append("Missing visit_occurrence table")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }


class PatternMatcher:
    """Pattern matching for fast conversion"""

    def __init__(self):
        self.patterns = {
            "visit_patterns": [
                (r"visit", "visit_name"),
                (r"timepoint", "visit_name"),
                (r"study.*visit", "visit_name")
            ],
            "day_patterns": [
                (r"day", "visit_day"),
                (r"study.*day", "visit_day"),
                (r"visit.*day", "visit_day")
            ],
            "procedure_patterns": [
                (r"procedure", "procedures"),
                (r"assessment", "procedures"),
                (r"test", "procedures")
            ]
        }

    def match(self, parsed_data: Dict) -> Dict[str, Any]:
        """Match columns to standard fields using patterns"""
        columns = parsed_data.get("columns", [])
        mappings = {}
        confidence = 0
        matches = 0

        for col in columns:
            col_lower = col.lower()
            for pattern_group in self.patterns.values():
                for pattern, target in pattern_group:
                    if re.search(pattern, col_lower):
                        mappings[col] = target
                        matches += 1
                        break

        if columns:
            confidence = (matches / len(columns)) * 100

        return {
            "mappings": mappings,
            "confidence": confidence,
            "method": "pattern_matching"
        }

    def detect_patterns(self, parsed_data: Dict) -> List[str]:
        """Detect patterns in the data"""
        detected = []
        columns = parsed_data.get("columns", [])

        for col in columns:
            col_lower = col.lower()
            if re.search(r"day|date", col_lower):
                detected.append(f"Date pattern in column: {col}")
            if re.search(r"visit", col_lower):
                detected.append(f"Visit pattern in column: {col}")
            if re.search(r"procedure|assessment", col_lower):
                detected.append(f"Procedure pattern in column: {col}")

        return detected

    def suggest_mappings(self, parsed_data: Dict) -> Dict[str, str]:
        """Suggest possible mappings"""
        result = self.match(parsed_data)
        return result.get("mappings", {})


class FuzzyMatcher:
    """Fuzzy logic validation"""

    def validate(self, llm_result: Dict, parsed_data: Dict) -> Dict[str, Any]:
        """Validate LLM results using fuzzy logic"""
        mappings = {}
        columns = parsed_data.get("columns", [])

        # Simple fuzzy matching simulation
        for col in columns:
            col_lower = col.lower()

            # Score-based matching
            scores = {
                "visit_name": self._calculate_similarity(col_lower, "visit"),
                "visit_day": self._calculate_similarity(col_lower, "day"),
                "procedures": self._calculate_similarity(col_lower, "procedure")
            }

            best_match = max(scores, key=scores.get)
            if scores[best_match] > 0.5:
                mappings[col] = best_match

        confidence = len(mappings) / len(columns) * 100 if columns else 0

        return {
            "mappings": mappings,
            "confidence": confidence,
            "method": "fuzzy_logic"
        }

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity (simplified)"""
        if str2 in str1:
            return 1.0
        if str1 in str2:
            return 0.8

        # Simple character overlap
        common = set(str1) & set(str2)
        return len(common) / max(len(str1), len(str2))


class LLMAnalyzer:
    """Simulated LLM analyzer (would use Azure OpenAI in production)"""

    def analyze_structure(self, parsed_data: Dict) -> Dict[str, Any]:
        """Analyze structure using LLM (simulated)"""
        columns = parsed_data.get("columns", [])
        mappings = {}

        # Simulate intelligent mapping
        for col in columns:
            col_lower = col.lower()
            if "visit" in col_lower or "timepoint" in col_lower:
                mappings[col] = "visit_name"
            elif "day" in col_lower or "date" in col_lower:
                mappings[col] = "visit_day"
            elif "procedure" in col_lower or "assessment" in col_lower or "test" in col_lower:
                mappings[col] = "procedures"

        return {
            "mappings": mappings,
            "confidence": 75,  # Simulated confidence
            "method": "llm_analysis"
        }


class LLMJudge:
    """Autonomous judge for disagreement resolution"""

    def arbitrate(self, llm_result: Dict, fuzzy_result: Dict, parsed_data: Dict) -> Dict[str, Any]:
        """Make final decision when systems disagree"""
        # In production, this would use GPT-4 or similar
        # For now, we'll use a simple heuristic

        # Prefer the result with higher confidence
        if llm_result.get("confidence", 0) > fuzzy_result.get("confidence", 0):
            chosen = llm_result
            reasoning = "LLM analysis showed higher confidence"
        else:
            chosen = fuzzy_result
            reasoning = "Fuzzy logic validation showed higher confidence"

        # Boost confidence since judge made decision
        chosen["confidence"] = min(chosen.get("confidence", 0) + 10, 95)
        chosen["reasoning"] = reasoning
        chosen["arbitrated"] = True

        return chosen


class MappingCache:
    """Cache for learned mappings"""

    def __init__(self, db_path: str = "schedule_mappings.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                org_id TEXT,
                fingerprint TEXT,
                mappings TEXT,
                confidence REAL,
                success_count INTEGER DEFAULT 1,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def store_mapping(self, org_id: Optional[str], result: Dict):
        """Store successful mapping"""
        if not org_id:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        mappings_json = json.dumps(result.get("mappings", {}))
        confidence = result.get("confidence", 0)

        cursor.execute("""
            INSERT OR REPLACE INTO mappings (org_id, fingerprint, mappings, confidence)
            VALUES (?, ?, ?, ?)
        """, (org_id, result.get("fingerprint", ""), mappings_json, confidence))

        conn.commit()
        conn.close()

    def get_org_mappings(self, org_id: str, fingerprint: str) -> Optional[Dict]:
        """Get cached mappings for organization"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT mappings, confidence FROM mappings
            WHERE org_id = ? AND fingerprint = ?
            ORDER BY confidence DESC, success_count DESC
            LIMIT 1
        """, (org_id, fingerprint))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                "mappings": json.loads(result[0]),
                "confidence": result[1]
            }
        return None

    def get_all_mappings(self, org_id: str) -> List[Dict]:
        """Get all mappings for an organization"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT fingerprint, mappings, confidence, success_count, last_used
            FROM mappings
            WHERE org_id = ?
            ORDER BY last_used DESC
        """, (org_id,))

        results = []
        for row in cursor.fetchall():
            results.append({
                "fingerprint": row[0],
                "mappings": json.loads(row[1]),
                "confidence": row[2],
                "success_count": row[3],
                "last_used": row[4]
            })

        conn.close()
        return results

    def clear(self, org_id: str) -> int:
        """Clear cache for organization"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if org_id == "all":
            cursor.execute("DELETE FROM mappings")
        else:
            cursor.execute("DELETE FROM mappings WHERE org_id = ?", (org_id,))

        count = cursor.rowcount
        conn.commit()
        conn.close()

        return count

    def get_statistics(self, org_id: Optional[str] = None) -> Dict[str, Any]:
        """Get usage statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if org_id:
            cursor.execute("""
                SELECT COUNT(*), AVG(confidence), MAX(success_count)
                FROM mappings
                WHERE org_id = ?
            """, (org_id,))
        else:
            cursor.execute("""
                SELECT COUNT(*), AVG(confidence), MAX(success_count)
                FROM mappings
            """)

        result = cursor.fetchone()
        conn.close()

        return {
            "total_mappings": result[0] or 0,
            "average_confidence": round(result[1] or 0, 2),
            "max_success_count": result[2] or 0
        }


def run(input_data: Dict) -> Dict:
    """
    Convert clinical trial schedule to standard format

    Example:
        Input: File content with visit schedule information
        Output: Converted data in CDISC SDTM, FHIR, or OMOP format

    Parameters:
        file_content : str
            Base64 encoded file content or raw text
        file_type : str
            Type of input file (csv, json, text)
        target_format : str, optional
            Target format: CDISC_SDTM, FHIR_R4, or OMOP_CDM (default: CDISC_SDTM)
        organization_id : str, optional
            Organization ID for cached mappings
    """
    converter = ScheduleConverter()

    return converter.convert(
        file_content=input_data.get("file_content", ""),
        file_type=input_data.get("file_type", "text"),
        target_format=input_data.get("target_format", "CDISC_SDTM"),
        organization_id=input_data.get("organization_id"),
        confidence_threshold=input_data.get("confidence_threshold", 85)
    )