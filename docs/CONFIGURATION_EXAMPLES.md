# InvenTag Configuration Examples

This document provides comprehensive configuration examples for all InvenTag features. You should never need to reverse engineer configuration formats - everything is documented here with working examples.

## Table of Contents

1. [Account Configuration Files](#account-configuration-files)
2. [CI/CD Integration Configuration](#cicd-integration-configuration)
3. [CLI Usage Examples](#cli-usage-examples)
4. [CI/CD Platform Integration](#cicd-platform-integration)
5. [Monitoring and Alerting](#monitoring-and-alerting)
6. [Environment Variables](#environment-variables)
7. [Docker and Container Deployment](#docker-and-container-deployment)
8. [Security Best Practices](#security-best-practices)

## 🔐 Security First

**Before using any configuration examples, please review the [Credential Security Guide](CREDENTIAL_SECURITY_GUIDE.md) for secure credential management across different environments.**

**Key Security Principles:**
- ✅ **GitHub Actions**: Use GitHub Secrets
- ✅ **AWS CodeBuild**: Use AWS Secrets Manager  
- ✅ **Local Development**: Use AWS CLI profiles
- ❌ **Never commit credentials to version control**

## Account Configuration Files

### Basic Multi-Account Configuration (JSON)

**File: `examples/accounts_basic.json`**

```json
{
  "version": "1.0",
  "encrypted": false,
  "accounts": [
    {
      "account_id": "123456789012",
      "account_name": "Production Account",
      "role_arn": "arn:aws:iam::123456789012:role/InvenTagCrossAccountRole",
      "external_id": "unique-external-id-for-security",
      "regions": ["us-east-1", "us-west-2"],
      "services": ["EC2", "S3", "RDS", "Lambda"],
      "tags": {
        "Environment": "production",
        "Owner": "devops-team"
      }
    }
  ],
  "global_config": {
    "default_regions": ["us-east-1"],
    "max_concurrent_accounts": 3,
    "continue_on_error": true
  }
}
```

**Usage:**
```bash
python scripts/cicd_bom_generation.py --accounts-file examples/accounts_basic.json --formats excel word
```

### CI/CD Environment Configuration

**File: `examples/accounts_cicd_environment.json`**

This configuration is designed for CI/CD environments where AWS credentials are provided via environment variables.

```json
{
  "version": "1.0",
  "encrypted": false,
  "accounts": [
    {
      "account_id": "123456789012",
      "account_name": "Production Account",
      "regions": ["us-east-1", "us-west-2"],
      "services": ["EC2", "S3", "RDS", "Lambda", "ECS"],
      "tags": {
        "Environment": "production",
        "Owner": "platform-team"
      }
    }
  ],
  "metadata": {
    "notes": [
      "This configuration assumes AWS credentials are provided via environment variables:",
      "AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN (optional)"
    ]
  }
}
```

### AWS CLI Profiles Configuration

**File: `examples/accounts_with_profiles.json`**

For local development using AWS CLI profiles.

```json
{
  "accounts": [
    {
      "account_id": "123456789012",
      "account_name": "Production Account",
      "profile_name": "prod-account",
      "regions": ["us-east-1", "us-west-2"]
    }
  ],
  "metadata": {
    "notes": [
      "Ensure profiles are configured in ~/.aws/credentials",
      "Use 'aws configure --profile <profile-name>' to set up each profile"
    ]
  }
}
```

### Cross-Account Role Configuration

**File: `examples/accounts_cross_account_roles.json`**

Enterprise configuration with cross-account role assumption.

```json
{
  "accounts": [
    {
      "account_id": "123456789012",
      "account_name": "Production Account",
      "role_arn": "arn:aws:iam::123456789012:role/InvenTagCrossAccountRole",
      "external_id": "prod-external-id-12345",
      "regions": ["us-east-1", "us-west-2", "eu-west-1"],
      "services": ["EC2", "S3", "RDS", "Lambda", "ECS", "EKS"]
    }
  ],
  "metadata": {
    "setup_instructions": [
      "1. Create InvenTagCrossAccountRole in each target account",
      "2. Configure trust relationship to allow assumption from management account",
      "3. Attach ReadOnlyAccess policy for resource discovery",
      "4. Set unique external IDs for each account"
    ]
  }
}
```

### YAML Format (Alternative)

**File: `examples/cicd_accounts_example.yaml`**

```yaml
version: "1.0"
encrypted: false

accounts:
  - account_id: "123456789012"
    account_name: "Production Account"
    role_arn: "arn:aws:iam::123456789012:role/InvenTagCrossAccountRole"
    external_id: "unique-external-id-for-security"
    regions:
      - "us-east-1"
      - "us-west-2"
    services:
      - "EC2"
      - "S3"
      - "RDS"
    tags:
      Environment: "production"
      Owner: "devops-team"

global_config:
  default_regions:
    - "us-east-1"
  max_concurrent_accounts: 3
  continue_on_error: true
```

## CI/CD Integration Configuration

### Complete CI/CD Configuration

**File: `examples/cicd_config_complete.json`**

```json
{
  "s3_config": {
    "bucket_name": "my-compliance-reports-bucket",
    "key_prefix": "inventag-bom-reports",
    "region": "us-east-1",
    "encryption": "AES256",
    "lifecycle_days": 90,
    "storage_class": "STANDARD"
  },
  "compliance_gate_config": {
    "minimum_compliance_percentage": 80.0,
    "critical_violations_threshold": 0,
    "required_tags": ["Environment", "Owner"],
    "fail_on_security_issues": true,
    "fail_on_network_issues": false
  },
  "notification_config": {
    "slack_webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
    "teams_webhook_url": "https://outlook.office.com/webhook/YOUR/TEAMS/WEBHOOK",
    "email_recipients": ["compliance@company.com"],
    "notify_on_success": true,
    "notify_on_failure": true
  },
  "prometheus_config": {
    "push_gateway_url": "http://prometheus-pushgateway:9091",
    "job_name": "inventag-bom-generation",
    "instance_name": "production"
  }
}
```

### S3 Configuration Variants

**Basic S3 Configuration:**
```json
{
  "bucket_name": "my-compliance-bucket",
  "key_prefix": "bom-reports",
  "region": "us-east-1"
}
```

**S3 with KMS Encryption:**
```json
{
  "bucket_name": "secure-compliance-bucket",
  "key_prefix": "encrypted-reports",
  "region": "us-west-2",
  "encryption": "aws:kms",
  "kms_key_id": "arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012",
  "lifecycle_days": 30,
  "storage_class": "STANDARD_IA"
}
```

### Compliance Gate Configurations

**Strict Compliance (Production):**
```json
{
  "minimum_compliance_percentage": 95.0,
  "critical_violations_threshold": 0,
  "required_tags": ["Environment", "Owner", "CostCenter", "Project"],
  "fail_on_security_issues": true,
  "fail_on_network_issues": true
}
```

**Lenient Compliance (Development):**
```json
{
  "minimum_compliance_percentage": 60.0,
  "critical_violations_threshold": 5,
  "required_tags": ["Environment"],
  "allowed_non_compliant_services": ["CloudTrail", "Config"],
  "fail_on_security_issues": false,
  "fail_on_network_issues": false
}
```

## CLI Usage Examples

### Basic Usage

```bash
# Simple BOM generation
python scripts/cicd_bom_generation.py \
  --accounts-file examples/accounts_basic.json \
  --formats excel word

# With specific output directory
python scripts/cicd_bom_generation.py \
  --accounts-file examples/accounts_basic.json \
  --formats excel word json \
  --output-dir ./my_bom_output
```

### S3 Upload

```bash
# Upload to S3 with basic configuration
python scripts/cicd_bom_generation.py \
  --accounts-file examples/accounts_basic.json \
  --formats excel word json \
  --s3-bucket my-compliance-bucket \
  --s3-key-prefix bom-reports

# S3 with KMS encryption
python scripts/cicd_bom_generation.py \
  --accounts-file examples/accounts_basic.json \
  --formats excel \
  --s3-bucket secure-bucket \
  --s3-encryption aws:kms \
  --s3-kms-key-id arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012
```

### Compliance Gates

```bash
# Strict compliance checking
python scripts/cicd_bom_generation.py \
  --accounts-file examples/accounts_basic.json \
  --formats excel \
  --compliance-threshold 85 \
  --fail-on-security-issues \
  --fail-on-network-issues \
  --required-tags Environment Owner CostCenter

# Lenient compliance for development
python scripts/cicd_bom_generation.py \
  --accounts-file examples/accounts_basic.json \
  --formats excel \
  --compliance-threshold 60 \
  --critical-violations-threshold 5
```

### Notifications

```bash
# Slack notifications
python scripts/cicd_bom_generation.py \
  --accounts-file examples/accounts_basic.json \
  --formats excel \
  --slack-webhook https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Multiple notification channels
python scripts/cicd_bom_generation.py \
  --accounts-file examples/accounts_basic.json \
  --formats excel \
  --slack-webhook https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK \
  --teams-webhook https://outlook.office.com/webhook/YOUR/TEAMS/WEBHOOK \
  --email-recipients admin@company.com compliance@company.com
```

### Prometheus Metrics

```bash
# Push metrics to Prometheus Push Gateway
python scripts/cicd_bom_generation.py \
  --accounts-file examples/accounts_basic.json \
  --formats excel \
  --prometheus-gateway http://prometheus-pushgateway:9091 \
  --prometheus-job inventag-manual \
  --prometheus-instance local-run
```

### Full-Featured Example

```bash
# Complete CI/CD integration
python scripts/cicd_bom_generation.py \
  --accounts-file examples/accounts_cross_account_roles.json \
  --formats excel word json \
  --output-dir ./bom_output \
  --s3-bucket my-compliance-bucket \
  --s3-key-prefix production-reports \
  --compliance-threshold 80 \
  --fail-on-security-issues \
  --required-tags Environment Owner \
  --slack-webhook https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK \
  --prometheus-gateway http://prometheus:9091 \
  --prometheus-job inventag-production \
  --verbose
```

### Dry Run and Validation

```bash
# Validate configuration without execution
python scripts/cicd_bom_generation.py \
  --accounts-file examples/accounts_basic.json \
  --formats excel \
  --dry-run \
  --verbose
```

## CI/CD Platform Integration

### GitHub Actions

**File: `examples/github_actions_cicd_example.yml`**

```yaml
name: Multi-Account BOM Generation

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  workflow_dispatch:
    inputs:
      compliance_threshold:
        description: 'Minimum compliance percentage'
        default: '80'

jobs:
  bom-generation:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Generate BOM
      env:
        INVENTAG_S3_BUCKET: ${{ secrets.INVENTAG_S3_BUCKET }}
        INVENTAG_SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK_URL }}
        PROMETHEUS_PUSH_GATEWAY_URL: ${{ secrets.PROMETHEUS_PUSH_GATEWAY_URL }}
      run: |
        python scripts/cicd_bom_generation.py \
          --accounts-file examples/accounts_cicd_environment.json \
          --formats excel word json \
          --compliance-threshold ${{ github.event.inputs.compliance_threshold || '80' }} \
          --fail-on-security-issues \
          --verbose
```

### Jenkins Pipeline

**File: `examples/jenkins_pipeline.groovy`**

```groovy
pipeline {
    agent any
    
    parameters {
        choice(name: 'ENVIRONMENT', choices: ['production', 'staging', 'development'])
        choice(name: 'OUTPUT_FORMATS', choices: ['excel', 'word', 'json', 'excel,word,json'])
        string(name: 'COMPLIANCE_THRESHOLD', defaultValue: '80')
    }
    
    environment {
        INVENTAG_S3_BUCKET = credentials('inventag-s3-bucket')
        INVENTAG_SLACK_WEBHOOK = credentials('slack-webhook-url')
        PROMETHEUS_PUSH_GATEWAY_URL = 'http://prometheus-pushgateway:9091'
    }
    
    stages {
        stage('Generate BOM') {
            steps {
                withCredentials([aws(credentialsId: 'aws-credentials')]) {
                    sh """
                        python scripts/cicd_bom_generation.py \
                          --accounts-file examples/accounts_${params.ENVIRONMENT}.json \
                          --formats ${params.OUTPUT_FORMATS} \
                          --compliance-threshold ${params.COMPLIANCE_THRESHOLD} \
                          --s3-bucket \${INVENTAG_S3_BUCKET} \
                          --slack-webhook \${INVENTAG_SLACK_WEBHOOK} \
                          --prometheus-gateway \${PROMETHEUS_PUSH_GATEWAY_URL} \
                          --verbose
                    """
                }
            }
        }
    }
}
```

### AWS CodeBuild

**File: `examples/aws_codebuild_buildspec.yml`**

```yaml
version: 0.2

env:
  variables:
    OUTPUT_FORMATS: "excel,word,json"
    COMPLIANCE_THRESHOLD: "80"
  parameter-store:
    INVENTAG_S3_BUCKET: "/inventag/s3/bucket-name"
    INVENTAG_SLACK_WEBHOOK: "/inventag/notifications/slack-webhook"
    PROMETHEUS_PUSH_GATEWAY_URL: "/inventag/prometheus/push-gateway-url"

phases:
  install:
    runtime-versions:
      python: 3.11
    commands:
      - pip install -r requirements.txt
      
  build:
    commands:
      - |
        python scripts/cicd_bom_generation.py \
          --accounts-file examples/accounts_cicd_environment.json \
          --formats $OUTPUT_FORMATS \
          --compliance-threshold $COMPLIANCE_THRESHOLD \
          --s3-bucket $INVENTAG_S3_BUCKET \
          --slack-webhook $INVENTAG_SLACK_WEBHOOK \
          --prometheus-gateway $PROMETHEUS_PUSH_GATEWAY_URL \
          --fail-on-security-issues \
          --verbose

artifacts:
  files:
    - 'bom_output/**/*'
    - '/tmp/pipeline_summary.json'
    - '/tmp/compliance_gate.json'
```

## Monitoring and Alerting

### Prometheus Configuration

**File: `examples/prometheus.yml`**

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'pushgateway'
    static_configs:
      - targets: ['prometheus-pushgateway:9091']
    scrape_interval: 30s
```

### Alerting Rules

**File: `examples/inventag_alerts.yml`**

```yaml
groups:
  - name: inventag_compliance_alerts
    rules:
      - alert: CompliancePercentageLow
        expr: inventag_compliance_percentage < 80
        labels:
          severity: warning
        annotations:
          summary: "Compliance percentage below threshold"
          description: "Compliance is {{ $value }}% for account {{ $labels.account_id }}"
      
      - alert: CriticalViolationsDetected
        expr: inventag_critical_violations > 0
        labels:
          severity: critical
        annotations:
          summary: "Critical compliance violations detected"
          description: "{{ $value }} critical violations in account {{ $labels.account_id }}"
```

## Environment Variables

### AWS Credentials

```bash
# Basic AWS credentials
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_SESSION_TOKEN="optional-session-token"
export AWS_DEFAULT_REGION="us-east-1"
```

### InvenTag Configuration

```bash
# S3 Configuration
export INVENTAG_S3_BUCKET="my-compliance-bucket"
export INVENTAG_S3_KEY_PREFIX="bom-reports"

# Notification Configuration
export INVENTAG_SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
export INVENTAG_TEAMS_WEBHOOK="https://outlook.office.com/webhook/YOUR/TEAMS/WEBHOOK"

# Prometheus Configuration
export PROMETHEUS_PUSH_GATEWAY_URL="http://prometheus-pushgateway:9091"
export PROMETHEUS_JOB_NAME="inventag-bom"
export PROMETHEUS_INSTANCE_NAME="default"
```

### Environment-Specific Credentials

```bash
# GitHub Actions - Multi-account credentials
export AWS_ACCESS_KEY_ID_PROD="production-access-key"
export AWS_SECRET_ACCESS_KEY_PROD="production-secret-key"
export AWS_SESSION_TOKEN_PROD="production-session-token"

export AWS_ACCESS_KEY_ID_STAGING="staging-access-key"
export AWS_SECRET_ACCESS_KEY_STAGING="staging-secret-key"

export AWS_ACCESS_KEY_ID_DEV="development-access-key"
export AWS_SECRET_ACCESS_KEY_DEV="development-secret-key"

# AWS Secrets Manager - Secret name overrides
export INVENTAG_SECRET_PRODUCTION="inventag/credentials/production"
export INVENTAG_SECRET_STAGING="inventag/credentials/staging"
export INVENTAG_SECRET_DEVELOPMENT="inventag/credentials/development"
```

### Usage with Environment Variables

```bash
# All configuration via environment variables
python scripts/cicd_bom_generation.py \
  --accounts-file examples/accounts_cicd_environment.json \
  --formats excel word \
  --compliance-threshold 80 \
  --fail-on-security-issues
```

## Docker and Container Deployment

### Docker Compose

**File: `examples/docker_compose_cicd.yml`**

```yaml
version: '3.8'

services:
  inventag-bom:
    build: .
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - INVENTAG_S3_BUCKET=${INVENTAG_S3_BUCKET}
      - INVENTAG_SLACK_WEBHOOK=${SLACK_WEBHOOK_URL}
      - PROMETHEUS_PUSH_GATEWAY_URL=http://prometheus-pushgateway:9091
    volumes:
      - ./examples:/app/examples:ro
      - ./output:/app/output
    command: >
      python scripts/cicd_bom_generation.py
      --accounts-file examples/accounts_cicd_environment.json
      --formats excel word json
      --compliance-threshold 80
      --fail-on-security-issues
      --verbose
    depends_on:
      - prometheus-pushgateway

  prometheus-pushgateway:
    image: prom/pushgateway:latest
    ports:
      - "9091:9091"
```

### Kubernetes Deployment

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: inventag-bom-generation
spec:
  schedule: "0 6 * * *"  # Daily at 6 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: inventag
            image: inventag:latest
            env:
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: access-key-id
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: secret-access-key
            - name: INVENTAG_S3_BUCKET
              valueFrom:
                configMapKeyRef:
                  name: inventag-config
                  key: s3-bucket
            command:
            - python
            - scripts/cicd_bom_generation.py
            - --accounts-file
            - examples/accounts_cicd_environment.json
            - --formats
            - excel
            - word
            - json
            - --compliance-threshold
            - "80"
            - --fail-on-security-issues
            - --verbose
          restartPolicy: OnFailure
```

## Quick Reference

### Most Common Use Cases

1. **Basic BOM Generation:**
   ```bash
   python scripts/cicd_bom_generation.py --accounts-file examples/accounts_basic.json --formats excel
   ```

2. **CI/CD with S3 Upload:**
   ```bash
   python scripts/cicd_bom_generation.py --accounts-file examples/accounts_cicd_environment.json --formats excel word --s3-bucket my-bucket
   ```

3. **Production with Full Monitoring:**
   ```bash
   python scripts/cicd_bom_generation.py --accounts-file examples/accounts_cross_account_roles.json --formats excel word json --s3-bucket prod-bucket --compliance-threshold 85 --fail-on-security-issues --slack-webhook $SLACK_WEBHOOK --prometheus-gateway http://prometheus:9091
   ```

4. **Validation Only:**
   ```bash
   python scripts/cicd_bom_generation.py --accounts-file examples/accounts_basic.json --formats excel --dry-run --verbose
   ```

### File Locations

- **Account Configurations:** `examples/accounts_*.json` or `examples/*.yaml`
- **CI/CD Examples:** `examples/github_actions_*.yml`, `examples/jenkins_*.groovy`, `examples/aws_codebuild_*.yml`
- **Monitoring:** `examples/prometheus.yml`, `examples/inventag_alerts.yml`
- **Container Deployment:** `examples/docker_compose_*.yml`

## Security Best Practices

### 🔐 Credential Management by Environment

| Environment | Recommended Method | Configuration File | Security Level |
|-------------|-------------------|-------------------|----------------|
| **Local Development** | AWS CLI Profiles | `accounts_with_profiles.json` | ✅ High |
| **GitHub Actions** | GitHub Secrets | `accounts_github_secrets.json` | ✅ High |
| **AWS CodeBuild** | AWS Secrets Manager | `accounts_aws_secrets_manager.json` | ✅ High |
| **Jenkins** | Jenkins Credential Store | `accounts_cicd_environment.json` | ✅ High |
| **Local Testing** | Direct Credentials | `accounts_local_with_credentials.json` | ⚠️ Use with caution |

### 🛡️ Security Requirements

**For all environments:**
- Use principle of least privilege for IAM permissions
- Enable CloudTrail logging for audit trails
- Rotate credentials regularly
- Never commit credentials to version control

**For production environments:**
- Use cross-account roles with external IDs
- Enable multi-factor authentication
- Set up monitoring and alerting
- Implement automated credential rotation

### 📚 Additional Resources

- **[Credential Security Guide](CREDENTIAL_SECURITY_GUIDE.md)** - Comprehensive security best practices
- **[AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)** - AWS official guidance
- **[GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)** - GitHub Actions security

---

All configuration files are fully documented with comments and examples. You should never need to reverse engineer the format - just copy and modify the appropriate example file for your use case.

**Remember: Security is paramount. Always choose the most secure credential management method for your environment.**
## Enviro
nment Detection and Flexible Credential Management

### 🔍 Automatic Environment Detection
The InvenTag CLI automatically detects the execution environment and applies appropriate credential handling:

- **GitHub Actions:** Uses GitHub Secrets via environment variables (flexible patterns)
- **AWS CodeBuild:** Uses AWS Secrets Manager integration (flexible secret names)
- **Jenkins:** Uses Jenkins credential store
- **Local:** Uses AWS CLI profiles or environment variables

### 🔑 Flexible Credential Management
✅ **No hardcoded account IDs or mappings** - works with any account configuration  
✅ **Multiple naming patterns** - automatically tries various environment variable and secret name patterns  
✅ **Environment variable overrides** - customize secret names as needed  
✅ **Clear error messages** - helpful guidance when credentials are missing  
✅ **Automatic pattern matching** - works with any account names and IDs  

### 📋 Credential Pattern Examples

#### GitHub Actions Environment Variable Patterns
For account ID `123456789012` with name `Production Account`:
- `AWS_ACCESS_KEY_ID_123456789012` / `AWS_SECRET_ACCESS_KEY_123456789012`
- `AWS_ACCESS_KEY_ID_PRODUCTION_ACCOUNT` / `AWS_SECRET_ACCESS_KEY_PRODUCTION_ACCOUNT`
- `PRODUCTION_ACCOUNT_AWS_ACCESS_KEY_ID` / `PRODUCTION_ACCOUNT_AWS_SECRET_ACCESS_KEY`
- `AWS_ACCESS_KEY_ID_9012` / `AWS_SECRET_ACCESS_KEY_9012` (last 4 digits)

#### AWS Secrets Manager Secret Name Patterns
For account ID `123456789012` with name `Production Account`:
- `inventag/credentials/123456789012`
- `inventag/credentials/production_account`
- `inventag/123456789012/credentials`
- `inventag-123456789012`
- Environment variable override: `INVENTAG_SECRET_PRODUCTION_ACCOUNT`

### 🧪 Testing Your Configuration
Use the provided test script to verify your credential management setup:

```bash
python examples/test_credential_management.py
```

This will test:
- Environment name sanitization
- Credential pattern matching
- Environment detection
- Flexible account configuration support

## Quick Reference

### Most Common Use Cases

1. **Basic BOM Generation:**
   ```bash
   python scripts/cicd_bom_generation.py --accounts-file examples/accounts_basic.json --formats excel
   ```

2. **CI/CD with S3 Upload:**
   ```bash
   python scripts/cicd_bom_generation.py --accounts-file examples/accounts_flexible_credentials.json --formats excel word --s3-bucket my-bucket
   ```

3. **Production with Full Monitoring:**
   ```bash
   python scripts/cicd_bom_generation.py --accounts-file examples/accounts_flexible_credentials.json --formats excel word json --s3-bucket prod-bucket --compliance-threshold 85 --fail-on-security-issues --slack-webhook $SLACK_WEBHOOK --prometheus-gateway http://prometheus:9091
   ```

4. **Validation Only:**
   ```bash
   python scripts/cicd_bom_generation.py --accounts-file examples/accounts_flexible_credentials.json --formats excel --dry-run --verbose
   ```

### File Locations

- **Account Configurations:** `examples/accounts_*.json` or `examples/*.yaml`
- **Flexible Configuration:** `examples/accounts_flexible_credentials.json`
- **CI/CD Examples:** `examples/github_actions_*.yml`, `examples/jenkins_*.groovy`, `examples/aws_codebuild_*.yml`
- **Monitoring:** `examples/prometheus.yml`, `examples/inventag_alerts.yml`
- **Container Deployment:** `examples/docker_compose_*.yml`
- **Testing:** `examples/test_credential_management.py`

All configuration files are fully documented with comments and examples. You should never need to reverse engineer the format - just copy and modify the appropriate example file for your use case.

**Remember: Security is paramount. Always choose the most secure credential management method for your environment.**