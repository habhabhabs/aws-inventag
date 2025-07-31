"""
InvenTag - Unified AWS Cloud Governance Platform

A comprehensive Python package for AWS resource discovery, compliance checking,
professional BOM (Bill of Materials) document generation, and state management
with advanced change tracking capabilities.

This package transforms the proven functionality from standalone scripts into
a unified, enterprise-grade platform suitable for both CLI usage and service deployment.
"""

__version__ = "1.0.0"
__author__ = "InvenTag Team"

# Core modules
from .discovery import AWSResourceInventory
from .compliance import ComprehensiveTagComplianceChecker
from .reporting import BOMConverter

# Analysis modules
from .discovery.network_analyzer import NetworkAnalyzer

# State management modules
from .state import StateManager, DeltaDetector, ChangelogGenerator

# Main orchestrator (will be implemented in later tasks)
# from .core import CloudBOMGenerator

__all__ = [
    "AWSResourceInventory",
    "ComprehensiveTagComplianceChecker", 
    "BOMConverter",
    "NetworkAnalyzer",
    "StateManager",
    "DeltaDetector",
    "ChangelogGenerator",
    # "CloudBOMGenerator",
]