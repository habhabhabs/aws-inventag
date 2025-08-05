# 📋 InvenTag Scripts

Standalone scripts for various InvenTag operations.

## 🛡️ Production Scripts
**Recommended for production environments**

- **[production_monitor.py](production/production_monitor.py)** - Real-time production safety monitoring
- **[security_validator.py](production/security_validator.py)** - Security validation for AWS operations  
- **[multi_account_scanner.py](production/multi_account_scanner.py)** - Comprehensive multi-account resource scanning

### Usage
```bash
# Production monitoring with compliance reporting
python scripts/production/production_monitor.py \
  --operations ec2:describe_instances s3:list_buckets \
  --report-output production-compliance.json

# Security validation with audit logging
python scripts/production/security_validator.py \
  --compliance-standard soc2 --audit-output security-audit.json

# Multi-account comprehensive scanning
python scripts/production/multi_account_scanner.py \
  --accounts-file accounts.json --output-format excel
```

## 🔧 Development Scripts
**For development and testing**

- **[cicd_bom_generation.py](development/cicd_bom_generation.py)** - CI/CD pipeline BOM generation

### Usage
```bash
# CI/CD BOM generation
python scripts/development/cicd_bom_generation.py \
  --config cicd-config.json --output build/
```

## 📚 Legacy Scripts
**Deprecated - Use unified CLI instead**

- **[aws_resource_inventory.py](legacy/aws_resource_inventory.py)** - ⚠️ Use `python -m inventag.cli.main --create-excel` instead
- **[bom_converter.py](legacy/bom_converter.py)** - ⚠️ Use `python -m inventag.cli.main --create-excel` instead  
- **[tag_compliance_checker.py](legacy/tag_compliance_checker.py)** - ⚠️ Use `python -m inventag.cli.main --compliance-standard` instead

### Migration Notice
These legacy scripts are maintained for backward compatibility but are deprecated. 
Please migrate to the unified CLI interface:

```bash
# Instead of legacy scripts, use:
python -m inventag.cli.main --create-excel --create-word \
  --enable-production-safety --security-validation
```

## 📖 Documentation
For complete documentation, see:
- **[CLI User Guide](../docs/user-guides/CLI_USER_GUIDE.md)** - Complete command reference
- **[Production Safety Guide](../docs/user-guides/PRODUCTION_SAFETY.md)** - Security and compliance features
- **[Configuration Examples](../docs/user-guides/CONFIGURATION_EXAMPLES.md)** - Setup and configuration