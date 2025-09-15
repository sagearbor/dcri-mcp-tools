#!/usr/bin/env python3
"""
MCP Server for Clinical Schedule Converter
Provides intelligent, autonomous conversion of clinical trial schedules
from any format to standard formats (CDISC SDTM, FHIR, OMOP)
"""

import sys
import os
import json
import logging
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server import MCPServer
from tools.schedule_converter import ScheduleConverter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class ScheduleConverterMCPServer(MCPServer):
    """MCP Server specifically for schedule conversion with autonomous arbitration"""

    def __init__(self):
        super().__init__(name="schedule-converter", version="1.0.0")

        # Initialize the converter
        self.converter = ScheduleConverter()

        # Set capabilities
        self.capabilities = {
            "tools": {},
            "resources": {},
            "prompts": {},
            "logging": {}
        }

        # Register the conversion tools
        self._register_conversion_tools()
        self._register_utility_tools()

    def _register_conversion_tools(self):
        """Register the main schedule conversion tools"""

        # Main conversion tool
        self.register_tool(
            name="convert_schedule",
            description="Convert clinical trial schedule to standard format (CDISC SDTM, FHIR, OMOP)",
            input_schema={
                "type": "object",
                "properties": {
                    "file_content": {
                        "type": "string",
                        "description": "Base64 encoded file content or raw text content"
                    },
                    "file_type": {
                        "type": "string",
                        "enum": ["csv", "xlsx", "json", "xml", "text"],
                        "description": "Type of the input file"
                    },
                    "target_format": {
                        "type": "string",
                        "enum": ["CDISC_SDTM", "FHIR_R4", "OMOP_CDM"],
                        "default": "CDISC_SDTM",
                        "description": "Target standard format for conversion"
                    },
                    "organization_id": {
                        "type": "string",
                        "description": "Optional organization ID for cached mappings"
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 100,
                        "default": 85,
                        "description": "Minimum confidence threshold for autonomous conversion"
                    }
                },
                "required": ["file_content", "file_type"]
            },
            handler=self._handle_convert_schedule
        )

        # Analyze schedule structure tool
        self.register_tool(
            name="analyze_schedule",
            description="Analyze schedule structure without converting",
            input_schema={
                "type": "object",
                "properties": {
                    "file_content": {
                        "type": "string",
                        "description": "Base64 encoded file content or raw text"
                    },
                    "file_type": {
                        "type": "string",
                        "enum": ["csv", "xlsx", "json", "xml", "text"],
                        "description": "Type of the input file"
                    }
                },
                "required": ["file_content", "file_type"]
            },
            handler=self._handle_analyze_schedule
        )

        # Validate converted output
        self.register_tool(
            name="validate_conversion",
            description="Validate that converted data meets standard requirements",
            input_schema={
                "type": "object",
                "properties": {
                    "converted_data": {
                        "type": "object",
                        "description": "The converted schedule data"
                    },
                    "target_format": {
                        "type": "string",
                        "enum": ["CDISC_SDTM", "FHIR_R4", "OMOP_CDM"],
                        "description": "The target format to validate against"
                    }
                },
                "required": ["converted_data", "target_format"]
            },
            handler=self._handle_validate_conversion
        )

    def _register_utility_tools(self):
        """Register utility tools for cache management and learning"""

        # Get cached mappings
        self.register_tool(
            name="get_cached_mappings",
            description="Retrieve cached mappings for an organization",
            input_schema={
                "type": "object",
                "properties": {
                    "organization_id": {
                        "type": "string",
                        "description": "Organization ID to retrieve mappings for"
                    }
                },
                "required": ["organization_id"]
            },
            handler=self._handle_get_cached_mappings
        )

        # Clear cache
        self.register_tool(
            name="clear_cache",
            description="Clear cached mappings for an organization",
            input_schema={
                "type": "object",
                "properties": {
                    "organization_id": {
                        "type": "string",
                        "description": "Organization ID to clear cache for (or 'all')"
                    }
                },
                "required": ["organization_id"]
            },
            handler=self._handle_clear_cache
        )

        # Get conversion statistics
        self.register_tool(
            name="get_statistics",
            description="Get conversion statistics and performance metrics",
            input_schema={
                "type": "object",
                "properties": {
                    "organization_id": {
                        "type": "string",
                        "description": "Optional organization ID for filtered stats"
                    }
                }
            },
            handler=self._handle_get_statistics
        )

    def _handle_convert_schedule(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the main schedule conversion request"""
        try:
            file_content = args.get("file_content")
            file_type = args.get("file_type")
            target_format = args.get("target_format", "CDISC_SDTM")
            organization_id = args.get("organization_id")
            confidence_threshold = args.get("confidence_threshold", 85)

            logger.info(f"Converting schedule: type={file_type}, target={target_format}, org={organization_id}")

            # Perform the conversion
            result = self.converter.convert(
                file_content=file_content,
                file_type=file_type,
                target_format=target_format,
                organization_id=organization_id,
                confidence_threshold=confidence_threshold
            )

            # Log the conversion result
            logger.info(f"Conversion completed with confidence: {result.get('confidence', 0)}%")

            # Add metadata
            result["metadata"] = {
                "converter_version": self.version,
                "target_format": target_format,
                "organization_id": organization_id,
                "autonomous": True,  # Always autonomous - no human intervention
                "arbitration_used": result.get("arbitration_used", False)
            }

            return result

        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return {
                "error": str(e),
                "success": False,
                "confidence": 0
            }

    def _handle_analyze_schedule(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze schedule structure without converting"""
        try:
            file_content = args.get("file_content")
            file_type = args.get("file_type")

            logger.info(f"Analyzing schedule structure: type={file_type}")

            # Use converter's analysis function
            analysis = self.converter.analyze_structure(
                file_content=file_content,
                file_type=file_type
            )

            return {
                "success": True,
                "analysis": analysis
            }

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                "error": str(e),
                "success": False
            }

    def _handle_validate_conversion(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate converted data against standard requirements"""
        try:
            converted_data = args.get("converted_data")
            target_format = args.get("target_format")

            logger.info(f"Validating conversion for format: {target_format}")

            # Use converter's validation function
            validation_result = self.converter.validate_output(
                data=converted_data,
                target_format=target_format
            )

            return {
                "success": True,
                "valid": validation_result.get("valid", False),
                "issues": validation_result.get("issues", []),
                "warnings": validation_result.get("warnings", [])
            }

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                "error": str(e),
                "success": False
            }

    def _handle_get_cached_mappings(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve cached mappings for an organization"""
        try:
            organization_id = args.get("organization_id")

            logger.info(f"Retrieving cached mappings for org: {organization_id}")

            mappings = self.converter.get_cached_mappings(organization_id)

            return {
                "success": True,
                "organization_id": organization_id,
                "mappings": mappings,
                "count": len(mappings)
            }

        except Exception as e:
            logger.error(f"Failed to retrieve mappings: {e}")
            return {
                "error": str(e),
                "success": False
            }

    def _handle_clear_cache(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Clear cached mappings"""
        try:
            organization_id = args.get("organization_id")

            logger.info(f"Clearing cache for org: {organization_id}")

            cleared = self.converter.clear_cache(organization_id)

            return {
                "success": True,
                "organization_id": organization_id,
                "cleared_entries": cleared
            }

        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return {
                "error": str(e),
                "success": False
            }

    def _handle_get_statistics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get conversion statistics"""
        try:
            organization_id = args.get("organization_id")

            logger.info(f"Getting statistics for org: {organization_id or 'all'}")

            stats = self.converter.get_statistics(organization_id)

            return {
                "success": True,
                "statistics": stats
            }

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {
                "error": str(e),
                "success": False
            }


def main():
    """Main entry point for the MCP server"""
    logger.info("Starting Schedule Converter MCP Server")

    try:
        server = ScheduleConverterMCPServer()
        server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()