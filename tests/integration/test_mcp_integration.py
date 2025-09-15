#!/usr/bin/env python3
"""
End-to-end integration tests for MCP servers
Tests the complete MCP implementation including all servers and tools
"""

import sys
import os
import json
import time
import subprocess
import asyncio
from typing import Dict, Any

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, '/dcri/sasusers/home/scb2/gitRepos/schedule-assessments-optimizer/backend')

from scripts.mcp_client import MCPClient, MCPServerConfig
try:
    from mcp_integration import MCPIntegration
except ImportError:
    MCPIntegration = None  # Handle if not available


class MCPIntegrationTester:
    """Test suite for MCP integration"""

    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0

    def log_result(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✓ PASS" if passed else "✗ FAIL"
        self.results.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
        if passed:
            self.passed += 1
            print(f"{status}: {test_name}")
        else:
            self.failed += 1
            print(f"{status}: {test_name} - {message}")

    def test_mcp_server_basic(self):
        """Test basic MCP server functionality"""
        print("\n=== Testing Basic MCP Server ===")

        config = MCPServerConfig(
            name="test-basic",
            command=["python", "mcp_server.py"],
            description="Basic test server"
        )

        client = MCPClient(config)

        try:
            # Start server
            if not client.start():
                self.log_result("Server startup", False, "Failed to start server")
                return

            self.log_result("Server startup", True)

            # Test ping
            if client.ping():
                self.log_result("Ping test", True)
            else:
                self.log_result("Ping test", False, "Ping failed")

            # Test tool listing
            tools = client.list_tools()
            if tools and len(tools) > 0:
                self.log_result("Tool listing", True, f"Found {len(tools)} tools")
            else:
                self.log_result("Tool listing", False, "No tools found")

            # Test echo tool if available
            echo_tools = [t for t in tools if t['name'] == 'echo']
            if echo_tools:
                result = client.call_tool("echo", {"message": "Test message"})
                if result and 'content' in result:
                    self.log_result("Echo tool", True)
                else:
                    self.log_result("Echo tool", False, "Invalid response")

        finally:
            client.stop()

    def test_tool_wrapper_server(self):
        """Test MCP tool wrapper server"""
        print("\n=== Testing Tool Wrapper Server ===")

        config = MCPServerConfig(
            name="tool-wrapper",
            command=["python", "mcp_tool_wrapper.py"],
            description="Tool wrapper server",
            cwd="/dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools"
        )

        client = MCPClient(config)

        try:
            # Start server
            if not client.start():
                self.log_result("Tool wrapper startup", False, "Failed to start")
                return

            self.log_result("Tool wrapper startup", True)

            # List tools
            tools = client.list_tools()
            if tools:
                self.log_result("Tool discovery", True, f"Discovered {len(tools)} tools")

                # Test a specific tool if available
                if any(t['name'] == 'test_echo' for t in tools):
                    result = client.call_tool("test_echo", {"text": "Hello MCP"})
                    if result:
                        self.log_result("Tool execution", True)
                    else:
                        self.log_result("Tool execution", False, "No result")
            else:
                self.log_result("Tool discovery", False, "No tools discovered")

        finally:
            client.stop()

    def test_complexity_analyzer_server(self):
        """Test Protocol Complexity Analyzer MCP server"""
        print("\n=== Testing Protocol Complexity Analyzer ===")

        config = MCPServerConfig(
            name="complexity-analyzer",
            command=["python", "mcp_server.py"],
            description="Protocol Complexity Analyzer",
            cwd="/dcri/sasusers/home/scb2/gitRepos/schedule-assessments-optimizer/services/mcp_ProtocolComplexityAnalyzer"
        )

        client = MCPClient(config)

        try:
            # Start server
            if not client.start():
                self.log_result("Complexity analyzer startup", False, "Failed to start")
                return

            self.log_result("Complexity analyzer startup", True)

            # Test complexity analysis
            test_data = {
                "protocol_name": "Test Protocol",
                "phase": "2",
                "num_visits": 12,
                "num_procedures": 60,
                "duration_days": 365,
                "num_sites": 10
            }

            result = client.call_tool("analyze-complexity", test_data)
            if result and 'content' in result:
                content = json.loads(result['content'][0]['text'])
                if 'complexity_score' in content:
                    score = content['complexity_score']
                    self.log_result("Complexity calculation", True,
                                  f"Score: {score}")
                else:
                    self.log_result("Complexity calculation", False,
                                  "Missing complexity score")
            else:
                self.log_result("Complexity calculation", False, "No result")

            # Test visit burden analysis
            visit_data = {
                "visits": [
                    {
                        "name": "Screening",
                        "day": 0,
                        "assessments": [
                            {"name": "Consent", "duration_minutes": 30},
                            {"name": "Physical Exam", "duration_minutes": 45}
                        ]
                    },
                    {
                        "name": "Baseline",
                        "day": 7,
                        "assessments": [
                            {"name": "Blood Draw", "duration_minutes": 15},
                            {"name": "ECG", "duration_minutes": 20}
                        ]
                    }
                ]
            }

            result = client.call_tool("analyze-visit-burden", visit_data)
            if result and 'content' in result:
                self.log_result("Visit burden analysis", True)
            else:
                self.log_result("Visit burden analysis", False, "No result")

        finally:
            client.stop()

    def test_compliance_kb_server(self):
        """Test Compliance Knowledge Base MCP server"""
        print("\n=== Testing Compliance Knowledge Base ===")

        config = MCPServerConfig(
            name="compliance-kb",
            command=["python", "mcp_server.py"],
            description="Compliance Knowledge Base",
            cwd="/dcri/sasusers/home/scb2/gitRepos/schedule-assessments-optimizer/services/mcp_ComplianceKnowledgeBase"
        )

        client = MCPClient(config)

        try:
            # Start server
            if not client.start():
                self.log_result("Compliance KB startup", False, "Failed to start")
                return

            self.log_result("Compliance KB startup", True)

            # Test compliance check
            test_data = {
                "schedule_data": {
                    "protocol_name": "Test Protocol",
                    "phase": "2",
                    "visits": [
                        {
                            "name": "Screening",
                            "day": 0,
                            "assessments": [
                                {"name": "Informed Consent"},
                                {"name": "Medical History"}
                            ]
                        },
                        {
                            "name": "Treatment",
                            "day": 14,
                            "assessments": [
                                {"name": "Drug Administration"},
                                {"name": "Safety Assessment"}
                            ]
                        }
                    ]
                },
                "region": "US"
            }

            result = client.call_tool("check-compliance", test_data)
            if result and 'content' in result:
                content = json.loads(result['content'][0]['text'])
                if 'compliance_score' in content:
                    score = content['compliance_score']
                    status = content.get('status', 'Unknown')
                    self.log_result("Compliance check", True,
                                  f"Score: {score}, Status: {status}")
                else:
                    self.log_result("Compliance check", False,
                                  "Missing compliance score")
            else:
                self.log_result("Compliance check", False, "No result")

            # Test regulations retrieval
            reg_data = {
                "region": "US",
                "phase": "2",
                "population": "adult"
            }

            result = client.call_tool("get-regulations", reg_data)
            if result and 'content' in result:
                self.log_result("Regulations retrieval", True)
            else:
                self.log_result("Regulations retrieval", False, "No result")

        finally:
            client.stop()

    async def test_mcp_integration_module(self):
        """Test the MCPIntegration module"""
        print("\n=== Testing MCP Integration Module ===")

        integration = MCPIntegration(use_mcp=True, fallback_to_rest=True)

        try:
            # Test complexity analysis
            complexity_data = {
                "protocol_name": "Integration Test",
                "phase": "3",
                "num_visits": 15,
                "num_procedures": 75,
                "duration_days": 540,
                "num_sites": 20
            }

            result = await integration.analyze_complexity(complexity_data)
            if result and 'complexity_score' in result:
                self.log_result("Integration: Complexity", True,
                              f"Score: {result['complexity_score']}")
            else:
                self.log_result("Integration: Complexity", False,
                              "Failed to get complexity score")

            # Test compliance check
            compliance_data = {
                "schedule_data": {
                    "protocol_name": "Integration Test",
                    "phase": "3",
                    "visits": [
                        {
                            "name": "Screening",
                            "day": 0,
                            "assessments": [
                                {"name": "Informed Consent"}
                            ]
                        }
                    ]
                },
                "region": "EU"
            }

            result = await integration.check_compliance(compliance_data)
            if result and 'compliance_score' in result:
                self.log_result("Integration: Compliance", True,
                              f"Score: {result['compliance_score']}")
            else:
                self.log_result("Integration: Compliance", False,
                              "Failed to get compliance score")

        finally:
            integration.close()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        print(f"Total tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")

        if self.failed > 0:
            print("\nFailed tests:")
            for result in self.results:
                if not result['passed']:
                    print(f"  - {result['test']}: {result['message']}")

        print("=" * 50)

        return self.failed == 0


def main():
    """Run all integration tests"""
    print("MCP Integration Test Suite")
    print("=" * 50)

    tester = MCPIntegrationTester()

    # Run synchronous tests
    tester.test_mcp_server_basic()
    tester.test_tool_wrapper_server()
    tester.test_complexity_analyzer_server()
    tester.test_compliance_kb_server()

    # Run async tests
    asyncio.run(tester.test_mcp_integration_module())

    # Print summary
    all_passed = tester.print_summary()

    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {tester.failed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())