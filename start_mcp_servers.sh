#!/bin/bash
#
# Start all MCP servers for local development
# Each server runs in background and logs to a separate file
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
MCP_DIR="/dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools"
SOA_DIR="/dcri/sasusers/home/scb2/gitRepos/schedule-assessments-optimizer"
LOG_DIR="$MCP_DIR/logs"
PID_DIR="$MCP_DIR/pids"

# Create directories if they don't exist
mkdir -p "$LOG_DIR"
mkdir -p "$PID_DIR"

# Function to start an MCP server
start_mcp_server() {
    local name=$1
    local script=$2
    local port=$3  # For future HTTP bridge support
    local log_file="$LOG_DIR/${name}.log"
    local pid_file="$PID_DIR/${name}.pid"

    echo -e "${YELLOW}Starting MCP server: ${name}...${NC}"

    # Check if already running
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ ${name} is already running (PID: $pid)${NC}"
            return 0
        else
            # Clean up stale PID file
            rm -f "$pid_file"
        fi
    fi

    # Start the server
    if [ -f "$script" ]; then
        # Run server in background, redirect stderr to log
        python "$script" > "$log_file" 2>&1 &
        pid=$!

        # Save PID
        echo $pid > "$pid_file"

        # Check if server started successfully
        sleep 1
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ ${name} started successfully (PID: $pid)${NC}"
            echo "  Log: $log_file"
        else
            echo -e "${RED}✗ Failed to start ${name}${NC}"
            echo "  Check log: $log_file"
            rm -f "$pid_file"
            return 1
        fi
    else
        echo -e "${RED}✗ Script not found: $script${NC}"
        return 1
    fi
}

# Function to stop an MCP server
stop_mcp_server() {
    local name=$1
    local pid_file="$PID_DIR/${name}.pid"

    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid"
            echo -e "${GREEN}✓ Stopped ${name} (PID: $pid)${NC}"
            rm -f "$pid_file"
        else
            echo -e "${YELLOW}${name} was not running${NC}"
            rm -f "$pid_file"
        fi
    else
        echo -e "${YELLOW}No PID file for ${name}${NC}"
    fi
}

# Function to check server status
check_mcp_status() {
    local name=$1
    local pid_file="$PID_DIR/${name}.pid"

    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ ${name} is running (PID: $pid)${NC}"
        else
            echo -e "${RED}✗ ${name} is not running (stale PID file)${NC}"
        fi
    else
        echo -e "${YELLOW}○ ${name} is not running${NC}"
    fi
}

# Function to tail logs
tail_logs() {
    echo -e "${YELLOW}Tailing all MCP server logs (Ctrl+C to stop)...${NC}"
    tail -f "$LOG_DIR"/*.log
}

# Parse command line arguments
case "$1" in
    start)
        echo -e "${GREEN}Starting MCP servers...${NC}"
        echo "================================"

        # Start main MCP tools server with wrapper
        start_mcp_server "mcp-tools-wrapper" "$MCP_DIR/mcp_tool_wrapper.py" 8210

        # Start Protocol Complexity Analyzer
        start_mcp_server "protocol-complexity" \
            "$SOA_DIR/services/mcp_ProtocolComplexityAnalyzer/mcp_server.py" 8001

        # Start Compliance Knowledge Base
        start_mcp_server "compliance-kb" \
            "$SOA_DIR/services/mcp_ComplianceKnowledgeBase/mcp_server.py" 8002

        echo "================================"
        echo -e "${GREEN}All servers started!${NC}"
        echo ""
        echo "To test servers, run:"
        echo "  python $MCP_DIR/mcp_client.py --test"
        echo ""
        echo "To view logs:"
        echo "  $0 logs"
        ;;

    stop)
        echo -e "${RED}Stopping MCP servers...${NC}"
        echo "================================"

        stop_mcp_server "mcp-tools-wrapper"
        stop_mcp_server "protocol-complexity"
        stop_mcp_server "compliance-kb"

        echo "================================"
        echo -e "${GREEN}All servers stopped!${NC}"
        ;;

    restart)
        $0 stop
        sleep 2
        $0 start
        ;;

    status)
        echo -e "${YELLOW}MCP Server Status${NC}"
        echo "================================"

        check_mcp_status "mcp-tools-wrapper"
        check_mcp_status "protocol-complexity"
        check_mcp_status "compliance-kb"

        echo "================================"
        ;;

    logs)
        tail_logs
        ;;

    test)
        echo -e "${YELLOW}Testing MCP servers...${NC}"
        echo "================================"

        # Test with the MCP client
        python "$MCP_DIR/mcp_client.py" --test

        echo "================================"
        ;;

    clean)
        echo -e "${YELLOW}Cleaning up logs and PID files...${NC}"
        rm -f "$LOG_DIR"/*.log
        rm -f "$PID_DIR"/*.pid
        echo -e "${GREEN}✓ Cleaned up${NC}"
        ;;

    *)
        echo "Usage: $0 {start|stop|restart|status|logs|test|clean}"
        echo ""
        echo "Commands:"
        echo "  start   - Start all MCP servers"
        echo "  stop    - Stop all MCP servers"
        echo "  restart - Restart all MCP servers"
        echo "  status  - Check status of all servers"
        echo "  logs    - Tail all server logs"
        echo "  test    - Run basic tests on all servers"
        echo "  clean   - Clean up log and PID files"
        exit 1
        ;;
esac

exit 0