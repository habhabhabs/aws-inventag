# 🏷️ InvenTag

> **Professional AWS™ Cloud Governance Platform - Comprehensive resource inventory, compliance checking, and BOM generation**

[![Automated Release](https://github.com/habhabhabs/inventag-aws/workflows/Automated%20Release/badge.svg)](https://github.com/habhabhabs/inventag-aws/actions)
[![Documentation](https://github.com/habhabhabs/inventag-aws/workflows/Documentation%20Deployment/badge.svg)](https://habhabhabs.github.io/inventag-aws/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/habhabhabs/inventag-aws.git
cd inventag-aws
pip install -r requirements.txt

# Generate professional BOM reports with production safety
# The script automatically detects python3/python
./inventag.sh --create-excel --create-word \
  --enable-production-safety --security-validation
```

## ✨ Key Features

- 🛡️ **Production Safety & Security** - Enterprise-grade security validation and compliance standards (SOC 2, PCI, HIPAA, GDPR)
- 📊 **Professional BOM Generation** - Excel/Word/Google Docs reports with logical column ordering and service-specific sheets
- 🔍 **Multi-Account Discovery** - Comprehensive resource scanning across multiple AWS accounts with parallel processing
- 🌐 **Advanced Analysis Suite** - Network security analysis, cost optimization, and security posture assessment
- 🏷️ **Tag Compliance Checking** - Automated validation against organizational tagging policies
- 🔄 **State Management** - Change tracking with delta detection and professional changelog generation
- 🚀 **CI/CD Ready** - Easy integration with automated workflows and S3 upload support
- ⚡ **Flexible Deployment** - Cross-account roles, interactive setup, and comprehensive credential management

## 📖 Documentation

> **🌟 NEW: [Visit our comprehensive documentation site →](https://habhabhabs.github.io/inventag-aws/)**
>
> We've migrated to a modern documentation platform with enhanced search, mobile-responsive design, and improved navigation. The documentation is automatically deployed from the `docs/` directory and stays synchronized with GitHub.

### Quick Links

- **[📖 User Guides](https://habhabhabs.github.io/inventag-aws/user-guides/cli-user-guide)** - CLI reference and examples
- **[🚀 Getting Started](https://habhabhabs.github.io/inventag-aws/getting-started/quick-start)** - Installation and quick start
- **[📋 Configuration Examples](https://habhabhabs.github.io/inventag-aws/user-guides/configuration-examples)** - Working configuration examples
- **[🛡️ Production Safety](https://habhabhabs.github.io/inventag-aws/user-guides/production-safety)** - Security and compliance features
- **[🏗️ Architecture](https://habhabhabs.github.io/inventag-aws/architecture/core-module-integration)** - System architecture and design
- **[🔧 Development](https://habhabhabs.github.io/inventag-aws/development/CONTRIBUTING)** - Contributing guide

### Legacy Documentation

For offline reference, documentation is also available in the `docs/` directory:

- **[CLI User Guide](docs/user-guides/cli-user-guide.md)** - Local CLI reference
- **[Quick Start Guide](docs/getting-started/quick-start.md)** - Local installation guide
- **[All Local Documentation](docs/)** - Complete documentation directory

## 💼 Enterprise Examples

```bash
# Multi-account BOM with comprehensive analysis
./inventag.sh --accounts-file accounts.json \
  --create-excel --create-word \
  --tag-mappings config/defaults/mappings/tag_to_column_mappings_example.yaml \
  --service-descriptions config/defaults/services/service_descriptions_example.yaml \
  --enable-network-analysis --enable-security-analysis \
  --compliance-standard soc2 --s3-bucket enterprise-reports

# Interactive multi-account setup with advanced features
./inventag.sh --accounts-prompt \
  --create-excel --create-google-docs \
  --tag-mappings config/defaults/mappings/tag_to_column_mappings_example.yaml \
  --enable-cost-analysis --generate-changelog

# Cross-account role with production safety
./inventag.sh --cross-account-role InvenTagRole \
  --create-excel --enable-production-safety \
  --security-validation --audit-output security-audit.json

# CI/CD integration with comprehensive reporting
./inventag.sh --accounts-file accounts.json \
  --create-excel --create-word \
  --s3-bucket reports-bucket --s3-key-prefix daily-reports/ \
  --max-concurrent-accounts 8 --per-account-reports
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

See [Production Safety Guide](https://habhabhabs.github.io/inventag-aws/user-guides/production-safety) for complete details.

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