# Setup Guide - Testing Bot

## Project Overview

This is a test project designed to validate the **Automated Remediation Agent**.

## Prerequisites

Before setting up, ensure you have:
- Python 3.8+
- Git
- Remediation Agent files (will be provided)

## Installation Steps

### 1. Clone Repository
```bash
git clone https://github.com/frenzydenzy/testing-bot.git
cd testing-bot
```

### 2. Create Python Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Remediation Agent
The agent files will be copied to this project:
- `local_code_analyzer.py`
- `commit_detector.py`
- `remediation_orchestrator.py`
- `remediation_branch_manager.py`
- `remediation_post_commit_hook.py`
- `normalize_findings.py`

### 5. Configure Git Hook
The git post-commit hook will be installed automatically:
```bash
# Hook installed at: .git/hooks/post-commit
```

### 6. Verify Installation
```bash
python local_code_analyzer.py --test
```

## Usage Workflow

### Create Feature Branch
```bash
git checkout -b feature/test-feature
# Add your code
```

### Commit Changes
```bash
git add .
git commit -m "Add test code"
# Agent runs automatically
```

### Review Findings
```bash
# View analysis results
# Approve: a | Reject: r | Manual: m
```

### Expected Behavior

✅ Commit detection  
✅ Automatic analysis (< 2 seconds)  
✅ Findings report displayed  
✅ Remediation branch created  
✅ User approval prompt  
✅ Auto-merge on approval  

## Troubleshooting

### Git hook not running?
```bash
# Verify hook exists
ls -la .git/hooks/post-commit

# Make executable
chmod +x .git/hooks/post-commit
```

### Analysis errors?
```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip install -r requirements.txt
```

### Reset project
```bash
# Remove agent files
rm local_code_analyzer.py commit_detector.py ...

# Remove hook
rm .git/hooks/post-commit

# Remove branches
git branch -D remediation/* feature/*
```

## Support

For issues or questions, refer to:
- [Project README](../README.md)
- Main remediation skill documentation
