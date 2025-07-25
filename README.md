# AWS Cloud BOM Automation

A comprehensive AWS resource inventory tool that discovers and catalogs all AWS resources across your environment. Generates detailed Bill of Materials (BOM) reports in JSON, YAML, Excel, and CSV formats.

## Features

- **Comprehensive Resource Discovery**: Discovers ALL AWS resources across ALL services using multiple discovery methods
- **Multi-Region Support**: Discovers resources across all AWS regions or specified regions
- **Multiple Output Formats**: JSON, YAML, Excel (.xlsx), and CSV
- **S3 Integration**: Upload inventory reports directly to S3
- **Detailed Resource Information**: Captures tags, configurations, and metadata
- **Enhanced Excel Output**: Separate sheets per AWS service with VPC/subnet name enrichment
- **Comprehensive Tag Compliance**: Validates ALL AWS resources against tagging policies
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

### Enhanced BOM Converter Utility

Convert existing JSON/YAML files to Excel/CSV with enhanced features:

```bash
# Convert to Excel with separate sheets per AWS service and VPC/subnet names
python bom_converter.py --input aws_resources_20250725_123456.json --output inventory.xlsx --format excel

# Convert to CSV with AWS service as column
python bom_converter.py --input aws_resources_20250725_123456.yaml --output inventory.csv --format csv

# Skip VPC enrichment for faster processing
python bom_converter.py --input inventory.json --output fast_report.xlsx --no-vpc-enrichment
```

## Supported AWS Services

**The tools discover ALL AWS resources across ALL services using multiple discovery methods:**

- **Primary Discovery**: Resource Groups Tagging API (discovers resources from ANY AWS service)
- **Additional Discovery**: AWS Config, CloudTrail, and service-specific APIs
- **Comprehensive Coverage**: EC2, S3, RDS, Lambda, IAM, VPC, CloudFormation, ECS, EKS, CloudWatch, DynamoDB, SNS, SQS, API Gateway, ElastiCache, OpenSearch, Route53, KMS, CloudWatch Logs, and many more
- **Future-Proof**: Automatically discovers resources from new AWS services as they're added

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

## Enhanced Excel Output Features

The enhanced Excel output includes:
- **Service-Specific Sheets**: Separate sheet for each AWS service (EC2, S3, RDS, etc.)
- **Summary Sheet**: Overview with service breakdown and resource counts
- **VPC/Subnet Enrichment**: Automatic lookup of VPC and subnet names from tags
- **Formatted Headers**: Bold headers with background colors and proper column sizing
- **Prioritized Columns**: Important fields (service, type, region, id, name, VPC info) appear first
- **Flattened Data**: Nested objects are flattened for tabular view

## CSV Output Features

The CSV output includes:
- **Service Column**: AWS service name prominently displayed as first column
- **VPC/Subnet Enrichment**: Includes VPC and subnet names when available
- **All Resource Data**: Complete flattened view of all resource attributes

## Error Handling

- Graceful handling of missing permissions
- Continues discovery even if some services fail
- Detailed logging of errors and warnings
- Fallback mechanisms for unavailable services

## Dependencies

- **boto3**: AWS SDK for Python
- **PyYAML**: YAML processing  
- **openpyxl**: Excel file generation with service sheets (optional, falls back to CSV if not available)
- **colorama**: Colored console output for tag compliance checker
- **colorama**: Colored console output for better readability

## Security & AWS Permissions

### 🔒 **Read-Only Operation Guarantee**

**All scripts operate in READ-ONLY mode and cannot modify your AWS infrastructure:**

- ✅ **Only read/describe/list operations** are used
- ✅ **No create, update, delete, or modify actions** 
- ✅ **No infrastructure changes possible**
- ✅ **Safe to run in production environments**

The only write operation is the optional `s3:PutObject` for uploading reports to S3.

### 📋 **Required IAM Permissions**

The tools require comprehensive read-only permissions across AWS services. Use the provided IAM policy file:

**File**: [`iam-policy-read-only.json`](./iam-policy-read-only.json)

This policy includes three permission sets:

#### 1. **Basic Resource Inventory** (aws_resource_inventory.py):
```json
"ec2:DescribeRegions", "ec2:DescribeInstances", "ec2:DescribeVolumes",
"s3:ListAllMyBuckets", "s3:GetBucketTagging", 
"rds:DescribeDBInstances", "lambda:ListFunctions",
"iam:ListRoles", "cloudformation:ListStacks", 
"ecs:ListClusters", "eks:ListClusters"
```

#### 2. **Comprehensive Discovery** (tag_compliance_checker.py):
```json
"resourcegroupstaggingapi:GetResources",
"config:DescribeConfigurationRecorderStatus",
"cloudtrail:LookupEvents",
"logs:DescribeLogGroups", "route53:ListHostedZones",
"apigateway:GET", "dynamodb:ListTables",
"sns:ListTopics", "sqs:ListQueues",
"kms:ListKeys", "elasticache:DescribeCacheClusters",
"opensearch:ListDomainNames", "es:ListDomainNames"
```

#### 3. **Optional S3 Upload**:
```json
"s3:PutObject" on "arn:aws:s3:::YOUR-REPORTS-BUCKET-NAME/*"
```

### 🛡️ **Security Best Practices**

1. **Use the minimal policy**: Only grant permissions for services you want to scan
2. **Restrict S3 upload**: Replace `YOUR-REPORTS-BUCKET-NAME` with your specific bucket
3. **Consider MFA**: Require MFA for the IAM user/role running these scripts
4. **Regular rotation**: Rotate access keys regularly
5. **Monitoring**: Enable CloudTrail to monitor API usage

### 🚀 **Quick Setup**

1. **Create IAM policy**:
   ```bash
   aws iam create-policy \
     --policy-name AWSResourceInventoryReadOnly \
     --policy-document file://iam-policy-read-only.json
   ```

2. **Attach to user/role**:
   ```bash
   aws iam attach-user-policy \
     --user-name your-user-name \
     --policy-arn arn:aws:iam::ACCOUNT:policy/AWSResourceInventoryReadOnly
   ```

3. **Update S3 bucket name** in the policy (if using S3 upload):
   ```bash
   # Edit iam-policy-read-only.json and replace YOUR-REPORTS-BUCKET-NAME
   ```

## Tag Compliance Checker

The `tag_compliance_checker.py` utility validates ALL AWS resources across your entire account against your organization's tagging policies using comprehensive discovery methods.

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

### Enhanced Output and Reports

The comprehensive compliance checker generates:

1. **Enhanced Console Summary**: 
   - Total resources discovered across all services
   - Service-by-service compliance breakdown with rates
   - Discovery methods used (RGT API, Config, CloudTrail, Service APIs)
   - Compliant vs non-compliant counts
   - Overall compliance percentage
   - Most commonly missing tags

2. **Comprehensive JSON/YAML Report**:
   - Complete list of all discovered resources (full inventory)
   - Compliant resources with full details
   - Non-compliant resources with missing/incorrect tags
   - Untagged resources
   - Summary statistics with service breakdown
   - Discovery method attribution

3. **Color-Coded Console Output**:
   - Cyan: Headers and section titles
   - Green: Compliant resources and success messages
   - Red: Non-compliant resources, errors, and failures
   - Yellow: Untagged resources and warnings
   - Service-level compliance rates with color coding

### Exit Codes

- `0`: All resources are compliant
- `1`: Non-compliant or untagged resources found, or errors occurred

This makes the tool suitable for CI/CD pipelines and automated compliance checking.

### Comprehensive Resource Discovery for Tag Compliance

The tag compliance checker discovers and validates ALL AWS resources using:

#### Discovery Methods:
1. **Resource Groups Tagging API**: Primary method discovering ALL taggable resources across ALL AWS services
2. **AWS Config Service**: Additional resources and configuration history (if enabled)
3. **CloudTrail Analysis**: Recently created resources from the last 7 days
4. **Service-Specific APIs**: Direct API calls for comprehensive coverage including:
   - CloudWatch Logs (Log Groups)
   - Route53 (Hosted Zones)
   - API Gateway (REST & HTTP APIs)
   - ElastiCache (Cache Clusters)
   - DynamoDB (Tables)
   - SNS/SQS (Topics & Queues)
   - KMS (Customer-managed Keys)
   - Elasticsearch/OpenSearch (Domains)

#### Service Coverage:
**All AWS services are covered** including but not limited to:
- **Compute**: EC2, Lambda, ECS, EKS, Batch, Lightsail
- **Storage**: S3, EBS, EFS, FSx, Storage Gateway
- **Database**: RDS, DynamoDB, ElastiCache, Neptune, DocumentDB
- **Networking**: VPC, Route53, CloudFront, API Gateway, Load Balancers
- **Security**: IAM, KMS, Secrets Manager, Certificate Manager
- **Management**: CloudFormation, Systems Manager, CloudWatch
- **Analytics**: Kinesis, EMR, Glue, Athena, QuickSight
- **Machine Learning**: SageMaker, Comprehend, Rekognition
- **And many more...**

The tool automatically discovers resources from ANY AWS service that supports the Resource Groups Tagging API, making it future-proof as new services are added.

## Output Files

Files are generated with timestamps:
- `aws_resources_YYYYMMDD_HHMMSS.json` - Complete resource inventory
- `aws_resources_YYYYMMDD_HHMMSS.yaml` - Complete resource inventory (YAML)
- `aws_resources_YYYYMMDD_HHMMSS.xlsx` - Enhanced Excel with service sheets and VPC names
- `aws_resources_YYYYMMDD_HHMMSS.csv` - CSV with service column and VPC names
- `comprehensive_tag_compliance_report_YYYYMMDD_HHMMSS.json` - Full compliance report
- `comprehensive_tag_compliance_report_YYYYMMDD_HHMMSS.yaml` - Full compliance report (YAML)

## Enhanced Features Summary

### Resource Discovery Enhancements:
- **4x Discovery Methods**: RGT API + Config + CloudTrail + Service APIs
- **Complete Coverage**: ALL AWS services, not just a subset
- **Automatic Deduplication**: Removes duplicates found by multiple methods
- **Future-Proof**: Discovers new services automatically

### Excel Output Enhancements:
- **Service-Specific Sheets**: Each AWS service gets its own sheet
- **VPC/Subnet Names**: Automatic lookup and inclusion of VPC/subnet names
- **Smart Column Ordering**: Important fields (service, type, region, VPC info) first
- **Enhanced Summary**: Service breakdown with resource types

### Tag Compliance Enhancements:
- **Comprehensive Discovery**: ALL resources across ALL services
- **Service Breakdown**: Compliance rates per AWS service
- **Discovery Attribution**: Shows which method found each resource
- **Enhanced Reporting**: Complete inventory included in compliance reports