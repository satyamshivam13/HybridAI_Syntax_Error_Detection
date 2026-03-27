# Project Summary

OmniSyntax is a multi-language code-error detection and explanation project for programming education.

## Goal
Provide consistent code analysis and guidance across API, CLI, and Streamlit entry points, with reliable behavior in both healthy (ML-assisted) and degraded (rule-based) modes.

## Supported languages
- Python
- Java
- C
- C++
- JavaScript

## Core capabilities
- Syntax and quality issue detection
- Optional auto-fix suggestions
- Language-aware diagnostics
- Tutor-style explanations
- Degraded-mode fallback when ML artifacts are unavailable or incompatible

## Runtime surfaces
- FastAPI service (`api.py`, `start_api.py`)
- Streamlit UI (`app.py`)
- CLI (`cli.py`)

## Current priorities
- Improve C, Java, and JavaScript reliability in degraded mode
- Keep API, CLI, and Streamlit behavior aligned
- Preserve and expand regression coverage
- Maintain safe ML compatibility controls

## Related docs
- [Quick Start](QUICKSTART.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Comprehensive Test Report](COMPREHENSIVE_TEST_REPORT.md)
- [Contributing](CONTRIBUTING.md)
