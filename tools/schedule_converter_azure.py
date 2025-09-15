"""
Clinical Trial Schedule Converter Tool with Azure OpenAI
Real LLM integration for production use
"""

import json
import base64
import csv
import io
import re
import logging
import os
import requests
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class AzureOpenAIClient:
    """Client for Azure OpenAI API calls"""

    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION")

        if not all([self.api_key, self.endpoint, self.deployment, self.api_version]):
            logger.warning("Azure OpenAI credentials not fully configured - will use fallback mode")
            self.configured = False
        else:
            self.configured = True
            self.url = f"{self.endpoint}openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
            self.headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }

    def call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.3, max_tokens: int = 500) -> Optional[str]:
        """Make a call to Azure OpenAI"""
        if not self.configured:
            return None

        data = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=data)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"Azure OpenAI API error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Azure OpenAI call failed: {e}")
            return None


class LLMAnalyzer:
    """Real LLM analyzer using Azure OpenAI"""

    def __init__(self):
        self.client = AzureOpenAIClient()
        self.fallback_mode = not self.client.configured

    def analyze_structure(self, parsed_data: Dict) -> Dict[str, Any]:
        """Analyze structure using Azure OpenAI LLM"""
        columns = parsed_data.get("columns", [])

        if self.fallback_mode:
            # Use pattern-based fallback
            return self._fallback_analysis(parsed_data)

        # Prepare prompt for Azure OpenAI
        system_prompt = """You are a clinical data standards expert specializing in CDISC SDTM mapping.
        Your task is to map column names from clinical trial schedules to standard CDISC fields.

        Standard mappings:
        - Visit information -> visit_name
        - Day/Date information -> visit_day
        - Procedures/Assessments -> procedures
        - Time windows -> visit_window
        - Subject/Patient ID -> subject_id

        Respond ONLY with valid JSON in this exact format:
        {
            "mappings": {
                "source_column": "target_field"
            },
            "confidence": 0-100,
            "reasoning": "brief explanation"
        }"""

        user_prompt = f"""Map these clinical trial schedule columns to CDISC standard fields:

        Columns: {', '.join(columns)}

        First few rows of data:
        {json.dumps(parsed_data.get('rows', [])[:3], indent=2)}"""

        response = self.client.call_llm(system_prompt, user_prompt, temperature=0.2)

        if response:
            try:
                result = json.loads(response)
                result["method"] = "azure_openai_llm"
                return result
            except json.JSONDecodeError:
                logger.error("Failed to parse LLM response as JSON")
                return self._fallback_analysis(parsed_data)
        else:
            return self._fallback_analysis(parsed_data)

    def _fallback_analysis(self, parsed_data: Dict) -> Dict[str, Any]:
        """Fallback analysis when Azure OpenAI is not available"""
        columns = parsed_data.get("columns", [])
        mappings = {}

        for col in columns:
            col_lower = col.lower()
            if "visit" in col_lower or "timepoint" in col_lower:
                mappings[col] = "visit_name"
            elif "day" in col_lower or "date" in col_lower:
                mappings[col] = "visit_day"
            elif "procedure" in col_lower or "assessment" in col_lower or "test" in col_lower:
                mappings[col] = "procedures"
            elif "window" in col_lower:
                mappings[col] = "visit_window"
            elif "subject" in col_lower or "patient" in col_lower:
                mappings[col] = "subject_id"

        confidence = (len(mappings) / len(columns) * 100) if columns else 0

        return {
            "mappings": mappings,
            "confidence": confidence,
            "method": "pattern_fallback",
            "reasoning": "Azure OpenAI not configured - using pattern matching"
        }


class LLMJudge:
    """Autonomous judge using Azure OpenAI for disagreement resolution"""

    def __init__(self):
        self.client = AzureOpenAIClient()
        self.fallback_mode = not self.client.configured

    def arbitrate(self, llm_result: Dict, fuzzy_result: Dict, parsed_data: Dict) -> Dict[str, Any]:
        """Make final decision when systems disagree using Azure OpenAI"""

        if self.fallback_mode:
            # Use heuristic fallback
            return self._fallback_arbitration(llm_result, fuzzy_result)

        system_prompt = """You are the final arbiter for clinical data mapping decisions.
        You must choose the BEST mapping between two conflicting analyses.
        Consider CDISC SDTM compliance, data consistency, and minimal information loss.

        Respond with JSON:
        {
            "chosen": "llm" or "fuzzy",
            "confidence": 0-100,
            "reasoning": "one sentence explanation",
            "final_mappings": {}
        }"""

        user_prompt = f"""Two systems disagree on mapping this clinical trial schedule:

        Columns in file: {parsed_data.get('columns', [])}

        LLM Analysis (confidence: {llm_result.get('confidence', 0)}):
        {json.dumps(llm_result.get('mappings', {}), indent=2)}

        Fuzzy Logic Analysis (confidence: {fuzzy_result.get('confidence', 0)}):
        {json.dumps(fuzzy_result.get('mappings', {}), indent=2)}

        Which mapping is more appropriate for CDISC SDTM compliance?"""

        response = self.client.call_llm(system_prompt, user_prompt, temperature=0.1, max_tokens=300)

        if response:
            try:
                decision = json.loads(response)

                # Select the chosen result
                if decision.get("chosen") == "llm":
                    final = llm_result.copy()
                else:
                    final = fuzzy_result.copy()

                # Override with judge's final mappings if provided
                if decision.get("final_mappings"):
                    final["mappings"] = decision["final_mappings"]

                final["confidence"] = decision.get("confidence", final.get("confidence", 85))
                final["reasoning"] = decision.get("reasoning", "Azure OpenAI arbitration")
                final["arbitrated"] = True
                final["judge"] = "azure_openai"

                return final

            except json.JSONDecodeError:
                logger.error("Failed to parse judge response as JSON")
                return self._fallback_arbitration(llm_result, fuzzy_result)
        else:
            return self._fallback_arbitration(llm_result, fuzzy_result)

    def _fallback_arbitration(self, llm_result: Dict, fuzzy_result: Dict) -> Dict[str, Any]:
        """Fallback arbitration when Azure OpenAI is not available"""
        # Choose the one with higher confidence
        if llm_result.get("confidence", 0) > fuzzy_result.get("confidence", 0):
            chosen = llm_result
            reasoning = "LLM analysis showed higher confidence"
        else:
            chosen = fuzzy_result
            reasoning = "Fuzzy logic validation showed higher confidence"

        chosen["confidence"] = min(chosen.get("confidence", 0) + 10, 95)
        chosen["reasoning"] = reasoning
        chosen["arbitrated"] = True
        chosen["judge"] = "heuristic_fallback"

        return chosen


# Import the rest of the components from the original implementation
from tools.schedule_converter import (
    ScheduleConverter as BaseScheduleConverter,
    PatternMatcher,
    FuzzyMatcher,
    MappingCache
)


class ScheduleConverterWithAzure(BaseScheduleConverter):
    """Enhanced Schedule Converter with real Azure OpenAI integration"""

    def __init__(self):
        """Initialize with Azure OpenAI components"""
        self.pattern_matcher = PatternMatcher()
        self.fuzzy_matcher = FuzzyMatcher()
        self.mapping_cache = MappingCache()
        self.llm_analyzer = LLMAnalyzer()  # Now uses Azure OpenAI
        self.llm_judge = LLMJudge()  # Now uses Azure OpenAI
        self.format_converters = {
            "CDISC_SDTM": self.to_cdisc_sdtm,
            "FHIR_R4": self.to_fhir_r4,
            "OMOP_CDM": self.to_omop_cdm
        }

        # Check Azure OpenAI status
        if self.llm_analyzer.client.configured:
            logger.info("Azure OpenAI is configured and ready")
        else:
            logger.warning("Azure OpenAI not configured - using fallback mode")


def run(input_data: Dict) -> Dict:
    """
    Convert clinical trial schedule to standard format using Azure OpenAI

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
    converter = ScheduleConverterWithAzure()

    result = converter.convert(
        file_content=input_data.get("file_content", ""),
        file_type=input_data.get("file_type", "text"),
        target_format=input_data.get("target_format", "CDISC_SDTM"),
        organization_id=input_data.get("organization_id"),
        confidence_threshold=input_data.get("confidence_threshold", 85)
    )

    # Add Azure OpenAI status to result
    if converter.llm_analyzer.client.configured:
        result["llm_mode"] = "azure_openai"
    else:
        result["llm_mode"] = "fallback_patterns"

    return result