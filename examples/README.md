# Examples

This directory contains example scripts and demo applications showcasing InvenTag's capabilities, including the new state management features.

## Demo Scripts

### `quick_start.sh`
**Automated demo script** that runs all tools in sequence to show basic functionality.

**Usage:**
```bash
# Make sure AWS is configured and IAM policy is set up first
./examples/quick_start.sh
```

**What it does:**
1. Checks AWS credentials
2. Runs basic resource inventory
3. Checks for untagged resources
4. Converts results to Excel with service sheets
5. Shows you where to find the outputs

### `state_manager_demo.py`
**State Management Demonstration** - Shows comprehensive state persistence and tracking capabilities.

**Usage:**
```bash
python examples/state_manager_demo.py
```

**Features demonstrated:**
- State saving with comprehensive metadata
- State loading and listing with timestamp tracking
- Change detection through checksum comparison
- Export functionality for CI/CD integration
- State integrity validation
- Storage statistics and retention management

### `delta_detector_demo.py`
**Change Detection Demonstration** - Comprehensive change tracking between AWS resource states.

**Usage:**
```bash
python examples/delta_detector_demo.py
```

**Features demonstrated:**
- Detection of added, removed, and modified resources
- Attribute-level change analysis with categorization
- Compliance change tracking
- Security and network impact assessment
- Change severity classification
- Detailed change statistics and reporting

### `changelog_generator_demo.py`
**Changelog Generation Demonstration** - Professional change reports and documentation.

**Usage:**
```bash
python examples/changelog_generator_demo.py
```

**Features demonstrated:**
- Markdown and HTML changelog generation
- Executive summary creation
- Detailed change documentation
- Impact analysis reporting
- Customizable formatting and templates
- Export capabilities for documentation systems

### `service_enrichment_demo.py`
**Service Enrichment Demonstration** - Deep service attribute extraction and analysis.

**Usage:**
```bash
python examples/service_enrichment_demo.py
```

**Features demonstrated:**
- Service-specific attribute enrichment for S3, RDS, EC2, Lambda, ECS, EKS
- Dynamic service discovery for unknown services
- Custom service handler development
- Enriched data structure examples
- Integration patterns with state management and compliance checking
- Performance optimization and caching strategies

### `network_security_analysis_demo.py`
**Network & Security Analysis Demonstration** - Comprehensive VPC/subnet analysis and security posture assessment.

**Usage:**
```bash
python examples/network_security_analysis_demo.py
```

**Features demonstrated:**
- VPC and subnet utilization analysis with IP capacity planning
- Multi-CIDR VPC support and comprehensive network mapping
- Resource-to-network context mapping with enrichment
- Network optimization recommendations and cost savings identification
- Security posture assessment and vulnerability detection
- Integration with service enrichment and state management

## Output Files

After running the tools, you'll find timestamped output files here:

### Core Tool Outputs
- `basic_inventory_YYYYMMDD_HHMMSS.json` - Complete resource inventory
- `untagged_check_YYYYMMDD_HHMMSS.json` - Resources without tags
- `resource_report.xlsx` - Excel report with service-specific sheets

### State Management Outputs
- `demo_state/` - State storage directory with metadata and snapshots
  - `metadata.json` - State index and metadata tracking
  - `state_YYYYMMDD_HHMMSS.json` - Individual state snapshots
- `demo_export.json` - Exported state data for CI/CD integration
- `changes_report.md` - Generated changelog in Markdown format
- `changes_report.html` - Generated changelog in HTML format

## Common Usage Patterns

### Core Tool Usage

#### Monthly Resource Audit
```bash
python scripts/aws_resource_inventory.py --export-excel --output examples/monthly_audit
```

#### Tag Compliance Check
```bash
python scripts/tag_compliance_checker.py --config config/tag_policy_example.yaml --output examples/compliance_check
```

#### Custom Region Scan
```bash
python scripts/aws_resource_inventory.py --regions us-east-1 eu-west-1 --output examples/custom_regions
```

#### S3 Upload
```bash
python scripts/aws_resource_inventory.py --s3-bucket my-reports-bucket --s3-key monthly/$(date +%Y-%m)/inventory.json
```

### Service Enrichment Usage

#### Basic Service Enrichment
```bash
# Enrich resources with service-specific attributes
python -c "
from inventag import AWSResourceInventory
from inventag.discovery.service_enrichment import ServiceAttributeEnricher

# Discover resources
inventory = AWSResourceInventory(regions=['us-east-1'])
resources = inventory.discover_resources()

# Enrich with service-specific attributes
enricher = ServiceAttributeEnricher()
enriched_resources = enricher.enrich_resources_with_attributes(resources)

# Get enrichment statistics
stats = enricher.get_enrichment_statistics()
print(f'Total resources: {stats[\"statistics\"][\"total_resources\"]}')
print(f'Successfully enriched: {stats[\"statistics\"][\"enriched_resources\"]}')
print(f'Discovered services: {stats[\"discovered_services\"]}')
"
```

#### Service-Specific Analysis
```bash
# Analyze S3 buckets with detailed configuration
python -c "
from inventag import AWSResourceInventory
from inventag.discovery.service_enrichment import ServiceAttributeEnricher

inventory = AWSResourceInventory(regions=['us-east-1'])
resources = inventory.discover_resources()

enricher = ServiceAttributeEnricher()
s3_resources = [r for r in resources if r.get('service') == 'S3']
enriched_s3 = enricher.enrich_resources_with_attributes(s3_resources)

for bucket in enriched_s3:
    if 'service_attributes' in bucket:
        attrs = bucket['service_attributes']
        print(f'Bucket: {bucket[\"name\"]}')
        print(f'  Encryption: {attrs.get(\"encryption\", {})}')
        print(f'  Versioning: {attrs.get(\"versioning_status\", \"Unknown\")}')
        print(f'  Public Access Block: {bool(attrs.get(\"public_access_block\"))}')
"
```

#### Integration with Compliance Checking
```bash
# Enhanced compliance analysis with enriched attributes
python -c "
from inventag import AWSResourceInventory, ComprehensiveTagComplianceChecker
from inventag.discovery.service_enrichment import ServiceAttributeEnricher

# Discover and enrich resources
inventory = AWSResourceInventory(regions=['us-east-1'])
resources = inventory.discover_resources()

enricher = ServiceAttributeEnricher()
enriched_resources = enricher.enrich_resources_with_attributes(resources)

# Run compliance check on enriched data
checker = ComprehensiveTagComplianceChecker(
    regions=['us-east-1'],
    config_file='config/tag_policy_example.yaml'
)
compliance_results = checker.check_compliance(enriched_resources)

# Enhanced analysis with service-specific insights
for resource in compliance_results['non_compliant_resources']:
    if 'service_attributes' in resource:
        print(f'Non-compliant {resource[\"service\"]}: {resource[\"name\"]}')
        if resource['service'] == 'S3':
            attrs = resource['service_attributes']
            if not attrs.get('encryption'):
                print('  - Missing encryption configuration')
        elif resource['service'] == 'RDS':
            attrs = resource['service_attributes']
            if not attrs.get('storage_encrypted', False):
                print('  - Database storage not encrypted')
"
```

### Network Analysis Usage

#### Basic Network Analysis
```bash
# Analyze VPC and subnet utilization
python -c "
from inventag import AWSResourceInventory
from inventag.discovery.network_analyzer import NetworkAnalyzer

# Discover resources
inventory = AWSResourceInventory(regions=['us-east-1'])
resources = inventory.discover_resources()

# Analyze network infrastructure
analyzer = NetworkAnalyzer()
vpc_analysis = analyzer.analyze_vpc_resources(resources)
network_summary = analyzer.generate_network_summary(vpc_analysis)

print(f'Total VPCs: {network_summary.total_vpcs}')
print(f'Total Subnets: {network_summary.total_subnets}')
print(f'Total Available IPs: {network_summary.total_available_ips}')
print(f'Highest Utilization: {network_summary.highest_utilization_percentage:.1f}%')
"
```

#### Capacity Planning and Monitoring
```bash
# Monitor network capacity and identify high-utilization subnets
python -c "
from inventag import AWSResourceInventory
from inventag.discovery.network_analyzer import NetworkAnalyzer

inventory = AWSResourceInventory(regions=['us-east-1'])
resources = inventory.discover_resources()

analyzer = NetworkAnalyzer()
vpc_analysis = analyzer.analyze_vpc_resources(resources)

# Check for high utilization
for vpc_id, vpc in vpc_analysis.items():
    print(f'VPC: {vpc.vpc_name} ({vpc.utilization_percentage:.1f}% utilized)')
    
    for subnet in vpc.subnets:
        if subnet.utilization_percentage > 80:
            print(f'  ⚠️  HIGH: {subnet.subnet_name} - {subnet.utilization_percentage:.1f}%')
            print(f'      {subnet.available_ips} IPs remaining')
"
```

#### Network-Enriched Resource Analysis
```bash
# Enrich resources with network context
python -c "
from inventag import AWSResourceInventory
from inventag.discovery.network_analyzer import NetworkAnalyzer

inventory = AWSResourceInventory(regions=['us-east-1'])
resources = inventory.discover_resources()

analyzer = NetworkAnalyzer()
enriched_resources = analyzer.map_resources_to_network(resources)

# Analyze resources by network context
for resource in enriched_resources:
    if 'vpc_name' in resource:
        print(f'{resource[\"service\"]} {resource[\"name\"]} in VPC {resource[\"vpc_name\"]}')
        if 'subnet_utilization_percentage' in resource:
            print(f'  Subnet utilization: {resource[\"subnet_utilization_percentage\"]:.1f}%')
"
```

### State Management Usage

#### Continuous State Tracking
```bash
# Run daily to build state history
python -c "
from inventag.state import StateManager
from inventag.discovery import AWSResourceInventory

# Discover current resources
inventory = AWSResourceInventory()
resources = inventory.discover_resources()

# Save state with metadata
state_manager = StateManager(state_dir='daily_states')
state_id = state_manager.save_state(
    resources=resources,
    account_id='123456789012',
    regions=['us-east-1', 'us-west-2'],
    tags={'purpose': 'daily-tracking', 'environment': 'production'}
)
print(f'State saved: {state_id}')
"
```

#### Change Detection Workflow
```bash
# Compare yesterday's state with today's
python -c "
from inventag.state import StateManager, DeltaDetector

state_manager = StateManager(state_dir='daily_states')
states = state_manager.list_states(limit=2)

if len(states) >= 2:
    detector = DeltaDetector()
    comparison = state_manager.get_state_comparison_data(
        states[1]['state_id'], states[0]['state_id']
    )
    
    delta_report = detector.detect_changes(
        old_resources=comparison['state1']['resources'],
        new_resources=comparison['state2']['resources'],
        state1_id=states[1]['state_id'],
        state2_id=states[0]['state_id']
    )
    
    print(f'Changes detected: {delta_report.summary[\"total_changes\"]}')
    print(f'Added: {delta_report.summary[\"added_count\"]}')
    print(f'Removed: {delta_report.summary[\"removed_count\"]}')
    print(f'Modified: {delta_report.summary[\"modified_count\"]}')
"
```

#### Automated Change Reports
```bash
# Generate weekly change summary
python -c "
from inventag.state import StateManager, DeltaDetector, ChangelogGenerator
from datetime import datetime, timedelta

state_manager = StateManager(state_dir='daily_states')
detector = DeltaDetector()
changelog_gen = ChangelogGenerator()

# Get states from last week
states = state_manager.list_states()
week_ago_states = [s for s in states if 
    (datetime.now() - datetime.strptime(s['state_id'], '%Y%m%d_%H%M%S')).days == 7
]

if week_ago_states:
    comparison = state_manager.get_state_comparison_data(
        week_ago_states[0]['state_id'], states[0]['state_id']
    )
    
    delta_report = detector.detect_changes(
        old_resources=comparison['state1']['resources'],
        new_resources=comparison['state2']['resources'],
        state1_id=week_ago_states[0]['state_id'],
        state2_id=states[0]['state_id']
    )
    
    changelog = changelog_gen.generate_changelog(
        delta_report, format='markdown', include_details=True
    )
    
    changelog_gen.export_changelog(changelog, 'weekly_changes.md')
    print('Weekly change report generated: weekly_changes.md')
"
```

## Pro Tips

### Core Tools
- **Timestamped files**: All outputs include timestamps for easy tracking
- **Excel reports**: Use the BOM converter for professional Excel reports with service sheets
- **VPC enrichment**: Excel reports automatically include VPC and subnet names
- **Compliance tracking**: Tag compliance reports show exactly which resources need attention

### Service Enrichment
- **Selective enrichment**: Only enrich resources that need detailed analysis to improve performance
- **Batch processing**: Process resources in batches for large environments
- **Cache management**: Monitor and clear caches periodically to prevent memory issues
- **Custom handlers**: Develop custom handlers for proprietary or specialized services
- **Integration benefits**: Use enriched data for enhanced compliance analysis and change detection
- **Performance monitoring**: Track enrichment success rates and adjust strategies accordingly

### State Management
- **Regular snapshots**: Take daily snapshots to build comprehensive change history
- **Meaningful tags**: Use descriptive tags when saving states for easy identification
- **Change thresholds**: Set up alerting based on change counts or severity levels
- **Retention policies**: Configure appropriate retention based on your compliance requirements
- **Export integration**: Use state exports for CI/CD pipeline integration and automated reporting

## Integration Examples

### Daily Change Monitoring
```bash
#!/bin/bash
# daily_change_monitor.sh - Add to cron for daily execution

# Run discovery and save state
python -c "
from inventag import AWSResourceInventory
from inventag.state import StateManager, DeltaDetector, ChangelogGenerator

# Discover current resources
inventory = AWSResourceInventory()
resources = inventory.discover_resources()

# Save current state
state_manager = StateManager(state_dir='daily_states')
current_state_id = state_manager.save_state(
    resources=resources,
    account_id='123456789012',
    regions=['us-east-1', 'us-west-2'],
    tags={'purpose': 'daily-monitoring', 'automated': 'true'}
)

# Compare with yesterday if available
states = state_manager.list_states(limit=2)
if len(states) >= 2:
    comparison = state_manager.get_state_comparison_data(
        states[1]['state_id'], states[0]['state_id']
    )
    
    detector = DeltaDetector()
    delta_report = detector.detect_changes(
        old_resources=comparison['state1']['resources'],
        new_resources=comparison['state2']['resources'],
        state1_id=states[1]['state_id'],
        state2_id=states[0]['state_id']
    )
    
    # Generate report if changes detected
    if delta_report.summary['total_changes'] > 0:
        generator = ChangelogGenerator()
        changelog = generator.generate_changelog(
            delta_report=delta_report,
            format='markdown',
            include_details=True
        )
        generator.export_changelog(changelog, f'daily_changes_{current_state_id}.md')
        print(f'Changes detected: {delta_report.summary[\"total_changes\"]}')
    else:
        print('No changes detected')
else:
    print('Baseline state saved')
"
```

### Weekly Executive Summary
```bash
#!/bin/bash
# weekly_executive_summary.sh - Generate weekly change summary

python -c "
from inventag.state import StateManager, DeltaDetector, ChangelogGenerator
from datetime import datetime, timedelta

state_manager = StateManager(state_dir='daily_states')
states = state_manager.list_states()

# Find state from 7 days ago
target_date = datetime.now() - timedelta(days=7)
week_ago_state = None

for state in states:
    state_date = datetime.strptime(state['state_id'], '%Y%m%d_%H%M%S')
    if abs((state_date - target_date).days) <= 1:  # Within 1 day tolerance
        week_ago_state = state
        break

if week_ago_state and len(states) > 0:
    comparison = state_manager.get_state_comparison_data(
        week_ago_state['state_id'], states[0]['state_id']
    )
    
    detector = DeltaDetector()
    delta_report = detector.detect_changes(
        old_resources=comparison['state1']['resources'],
        new_resources=comparison['state2']['resources'],
        state1_id=week_ago_state['state_id'],
        state2_id=states[0]['state_id']
    )
    
    generator = ChangelogGenerator()
    executive_summary = generator.generate_executive_summary(delta_report)
    generator.export_changelog(executive_summary, 'weekly_executive_summary.md')
    print('Weekly executive summary generated')
else:
    print('Insufficient data for weekly comparison')
"
```

## Getting Started

### Quick Start - All Features
1. **Run the comprehensive demo** to see all capabilities:
   ```bash
   ./examples/quick_start.sh
   ```

2. **Explore individual features** with dedicated demos:
   ```bash
   python examples/service_enrichment_demo.py    # Service attribute enrichment
   python examples/state_manager_demo.py         # State persistence and tracking
   python examples/delta_detector_demo.py        # Change detection and analysis
   python examples/changelog_generator_demo.py   # Professional change reports
   ```

### Service Enrichment Setup
1. **Basic enrichment** for enhanced resource analysis:
   ```bash
   # Test service enrichment with your AWS resources
   python -c "
   from inventag import AWSResourceInventory
   from inventag.discovery.service_enrichment import ServiceAttributeEnricher
   
   inventory = AWSResourceInventory(regions=['us-east-1'])
   resources = inventory.discover_resources()
   
   enricher = ServiceAttributeEnricher()
   enriched = enricher.enrich_resources_with_attributes(resources)
   
   stats = enricher.get_enrichment_statistics()
   print(f'Enriched {stats[\"statistics\"][\"enriched_resources\"]} resources')
   "
   ```

2. **Integrate with existing workflows** by adding enrichment to your current scripts

3. **Develop custom handlers** for specialized services using the framework

### State Management Setup
1. **Initialize state tracking** for your environment:
   ```bash
   # Create baseline state
   python -c "
   from inventag import AWSResourceInventory
   from inventag.state import StateManager
   
   inventory = AWSResourceInventory()
   resources = inventory.discover_resources()
   
   state_manager = StateManager(state_dir='production_states')
   state_id = state_manager.save_state(
       resources=resources,
       account_id='YOUR_ACCOUNT_ID',
       regions=['us-east-1', 'us-west-2'],
       tags={'purpose': 'baseline', 'environment': 'production'}
   )
   print(f'Baseline state saved: {state_id}')
   "
   ```

2. **Set up daily monitoring** using the integration examples above

3. **Configure retention policies** based on your compliance requirements

4. **Integrate with your CI/CD pipeline** using the state export capabilities

5. **Set up alerting** based on change thresholds and severity levels

### Documentation References
- **Network Analysis**: [`docs/NETWORK_ANALYSIS.md`](../docs/NETWORK_ANALYSIS.md) - Comprehensive VPC/subnet analysis and capacity planning
- **Service Enrichment**: [`docs/SERVICE_ENRICHMENT.md`](../docs/SERVICE_ENRICHMENT.md) - Deep service attribute extraction
- **State Management**: [`docs/STATE_MANAGEMENT.md`](../docs/STATE_MANAGEMENT.md) - Comprehensive change tracking
- **Security**: [`docs/SECURITY.md`](../docs/SECURITY.md) - Security considerations and permissions