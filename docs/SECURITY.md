# Security Documentation

## 🔒 Read-Only Operation Guarantee

This document provides detailed security information about the AWS Cloud BOM Automation tools.

### **Verified Read-Only Operations**

All scripts have been audited and **only perform read-only operations**:

#### ✅ **Allowed Operations (Read-Only)**
- `describe_*` - Get detailed information about resources
- `list_*` - List resources and their basic information  
- `get_*` - Retrieve specific resource data and configurations
- `lookup_*` - Search for events and historical data

#### ❌ **Prohibited Operations (None Present)**
- `create_*` - Create new resources
- `update_*` - Modify existing resources
- `delete_*` - Remove resources
- `put_*` - Upload or modify data (except optional S3 report upload)
- `modify_*` - Change resource configurations
- `attach_*` / `detach_*` - Modify resource associations
- `associate_*` / `disassociate_*` - Change network associations

### **Code Audit Results**

**Files Audited:**
- `aws_resource_inventory.py` - ✅ Read-only verified
- `tag_compliance_checker.py` - ✅ Read-only verified  
- `bom_converter.py` - ✅ Local file operations only

**Only Write Operation:**
- `s3.put_object()` - Used only for optional report upload to S3

## 📋 IAM Permission Requirements

### **Minimum Required Permissions**

The tools require the following read-only permissions:

#### **Core EC2 Permissions**
```json
"ec2:DescribeRegions",
"ec2:DescribeInstances", 
"ec2:DescribeVolumes",
"ec2:DescribeSecurityGroups",
"ec2:DescribeVpcs",
"ec2:DescribeSubnets"
```

#### **Resource Groups Tagging API** (Primary Discovery)
```json
"resourcegroupstaggingapi:GetResources"
```
*This single permission enables discovery of ALL taggable resources across ALL AWS services*

#### **Service-Specific Permissions**
```json
"s3:ListAllMyBuckets",
"s3:GetBucketLocation", 
"s3:GetBucketTagging",
"rds:DescribeDBInstances",
"rds:ListTagsForResource",
"lambda:ListFunctions",
"lambda:ListTags",
"iam:ListRoles",
"iam:ListRoleTags", 
"iam:ListUsers",
"iam:ListUserTags",
"cloudformation:ListStacks",
"cloudformation:DescribeStacks",
"ecs:ListClusters",
"ecs:DescribeClusters",
"ecs:ListTagsForResource",
"eks:ListClusters", 
"eks:DescribeCluster",
"cloudwatch:DescribeAlarms"
```

#### **Extended Discovery Permissions**
```json
"config:DescribeConfigurationRecorderStatus",
"config:ListDiscoveredResources",
"config:ListAggregateDiscoveredResources", 
"config:GetResourceConfigHistory",
"cloudtrail:LookupEvents",
"logs:DescribeLogGroups",
"logs:ListTagsLogGroup",
"route53:ListHostedZones",
"route53:ListTagsForResource",
"apigateway:GET",
"dynamodb:ListTables",
"dynamodb:DescribeTable", 
"dynamodb:ListTagsOfResource",
"sns:ListTopics",
"sns:ListTagsForResource",
"sqs:ListQueues",
"sqs:GetQueueAttributes",
"sqs:ListQueueTags",
"kms:ListKeys",
"kms:DescribeKey",
"kms:ListResourceTags",
"elasticache:DescribeCacheClusters",
"elasticache:ListTagsForResource",
"opensearch:ListDomainNames",
"opensearch:DescribeDomain", 
"opensearch:ListTags",
"es:ListDomainNames",
"es:DescribeElasticsearchDomain",
"es:ListTags"
```

#### **Optional S3 Upload Permission**
```json
"s3:PutObject" on "arn:aws:s3:::YOUR-BUCKET-NAME/*"
```

## 🛡️ Security Best Practices

### **1. Principle of Least Privilege**
- Use the exact permissions listed in `iam-policy-read-only.json`
- Remove permissions for services you don't need to scan
- Restrict S3 upload to specific bucket ARNs

### **2. Access Control**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RestrictToSpecificUser",
      "Effect": "Allow", 
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT:user/inventory-scanner"
      },
      "Action": "*",
      "Resource": "*"
    }
  ]
}
```

### **3. Conditional Access**
```json
{
  "Condition": {
    "IpAddress": {
      "aws:SourceIp": ["203.0.113.0/24"]
    },
    "Bool": {
      "aws:MultiFactorAuthPresent": "true"
    },
    "DateGreaterThan": {
      "aws:CurrentTime": "2025-01-01T00:00:00Z"
    }
  }
}
```

### **4. Monitoring and Auditing**
```bash
# Enable CloudTrail for API monitoring
aws cloudtrail create-trail \
  --name inventory-audit-trail \
  --s3-bucket-name audit-logs-bucket

# Monitor for unexpected API calls
aws logs create-log-group --log-group-name /aws/inventory/audit
```

### **5. Network Security**
- Run from secure networks with restricted egress
- Use VPC endpoints for AWS API calls when possible
- Implement network ACLs to restrict access

## 🚨 Security Considerations

### **What These Tools Can Access**
- ✅ Resource metadata and configurations
- ✅ Tag information across all resources
- ✅ Network topology information (VPC/subnet details)
- ✅ Resource relationships and dependencies
- ✅ Historical resource configuration (via Config)
- ✅ Recent resource creation events (via CloudTrail)

### **What These Tools Cannot Do**
- ❌ Create, modify, or delete any AWS resources
- ❌ Change resource configurations or settings
- ❌ Access resource data/content (e.g., S3 object contents, database data)
- ❌ Modify IAM policies or permissions
- ❌ Start, stop, or restart services
- ❌ Modify network configurations
- ❌ Access encrypted data or secrets

### **Data Sensitivity**
The tools collect:
- **Low Sensitivity**: Resource IDs, types, regions, states
- **Medium Sensitivity**: Resource names, tags, network configurations
- **High Sensitivity**: ARNs (contain account IDs), resource relationships

**Recommendation**: Treat output files as sensitive and store securely.

## 🔐 Compliance Considerations

### **SOC 2 / ISO 27001**
- Tools support audit requirements through comprehensive resource discovery
- Read-only operations ensure no impact on system integrity
- Detailed logging enables audit trails

### **PCI DSS**
- No access to cardholder data
- Supports environment documentation requirements
- Network topology discovery aids in scope definition

### **GDPR**
- No access to personal data
- Supports data mapping requirements through resource discovery
- Tag compliance helps ensure proper data classification

### **HIPAA**
- No access to PHI (Protected Health Information)
- Supports environment documentation for compliance audits
- Tag validation ensures proper resource classification

## 📞 Security Contact

For security-related questions or to report security issues:

1. **Review this documentation** thoroughly
2. **Test in non-production** environments first
3. **Use minimal permissions** for your specific use case
4. **Monitor AWS CloudTrail** for API usage validation

## 🔄 Security Updates

This security documentation is maintained alongside the codebase. Any changes to AWS API usage will be reflected here with version updates.