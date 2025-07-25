# AWS Cloud BOM Automation

**Comprehensive AWS resource discovery and tag compliance tools with Excel reporting.**

Discovers ALL AWS resources across ALL services and validates them against your tagging policies. Generates professional Excel reports with separate sheets per service.

## 📁 Project Structure

```
aws-cloud-bom-automation/
├── README.md                    # This file - main documentation
├── requirements.txt             # Python dependencies
├── scripts/                     # Main tools
│   ├── aws_resource_inventory.py      # Resource discovery
│   ├── tag_compliance_checker.py      # Tag validation  
│   ├── bom_converter.py               # Excel/CSV generator
│   └── README.md                      # Script documentation
├── config/                      # Configuration files
│   ├── iam-policy-read-only.json      # Required IAM permissions
│   ├── tag_policy_example.yaml        # Example tag policy
│   ├── tag_policy_example.json        # Example tag policy (JSON)
│   └── README.md                      # Config documentation
├── docs/                        # Detailed documentation
│   └── SECURITY.md                    # Security guide & permissions
└── examples/                    # Examples and outputs
    ├── quick_start.sh                 # Automated demo script
    └── README.md                      # Usage examples
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure AWS Credentials
```bash
aws configure
# OR set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
```

### 3. Set Up Permissions
```bash
aws iam create-policy --policy-name AWSResourceInventoryReadOnly --policy-document file://config/iam-policy-read-only.json
aws iam attach-user-policy --user-name YOUR_USER --policy-arn arn:aws:iam::ACCOUNT:policy/AWSResourceInventoryReadOnly
```

### 4. Run the Demo
```bash
./examples/quick_start.sh
```

**Or run tools individually:**
```bash
# Basic resource inventory
python scripts/aws_resource_inventory.py

# Tag compliance check
python scripts/tag_compliance_checker.py --config config/tag_policy_example.yaml

# Convert to Excel with service sheets
python scripts/bom_converter.py --input examples/basic_inventory_*.json --output examples/report.xlsx
```

## 📋 Main Tools

### 🔍 **Resource Inventory** (`scripts/aws_resource_inventory.py`)
Discovers ALL AWS resources across your account.

```bash
# Discover all resources in all regions
python scripts/aws_resource_inventory.py

# Export to Excel automatically  
python scripts/aws_resource_inventory.py --export-excel

# Upload to S3
python scripts/aws_resource_inventory.py --s3-bucket my-reports-bucket
```

### 🏷️ **Tag Compliance** (`scripts/tag_compliance_checker.py`)
Validates ALL resources against your tagging policies.

```bash
# Check for untagged resources only
python scripts/tag_compliance_checker.py

# Use your tagging policy
python scripts/tag_compliance_checker.py --config config/tag_policy_example.yaml

# Get compliance report with S3 upload
python scripts/tag_compliance_checker.py --config my_policy.yaml --s3-bucket compliance-reports
```

### 📊 **BOM Converter** (`scripts/bom_converter.py`)
Converts JSON/YAML to professional Excel reports.

```bash
# Create Excel with service-specific sheets
python scripts/bom_converter.py --input inventory.json --output report.xlsx

# Create CSV with service column
python scripts/bom_converter.py --input inventory.json --output report.csv --format csv
```

## 🏷️ Tag Policy Configuration

Create your own tag policy by copying and editing the example:

```bash
cp config/tag_policy_example.yaml my_tag_policy.yaml
# Edit my_tag_policy.yaml with your requirements
```

**Example policy structure:**
```yaml
required_tags:
  - "Environment"      # Any value allowed
  - "Owner"
  - "Project" 
  
  # Specific allowed values
  - key: "Environment"
    allowed_values: ["production", "staging", "development"]
  
  - key: "CostCenter"
    required_values: ["engineering", "marketing", "finance"]
```

## 📊 Excel Output Features

- **Service-Specific Sheets**: Each AWS service gets its own sheet (EC2, S3, RDS, etc.)
- **VPC/Subnet Names**: Automatic lookup and inclusion from resource tags
- **Professional Formatting**: Color-coded headers, auto-sized columns
- **Summary Dashboard**: Overview with service breakdown and statistics

## 🔐 Security

**✅ 100% READ-ONLY**: Cannot modify your AWS infrastructure  
**✅ MINIMAL PERMISSIONS**: Only requires read access to AWS services  
**✅ PRODUCTION SAFE**: Designed for safe execution in production environments

See [`docs/SECURITY.md`](docs/SECURITY.md) for detailed security information.

## 🌍 Region Handling

- **Default**: Scans ALL AWS regions automatically
- **Fallback**: Uses us-east-1 and ap-southeast-1 if region discovery fails
- **Custom**: Specify specific regions with `--regions us-east-1 eu-west-1`

## ⚡ Common Use Cases

### Monthly Resource Audit
```bash
python scripts/aws_resource_inventory.py --export-excel --s3-bucket monthly-reports
```

### Tag Compliance Monitoring
```bash
python scripts/tag_compliance_checker.py --config config/production_tags.yaml --s3-bucket compliance-reports
```

### Cost Center Reporting
```bash
python scripts/aws_resource_inventory.py
python scripts/bom_converter.py --input aws_resources_*.json --output cost_center_report.xlsx
```

### Security Audit Preparation
```bash
python scripts/tag_compliance_checker.py --config config/security_tags.yaml --verbose
```

## 🛠️ Advanced Options

### Resource Inventory
- `--regions us-east-1 eu-west-1` - Scan specific regions only
- `--format yaml` - Output in YAML format
- `--s3-bucket BUCKET --s3-key path/file.json` - Custom S3 upload
- `--export-excel` - Auto-generate Excel report
- `--verbose` - Detailed logging

### Tag Compliance
- `--config FILE` - Use custom tag policy
- `--regions LIST` - Check specific regions
- `--format yaml` - YAML output format
- `--s3-bucket BUCKET` - Upload compliance report
- `--verbose` - Show detailed progress

### BOM Converter
- `--format csv` - Export as CSV instead of Excel
- `--no-vpc-enrichment` - Skip VPC/subnet name lookup (faster)

## 📦 Dependencies

- **boto3** - AWS SDK
- **PyYAML** - YAML support
- **openpyxl** - Excel generation
- **colorama** - Colored output

## 🆘 Troubleshooting

**"No credentials found"**  
→ Run `aws configure` or set environment variables

**"Access denied for service X"**  
→ Update IAM policy with permissions for that service

**"No resources found"**  
→ Check if you have any resources in the scanned regions

**Excel export fails**  
→ Install openpyxl: `pip install openpyxl`

## 📁 Output Files

All files include timestamps for easy tracking:
- `aws_resources_YYYYMMDD_HHMMSS.json` - Complete inventory
- `aws_resources_YYYYMMDD_HHMMSS.xlsx` - Excel with service sheets
- `tag_compliance_report_YYYYMMDD_HHMMSS.json` - Compliance results

## 🏢 Enterprise Features

- **Multi-account support** via cross-account roles
- **Automated scheduling** via AWS Lambda or cron
- **Integration** with CMDB/ITSM systems via S3 uploads
- **Compliance reporting** for SOC2, PCI-DSS, HIPAA audits
- **Cost optimization** through resource discovery and tagging

---

## 📚 Documentation

- **[Security Guide](docs/SECURITY.md)** - Detailed permissions and security info
- **[Configuration Guide](config/README.md)** - Tag policies and IAM setup
- **[Script Documentation](scripts/README.md)** - Detailed script usage
- **[Examples](examples/README.md)** - Usage patterns and outputs

**Quick help:** Run `./examples/quick_start.sh` for an automated demo of all features!