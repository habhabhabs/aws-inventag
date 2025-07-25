# Examples

This directory contains example scripts and will store output files from your runs.

## Files

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

## Output Files

After running the tools, you'll find timestamped output files here:

- `basic_inventory_YYYYMMDD_HHMMSS.json` - Complete resource inventory
- `untagged_check_YYYYMMDD_HHMMSS.json` - Resources without tags
- `resource_report.xlsx` - Excel report with service-specific sheets

## Common Usage Patterns

### Monthly Resource Audit
```bash
python scripts/aws_resource_inventory.py --export-excel --output examples/monthly_audit
```

### Tag Compliance Check
```bash
python scripts/tag_compliance_checker.py --config config/tag_policy_example.yaml --output examples/compliance_check
```

### Custom Region Scan
```bash
python scripts/aws_resource_inventory.py --regions us-east-1 eu-west-1 --output examples/custom_regions
```

### S3 Upload
```bash
python scripts/aws_resource_inventory.py --s3-bucket my-reports-bucket --s3-key monthly/$(date +%Y-%m)/inventory.json
```

## Pro Tips

- **Timestamped files**: All outputs include timestamps for easy tracking
- **Excel reports**: Use the BOM converter for professional Excel reports with service sheets
- **VPC enrichment**: Excel reports automatically include VPC and subnet names
- **Compliance tracking**: Tag compliance reports show exactly which resources need attention