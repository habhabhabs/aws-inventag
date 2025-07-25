#!/bin/bash
# AWS Cloud BOM Automation - Quick Start Script
# This script demonstrates the basic usage of all tools

set -e

echo "🚀 AWS Cloud BOM Automation - Quick Start Demo"
echo "=============================================="

# Check if AWS credentials are configured
echo "1. Checking AWS credentials..."
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi
echo "✅ AWS credentials configured"

# Check if IAM policy exists
echo ""
echo "2. Checking IAM permissions..."
echo "   Make sure you've created the IAM policy with:"
echo "   aws iam create-policy --policy-name AWSResourceInventoryReadOnly --policy-document file://config/iam-policy-read-only.json"

# Run basic resource inventory
echo ""
echo "3. Running basic resource inventory..."
python scripts/aws_resource_inventory.py --output examples/basic_inventory

# Run tag compliance check (without config - checks for untagged resources)
echo ""
echo "4. Running tag compliance check (untagged resources only)..."
python scripts/tag_compliance_checker.py --output examples/untagged_check

# Convert to Excel with service sheets
echo ""
echo "5. Converting to Excel with service-specific sheets..."
python scripts/bom_converter.py --input examples/basic_inventory_*.json --output examples/resource_report.xlsx

echo ""
echo "✅ Quick start complete! Check the examples/ directory for outputs:"
echo "   - examples/basic_inventory_*.json - Raw resource data"
echo "   - examples/untagged_check_*.json - Compliance report"
echo "   - examples/resource_report.xlsx - Excel report with service sheets"
echo ""
echo "Next steps:"
echo "   - Create a tag policy using config/tag_policy_example.yaml as template"
echo "   - Run: python scripts/tag_compliance_checker.py --config your_policy.yaml"
echo "   - Upload reports to S3: --s3-bucket your-reports-bucket"