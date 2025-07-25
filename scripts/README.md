# Scripts

This directory contains the main AWS Cloud BOM Automation tools.

## Scripts

### `aws_resource_inventory.py`
**Comprehensive AWS resource discovery** across all services and regions.

**Features:**
- Discovers ALL AWS resources using multiple methods
- Supports all AWS regions with automatic fallback
- Multiple output formats (JSON, YAML)
- Optional Excel export and S3 upload

**Usage:**
```bash
# Basic usage - discovers all resources
python scripts/aws_resource_inventory.py

# With Excel export
python scripts/aws_resource_inventory.py --export-excel

# Specific regions only  
python scripts/aws_resource_inventory.py --regions us-east-1 eu-west-1

# Upload to S3
python scripts/aws_resource_inventory.py --s3-bucket reports-bucket
```

### `tag_compliance_checker.py`
**Comprehensive tag compliance validation** against your organization's policies.

**Features:**
- Discovers ALL AWS resources across ALL services
- Validates against custom tag policies
- Service-by-service compliance breakdown
- Color-coded console output with detailed reporting

**Usage:**
```bash
# Check for untagged resources only
python scripts/tag_compliance_checker.py

# Use custom tag policy
python scripts/tag_compliance_checker.py --config config/tag_policy_example.yaml

# Upload compliance report
python scripts/tag_compliance_checker.py --config my_policy.yaml --s3-bucket compliance-reports
```

### `bom_converter.py`
**Professional Excel/CSV report generator** with enhanced formatting.

**Features:**
- Separate Excel sheets per AWS service
- Automatic VPC/subnet name enrichment
- Professional formatting with color-coded headers
- CSV export with service column

**Usage:**
```bash
# Convert to Excel with service sheets
python scripts/bom_converter.py --input data.json --output report.xlsx

# Convert to CSV
python scripts/bom_converter.py --input data.json --output report.csv --format csv

# Skip VPC enrichment for faster processing
python scripts/bom_converter.py --input data.json --output fast_report.xlsx --no-vpc-enrichment
```

## Requirements

All scripts require:
- Python 3.7+
- AWS credentials configured (`aws configure`)
- Required Python packages (`pip install -r requirements.txt`)
- Appropriate IAM permissions (`config/iam-policy-read-only.json`)

## Common Options

All scripts support these common options:
- `--verbose` - Detailed logging output
- `--regions LIST` - Specify regions to scan
- `--output NAME` - Custom output filename
- `--s3-bucket BUCKET` - Upload results to S3

## Integration

These scripts are designed to work together:

1. **Discover resources**: `aws_resource_inventory.py`
2. **Check compliance**: `tag_compliance_checker.py --config policy.yaml`  
3. **Generate reports**: `bom_converter.py --input results.json --output report.xlsx`

Or use the automated quick start: `examples/quick_start.sh`