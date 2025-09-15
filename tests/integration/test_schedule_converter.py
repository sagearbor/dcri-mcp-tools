#!/usr/bin/env python3
"""
Test script for the Schedule Converter MCP Server
Tests both MCP protocol communication and conversion functionality
"""

import json
import subprocess
import sys
import time
import base64
from typing import Dict, Any


def send_json_rpc(proc, method: str, params: Dict[str, Any], msg_id: int) -> Dict:
    """Send a JSON-RPC request and read response"""
    request = {
        "jsonrpc": "2.0",
        "id": msg_id,
        "method": method,
        "params": params
    }

    # Send with Content-Length header
    json_str = json.dumps(request)
    content_length = len(json_str.encode('utf-8'))

    proc.stdin.write(f"Content-Length: {content_length}\r\n\r\n")
    proc.stdin.write(json_str)
    proc.stdin.flush()

    # Read response with Content-Length
    header = proc.stdout.readline()
    if header.startswith("Content-Length:"):
        # Read empty line
        proc.stdout.readline()
        # Read content
        content_length = int(header.split(":")[1].strip())
        response_str = proc.stdout.read(content_length)
        return json.loads(response_str)
    else:
        # Try direct JSON
        return json.loads(header)


def test_mcp_server():
    """Test the MCP server with various scenarios"""

    print("Starting Schedule Converter MCP Server tests...")
    print("=" * 60)

    # Start the MCP server
    proc = subprocess.Popen(
        [sys.executable, "schedule_converter_mcp.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        # Test 1: Initialize
        print("\nTest 1: Initialize MCP connection")
        response = send_json_rpc(proc, "initialize", {
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }, 1)

        if "result" in response:
            print(f"✅ Initialized successfully")
            print(f"   Server: {response['result']['serverInfo']['name']} v{response['result']['serverInfo']['version']}")
        else:
            print(f"❌ Initialize failed: {response}")
            return

        # Send initialized notification
        send_json_rpc(proc, "initialized", {}, None)

        # Test 2: List tools
        print("\nTest 2: List available tools")
        response = send_json_rpc(proc, "tools/list", {}, 2)

        if "result" in response:
            tools = response["result"]["tools"]
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description'][:50]}...")
        else:
            print(f"❌ List tools failed: {response}")

        # Test 3: Simple CSV conversion
        print("\nTest 3: Convert simple CSV to CDISC SDTM")
        test_csv = """Visit Name,Study Day,Procedures
Screening,-14,Informed Consent
Baseline,0,Vital Signs
Week 1,7,Blood Draw
Week 2,14,ECG"""

        response = send_json_rpc(proc, "tools/call", {
            "name": "convert_schedule",
            "arguments": {
                "file_content": test_csv,
                "file_type": "csv",
                "target_format": "CDISC_SDTM",
                "organization_id": "test_org"
            }
        }, 3)

        if "result" in response:
            content = json.loads(response["result"]["content"][0]["text"])
            if content.get("success"):
                print(f"✅ Conversion successful with confidence: {content['confidence']}%")
                print(f"   Converted {content['row_count']} rows")
                print(f"   TV domain records: {len(content['data']['TV'])}")
                print(f"   PR domain records: {len(content['data']['PR'])}")
            else:
                print(f"❌ Conversion failed: {content.get('error')}")
        else:
            print(f"❌ Tool call failed: {response}")

        # Test 4: Analyze structure
        print("\nTest 4: Analyze schedule structure")
        response = send_json_rpc(proc, "tools/call", {
            "name": "analyze_schedule",
            "arguments": {
                "file_content": test_csv,
                "file_type": "csv"
            }
        }, 4)

        if "result" in response:
            content = json.loads(response["result"]["content"][0]["text"])
            if content.get("success"):
                print(f"✅ Analysis successful")
                print(f"   Columns: {', '.join(content['analysis']['columns'])}")
                print(f"   Detected patterns: {len(content['analysis']['detected_patterns'])}")
            else:
                print(f"❌ Analysis failed: {content.get('error')}")

        # Test 5: FHIR conversion
        print("\nTest 5: Convert to FHIR R4")
        response = send_json_rpc(proc, "tools/call", {
            "name": "convert_schedule",
            "arguments": {
                "file_content": test_csv,
                "file_type": "csv",
                "target_format": "FHIR_R4"
            }
        }, 5)

        if "result" in response:
            content = json.loads(response["result"]["content"][0]["text"])
            if content.get("success"):
                print(f"✅ FHIR conversion successful")
                fhir_data = content['data']
                print(f"   Resource type: {fhir_data.get('resourceType')}")
                print(f"   Activities: {len(fhir_data.get('activity', []))}")
            else:
                print(f"❌ FHIR conversion failed")

        # Test 6: Get statistics
        print("\nTest 6: Get conversion statistics")
        response = send_json_rpc(proc, "tools/call", {
            "name": "get_statistics",
            "arguments": {
                "organization_id": "test_org"
            }
        }, 6)

        if "result" in response:
            content = json.loads(response["result"]["content"][0]["text"])
            if content.get("success"):
                stats = content['statistics']
                print(f"✅ Statistics retrieved")
                print(f"   Total mappings: {stats['total_mappings']}")
                print(f"   Average confidence: {stats['average_confidence']}%")

        # Test 7: Complex data with disagreement simulation
        print("\nTest 7: Complex conversion triggering arbitration")
        complex_csv = """TimePoint,Day Number,Assessments and Procedures
Pre-Study Visit,-21,Screening Labs|Consent Form
Study Start,1,Physical Exam|Baseline Measurements
Treatment Period 1,8,Drug Administration|Safety Labs
Treatment Period 2,15,Drug Administration|ECG|Safety Assessment"""

        response = send_json_rpc(proc, "tools/call", {
            "name": "convert_schedule",
            "arguments": {
                "file_content": complex_csv,
                "file_type": "csv",
                "target_format": "CDISC_SDTM",
                "confidence_threshold": 95  # High threshold to trigger arbitration
            }
        }, 7)

        if "result" in response:
            content = json.loads(response["result"]["content"][0]["text"])
            if content.get("success"):
                print(f"✅ Complex conversion successful")
                if content.get("arbitration_used"):
                    print(f"   🤖 Arbitration was used: {content.get('judge_reasoning', 'N/A')}")
                print(f"   Final confidence: {content['confidence']}%")

        # Test 8: Shutdown
        print("\nTest 8: Shutdown server")
        response = send_json_rpc(proc, "shutdown", {}, 8)
        print("✅ Shutdown signal sent")

    except Exception as e:
        print(f"\n❌ Test error: {e}")
    finally:
        # Clean up
        proc.terminate()
        proc.wait(timeout=5)
        print("\n" + "=" * 60)
        print("Tests completed!")


def test_rest_api():
    """Test the tool via REST API"""
    import requests

    print("\nTesting REST API integration...")
    print("=" * 60)

    base_url = "http://localhost:8210"

    # Test data
    test_csv = """Visit,Day,Procedures
Screening,-14,Consent
Baseline,0,Labs
Week 1,7,Drug Admin"""

    # Test the schedule_converter tool via REST
    print("\nTesting schedule_converter via REST API...")

    try:
        response = requests.post(
            f"{base_url}/run_tool/schedule_converter",
            json={
                "file_content": test_csv,
                "file_type": "csv",
                "target_format": "CDISC_SDTM"
            }
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ REST API conversion successful")
                print(f"   Confidence: {result['confidence']}%")
                print(f"   TV records: {len(result['data']['TV'])}")
            else:
                print(f"❌ Conversion failed: {result.get('error')}")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")

    except requests.exceptions.ConnectionError:
        print("⚠️  Flask server not running. Start with: python server.py")
    except Exception as e:
        print(f"❌ REST API test error: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test Schedule Converter")
    parser.add_argument(
        "--mode",
        choices=["mcp", "rest", "both"],
        default="mcp",
        help="Test mode: mcp (JSON-RPC), rest (HTTP API), or both"
    )

    args = parser.parse_args()

    if args.mode in ["mcp", "both"]:
        test_mcp_server()

    if args.mode in ["rest", "both"]:
        test_rest_api()