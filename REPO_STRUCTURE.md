# Repository Structure - DCRI MCP Tools

## 🎯 Overview
This repository has been reorganized for clarity and maintainability. All files are now organized into logical directories.

## 📁 Directory Structure

```
dcri-mcp-tools/
│
├── 📱 Main Application Files (Root)
│   ├── server.py                 # Main Flask REST API server
│   ├── server_demo.py            # Demo page generator
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                 # Container configuration
│   ├── .env.example              # Environment template
│   └── developer_checklist.yaml  # Active development tracking
│
├── 🔧 scripts/                   # Utility and MCP scripts
│   ├── mcp_server.py            # Base MCP protocol implementation
│   ├── mcp_client.py            # MCP client library
│   ├── schedule_converter_mcp.py # Schedule converter MCP server
│   ├── use_schedule_converter.py # Client for schedule converter
│   ├── cleanup_repo.py          # Repository maintenance script
│   └── verify_tools.py          # Tool verification utility
│
├── 🏥 tools/                     # 95 Clinical Trial Tools
│   ├── adverse_event_coder.py
│   ├── data_dictionary_validator.py
│   ├── schedule_converter.py
│   ├── schedule_converter_azure.py
│   └── ... (91 more tools)
│
├── 🧪 tests/                     # Test suites
│   ├── unit/                    # Unit tests for individual tools
│   │   ├── test_adverse_event_coder.py
│   │   └── ... (100+ test files)
│   └── integration/             # Integration tests
│       ├── test_mcp_integration.py
│       ├── test_schedule_converter.py
│       └── test_azure_openai.py
│
├── 📚 docs/                      # Documentation
│   ├── API_DOCUMENTATION.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── MCP_IMPLEMENTATION_GUIDE.md
│   ├── MCP_USAGE_GUIDE.md
│   └── USER_TRAINING.md
│
├── 📦 archive/                   # Historical artifacts
│   ├── developer_checklist_archive_20250915.md
│   └── ... (old development files)
│
├── 🔐 auth/                      # Authentication modules
│   └── graph_auth.py            # Microsoft Graph authentication
│
├── 📂 sharepoint/                # SharePoint integration
│   └── sharepoint_client.py     # SharePoint file operations
│
└── 💾 cache/                     # Caching layer
    └── redis_cache.py           # Redis cache implementation
```

## 🚀 Quick Start

### Running the Flask Server
```bash
# From repository root
python server.py
# Access at http://localhost:8210
```

### Running the MCP Schedule Converter
```bash
# Using the startup script
./start_schedule_converter.sh

# Or directly
python scripts/schedule_converter_mcp.py

# Or using the client
python scripts/use_schedule_converter.py
```

### Running Tests
```bash
# All tests
pytest tests/ -v

# Specific test category
pytest tests/unit/test_data_dictionary_validator.py -v
```

### Repository Maintenance
```bash
# Generate status report
python scripts/cleanup_repo.py --report

# Clean cache files
python scripts/cleanup_repo.py --clean

# Full cleanup (archive, organize, clean)
python scripts/cleanup_repo.py --all
```

## 📊 Statistics
- **95** Clinical trial tools
- **104** Test files
- **7** Utility scripts
- **5** Documentation guides
- **99.3%** Project completion

## 🔗 Integration Points

### For schedule-assessments-optimizer
```python
# The integration file has been updated
from mcp_integration import MCPScheduleConverterContext

with MCPScheduleConverterContext() as converter:
    result = converter.convert_schedule(
        file_path="schedule.csv",
        target_format="CDISC_SDTM"
    )
```

### For Claude Desktop
```json
{
  "mcpServers": {
    "schedule-converter": {
      "command": "python",
      "args": ["/path/to/dcri-mcp-tools/scripts/schedule_converter_mcp.py"]
    }
  }
}
```

## 📝 Developer Notes

### Active Development
See `developer_checklist.yaml` for current tasks and status.

### Adding New Tools
1. Create tool in `tools/` directory
2. Add test in `tests/unit/`
3. Update documentation
4. Run verification: `python scripts/verify_tools.py`

### Import Paths
After reorganization, imports have been updated:
- Scripts import from `scripts.module_name`
- Tools import from `tools.module_name`
- Tests use relative imports with parent path additions

## 🧹 Cleanup Complete
Repository has been reorganized with:
- ✅ All Python scripts moved to `scripts/`
- ✅ All tests moved to `tests/integration/`
- ✅ All guides moved to `docs/`
- ✅ Single `developer_checklist.yaml` for tracking
- ✅ Old checklist archived with date stamp
- ✅ Import paths updated in all moved files
- ✅ Cleanup script created for maintenance
- ✅ Cache files cleaned (saved 100+ MB)