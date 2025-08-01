# CI/CD Integration Guide

This guide covers the comprehensive CI/CD integration capabilities of InvenTag, including automated BOM generation, compliance gates, S3 document storage, notifications, and monitoring.

## Overview

The `CICDIntegration` class provides a complete solution for integrating InvenTag into your CI/CD pipelines with:

- **Automated BOM Generation**: Multi-account resource discovery and document generation
- **Compliance Gates**: Configurable compliance thresholds that can fail builds
- **S3 Document Storage**: Automated upload of generated documents with lifecycle management
- **Multi-Channel Notifications**: Slack, Teams, and email notifications with document links
- **Prometheus Metrics**: Comprehensive metrics export for monitoring and alerting
- **Pipeline Artifacts**: JSON artifacts for downstream pipeline consumption

## Quick Start

### CLI Script (Recommended)

The easiest way to use InvenTag CI/CD integration is through the provided CLI script:

```bash
# Basic multi-account BOM generation
python scripts/cicd_bom_generation.py \
  --accounts-file examples/accounts_basic.json \
  --formats excel word

# Full CI/CD integration with S3, notifications, and monitoring
python scripts/cicd_bom_generation.py \
  --accounts-file examples/accounts_cicd_environment.json \
  --formats excel word json \
  --s3-bucket my-compliance-bucket \
  --compliance-threshold 80 \
  --fail-on-security-issues \
  --slack-webhook https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK \
  --prometheus-gateway http://prometheus-pushgateway:9091 \
  --verbose
```

**📁 Complete configuration examples are available in:**
- `examples/accounts_basic.json` - Basic multi-account setup
- `examples/accounts_cicd_environment.json` - CI/CD environment setup
- `examples/accounts_cross_account_roles.json` - Enterprise cross-account roles
- `examples/cicd_config_complete.json` - All CI/CD configuration options
- `docs/CONFIGURATION_EXAMPLES.md` - Comprehensive documentation

### Programmatic Integration

```python
from inventag.core.cicd_integration import CICDIntegration, S3UploadConfig, ComplianceGateConfig
from inventag.core.cloud_bom_generator import CloudBOMGenerator

# Configure S3 upload
s3_config = S3UploadConfig(
    bucket_name="my-compliance-bucket",
    key_prefix="bom-reports",
    region="us-east-1"
)

# Configure compliance gate
compliance_config = ComplianceGateConfig(
    minimum_compliance_percentage=80.0,
    fail_on_security_issues=True
)

# Initialize CI/CD integration
cicd = CICDIntegration(
    s3_config=s3_config,
    compliance_gate_config=compliance_config
)

# Create BOM generator
generator = CloudBOMGenerator.from_credentials_file("examples/accounts_basic.json")

# Execute pipeline integration
result = cicd.execute_pipeline_integration(
    bom_generator=generator,
    output_formats=["excel", "word", "json"],
    upload_to_s3=True,
    send_notifications=True,
    export_metrics=True
)

# Check results
if result.success and result.compliance_gate_passed:
    print("✅ Pipeline completed successfully")
    print(f"Documents uploaded: {list(result.s3_uploads.keys())}")
else:
    print("❌ Pipeline failed")
    if not result.compliance_gate_passed:
        print("Compliance gate failed")
    exit(1)
```

## Configuration Components

### S3UploadConfig

Configures automated document upload to S3 with comprehensive storage options.

```python
from inventag.core.cicd_integration import S3UploadConfig

s3_config = S3UploadConfig(
    bucket_name="compliance-reports",           # Required: S3 bucket name
    key_prefix="inventag-bom",                  # S3 key prefix for organization
    region="us-east-1",                         # AWS region
    encryption="AES256",                        # Encryption: AES256 or aws:kms
    kms_key_id=None,                           # KMS key ID for aws:kms encryption
    public_read=False,                         # Whether to make objects public
    lifecycle_days=90,                         # Lifecycle policy (days)
    storage_class="STANDARD"                   # Storage class: STANDARD, STANDARD_IA, GLACIER
)
```

**Advanced S3 Configuration:**

```python
# KMS encryption with custom key
s3_config = S3UploadConfig(
    bucket_name="secure-compliance-bucket",
    key_prefix="bom-reports",
    region="us-west-2",
    encryption="aws:kms",
    kms_key_id="arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012",
    lifecycle_days=30,
    storage_class="STANDARD_IA"
)

# Public read access for shared reports
s3_config = S3UploadConfig(
    bucket_name="public-compliance-reports",
    key_prefix="public-bom",
    public_read=True,
    lifecycle_days=7  # Short retention for public access
)
```

### ComplianceGateConfig

Configures compliance validation thresholds that can control pipeline execution.

```python
from inventag.core.cicd_integration import ComplianceGateConfig

compliance_config = ComplianceGateConfig(
    minimum_compliance_percentage=80.0,        # Minimum compliance % to pass
    critical_violations_threshold=0,           # Max critical violations allowed
    required_tags=["Environment", "Owner"],    # Tags that must be present
    allowed_non_compliant_services=[],         # Services exempt from compliance
    fail_on_security_issues=True,             # Fail on security violations
    fail_on_network_issues=False              # Fail on network issues
)
```

**Compliance Gate Examples:**

```python
# Strict compliance for production
strict_compliance = ComplianceGateConfig(
    minimum_compliance_percentage=95.0,
    critical_violations_threshold=0,
    required_tags=["Environment", "Owner", "CostCenter", "Project"],
    fail_on_security_issues=True,
    fail_on_network_issues=True
)

# Lenient compliance for development
dev_compliance = ComplianceGateConfig(
    minimum_compliance_percentage=60.0,
    critical_violations_threshold=5,
    required_tags=["Environment"],
    allowed_non_compliant_services=["CloudTrail", "Config"],
    fail_on_security_issues=False,
    fail_on_network_issues=False
)
```

### NotificationConfig

Configures multi-channel notifications with rich content and document links.

```python
from inventag.core.cicd_integration import NotificationConfig

notification_config = NotificationConfig(
    slack_webhook_url="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
    teams_webhook_url="https://outlook.office.com/webhook/YOUR/TEAMS/WEBHOOK",
    email_recipients=["compliance@company.com", "devops@company.com"],
    include_summary=True,                      # Include execution summary
    include_document_links=True,               # Include S3 document links
    notify_on_success=True,                    # Send success notifications
    notify_on_failure=True                     # Send failure notifications
)
```

## Pipeline Integration Patterns

### GitHub Actions Integration

**Daily Compliance Report:**

```yaml
name: Daily Multi-Account BOM Generation
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  workflow_dispatch:

jobs:
  generate-bom:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Generate Multi-Account BOM
      run: |
        python scripts/cicd_bom_generation.py \
          --accounts-file accounts.json \
          --s3-bucket ${{ secrets.S3_BUCKET }} \
          --s3-key-prefix daily-reports \
          --slack-webhook ${{ secrets.SLACK_WEBHOOK }} \
          --compliance-threshold 80 \
          --formats excel word json
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

**Compliance Gate for Pull Requests:**

```yaml
name: Compliance Gate Check
on: [pull_request]

jobs:
  compliance-gate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Run Compliance Gate
      run: |
        python -c "
        from inventag.core.cicd_integration import CICDIntegration, ComplianceGateConfig
        from inventag.core.cloud_bom_generator import CloudBOMGenerator
        
        # Configure strict compliance gate for PR checks
        compliance_config = ComplianceGateConfig(
            minimum_compliance_percentage=85.0,
            critical_violations_threshold=0,
            required_tags=['Environment', 'Owner'],
            fail_on_security_issues=True
        )
        
        cicd = CICDIntegration(compliance_gate_config=compliance_config)
        generator = CloudBOMGenerator.from_credentials_file('accounts.json')
        
        result = cicd.execute_pipeline_integration(
            bom_generator=generator,
            upload_to_s3=False,  # Don't upload for PR checks
            send_notifications=False
        )
        
        if not result.compliance_gate_passed:
            print('❌ Compliance gate failed - PR blocked')
            exit(1)
        else:
            print('✅ Compliance gate passed - PR approved')
        "
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### AWS CodeBuild Integration

**buildspec.yml for CodeBuild:**

```yaml
version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.10
    commands:
      - pip install -r requirements.txt
  
  build:
    commands:
      - echo "Starting multi-account BOM generation"
      - |
        python -c "
        import os
        from inventag.core.cicd_integration import CICDIntegration, S3UploadConfig, ComplianceGateConfig, NotificationConfig
        from inventag.core.cloud_bom_generator import CloudBOMGenerator
        
        # Configure from environment variables
        s3_config = S3UploadConfig(
            bucket_name=os.environ['S3_BUCKET'],
            key_prefix=f'codebuild-reports/{os.environ['CODEBUILD_BUILD_ID']}',
            region=os.environ['AWS_DEFAULT_REGION']
        )
        
        compliance_config = ComplianceGateConfig(
            minimum_compliance_percentage=float(os.environ.get('COMPLIANCE_THRESHOLD', '80')),
            fail_on_security_issues=True
        )
        
        notification_config = NotificationConfig(
            slack_webhook_url=os.environ.get('SLACK_WEBHOOK'),
            notify_on_success=True,
            notify_on_failure=True
        )
        
        # Execute pipeline
        cicd = CICDIntegration(s3_config, compliance_config, notification_config)
        generator = CloudBOMGenerator.from_credentials_file('accounts.json')
        
        result = cicd.execute_pipeline_integration(
            bom_generator=generator,
            output_formats=['excel', 'word', 'json'],
            upload_to_s3=True,
            send_notifications=True,
            export_metrics=True
        )
        
        # Export results for CodeBuild
        with open('pipeline_result.json', 'w') as f:
            import json
            json.dump({
                'success': result.success,
                'compliance_gate_passed': result.compliance_gate_passed,
                'documents_generated': len(result.generated_documents),
                's3_uploads': result.s3_uploads,
                'execution_time': result.execution_time_seconds
            }, f, indent=2)
        
        if not result.success or not result.compliance_gate_passed:
            exit(1)
        "

artifacts:
  files:
    - pipeline_result.json
    - artifacts/*.json
  name: bom-generation-artifacts
```

## Prometheus Metrics

The CI/CD integration automatically exports comprehensive metrics for monitoring:

### Core Metrics

```prometheus
# Resource metrics
inventag_total_resources{account_id="123456789012"} 1250
inventag_compliant_resources{account_id="123456789012"} 1000
inventag_non_compliant_resources{account_id="123456789012"} 250
inventag_compliance_percentage{account_id="123456789012"} 80.0

# Processing metrics
inventag_processing_time_seconds{account_id="123456789012"} 45.2
inventag_successful_accounts 3
inventag_failed_accounts 0
inventag_total_accounts 3

# Security and network metrics
inventag_security_issues{account_id="123456789012"} 5
inventag_network_issues{account_id="123456789012"} 2

# Document generation metrics
inventag_document_generation_time_seconds{format="excel"} 12.3
inventag_document_generation_time_seconds{format="word"} 8.7
inventag_s3_upload_time_seconds 3.2
```

### Grafana Dashboard Example

```json
{
  "dashboard": {
    "title": "InvenTag Compliance Monitoring",
    "panels": [
      {
        "title": "Compliance Percentage by Account",
        "type": "stat",
        "targets": [
          {
            "expr": "inventag_compliance_percentage",
            "legendFormat": "{{account_id}}"
          }
        ]
      },
      {
        "title": "Security Issues Trend",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(inventag_security_issues)",
            "legendFormat": "Total Security Issues"
          }
        ]
      },
      {
        "title": "Processing Time by Account",
        "type": "heatmap",
        "targets": [
          {
            "expr": "inventag_processing_time_seconds",
            "legendFormat": "{{account_id}}"
          }
        ]
      }
    ]
  }
}
```

## Notification Examples

### Slack Notification Format

```json
{
  "text": "InvenTag Multi-Account BOM Generation Complete",
  "attachments": [
    {
      "color": "good",
      "fields": [
        {
          "title": "Status",
          "value": "SUCCESS",
          "short": true
        },
        {
          "title": "Compliance Gate",
          "value": "PASSED",
          "short": true
        },
        {
          "title": "Accounts",
          "value": "3/3 successful",
          "short": true
        },
        {
          "title": "Resources",
          "value": "1,250 (80.0% compliant)",
          "short": true
        },
        {
          "title": "Execution Time",
          "value": "45.2s",
          "short": true
        },
        {
          "title": "Documents Generated",
          "value": "3",
          "short": true
        }
      ],
      "footer": "InvenTag CI/CD Integration"
    },
    {
      "color": "good",
      "title": "Generated Documents",
      "text": "• EXCEL: <https://bucket.s3.amazonaws.com/reports/report.xlsx|Download>\n• WORD: <https://bucket.s3.amazonaws.com/reports/report.docx|Download>\n• JSON: <https://bucket.s3.amazonaws.com/reports/report.json|Download>"
    }
  ]
}
```

### Teams Notification Format

```json
{
  "@type": "MessageCard",
  "@context": "http://schema.org/extensions",
  "themeColor": "00FF00",
  "summary": "InvenTag Multi-Account BOM Generation Complete",
  "sections": [
    {
      "activityTitle": "InvenTag Multi-Account BOM Generation Complete",
      "activitySubtitle": "Status: SUCCESS | Compliance Gate: PASSED",
      "facts": [
        {
          "name": "Total Accounts",
          "value": "3"
        },
        {
          "name": "Successful Accounts",
          "value": "3"
        },
        {
          "name": "Total Resources",
          "value": "1,250"
        },
        {
          "name": "Compliance Percentage",
          "value": "80.0%"
        },
        {
          "name": "Execution Time",
          "value": "45.2s"
        },
        {
          "name": "Documents Generated",
          "value": "3"
        }
      ]
    }
  ],
  "potentialAction": [
    {
      "@type": "OpenUri",
      "name": "Download Excel Report",
      "targets": [
        {
          "os": "default",
          "uri": "https://bucket.s3.amazonaws.com/reports/report.xlsx"
        }
      ]
    }
  ]
}
```

## Pipeline Artifacts

The CI/CD integration generates JSON artifacts for downstream pipeline consumption:

### pipeline_summary.json

```json
{
  "execution_timestamp": "2024-01-15T10:30:00Z",
  "success": true,
  "compliance_gate_passed": true,
  "execution_time_seconds": 45.2,
  "generated_documents": 3,
  "s3_uploads": 3,
  "notifications_sent": 2,
  "total_accounts": 3,
  "successful_accounts": 3,
  "failed_accounts": 0,
  "total_resources": 1250
}
```

### compliance_gate.json

```json
{
  "passed": true,
  "configuration": {
    "minimum_compliance_percentage": 80.0,
    "critical_violations_threshold": 0,
    "required_tags": ["Environment", "Owner"],
    "fail_on_security_issues": true,
    "fail_on_network_issues": false
  },
  "results": {
    "total_resources": 1250,
    "compliant_resources": 1000,
    "non_compliant_resources": 250,
    "compliance_percentage": 80.0,
    "critical_violations": 0,
    "security_issues": 5,
    "network_issues": 2
  }
}
```

### s3_links.json

```json
{
  "bucket": "compliance-reports",
  "region": "us-east-1",
  "documents": {
    "excel": "https://compliance-reports.s3.us-east-1.amazonaws.com/bom-reports/20240115_103000/report.xlsx",
    "word": "https://compliance-reports.s3.us-east-1.amazonaws.com/bom-reports/20240115_103000/report.docx",
    "json": "https://compliance-reports.s3.us-east-1.amazonaws.com/bom-reports/20240115_103000/report.json"
  },
  "upload_timestamp": "2024-01-15T10:30:45Z"
}
```

### account_summary.json

```json
{
  "total_accounts": 3,
  "accounts": [
    {
      "account_id": "123456789012",
      "account_name": "Production Account",
      "resource_count": 850,
      "processing_time_seconds": 32.1,
      "error_count": 0,
      "accessible_regions": ["us-east-1", "us-west-2"],
      "discovered_services": ["EC2", "S3", "RDS", "Lambda"]
    },
    {
      "account_id": "123456789013",
      "account_name": "Development Account",
      "resource_count": 250,
      "processing_time_seconds": 8.3,
      "error_count": 0,
      "accessible_regions": ["us-east-1"],
      "discovered_services": ["EC2", "S3", "Lambda"]
    },
    {
      "account_id": "123456789014",
      "account_name": "Staging Account",
      "resource_count": 150,
      "processing_time_seconds": 4.8,
      "error_count": 0,
      "accessible_regions": ["us-east-1"],
      "discovered_services": ["EC2", "S3"]
    }
  ]
}
```

## Error Handling and Troubleshooting

### Common Issues

**1. S3 Upload Failures**
```python
# Check S3 permissions and bucket configuration
try:
    result = cicd.execute_pipeline_integration(...)
    if not result.s3_uploads:
        print("S3 upload failed - check bucket permissions")
except Exception as e:
    if "AccessDenied" in str(e):
        print("S3 bucket access denied - verify IAM permissions")
    elif "NoSuchBucket" in str(e):
        print("S3 bucket does not exist - create bucket first")
```

**2. Compliance Gate Failures**
```python
# Debug compliance gate failures
result = cicd.execute_pipeline_integration(...)
if not result.compliance_gate_passed:
    print("Compliance gate failed:")
    print(f"- Compliance percentage: {result.metrics.compliance_percentage}%")
    print(f"- Security issues: {result.metrics.security_issues}")
    print(f"- Network issues: {result.metrics.network_issues}")
```

**3. Notification Failures**
```python
# Check notification configuration
if not result.notifications_sent:
    print("No notifications sent - check webhook URLs and configuration")
    # Test webhook connectivity
    import requests
    response = requests.post(notification_config.slack_webhook_url, 
                           json={"text": "Test message"})
    print(f"Webhook test status: {response.status_code}")
```

### Debugging Tips

1. **Enable Debug Logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check AWS Permissions**:
   ```bash
   aws sts get-caller-identity
   aws s3 ls s3://your-bucket-name
   ```

3. **Validate Configuration**:
   ```python
   # Test S3 configuration
   s3_client = boto3.client('s3', region_name=s3_config.region)
   s3_client.head_bucket(Bucket=s3_config.bucket_name)
   ```

4. **Monitor Execution Time**:
   ```python
   # Set reasonable timeouts for large accounts
   result = cicd.execute_pipeline_integration(
       bom_generator=generator,
       # ... other parameters
   )
   print(f"Execution time: {result.execution_time_seconds}s")
   ```

## Best Practices

### Security

1. **Use IAM Roles**: Prefer IAM roles over access keys in CI/CD environments
2. **Encrypt S3 Objects**: Always use encryption for sensitive compliance data
3. **Secure Webhooks**: Use HTTPS webhooks and validate webhook signatures
4. **Limit Permissions**: Use least-privilege IAM policies

### Performance

1. **Parallel Processing**: Enable parallel account processing for large environments
2. **Regional Optimization**: Limit regions to reduce processing time
3. **Service Filtering**: Filter services to focus on compliance-critical resources
4. **Caching**: Use state management to avoid redundant processing

### Reliability

1. **Error Handling**: Implement comprehensive error handling and retries
2. **Monitoring**: Set up alerts on compliance gate failures
3. **Backup Storage**: Use multiple S3 regions for document storage
4. **Graceful Degradation**: Continue processing even if some accounts fail

### Cost Optimization

1. **Lifecycle Policies**: Configure S3 lifecycle policies for cost management
2. **Storage Classes**: Use appropriate S3 storage classes for retention requirements
3. **Regional Placement**: Store documents in cost-effective regions
4. **Cleanup**: Implement automated cleanup of old reports and artifacts

## Advanced Configuration

### Custom Metrics Export

```python
from inventag.core.cicd_integration import PrometheusMetrics

# Create custom metrics
custom_metrics = PrometheusMetrics(
    total_resources=1500,
    compliant_resources=1200,
    compliance_percentage=80.0,
    processing_time_seconds=60.0,
    # ... other metrics
)

# Export to custom endpoint
cicd._export_prometheus_metrics(custom_metrics, endpoint="http://pushgateway:9091")
```

### Multi-Environment Configuration

```python
# Environment-specific configurations
environments = {
    "production": {
        "compliance_threshold": 95.0,
        "s3_bucket": "prod-compliance-reports",
        "notification_channels": ["slack", "email"],
        "required_tags": ["Environment", "Owner", "CostCenter", "Project"]
    },
    "staging": {
        "compliance_threshold": 85.0,
        "s3_bucket": "staging-compliance-reports", 
        "notification_channels": ["slack"],
        "required_tags": ["Environment", "Owner"]
    },
    "development": {
        "compliance_threshold": 70.0,
        "s3_bucket": "dev-compliance-reports",
        "notification_channels": [],
        "required_tags": ["Environment"]
    }
}

# Select configuration based on environment
env = os.environ.get("ENVIRONMENT", "development")
config = environments[env]

compliance_config = ComplianceGateConfig(
    minimum_compliance_percentage=config["compliance_threshold"],
    required_tags=config["required_tags"]
)
```

This comprehensive CI/CD integration system enables seamless automation of compliance monitoring and BOM generation across your entire AWS infrastructure.

## Complete Configuration Reference

For comprehensive configuration examples and documentation, see:

### 📁 Configuration Files
- **`examples/accounts_basic.json`** - Basic multi-account configuration
- **`examples/accounts_cicd_environment.json`** - CI/CD environment setup
- **`examples/accounts_with_profiles.json`** - AWS CLI profiles configuration
- **`examples/accounts_cross_account_roles.json`** - Enterprise cross-account roles
- **`examples/cicd_config_complete.json`** - Complete CI/CD configuration options

### 🚀 CI/CD Platform Examples
- **`examples/github_actions_cicd_example.yml`** - Complete GitHub Actions workflow
- **`examples/jenkins_pipeline.groovy`** - Jenkins pipeline configuration
- **`examples/aws_codebuild_buildspec.yml`** - AWS CodeBuild buildspec
- **`examples/docker_compose_cicd.yml`** - Docker Compose setup

### 📊 Monitoring and Alerting
- **`examples/prometheus.yml`** - Prometheus configuration
- **`examples/inventag_alerts.yml`** - Alerting rules
- **`examples/docker_compose_cicd.yml`** - Complete monitoring stack

### 📖 Documentation
- **`docs/CONFIGURATION_EXAMPLES.md`** - Comprehensive configuration guide with all examples
- **`scripts/cicd_bom_generation.py --help`** - CLI help with all options

### 🔧 CLI Script
The `scripts/cicd_bom_generation.py` script provides a complete command-line interface for all CI/CD integration features. Use `--help` to see all available options, or `--dry-run` to validate your configuration without execution.

**Never reverse engineer configuration formats** - all examples are provided and documented!