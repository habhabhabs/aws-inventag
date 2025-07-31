"""
InvenTag Discovery Module

Extracted and enhanced functionality from aws_resource_inventory.py
Provides comprehensive AWS resource discovery across all services and regions.
"""

from .inventory import AWSResourceInventory
from .service_enrichment import (
    ServiceAttributeEnricher,
    ServiceHandler,
    ServiceHandlerFactory,
    DynamicServiceHandler,
    ServiceDiscoveryResult
)

# Import specific service handlers
try:
    from .service_handlers import (
        S3Handler,
        RDSHandler,
        EC2Handler,
        LambdaHandler,
        ECSHandler,
        EKSHandler
    )
    
    __all__ = [
        "AWSResourceInventory",
        "ServiceAttributeEnricher", 
        "ServiceHandler",
        "ServiceHandlerFactory",
        "DynamicServiceHandler",
        "ServiceDiscoveryResult",
        "S3Handler",
        "RDSHandler", 
        "EC2Handler",
        "LambdaHandler",
        "ECSHandler",
        "EKSHandler"
    ]
    
except ImportError:
    # Fallback if service handlers are not available
    __all__ = [
        "AWSResourceInventory",
        "ServiceAttributeEnricher", 
        "ServiceHandler",
        "ServiceHandlerFactory",
        "DynamicServiceHandler",
        "ServiceDiscoveryResult"
    ]