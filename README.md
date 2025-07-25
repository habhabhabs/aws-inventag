# AWS Cloud BOM Automation

A comprehensive AWS resource inventory tool that discovers and catalogs all AWS resources across your environment. Generates detailed Bill of Materials (BOM) reports in JSON, YAML, Excel, and CSV formats.

## Features

- **Comprehensive Resource Discovery**: Scans EC2, S3, RDS, Lambda, IAM, VPC, CloudFormation, ECS, EKS, and CloudWatch resources
- **Multi-Region Support**: Discovers resources across all AWS regions or specified regions
- **Multiple Output Formats**: JSON, YAML, Excel (.xlsx), and CSV
- **S3 Integration**: Upload inventory reports directly to S3
- **Detailed Resource Information**: Captures tags, configurations, and metadata
- **Lightweight Converter**: Separate utility for format conversion with minimal dependencies

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure AWS credentials (using AWS CLI, environment variables, or IAM roles):
```bash
aws configure
```

## Usage

### Main Inventory Script

Basic usage:
```bash
python aws_resource_inventory.py
```

Advanced options:
```bash
# Scan specific regions
python aws_resource_inventory.py --regions us-east-1 us-west-2

# Output in YAML format
python aws_resource_inventory.py --format yaml

# Custom output filename
python aws_resource_inventory.py --output my_inventory

# Upload to S3
python aws_resource_inventory.py --s3-bucket my-bucket --s3-key inventory/latest.json

# Also export to Excel
python aws_resource_inventory.py --export-excel

# Verbose logging
python aws_resource_inventory.py --verbose
```

### BOM Converter Utility

Convert existing JSON/YAML files to Excel/CSV:

```bash
# Convert to Excel
python bom_converter.py --input aws_resources_20250725_123456.json --output inventory.xlsx --format excel

# Convert to CSV
python bom_converter.py --input aws_resources_20250725_123456.yaml --output inventory.csv --format csv
```

## Supported AWS Services

- **EC2**: Instances, EBS Volumes, Security Groups
- **S3**: Buckets
- **RDS**: Database Instances
- **Lambda**: Functions
- **IAM**: Roles, Users (global)
- **VPC**: VPCs, Subnets
- **CloudFormation**: Stacks
- **ECS**: Clusters
- **EKS**: Clusters
- **CloudWatch**: Alarms

## Output Format

Each resource includes:
- Service name and type
- Region (or 'global' for global services)
- Resource ID and name
- Current state/status
- Tags and metadata
- Discovery timestamp

Example resource entry:
```json
{
  "service": "EC2",
  "type": "Instance",
  "region": "us-east-1",
  "id": "i-1234567890abcdef0",
  "name": "web-server-01",
  "state": "running",
  "instance_type": "t3.medium",
  "vpc_id": "vpc-12345678",
  "subnet_id": "subnet-12345678",
  "launch_time": "2025-07-25T10:30:00",
  "tags": {
    "Name": "web-server-01",
    "Environment": "production"
  },
  "discovered_at": "2025-07-25T14:15:30.123456"
}
```

## Excel Output Features

The Excel output includes:
- **Main Sheet**: Complete resource inventory with auto-sized columns
- **Summary Sheet**: Resource counts by service, region, and type
- **Formatted Headers**: Bold headers with background colors
- **Flattened Data**: Nested objects are flattened for tabular view

## Error Handling

- Graceful handling of missing permissions
- Continues discovery even if some services fail
- Detailed logging of errors and warnings
- Fallback mechanisms for unavailable services

## Dependencies

- **boto3**: AWS SDK for Python
- **PyYAML**: YAML processing
- **openpyxl**: Excel file generation (optional, falls back to CSV if not available)

## AWS Permissions

The tool requires read-only permissions for the AWS services it scans. Example IAM policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation",
        "s3:GetBucketTagging",
        "rds:Describe*",
        "lambda:List*",
        "iam:List*",
        "cloudformation:List*",
        "cloudformation:Describe*",
        "ecs:List*",
        "ecs:Describe*",
        "eks:List*",
        "eks:Describe*",
        "cloudwatch:Describe*"
      ],
      "Resource": "*"
    }
  ]
}
```

For S3 upload functionality, also add:
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:PutObject"
  ],
  "Resource": "arn:aws:s3:::your-bucket-name/*"
}
```

## Tag Compliance Checker

The `tag_compliance_checker.py` utility validates AWS resources against your organization's tagging policies.

### Usage

Basic compliance check (untagged resources only):
```bash
python tag_compliance_checker.py
```

With tag policy configuration:
```bash
python tag_compliance_checker.py --config tag_policy.yaml
```

Advanced options:
```bash
# Specific regions
python tag_compliance_checker.py --config tag_policy.json --regions us-east-1 us-west-2

# Upload report to S3
python tag_compliance_checker.py --config tag_policy.yaml --s3-bucket compliance-reports --s3-key monthly-compliance.json

# YAML output format
python tag_compliance_checker.py --config tag_policy.yaml --format yaml --output compliance_report

# Verbose logging
python tag_compliance_checker.py --config tag_policy.yaml --verbose
```

### Tag Policy Configuration

Create a configuration file (JSON or YAML) to define your tagging requirements. The configuration supports:

1. **Simple Required Tags**: Keys that must exist with any value
2. **Tags with Allowed Values**: Keys that must exist with specific allowed values
3. **Tags with Required Values**: Keys that must exist with one of the required values
4. **Service-Specific Requirements**: Different rules for different AWS services
5. **Exemptions**: Resources that don't need to follow the policy

#### Example YAML Configuration:

```yaml
required_tags:
  # Simple required tags (key must exist, any value allowed)
  - "Environment"
  - "Owner"
  - "Project"
  
  # Required tags with specific allowed values
  - key: "Environment"
    allowed_values:
      - "production"
      - "staging"
      - "development"
      - "testing"
  
  - key: "CostCenter"
    required_values:
      - "engineering"
      - "marketing"
      - "finance"
      - "operations"

# Optional: Service-specific requirements
service_specific:
  EC2:
    Instance:
      additional_required_tags:
        - "InstanceType"
        - "Patch-Group"

# Optional: Exemptions
exemptions:
  - service: "IAM"
    type: "Role" 
    reason: "Service roles don't require standard tags"
```

#### Example JSON Configuration:

```json
{
  "required_tags": [
    "Environment",
    "Owner", 
    "Project",
    {
      "key": "Environment",
      "allowed_values": ["production", "staging", "development", "testing"]
    },
    {
      "key": "CostCenter",
      "required_values": ["engineering", "marketing", "finance", "operations"] 
    }
  ]
}
```

### Configuration File Structure

#### Required Tags Section
- **String format**: `"TagName"` - Tag key must exist with any value
- **Object format**: 
  - `key`: Tag key name (required)
  - `allowed_values`: List of acceptable values (optional)
  - `required_values`: List of values, resource must have one of these (optional)

#### Service Specific Section (Optional)
Define additional requirements for specific AWS services:
```yaml
service_specific:
  ServiceName:
    ResourceType:
      additional_required_tags:
        - "AdditionalTag"
```

#### Exemptions Section (Optional)
Resources that don't need to follow the policy:
```yaml
exemptions:
  - service: "ServiceName"
    type: "ResourceType"
    reason: "Why this is exempt"
  - service: "ServiceName"
    name_pattern: "pattern*"
    reason: "Exempt by name pattern"
  - service: "ServiceName"
    resource_ids: ["id1", "id2"]
    reason: "Specific resource exemptions"
```

### Output and Reports

The compliance checker generates:

1. **Console Summary**: 
   - Total resources scanned
   - Compliant vs non-compliant counts
   - Compliance percentage
   - Most commonly missing tags

2. **Detailed JSON/YAML Report**:
   - Complete list of compliant resources
   - Non-compliant resources with missing/incorrect tags
   - Untagged resources
   - Summary statistics

3. **Color-Coded Output**:
   - Green: Compliant resources
   - Red: Non-compliant resources and errors
   - Yellow: Untagged resources and warnings

### Exit Codes

- `0`: All resources are compliant
- `1`: Non-compliant or untagged resources found, or errors occurred

This makes the tool suitable for CI/CD pipelines and automated compliance checking.

### Supported Services for Tag Compliance

The checker validates tags on the same services as the inventory tool:
- EC2 (Instances, EBS Volumes, Security Groups)
- S3 (Buckets)
- RDS (Database Instances)
- Lambda (Functions)
- IAM (Roles, Users)
- VPC (VPCs, Subnets)
- CloudFormation (Stacks)
- ECS (Clusters)
- EKS (Clusters)

## Output Files

Files are generated with timestamps:
- `aws_resources_YYYYMMDD_HHMMSS.json`
- `aws_resources_YYYYMMDD_HHMMSS.yaml`
- `aws_resources_YYYYMMDD_HHMMSS.xlsx`
- `aws_resources_YYYYMMDD_HHMMSS.csv`
- `tag_compliance_report_YYYYMMDD_HHMMSS.json`
- `tag_compliance_report_YYYYMMDD_HHMMSS.yaml`