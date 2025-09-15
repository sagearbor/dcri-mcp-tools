#!/usr/bin/env python3
"""
Repository Cleanup and Maintenance Script
Helps keep the DCRI MCP Tools repository organized
"""

import os
import sys
import shutil
import glob
from datetime import datetime
from pathlib import Path
import argparse
import json
import yaml


class RepoCleanup:
    """Repository cleanup and organization utilities"""

    def __init__(self, repo_path=None):
        if repo_path:
            self.repo_path = Path(repo_path)
        else:
            self.repo_path = Path(__file__).parent.parent

        self.archive_dir = self.repo_path / "archive"
        self.docs_dir = self.repo_path / "docs"
        self.scripts_dir = self.repo_path / "scripts"
        self.tests_dir = self.repo_path / "tests"

        # Ensure directories exist
        for dir_path in [self.archive_dir, self.docs_dir, self.scripts_dir, self.tests_dir]:
            dir_path.mkdir(exist_ok=True)

    def archive_old_files(self, days_old=30):
        """Archive files older than specified days"""
        archived = []
        timestamp = datetime.now().strftime("%Y%m%d")

        # Files to potentially archive
        patterns = [
            "*.log",
            "*.bak",
            "*_old.*",
            "*_backup.*",
            "test_*.json",  # Old test outputs
        ]

        for pattern in patterns:
            for file_path in self.repo_path.glob(pattern):
                if file_path.is_file():
                    file_age = (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).days
                    if file_age > days_old:
                        archive_path = self.archive_dir / f"{timestamp}_{file_path.name}"
                        shutil.move(str(file_path), str(archive_path))
                        archived.append(file_path.name)
                        print(f"  Archived: {file_path.name}")

        return archived

    def organize_python_files(self):
        """Move Python files to appropriate directories"""
        moved = []

        # Python files in root that should be in scripts
        for py_file in self.repo_path.glob("*.py"):
            if py_file.name in ["server.py", "server_demo.py", "setup.py"]:
                continue  # Keep these in root

            if py_file.name.startswith("test_"):
                # Move to tests
                dest = self.tests_dir / "integration" / py_file.name
                dest.parent.mkdir(exist_ok=True)
                if not dest.exists():
                    shutil.move(str(py_file), str(dest))
                    moved.append(f"{py_file.name} -> tests/integration/")
                    print(f"  Moved: {py_file.name} -> tests/integration/")
            else:
                # Move to scripts
                dest = self.scripts_dir / py_file.name
                if not dest.exists():
                    shutil.move(str(py_file), str(dest))
                    moved.append(f"{py_file.name} -> scripts/")
                    print(f"  Moved: {py_file.name} -> scripts/")

        return moved

    def organize_documentation(self):
        """Move documentation files to docs directory"""
        moved = []

        patterns = [
            "*GUIDE*.md",
            "*Guide*.md",
            "*DOCUMENTATION*.md",
            "*TRAINING*.md",
            "*DESIGN*.md"
        ]

        for pattern in patterns:
            for doc_file in self.repo_path.glob(pattern):
                if doc_file.name not in ["README.md", "CLAUDE.md"]:
                    dest = self.docs_dir / doc_file.name
                    if not dest.exists():
                        shutil.move(str(doc_file), str(dest))
                        moved.append(doc_file.name)
                        print(f"  Moved: {doc_file.name} -> docs/")

        return moved

    def clean_cache_files(self):
        """Remove Python cache and temporary files"""
        removed = []

        # Patterns to clean
        patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            "**/*.pyd",
            "**/.pytest_cache",
            "**/.coverage",
            "**/*.egg-info",
            "**/dist",
            "**/build",
            "**/.DS_Store",
            "**/Thumbs.db"
        ]

        for pattern in patterns:
            for path in self.repo_path.glob(pattern):
                if path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    removed.append(str(path.relative_to(self.repo_path)))

        if removed:
            print(f"  Removed {len(removed)} cache files/directories")

        return removed

    def update_checklist(self):
        """Update the developer checklist with current status"""
        checklist_path = self.repo_path / "developer_checklist.yaml"

        if checklist_path.exists():
            with open(checklist_path, 'r') as f:
                checklist = yaml.safe_load(f)

            # Count tools
            tools_count = len(list((self.repo_path / "tools").glob("*.py")))
            checklist['tools_summary']['total'] = tools_count

            # Update timestamp
            checklist['last_updated'] = datetime.now().isoformat()

            with open(checklist_path, 'w') as f:
                yaml.dump(checklist, f, default_flow_style=False, sort_keys=False)

            print(f"  Updated checklist: {tools_count} tools found")

    def generate_report(self):
        """Generate a cleanup report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "directories": {
                "tools": len(list((self.repo_path / "tools").glob("*.py"))),
                "tests": len(list(self.tests_dir.rglob("test_*.py"))),
                "scripts": len(list(self.scripts_dir.glob("*.py"))),
                "docs": len(list(self.docs_dir.glob("*.md")))
            },
            "cache_size": sum(f.stat().st_size for f in self.repo_path.rglob("__pycache__/*")) / 1024 / 1024,
            "total_files": len(list(self.repo_path.rglob("*")))
        }

        return report

    def fix_imports(self):
        """Fix import paths after reorganization"""
        fixes = 0

        # Common import replacements
        replacements = [
            ("from mcp_server import", "from scripts.mcp_server import"),
            ("from mcp_client import", "from scripts.mcp_client import"),
            ("import mcp_server", "import scripts.mcp_server"),
            ("import mcp_client", "import scripts.mcp_client"),
        ]

        # Fix imports in scripts directory
        for py_file in self.scripts_dir.glob("*.py"):
            content = py_file.read_text()
            modified = False

            for old, new in replacements:
                if old in content and new not in content:
                    content = content.replace(old, new)
                    modified = True
                    fixes += 1

            if modified:
                py_file.write_text(content)
                print(f"  Fixed imports in: {py_file.name}")

        return fixes


def main():
    """Main cleanup function"""
    parser = argparse.ArgumentParser(description="Repository cleanup and maintenance")
    parser.add_argument("--archive", action="store_true", help="Archive old files")
    parser.add_argument("--organize", action="store_true", help="Organize files into directories")
    parser.add_argument("--clean", action="store_true", help="Clean cache files")
    parser.add_argument("--fix-imports", action="store_true", help="Fix import paths")
    parser.add_argument("--update-checklist", action="store_true", help="Update developer checklist")
    parser.add_argument("--all", action="store_true", help="Run all cleanup tasks")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")
    parser.add_argument("--report", action="store_true", help="Generate status report")

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        return

    cleanup = RepoCleanup()

    print("=" * 60)
    print("DCRI MCP Tools - Repository Cleanup")
    print("=" * 60)
    print()

    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        print()

    if args.report:
        report = cleanup.generate_report()
        print("Repository Status:")
        print(f"  Tools: {report['directories']['tools']}")
        print(f"  Tests: {report['directories']['tests']}")
        print(f"  Scripts: {report['directories']['scripts']}")
        print(f"  Docs: {report['directories']['docs']}")
        print(f"  Total files: {report['total_files']}")
        print(f"  Cache size: {report['cache_size']:.2f} MB")
        print()

    if args.all or args.archive:
        print("Archiving old files...")
        if not args.dry_run:
            archived = cleanup.archive_old_files()
            if archived:
                print(f"  Archived {len(archived)} files")
            else:
                print("  No files to archive")
        print()

    if args.all or args.organize:
        print("Organizing files...")
        if not args.dry_run:
            moved_py = cleanup.organize_python_files()
            moved_docs = cleanup.organize_documentation()
            total_moved = len(moved_py) + len(moved_docs)
            if total_moved:
                print(f"  Organized {total_moved} files")
            else:
                print("  No files to organize")
        print()

    if args.all or args.clean:
        print("Cleaning cache files...")
        if not args.dry_run:
            removed = cleanup.clean_cache_files()
            if removed:
                print(f"  Cleaned {len(removed)} items")
            else:
                print("  No cache files to clean")
        print()

    if args.all or args.fix_imports:
        print("Fixing import paths...")
        if not args.dry_run:
            fixes = cleanup.fix_imports()
            if fixes:
                print(f"  Fixed {fixes} imports")
            else:
                print("  No imports to fix")
        print()

    if args.all or args.update_checklist:
        print("Updating developer checklist...")
        if not args.dry_run:
            cleanup.update_checklist()
        print()

    print("=" * 60)
    print("Cleanup complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()