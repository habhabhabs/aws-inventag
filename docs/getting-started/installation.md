---
title: Installation
description: How to install and set up InvenTag
sidebar_position: 2
---

# Installation Guide

## Prerequisites

- **Python 3.8+** - InvenTag requires Python 3.8 or higher
- **AWS CLI** - Configured with appropriate permissions
- **Git** - For cloning the repository

## Installation Methods

### Method 1: Clone from GitHub (Recommended)

```bash
# Clone the repository
git clone https://github.com/habhabhabs/inventag-aws.git
cd inventag-aws

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python inventag_cli.py --help
```

### Method 2: Direct Download

1. Download the latest release from [GitHub Releases](https://github.com/habhabhabs/inventag-aws/releases)
2. Extract the archive
3. Navigate to the extracted directory
4. Install dependencies: `pip install -r requirements.txt`

## AWS Configuration

### Configure AWS CLI

InvenTag uses AWS CLI credentials. Configure them using:

```bash
aws configure
```

Or set environment variables:

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### Required AWS Permissions

InvenTag requires read-only permissions for AWS resources. Here's a minimal IAM policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:Describe*",
                "s3:List*",
                "s3:Get*",
                "rds:Describe*",
                "lambda:List*",
                "lambda:Get*",
                "iam:List*",
                "iam:Get*",
                "cloudformation:Describe*",
                "cloudformation:List*",
                "elasticloadbalancing:Describe*",
                "autoscaling:Describe*",
                "cloudwatch:Describe*",
                "cloudwatch:List*",
                "logs:Describe*",
                "route53:List*",
                "route53:Get*"
            ],
            "Resource": "*"
        }
    ]
}
```

## Verification

Test your installation:

```bash
# Test basic functionality
./inventag.sh --help

# Test AWS connectivity
./inventag.sh --validate-credentials

# Generate a test report
./inventag.sh --create-excel --verbose
```

## Optional Dependencies

### Google Docs Integration

For Google Docs output, install additional dependencies:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Development Dependencies

For development and testing:

```bash
pip install -r requirements-dev.txt
```

## Troubleshooting

### Common Issues

**Python Version Error**
```bash
# Check Python version
python --version
# Should be 3.8 or higher
```

**AWS Credentials Error**
```bash
# Test AWS CLI
aws sts get-caller-identity
```

**Permission Denied**
```bash
# Make scripts executable (Unix/Linux/macOS)
chmod +x inventag.sh
```

**Module Import Errors**
```bash
# Ensure you're in the correct directory
cd inventag-aws
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Next Steps

- Follow the [Quick Start Guide](quick-start.md) to generate your first BOM
- Read the [CLI User Guide](../user-guides/CLI_USER_GUIDE.md) for comprehensive usage
- Check [Configuration Examples](../user-guides/CONFIGURATION_EXAMPLES.md) for advanced setups