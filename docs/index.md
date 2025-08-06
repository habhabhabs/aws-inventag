---
title: InvenTag Documentation
description: Complete documentation for InvenTag AWS Cloud Governance Platform
sidebar_position: 1
---

# 🏷️ InvenTag

> **Professional AWS™ Cloud Governance Platform - Comprehensive resource inventory, compliance checking, and BOM generation**

[![Automated Release](https://github.com/habhabhabs/inventag-aws/workflows/Automated%20Release/badge.svg)](https://github.com/habhabhabs/inventag-aws/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![InvenTag Logo](assets/images/inventag-logo-placeholder.svg)

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

See [Production Safety Guide](user-guides/production-safety) for complete details.

## 🚀 Getting Started

New to InvenTag? Start here to get up and running quickly.

- **[Introduction](getting-started/introduction)** - Overview of InvenTag and its key features
- **[Installation](getting-started/installation)** - How to install and set up InvenTag
- **[Quick Start Guide](getting-started/quick-start)** - Get started in minutes with basic examples

## 📖 User Guides

Comprehensive guides for using InvenTag in different scenarios.

- **[CLI User Guide](user-guides/cli-user-guide)** - Comprehensive CLI reference and usage examples
- **[Configuration Examples](user-guides/configuration-examples)** - Setup and configuration guidance
- **[Production Safety Guide](user-guides/production-safety)** - Security, compliance, and safety features
- **[Troubleshooting Guide](user-guides/troubleshooting-guide)** - Common issues and solutions

## 🏗️ Architecture & Technical Design

Technical documentation for developers and system architects.

- **[Core Module Integration](architecture/core-module-integration)** - System architecture overview
- **[State Management](architecture/state-management)** - Change tracking and delta detection
- **[Template Framework](architecture/template-framework)** - Document generation system
- **[Service Enrichment](architecture/service-enrichment)** - AWS service attribute enhancement
- **[BOM Data Processor](architecture/bom-data-processor)** - Data processing pipeline
- **[Network Analysis](architecture/network-analysis)** - VPC and network analysis capabilities
- **[Cost Analysis](architecture/cost-analysis)** - Cost estimation and optimization
- **[Tag Compliance](architecture/tag-compliance)** - Compliance checking framework

## 🛠️ Development & Deployment

Resources for developers contributing to InvenTag or deploying it in production.

- **[Contributing Guide](development/CONTRIBUTING)** - Development setup and guidelines
- **[Deployment Guide](development/DEPLOYMENT)** - Production deployment instructions
- **[CI/CD Integration](development/cicd-integration)** - Pipeline integration examples
- **[Security Guide](development/SECURITY)** - Security best practices
- **[Backward Compatibility](development/backward-compatibility)** - Version compatibility matrix
- **[Migration Guide](development/bom-migration-guide)** - Upgrade and migration procedures

## 📖 Documentation

- **[📖 Complete User Guide](user-guides/cli-user-guide)** - Comprehensive CLI reference and examples
- **[🚀 Quick Start Guide](getting-started/quick-start)** - Get started in minutes
- **[📋 Configuration Examples](examples/)** - Working configuration examples  
- **[🛡️ Production Safety Guide](user-guides/production-safety)** - Security and compliance features
- **[⚙️ Configuration Guide](user-guides/configuration-examples)** - Setup and customization
- **[🔧 Troubleshooting](user-guides/troubleshooting-guide)** - Common issues and solutions

## 🚀 Quick Navigation

- **New User?** Start with [Introduction](getting-started/introduction) and [Quick Start Guide](getting-started/quick-start)
- **Setting Up?** Check [Installation](getting-started/installation) and [Configuration Examples](user-guides/configuration-examples)  
- **Production Deployment?** See [Production Safety Guide](user-guides/production-safety) and [Deployment Guide](development/DEPLOYMENT)
- **Having Issues?** Visit [Troubleshooting Guide](user-guides/troubleshooting-guide)
- **Developer?** Read [Contributing Guide](development/CONTRIBUTING)

## 🔗 Support & Community

- **[🐛 Issues](https://github.com/habhabhabs/inventag-aws/issues)** - Bug reports and feature requests
- **[💬 Discussions](https://github.com/habhabhabs/inventag-aws/discussions)** - Community Q&A
- **[📋 Wiki](https://github.com/habhabhabs/inventag-aws/wiki)** - Additional resources

## 📄 License

MIT License - see the [LICENSE](https://github.com/habhabhabs/inventag-aws/blob/main/LICENSE) file for details.

---

> **InvenTag** - Professional AWS™ cloud governance made simple
>
> *AWS™ is a trademark of Amazon Web Services, Inc. InvenTag is an independent tool and is not affiliated with, endorsed by, or sponsored by Amazon Web Services, Inc.*

## 📋 Documentation Standards

All documentation follows consistent formatting and includes:
- Clear examples with working code
- Step-by-step procedures
- Troubleshooting sections
- Cross-references to related topics
- Regular updates with each release
