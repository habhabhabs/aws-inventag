"""
InvenTag - Unified AWS Cloud Governance Platform

A comprehensive Python package for AWS resource discovery, compliance checking,
and professional BOM (Bill of Materials) document generation.

This package transforms the proven functionality from standalone scripts into
a unified, enterprise-grade platform suitable for both CLI usage and service deployment.
"""

__version__ = "1.0.0"
__author__ = "InvenTag Team"

# Core modules
from .discovery import AWSResourceInventory
from .compliance import ComprehensiveTagComplianceChecker
from .reporting import BOMConverter

# Main orchestrator (will be implemented in later tasks)
# from .core import CloudBOMGenerator

__all__ = [
    "AWSResourceInventory",
    "ComprehensiveTagComplianceChecker", 
    "BOMConverter",
    # "CloudBOMGenerator",
]