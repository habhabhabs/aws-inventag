# 🏷️ InvenTag

> **Professional AWS™ Cloud Governance Platform - Comprehensive resource inventory, compliance checking, and BOM generation**

[![Automated Release](https://github.com/habhabhabs/inventag-aws/workflows/Automated%20Release/badge.svg)](https://github.com/habhabhabs/inventag-aws/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/habhabhabs/inventag-aws.git
cd inventag-aws
pip install -r requirements.txt

# Generate professional BOM reports with production safety
python -m inventag.cli.main --create-excel --create-word \
  --enable-production-safety --security-validation
```

## ✨ Key Features

- 🛡️ **Production Safety & Security** - Enterprise-grade security validation and compliance standards (SOC 2, PCI, HIPAA, GDPR)
- 📊 **Professional BOM Generation** - Excel/Word/CSV reports with logical column ordering and service-specific sheets
- 🔍 **Multi-Account Discovery** - Comprehensive resource scanning across multiple AWS accounts with parallel processing
- 🌐 **Network & Security Analysis** - VPC/subnet analysis with security posture assessment and cost optimization
- 🏷️ **Tag Compliance Checking** - Automated validation against organizational tagging policies
- 🔄 **State Management** - Change tracking with delta detection and professional changelog generation
- 🚀 **CI/CD Ready** - Easy integration with automated workflows and S3 upload support

## 📖 Documentation

- **[📖 Complete User Guide](docs/user-guides/CLI_USER_GUIDE.md)** - Comprehensive CLI reference and examples
- **[🚀 Quick Start Examples](examples/README.md)** - Working configuration examples  
- **[🛡️ Production Safety Guide](docs/user-guides/PRODUCTION_SAFETY.md)** - Security and compliance features
- **[⚙️ Configuration Guide](docs/user-guides/CONFIGURATION_EXAMPLES.md)** - Setup and customization
- **[🔧 Troubleshooting](docs/user-guides/TROUBLESHOOTING_GUIDE.md)** - Common issues and solutions
- **[📚 All Documentation](docs/README.md)** - Complete documentation index

## 💼 Enterprise Examples

```bash
# Multi-account BOM with comprehensive analysis
python -m inventag.cli.main --accounts-file accounts.json \
  --create-excel --enable-network-analysis --enable-security-analysis \
  --compliance-standard soc2 --s3-bucket enterprise-reports

# Production monitoring with audit logging
python scripts/production/production_monitor.py \
  --operations ec2:describe_instances s3:list_buckets \
  --report-output compliance-audit.json

# Security validation with risk assessment
python scripts/production/security_validator.py \
  --compliance-standard soc2 --audit-output security-audit.json
```

## 🏗️ Project Structure

```text
inventag-aws/
├── README.md                    # This overview
├── inventag/                    # Core Python package
│   ├── cli/                     # Unified CLI interface
│   ├── core/                    # Core orchestration
│   ├── discovery/               # Resource discovery
│   ├── compliance/              # Security & compliance
│   ├── reporting/               # BOM generation
│   └── state/                   # Change management
├── docs/                        # Complete documentation
├── examples/                    # Configuration examples
├── config/                      # Default configurations
├── scripts/                     # Standalone tools
└── tests/                       # Comprehensive test suite
```

## 🛡️ Security & Compliance

InvenTag includes enterprise-grade security features:

- **Read-Only Enforcement** - All operations are strictly read-only by default
- **Compliance Standards** - Built-in support for SOC 2, PCI, HIPAA, GDPR
- **Audit Logging** - Comprehensive audit trails for all operations
- **Risk Assessment** - Automated security risk evaluation
- **Production Safety** - Real-time monitoring and validation

See [Production Safety Guide](docs/user-guides/PRODUCTION_SAFETY.md) for complete details.

## 🔗 Support & Community

- **[🐛 Issues](https://github.com/habhabhabs/inventag-aws/issues)** - Bug reports and feature requests
- **[💬 Discussions](https://github.com/habhabhabs/inventag-aws/discussions)** - Community Q&A
- **[📋 Wiki](https://github.com/habhabhabs/inventag-aws/wiki)** - Additional resources

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

> **InvenTag** - Professional AWS™ cloud governance made simple
>
> *AWS™ is a trademark of Amazon Web Services, Inc. InvenTag is an independent tool and is not affiliated with, endorsed by, or sponsored by Amazon Web Services, Inc.*