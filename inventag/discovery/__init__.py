"""
InvenTag Discovery Module

Extracted and enhanced functionality from aws_resource_inventory.py
Provides comprehensive AWS resource discovery across all services and regions.
"""

from .inventory import AWSResourceInventory

__all__ = ["AWSResourceInventory"]