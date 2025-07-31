# 🎯 InvenTag Service Enrichment Framework

InvenTag's service enrichment framework provides deep attribute extraction for AWS resources, going beyond basic resource discovery to capture detailed configuration and operational data. This comprehensive system includes both specific service handlers for major AWS services and a dynamic discovery system for unknown services.

## 📋 Overview

The service enrichment system consists of three main components:

- **ServiceHandler**: Abstract base class for service-specific attribute handlers
- **ServiceHandlerFactory**: Factory for creating and managing service handlers
- **ServiceAttributeEnricher**: Main orchestrator for the enrichment process

## 🏗️ Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│ ServiceAttributeEnricher │    │ ServiceHandlerFactory │    │   ServiceHandler    │
│                     │    │                     │    │                     │
│ • Resource Processing│───▶│ • Handler Management│───▶│ • Service-Specific  │
│ • Statistics Tracking│    │ • Dynamic Discovery │    │   Attribute Extraction│
│ • Batch Operations  │    │ • Handler Registry  │    │ • Read-Only Validation│
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## 🔧 Supported Services with Deep Enrichment

### Amazon S3 Handler

The S3 handler provides comprehensive bucket analysis with detailed configuration extraction:

#### Supported Attributes
- **Encryption Configuration**: Server-side encryption settings, KMS key details
- **Versioning Status**: Bucket versioning configuration and status
- **Lifecycle Management**: Lifecycle rules and transition policies
- **Public Access Controls**: Public access block configuration
- **Object Lock**: Object lock configuration and retention policies
- **Location Constraints**: Bucket region and location details

#### Usage Example
```python
from inventag.discovery.service_enrichment import ServiceAttributeEnricher

enricher = ServiceAttributeEnricher()
s3_resources = [r for r in resources if r.get('service') == 'S3']
enriched_s3 = enricher.enrich_resources_with_attributes(s3_resources)

for bucket in enriched_s3:
    if 'service_attributes' in bucket:
        attrs = bucket['service_attributes']
        print(f"Bucket: {bucket['name']}")
        print(f"  Encryption: {attrs.get('encryption')}")
        print(f"  Versioning: {attrs.get('versioning_status')}")
        print(f"  Lifecycle Rules: {len(attrs.get('lifecycle_rules', []))}")
        print(f"  Public Access Block: {attrs.get('public_access_block')}")
```

### Amazon RDS Handler

The RDS handler provides database configuration deep dive with comprehensive operational data:

#### Supported Attributes
- **Engine Details**: Database engine, version, and class information
- **Storage Configuration**: Allocated storage, type, and encryption settings
- **High Availability**: Multi-AZ deployment and backup configuration
- **Security Settings**: VPC security groups, subnet groups, and parameter groups
- **Performance Insights**: Monitoring and performance configuration
- **Maintenance Windows**: Backup and maintenance scheduling

#### Usage Example
```python
rds_resources = [r for r in resources if r.get('service') == 'RDS']
enriched_rds = enricher.enrich_resources_with_attributes(rds_resources)

for db in enriched_rds:
    if 'service_attributes' in db:
        attrs = db['service_attributes']
        print(f"Database: {db['name']}")
        print(f"  Engine: {attrs.get('engine')} {attrs.get('engine_version')}")
        print(f"  Multi-AZ: {attrs.get('multi_az', False)}")
        print(f"  Encrypted: {attrs.get('storage_encrypted', False)}")
        print(f"  Backup Retention: {attrs.get('backup_retention_period', 0)} days")
```

### Amazon EC2 Handler

The EC2 handler provides instance and volume analysis with detailed configuration data:

#### Supported Attributes
- **Instance Configuration**: Type, state, platform, and architecture details
- **Network Configuration**: VPC, subnet, security groups, and IP addresses
- **Storage Details**: EBS optimization, block device mappings, and root device info
- **Security Features**: IAM instance profiles, key pairs, and monitoring state
- **Advanced Features**: CPU options, hibernation, metadata options, and enclave settings
- **Volume Attributes**: Size, type, IOPS, throughput, encryption, and attachment details

#### Usage Example
```python
ec2_resources = [r for r in resources if r.get('service') == 'EC2']
enriched_ec2 = enricher.enrich_resources_with_attributes(ec2_resources)

for instance in enriched_ec2:
    if 'service_attributes' in instance and instance.get('type') == 'Instance':
        attrs = instance['service_attributes']
        print(f"Instance: {instance['name']}")
        print(f"  Type: {attrs.get('instance_type')}")
        print(f"  State: {attrs.get('state')}")
        print(f"  VPC: {attrs.get('vpc_id')}")
        print(f"  Security Groups: {attrs.get('security_groups', [])}")
        print(f"  EBS Optimized: {attrs.get('ebs_optimized', False)}")
```

### AWS Lambda Handler

The Lambda handler provides function configuration analysis with comprehensive runtime data:

#### Supported Attributes
- **Runtime Environment**: Runtime version, handler, and execution role
- **Resource Configuration**: Memory size, timeout, and ephemeral storage
- **Network Configuration**: VPC settings and security groups
- **Code Configuration**: Code size, SHA256, deployment package details
- **Advanced Features**: Layers, environment variables, dead letter queues
- **Monitoring**: Tracing configuration and logging settings

#### Usage Example
```python
lambda_resources = [r for r in resources if r.get('service') == 'Lambda']
enriched_lambda = enricher.enrich_resources_with_attributes(lambda_resources)

for function in enriched_lambda:
    if 'service_attributes' in function:
        attrs = function['service_attributes']
        print(f"Function: {function['name']}")
        print(f"  Runtime: {attrs.get('runtime')}")
        print(f"  Memory: {attrs.get('memory_size')} MB")
        print(f"  Timeout: {attrs.get('timeout')} seconds")
        print(f"  Layers: {len(attrs.get('layers', []))}")
```

### Amazon ECS Handler

The ECS handler provides container service details with cluster and service configuration:

#### Supported Attributes
- **Cluster Configuration**: Status, capacity providers, and service counts
- **Service Configuration**: Task definitions, desired count, and deployment settings
- **Network Configuration**: Load balancers, service registries, and VPC settings
- **Scaling Configuration**: Auto scaling and capacity provider strategies

#### Usage Example
```python
ecs_resources = [r for r in resources if r.get('service') == 'ECS']
enriched_ecs = enricher.enrich_resources_with_attributes(ecs_resources)

for cluster in enriched_ecs:
    if 'service_attributes' in cluster and cluster.get('type') == 'Cluster':
        attrs = cluster['service_attributes']
        print(f"Cluster: {cluster['name']}")
        print(f"  Status: {attrs.get('status')}")
        print(f"  Running Tasks: {attrs.get('running_tasks_count', 0)}")
        print(f"  Active Services: {attrs.get('active_services_count', 0)}")
```

### Amazon EKS Handler

The EKS handler provides Kubernetes cluster analysis with comprehensive configuration data:

#### Supported Attributes
- **Cluster Configuration**: Version, endpoint, and platform details
- **Network Configuration**: VPC settings and Kubernetes network config
- **Security Configuration**: Encryption, identity providers, and access controls
- **Node Group Details**: Instance types, scaling configuration, and launch templates
- **Add-on Configuration**: Installed add-ons and their versions

#### Usage Example
```python
eks_resources = [r for r in resources if r.get('service') == 'EKS']
enriched_eks = enricher.enrich_resources_with_attributes(eks_resources)

for cluster in enriched_eks:
    if 'service_attributes' in cluster and cluster.get('type') == 'Cluster':
        attrs = cluster['service_attributes']
        print(f"EKS Cluster: {cluster['name']}")
        print(f"  Version: {attrs.get('version')}")
        print(f"  Endpoint: {attrs.get('endpoint')}")
        print(f"  Platform Version: {attrs.get('platform_version')}")
```

## 🔄 Dynamic Service Discovery

For services not explicitly supported, InvenTag includes an intelligent dynamic discovery system that automatically attempts to enrich resources using pattern-based API discovery.

### Key Features

- **Pattern-Based API Discovery**: Automatically discovers and tests read-only API operations
- **Intelligent Parameter Mapping**: Maps resource identifiers to appropriate API parameters
- **Response Analysis**: Extracts meaningful attributes from API responses
- **Caching System**: Optimizes performance by caching successful patterns
- **Comprehensive Coverage**: Attempts multiple API patterns for maximum data extraction

### How It Works

1. **Operation Pattern Generation**: Creates potential API operation names based on resource type
2. **Parameter Pattern Matching**: Maps resource identifiers to API parameters
3. **Safe API Execution**: Validates operations as read-only before execution
4. **Response Extraction**: Intelligently extracts attributes from API responses
5. **Result Caching**: Caches successful patterns for performance optimization

### Usage Example

```python
from inventag.discovery.service_enrichment import DynamicServiceHandler

# The dynamic handler is automatically used for unknown services
enricher = ServiceAttributeEnricher()
unknown_resources = [r for r in resources if r.get('service') == 'UnknownService']
enriched_unknown = enricher.enrich_resources_with_attributes(unknown_resources)

# Check dynamic discovery results
for resource in enriched_unknown:
    if 'service_attributes' in resource:
        attrs = resource['service_attributes']
        if 'discovery_metadata' in attrs:
            metadata = attrs['discovery_metadata']
            print(f"Resource: {resource['name']}")
            print(f"  Discovery Method: {metadata.get('discovery_method')}")
            print(f"  Successful Pattern: {metadata.get('successful_pattern')}")
            print(f"  Attempted Patterns: {len(metadata.get('attempted_patterns', []))}")
```

## 🛠️ Service Enrichment Framework

### ServiceAttributeEnricher

The main orchestrator for the enrichment process:

```python
from inventag.discovery.service_enrichment import ServiceAttributeEnricher

# Initialize enricher
enricher = ServiceAttributeEnricher()

# Enrich all resources
enriched_resources = enricher.enrich_resources_with_attributes(resources)

# Enrich single resource
enriched_resource = enricher.enrich_single_resource(resource)

# Get enrichment statistics
stats = enricher.get_enrichment_statistics()
print(f"Total resources: {stats['statistics']['total_resources']}")
print(f"Successfully enriched: {stats['statistics']['enriched_resources']}")
print(f"Failed enrichments: {stats['statistics']['failed_enrichments']}")
print(f"Discovered services: {stats['discovered_services']}")
print(f"Unknown services: {stats['unknown_services']}")
```

### ServiceHandlerFactory

Factory for creating and managing service handlers:

```python
from inventag.discovery.service_enrichment import ServiceHandlerFactory

# Initialize factory
factory = ServiceHandlerFactory(session=boto3.Session())

# Get handler for specific service
handler = factory.get_handler('S3', 'Bucket')

# List registered handlers
handlers = factory.list_registered_handlers()
print(f"Registered handlers: {handlers}")
```

## 🎯 Custom Service Handlers

Extend InvenTag with custom service handlers for proprietary or specialized services:

### Creating a Custom Handler

```python
from inventag.discovery.service_enrichment import ServiceHandler
from typing import Dict, List, Any

class CustomServiceHandler(ServiceHandler):
    """Custom handler for specialized service."""
    
    def can_handle(self, service: str, resource_type: str) -> bool:
        """Check if this handler can process the service/resource type."""
        return service.upper() == 'CUSTOM_SERVICE'
    
    def _define_read_only_operations(self) -> List[str]:
        """Define read-only operations this handler uses."""
        return [
            'describe_custom_resource',
            'get_custom_configuration',
            'list_custom_attributes'
        ]
    
    def enrich_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich resource with service-specific attributes."""
        resource_id = resource.get('id', '')
        if not resource_id:
            return resource
            
        try:
            # Get service client
            client = self.session.client('custom-service')
            attributes = {}
            
            # Get resource configuration
            config_response = self._safe_api_call(
                client, 'describe_custom_resource', ResourceId=resource_id
            )
            if config_response:
                attributes.update({
                    'configuration': config_response.get('Configuration', {}),
                    'status': config_response.get('Status'),
                    'created_date': config_response.get('CreatedDate')
                })
            
            # Get additional attributes
            attrs_response = self._safe_api_call(
                client, 'get_custom_configuration', ResourceId=resource_id
            )
            if attrs_response:
                attributes.update({
                    'custom_settings': attrs_response.get('Settings', {}),
                    'performance_metrics': attrs_response.get('Metrics', {})
                })
            
            return {**resource, 'service_attributes': attributes}
            
        except Exception as e:
            self.logger.warning(f"Failed to enrich custom resource {resource_id}: {e}")
            return resource
```

### Registering Custom Handlers

```python
# Register custom handler
enricher = ServiceAttributeEnricher()
enricher.register_custom_handler('CUSTOM_SERVICE', CustomServiceHandler)

# Use enricher with custom handler
enriched_resources = enricher.enrich_resources_with_attributes(resources)
```

## 🔒 Security and Read-Only Operations

The service enrichment framework includes comprehensive security measures to ensure only read-only operations are performed:

### Read-Only Validation

```python
# All handlers validate operations as read-only
handler = S3Handler(session)
is_safe = handler.validate_read_only_operation('describe_buckets')  # True
is_safe = handler.validate_read_only_operation('delete_bucket')     # False
```

### Safe API Calls

```python
# All API calls go through safe execution wrapper
response = handler._safe_api_call(client, 'describe_buckets')
# Automatically validates operation and handles errors
```

### Operation Whitelisting

Each handler explicitly defines allowed read-only operations:

```python
def _define_read_only_operations(self) -> List[str]:
    """Define S3 read-only operations."""
    return [
        'get_bucket_encryption',
        'get_bucket_versioning',
        'get_bucket_location',
        'get_bucket_tagging',
        'get_public_access_block',
        # ... more read-only operations
    ]
```

## 📊 Performance Optimization

### Caching System

The dynamic service handler includes intelligent caching to optimize performance:

```python
# Get cache statistics
dynamic_handler = DynamicServiceHandler(session)
stats = dynamic_handler.get_cache_statistics()
print(f"Cached results: {stats['cached_results']}")
print(f"Failed patterns: {stats['failed_patterns']}")
print(f"Service operations cached: {stats['service_operations_cached']}")

# Clear cache if needed
dynamic_handler.clear_cache()
```

### Batch Processing

Process multiple resources efficiently:

```python
# Process resources in batches
enricher = ServiceAttributeEnricher()

# Process all resources at once (recommended)
enriched_resources = enricher.enrich_resources_with_attributes(resources)

# Or process by service for better control
services = enricher.discover_all_services(resources)
for service in services:
    service_resources = [r for r in resources if r.get('service') == service]
    enriched_service_resources = enricher.enrich_resources_with_attributes(service_resources)
```

## 🔧 Integration Patterns

### With Resource Discovery

```python
from inventag import AWSResourceInventory
from inventag.discovery.service_enrichment import ServiceAttributeEnricher

# Discover resources
inventory = AWSResourceInventory(regions=['us-east-1', 'us-west-2'])
resources = inventory.discover_resources()

# Enrich with service-specific attributes
enricher = ServiceAttributeEnricher()
enriched_resources = enricher.enrich_resources_with_attributes(resources)

# Resources now include detailed service attributes
for resource in enriched_resources:
    if 'service_attributes' in resource:
        print(f"Enriched {resource['service']}/{resource['type']}: {resource['name']}")
```

### With State Management

```python
from inventag.state import StateManager

# Save enriched resources to state
state_manager = StateManager()
state_id = state_manager.save_state(
    resources=enriched_resources,
    account_id='123456789012',
    regions=['us-east-1', 'us-west-2'],
    tags={'enrichment': 'enabled', 'version': '1.0'}
)

# Load and compare enriched states
previous_state = state_manager.load_state(previous_state_id)
current_state = state_manager.load_state(state_id)

# Delta detection with enriched attributes
from inventag.state import DeltaDetector
detector = DeltaDetector()
delta_report = detector.detect_changes(
    old_resources=previous_state.resources,
    new_resources=current_state.resources,
    state1_id=previous_state_id,
    state2_id=state_id
)
```

### With Compliance Checking

```python
from inventag.compliance import ComprehensiveTagComplianceChecker

# Check compliance on enriched resources
checker = ComprehensiveTagComplianceChecker(
    regions=['us-east-1', 'us-west-2'],
    config_file='config/tag_policy.yaml'
)

# Compliance checking benefits from enriched attributes
compliance_results = checker.check_compliance(enriched_resources)

# Enhanced compliance analysis with service-specific data
for resource in compliance_results['non_compliant_resources']:
    if 'service_attributes' in resource:
        attrs = resource['service_attributes']
        print(f"Non-compliant {resource['service']}: {resource['name']}")
        
        # Service-specific compliance insights
        if resource['service'] == 'S3':
            encryption = attrs.get('encryption', {})
            if not encryption or not encryption.get('enabled'):
                print("  - Missing encryption configuration")
        
        elif resource['service'] == 'RDS':
            if not attrs.get('storage_encrypted', False):
                print("  - Database storage not encrypted")
            if not attrs.get('multi_az', False):
                print("  - Not configured for high availability")
```

## 🚨 Troubleshooting

### Common Issues

**Handler Not Found**
```python
# Check registered handlers
factory = ServiceHandlerFactory(session)
handlers = factory.list_registered_handlers()
print(f"Available handlers: {handlers}")

# Register missing handler
factory.register_handler('MISSING_SERVICE', CustomHandler)
```

**API Permission Errors**
```python
# Check handler's required operations
handler = factory.get_handler('S3', 'Bucket')
operations = handler.get_read_only_operations()
print(f"Required operations: {operations}")

# Ensure IAM policy includes these operations
```

**Performance Issues**
```python
# Monitor enrichment statistics
stats = enricher.get_enrichment_statistics()
if stats['statistics']['failed_enrichments'] > 0:
    print(f"Failed enrichments: {stats['statistics']['failed_enrichments']}")
    
# Clear dynamic handler cache if needed
if hasattr(enricher.handler_factory._dynamic_handler, 'clear_cache'):
    enricher.handler_factory._dynamic_handler.clear_cache()
```

**Memory Usage**
```python
# For large resource sets, process in batches
batch_size = 100
for i in range(0, len(resources), batch_size):
    batch = resources[i:i + batch_size]
    enriched_batch = enricher.enrich_resources_with_attributes(batch)
    # Process enriched_batch immediately
```

## 📈 Best Practices

### Handler Development

1. **Always Validate Read-Only**: Ensure all operations are truly read-only
2. **Handle Errors Gracefully**: Use `_safe_api_call` for all API operations
3. **Minimize API Calls**: Cache results and batch operations where possible
4. **Document Attributes**: Clearly document what attributes are extracted
5. **Test Thoroughly**: Test with various resource configurations

### Performance Optimization

1. **Use Caching**: Leverage the built-in caching system for repeated operations
2. **Batch Processing**: Process resources in batches for better performance
3. **Filter Resources**: Only enrich resources that need detailed attributes
4. **Monitor Statistics**: Track enrichment success rates and performance
5. **Clear Caches**: Periodically clear caches to prevent memory issues

### Security Considerations

1. **Read-Only Operations**: Never use operations that modify resources
2. **Error Handling**: Don't expose sensitive information in error messages
3. **Credential Management**: Use IAM roles and temporary credentials
4. **Audit Logging**: Log enrichment activities for security auditing
5. **Permission Validation**: Regularly validate required IAM permissions

## 🎯 Interactive Demo

Explore the service enrichment framework with the comprehensive interactive demo:

```bash
# Run the service enrichment demonstration
python examples/service_enrichment_demo.py
```

The demo script provides:

- **Framework Overview**: Detailed explanation of the service enrichment architecture
- **Service Handler Capabilities**: Comprehensive breakdown of each supported service
- **Dynamic Discovery Demonstration**: Shows how unknown services are handled
- **Enrichment Process Simulation**: Step-by-step walkthrough with sample data
- **Usage Patterns**: Common integration patterns and best practices
- **Cross-Platform Compatibility**: Uses text-based indicators for universal terminal support

### Demo Output Features

The demonstration includes:
- Service handler registration and capabilities overview
- Detailed attribute extraction examples for each supported service
- Dynamic discovery process explanation and simulation
- Enriched data structure examples with real-world configurations
- Performance statistics and enrichment success metrics
- Integration examples with state management and compliance checking

### Terminal Compatibility

The demo script has been optimized for cross-platform compatibility:
- Uses `[OK]` and `[DYNAMIC]` text indicators instead of emoji characters
- Ensures proper UTF-8 encoding on Windows systems
- Provides clear, readable output across different terminal environments
- Maintains professional formatting while ensuring universal accessibility

---

For more examples and advanced usage patterns, see the demo scripts in the `examples/` directory and the comprehensive test suite in `tests/unit/test_service_handlers.py`.