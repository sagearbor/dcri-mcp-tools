#!/usr/bin/env python3
"""
Client for using the Schedule Converter MCP Server
This can be called by other LLMs or applications
"""

import json
import subprocess
import sys
import os
from typing import Dict, Any, Optional


class ScheduleConverterClient:
    """Client for interacting with the Schedule Converter MCP Server"""

    def __init__(self, server_path: str = None):
        """
        Initialize the client

        Args:
            server_path: Path to schedule_converter_mcp.py (defaults to current directory)
        """
        if server_path is None:
            server_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "schedule_converter_mcp.py"
            )
        self.server_path = server_path
        self.process = None
        self.initialized = False
        self.msg_id = 0

    def start(self):
        """Start the MCP server subprocess"""
        self.process = subprocess.Popen(
            [sys.executable, self.server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Initialize the connection
        response = self._send_request("initialize", {
            "clientInfo": {
                "name": "schedule-converter-client",
                "version": "1.0.0"
            }
        })

        if response and "result" in response:
            # Send initialized notification
            self._send_notification("initialized", {})
            self.initialized = True
            return True
        return False

    def stop(self):
        """Stop the MCP server"""
        if self.process:
            self._send_request("shutdown", {})
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process = None
            self.initialized = False

    def _send_request(self, method: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Send a JSON-RPC request and get response"""
        if not self.process:
            return None

        self.msg_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.msg_id,
            "method": method,
            "params": params
        }

        # Send with Content-Length header
        json_str = json.dumps(request)
        content_length = len(json_str.encode('utf-8'))

        self.process.stdin.write(f"Content-Length: {content_length}\r\n\r\n")
        self.process.stdin.write(json_str)
        self.process.stdin.flush()

        # Read response
        header = self.process.stdout.readline()
        if header.startswith("Content-Length:"):
            self.process.stdout.readline()  # Empty line
            content_length = int(header.split(":")[1].strip())
            response_str = self.process.stdout.read(content_length)
            return json.loads(response_str)

        return None

    def _send_notification(self, method: str, params: Dict[str, Any]):
        """Send a JSON-RPC notification (no response expected)"""
        if not self.process:
            return

        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }

        json_str = json.dumps(request)
        content_length = len(json_str.encode('utf-8'))

        self.process.stdin.write(f"Content-Length: {content_length}\r\n\r\n")
        self.process.stdin.write(json_str)
        self.process.stdin.flush()

    def convert_schedule(self,
                        file_content: str,
                        file_type: str = "csv",
                        target_format: str = "CDISC_SDTM",
                        organization_id: str = None,
                        confidence_threshold: float = 85) -> Dict[str, Any]:
        """
        Convert a clinical trial schedule to standard format

        Args:
            file_content: The content of the file (CSV, JSON, etc.)
            file_type: Type of file (csv, json, text)
            target_format: Target format (CDISC_SDTM, FHIR_R4, OMOP_CDM)
            organization_id: Optional org ID for caching
            confidence_threshold: Minimum confidence for conversion

        Returns:
            Conversion result dictionary
        """
        if not self.initialized:
            if not self.start():
                return {"error": "Failed to start MCP server"}

        response = self._send_request("tools/call", {
            "name": "convert_schedule",
            "arguments": {
                "file_content": file_content,
                "file_type": file_type,
                "target_format": target_format,
                "organization_id": organization_id,
                "confidence_threshold": confidence_threshold
            }
        })

        if response and "result" in response:
            # Extract the result from the MCP response
            content = response["result"]["content"][0]["text"]
            return json.loads(content)

        return {"error": "Failed to get response from MCP server"}

    def analyze_schedule(self, file_content: str, file_type: str = "csv") -> Dict[str, Any]:
        """
        Analyze schedule structure without converting

        Args:
            file_content: The content of the file
            file_type: Type of file (csv, json, text)

        Returns:
            Analysis result dictionary
        """
        if not self.initialized:
            if not self.start():
                return {"error": "Failed to start MCP server"}

        response = self._send_request("tools/call", {
            "name": "analyze_schedule",
            "arguments": {
                "file_content": file_content,
                "file_type": file_type
            }
        })

        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            return json.loads(content)

        return {"error": "Failed to analyze schedule"}


def example_usage():
    """Example of how to use the Schedule Converter from another application"""

    # Create client
    client = ScheduleConverterClient()

    try:
        # Start the MCP server
        print("Starting MCP server...")
        if not client.start():
            print("Failed to start server")
            return

        print("✅ MCP server started successfully\n")

        # Example 1: Convert a simple CSV schedule
        csv_data = """Visit Name,Study Day,Procedures
Screening,-14,Informed Consent
Baseline,0,Vital Signs|Labs
Week 1,7,Drug Administration
Week 2,14,Safety Assessment|ECG"""

        print("Converting CSV to CDISC SDTM...")
        result = client.convert_schedule(
            file_content=csv_data,
            file_type="csv",
            target_format="CDISC_SDTM"
        )

        if result.get("success"):
            print(f"✅ Conversion successful!")
            print(f"   Confidence: {result.get('confidence')}%")
            print(f"   LLM Mode: {result.get('llm_mode', 'unknown')}")
            print(f"   TV Records: {len(result['data']['TV'])}")
            print(f"   PR Records: {len(result['data']['PR'])}")
        else:
            print(f"❌ Conversion failed: {result.get('error')}")

        # Example 2: Analyze structure
        print("\nAnalyzing schedule structure...")
        analysis = client.analyze_schedule(csv_data, "csv")

        if analysis.get("success"):
            print(f"✅ Analysis complete")
            print(f"   Columns: {', '.join(analysis['analysis']['columns'])}")
            print(f"   Row count: {analysis['analysis']['row_count']}")

        # Example 3: Convert to FHIR
        print("\nConverting to FHIR R4...")
        result = client.convert_schedule(
            file_content=csv_data,
            file_type="csv",
            target_format="FHIR_R4"
        )

        if result.get("success"):
            print(f"✅ FHIR conversion successful!")
            fhir_data = result['data']
            print(f"   Resource Type: {fhir_data.get('resourceType')}")
            print(f"   Activities: {len(fhir_data.get('activity', []))}")

    finally:
        # Always stop the server
        print("\nStopping MCP server...")
        client.stop()
        print("✅ Server stopped")


# Simple command-line interface
def main():
    """Command-line interface for the Schedule Converter"""
    import argparse

    parser = argparse.ArgumentParser(description="Convert clinical trial schedules")
    parser.add_argument("file", help="Path to schedule file")
    parser.add_argument("--type", default="csv", choices=["csv", "json", "text"],
                       help="File type (default: csv)")
    parser.add_argument("--format", default="CDISC_SDTM",
                       choices=["CDISC_SDTM", "FHIR_R4", "OMOP_CDM"],
                       help="Target format (default: CDISC_SDTM)")
    parser.add_argument("--org", help="Organization ID for caching")
    parser.add_argument("--output", help="Output file (optional)")

    args = parser.parse_args()

    # Read input file
    with open(args.file, 'r') as f:
        content = f.read()

    # Create client and convert
    client = ScheduleConverterClient()

    try:
        if not client.start():
            print("Failed to start MCP server")
            sys.exit(1)

        result = client.convert_schedule(
            file_content=content,
            file_type=args.type,
            target_format=args.format,
            organization_id=args.org
        )

        if result.get("success"):
            output = json.dumps(result['data'], indent=2)

            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"✅ Converted to {args.format} and saved to {args.output}")
            else:
                print(output)
        else:
            print(f"❌ Conversion failed: {result.get('error')}")
            sys.exit(1)

    finally:
        client.stop()


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        # No arguments - run example
        example_usage()
    else:
        # Arguments provided - run CLI
        main()