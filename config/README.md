# ⚙️ InvenTag Configuration

Configuration files and examples for customizing InvenTag behavior.

## 📁 Directory Structure

```
config/
├── README.md                           # This file
├── defaults/                           # Default configuration examples
│   ├── complete_configuration_example.yaml
│   ├── service_descriptions_example.yaml
│   ├── tag_mappings_example.yaml
│   ├── tag_policy_example.json
│   ├── tag_policy_example.yaml
│   └── iam-policy-read-only.json
└── schemas/                           # JSON schemas for validation
    └── account-config.schema.json
```

## 🚀 Quick Start

1. **Copy default configurations:**
```bash
# Basic BOM configuration
cp config/defaults/complete_configuration_example.yaml config/my_config.yaml

# Tag compliance policy
cp config/defaults/tag_policy_example.yaml config/my_tag_policy.yaml

# Multi-account setup
cp examples/accounts_basic.json config/my_accounts.json
```

2. **Use with InvenTag CLI:**
```bash
# With custom configuration
python -m inventag.cli.main --config config/my_config.yaml

# With multi-account setup
python -m inventag.cli.main --accounts-file config/my_accounts.json
```

## 📋 Configuration Files

### 🔧 **Default Examples** (`defaults/`)

- **`complete_configuration_example.yaml`** - Comprehensive BOM generation settings
- **`service_descriptions_example.yaml`** - Custom AWS service descriptions
- **`tag_mappings_example.yaml`** - Tag transformation and normalization rules
- **`tag_policy_example.json`** - Tag compliance policies (JSON format)
- **`tag_policy_example.yaml`** - Tag compliance policies (YAML format)
- **`iam-policy-read-only.json`** - Minimum required IAM permissions

### 🔍 **Validation Schemas** (`schemas/`)

- **`account-config.schema.json`** - JSON schema for multi-account configuration validation

## 🛡️ Security Configuration

### IAM Permissions
InvenTag requires minimal read-only access. Use the provided IAM policy:

```bash
# Review the policy
cat config/defaults/iam-policy-read-only.json

# Apply to your IAM user/role
aws iam put-user-policy --user-name inventag-user \
  --policy-name InvenTagReadOnly \
  --policy-document file://config/defaults/iam-policy-read-only.json
```

### Multi-Account Authentication
Supports multiple authentication methods:

- **AWS CLI Profiles** - Recommended for local development
- **Cross-Account Roles** - Recommended for production/CI-CD
- **Access Keys** - For specific use cases (not recommended)

## 📖 Configuration Examples

See the [examples/](../examples/) directory for complete working configurations:

- **Basic Setup**: `examples/accounts_basic.json`
- **AWS Profiles**: `examples/accounts_with_profiles.json`
- **Cross-Account Roles**: `examples/accounts_cross_account_roles.json`
- **CI/CD Environment**: `examples/accounts_cicd_environment.json`

## 🔗 Documentation Links

- **[Configuration Examples Guide](../docs/user-guides/CONFIGURATION_EXAMPLES.md)** - Detailed setup instructions
- **[CLI User Guide](../docs/user-guides/CLI_USER_GUIDE.md)** - Command-line usage
- **[Production Safety Guide](../docs/user-guides/PRODUCTION_SAFETY.md)** - Security best practices