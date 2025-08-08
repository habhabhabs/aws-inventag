---
title: AWS Prescriptive Guidance Templates
description: Professional templates following AWS Prescriptive Guidance for Cost Allocation Tagging
sidebar_position: 2
---

# 🏛️ AWS Prescriptive Guidance Templates

Professional templates designed following [AWS Prescriptive Guidance for Cost Allocation Tagging](https://docs.aws.amazon.com/prescriptive-guidance/latest/cost-allocation-tagging/) to enable comprehensive financial governance, cost allocation, and compliance reporting.

## 🎯 Overview

These templates implement AWS best practices for:

- **Cost Allocation Tagging** - Comprehensive tag dictionary with validation rules
- **Financial Governance** - Multi-level cost allocation hierarchy 
- **Compliance Frameworks** - SOC 2, PCI, HIPAA, GDPR integration
- **Operational Excellence** - Automation, monitoring, and governance

## 📋 Available Templates

### 1. Tagging Dictionary Template
**File**: [tagging-dictionary.yaml](/files/tagging-dictionary.yaml)

Comprehensive tag definitions following AWS prescriptive guidance:

```yaml
# Required Tags (Financial Management)
- CostCenter: "CC-1001" 
- Project: "PROJ-2024-WEBAPP"
- BusinessUnit: "Engineering"
- Environment: "prod"
- Application: "user-authentication-service"

# Recommended Tags
- TeamName: "Platform Engineering"
- ContactEmail: "platform-team@company.com"
- DataClassification: "confidential"
- BackupRequired: "true"

# Conditional Tags (Environment-Specific)
- MaintenanceWindow: "Sunday-0200-0400" (Production only)
- SLALevel: "gold" (Production only)
- ComplianceFramework: "soc2" (Production only)
```

**Key Features:**
- ✅ Validation patterns and rules
- ✅ Cost allocation hierarchy
- ✅ Governance framework integration
- ✅ Industry-specific configurations
- ✅ Exception handling processes

### 2. Service Descriptions Template  
**File**: [service-descriptions.yaml](/files/service-descriptions.yaml)

Enhanced service descriptions with cost allocation focus:

```yaml
services:
  ec2:
    cost_allocation_priority: "high"
    required_tags: ["CostCenter", "Project", "Environment", "BusinessUnit", "Application"]
    cost_factors:
      - "Instance type and size"
      - "Reserved vs On-Demand pricing"
      - "EBS storage attached"
    governance_notes: "Critical for cost optimization - enable detailed monitoring"
    
  s3:
    cost_allocation_priority: "high" 
    cost_factors:
      - "Storage class (Standard, IA, Glacier)"
      - "Data transfer costs"
      - "Request costs (GET, PUT, DELETE)"
    governance_notes: "Implement lifecycle policies for optimal spend visibility"
```

**Key Features:**
- 🎯 Cost allocation priorities per service
- 💰 Detailed cost factor analysis
- 🏷️ Service-specific tagging requirements
- 📊 Industry template configurations
- 🔧 Automation recommendations

### 3. Tag Mappings Template
**File**: [tag-mappings.yaml](/files/tag-mappings.yaml)

Financial governance optimized column mappings:

```yaml
financial_governance:
  cost_center:
    tag_key: "CostCenter"
    column_name: "Cost Center"
    column_order: 1
    required: true
    validation_pattern: "^CC-[0-9]{4}$"
    report_grouping: "primary"
    
organizational:
  business_unit:
    tag_key: "BusinessUnit" 
    column_name: "Business Unit"
    column_order: 5
    required: true
    report_grouping: "primary"
```

**Key Features:**
- 📈 Multi-level cost allocation hierarchy
- 📊 Executive and operational dashboards
- ✅ Comprehensive validation rules
- 🎨 Professional report formatting
- 📋 Compliance audit configurations

## 🚀 Quick Start

### 1. Download Templates

```bash
# Download all AWS Prescriptive Guidance templates
curl -O https://habhabhabs.github.io/inventag-aws/files/tagging-dictionary.yaml
curl -O https://habhabhabs.github.io/inventag-aws/files/service-descriptions.yaml  
curl -O https://habhabhabs.github.io/inventag-aws/files/tag-mappings.yaml
```

### 2. Generate Cost Allocation Reports

```bash
# Basic cost allocation reporting
./inventag.sh --accounts-file accounts.json \
  --create-excel --create-word \
  --tag-mappings config/aws-prescriptive-guidance/tag-mappings.yaml \
  --service-descriptions config/aws-prescriptive-guidance/service-descriptions.yaml \
  --compliance-standard aws-prescriptive-guidance

# Advanced financial governance reporting
./inventag.sh --accounts-file accounts.json \
  --create-excel --create-word \
  --tag-mappings config/aws-prescriptive-guidance/tag-mappings.yaml \
  --service-descriptions config/aws-prescriptive-guidance/service-descriptions.yaml \
  --enable-cost-analysis --enable-governance-reporting \
  --cost-allocation-focus --financial-governance \
  --budget-tracking --chargeback-reporting
```

### 3. Validate Tag Compliance

```bash
# Check tag compliance against AWS Prescriptive Guidance
./inventag.sh --accounts-file accounts.json \
  --validate-tags \
  --tagging-dictionary config/aws-prescriptive-guidance/tagging-dictionary.yaml \
  --compliance-report compliance-audit.json \
  --governance-dashboard
```

## 📊 Cost Allocation Hierarchy

The templates implement a 4-level cost allocation hierarchy following AWS best practices:

```text
Level 1: Business Unit
├── Level 2: Cost Center  
│   ├── Level 3: Project
│   │   └── Level 4: Application
│   └── Level 3: Project
│       └── Level 4: Application
└── Level 2: Cost Center
    └── Level 3: Project
        └── Level 4: Application
```

**Example Hierarchy:**
- **Business Unit**: Engineering
  - **Cost Center**: CC-1001 (Platform Team)
    - **Project**: PROJ-2024-WEBAPP
      - **Application**: user-authentication-service
      - **Application**: payment-processing-api
    - **Project**: PROJ-2024-MOBILE
      - **Application**: mobile-app-backend

## 🎯 Compliance Frameworks

### Financial Governance
- **Cost Center Attribution** - Mandatory for all resources
- **Project-Based Allocation** - Detailed project cost tracking
- **Budget Category Mapping** - Infrastructure, Development, Operations, Security
- **Chargeback Integration** - Internal billing and cost recovery

### Security and Compliance
- **SOC 2** - System and Organization Controls
- **PCI DSS** - Payment Card Industry Data Security Standard  
- **HIPAA** - Health Insurance Portability and Accountability Act
- **GDPR** - General Data Protection Regulation

### Operational Excellence
- **SLA-Based Classifications** - Gold, Silver, Bronze service levels
- **Automated Governance** - Tag policies and Service Control Policies
- **Monitoring and Alerting** - Cost anomaly detection and compliance dashboards
- **Lifecycle Management** - Data retention and backup policies

## 🏭 Industry Templates

### Financial Services
```yaml
additional_tags: 
  - "ComplianceFramework"
  - "DataClassification" 
  - "RegulatoryConcern"
enhanced_governance: true
retention_requirements: "7 years"
```

### Healthcare
```yaml
additional_tags:
  - "PHI_Status"
  - "HIPAA_Applicable"
  - "PatientData"
enhanced_security: true
encryption_required: true
```

### Government  
```yaml
additional_tags:
  - "SecurityLevel"
  - "AuthorityToOperate"
  - "FISMA_Level"
enhanced_compliance: true
audit_trail_required: true
```

## 🔧 Implementation Roadmap

### Phase 1: Foundation (30 days)
- ✅ Deploy tagging dictionary
- ✅ Implement required tags on production resources
- ✅ Setup basic cost allocation reporting
- 🎯 **Target**: 90% compliance on required tags

### Phase 2: Enhancement (60 days)  
- ✅ Add recommended tags across all environments
- ✅ Deploy governance automation (SCPs, Tag Policies)
- ✅ Setup monitoring dashboards
- 🎯 **Target**: 85% compliance on recommended tags

### Phase 3: Optimization (30 days)
- ✅ Full enforcement with conditional tags
- ✅ Advanced cost allocation and chargeback
- ✅ Compliance audit automation
- 🎯 **Target**: 95% overall compliance

## 📈 Expected Outcomes

### Cost Visibility
- **Granular Cost Tracking** - Project and application level visibility
- **Budget Accountability** - Clear cost center responsibility
- **Trend Analysis** - Historical cost patterns and forecasting
- **Optimization Opportunities** - Right-sizing and scheduling recommendations

### Governance Benefits
- **Automated Compliance** - Continuous policy enforcement
- **Audit Readiness** - Complete resource attribution and tracking
- **Risk Mitigation** - Data classification and security controls
- **Operational Excellence** - Standardized resource management

### Financial Impact
- **15-30% Cost Reduction** - Through better visibility and optimization
- **Accurate Chargeback** - Fair cost allocation across business units
- **Budget Planning** - Data-driven financial planning
- **ROI Tracking** - Project-level return on investment analysis

## 🛠️ Tools and Automation

### Native AWS Tools
- **AWS Cost Explorer** - Cost analysis and reporting
- **AWS Budgets** - Budget alerts and controls
- **AWS Tag Policies** - Centralized tag governance
- **Service Control Policies** - Preventive controls
- **AWS Config Rules** - Compliance monitoring

### Third-Party Integration
- **CloudHealth** - Advanced cost management
- **CloudCheckr** - Governance and optimization
- **Terraform** - Infrastructure as Code with tags
- **InvenTag AWS** - Comprehensive discovery and reporting

## 📚 Additional Resources

### AWS Documentation
- [AWS Prescriptive Guidance: Cost Allocation Tagging](https://docs.aws.amazon.com/prescriptive-guidance/latest/cost-allocation-tagging/)
- [AWS Tagging Best Practices](https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html)
- [AWS Cost Management User Guide](https://docs.aws.amazon.com/cost-management/)

### InvenTag Resources
- [Getting Started Guide](/getting-started/quick-start)
- [CLI User Guide](/user-guides/cli-user-guide)
- [Configuration Examples](/examples/)
- [Production Safety Guide](/user-guides/production-safety)

## 🤝 Support and Community

Need help implementing AWS Prescriptive Guidance templates?

- **📖 Documentation**: Complete guides and examples
- **🐛 Issues**: [GitHub Issues](https://github.com/habhabhabs/inventag-aws/issues)
- **💬 Discussions**: [Community Q&A](https://github.com/habhabhabs/inventag-aws/discussions)
- **📧 Enterprise Support**: Contact your AWS Solutions Architect

---

**Ready to transform your AWS cost allocation and governance?** Start with our [Quick Start Guide](/getting-started/quick-start) and download the professional templates above.