# Pull Request

## 📝 Description
<!-- Provide a brief description of the changes in this PR -->


## 🔧 Type of Change
<!-- Mark the relevant option with an "x" -->

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🔧 Code refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] 🧪 Test additions or modifications
- [ ] 🔨 Build/CI changes

## 🎯 Related Issue
<!-- Link to the issue this PR addresses -->
Closes #<!-- issue number -->

## 🧪 Testing
<!-- Describe the tests you ran to verify your changes -->

### Test Environment
- [ ] Local testing completed
- [ ] Integration tests pass
- [ ] Manual testing performed

### Test Cases
<!-- List specific test cases covered -->
- [ ] 
- [ ] 
- [ ] 

## 📋 Checklist
<!-- Mark completed items with an "x" -->

### Code Quality
- [ ] My code follows the project's coding standards
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings or errors

### Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have tested the BOM converter with sample data
- [ ] I have verified tag compliance checker functionality
- [ ] I have tested CI/CD integration scripts if applicable

### Documentation
- [ ] I have made corresponding changes to the documentation
- [ ] I have updated the README if needed
- [ ] I have added docstrings to new functions/methods

### Security & Performance
- [ ] My changes do not introduce security vulnerabilities
- [ ] I have considered the performance impact of my changes
- [ ] I have not exposed any secrets or sensitive information

## 📊 InvenTag Specific Testing
<!-- For changes to core InvenTag functionality -->

### BOM Generation
- [ ] Tested BOM converter with different AWS service data
- [ ] Confirmed Excel/Word/CSV output is properly formatted
- [ ] Verified advanced analysis features (network, security, cost)
- [ ] Tested with both single and multi-account configurations

### Tag Compliance
- [ ] Verified tag compliance checking works correctly
- [ ] Tested with various tag policy configurations
- [ ] Confirmed compliance reports are accurate
- [ ] Validated integrated compliance-BOM workflow

### CI/CD Integration
- [ ] Tested multi-account credential management
- [ ] Verified GitHub Actions/CodeBuild integration
- [ ] Confirmed S3 upload and notification features
- [ ] Tested Prometheus metrics collection

### Core Package
- [ ] Tested resource discovery and enrichment
- [ ] Verified template framework functionality
- [ ] Confirmed production safety features
- [ ] Validated security and audit logging

## 🔄 Migration Notes
<!-- Any special migration steps or breaking changes -->


## 📸 Screenshots/Logs
<!-- Add screenshots, logs, or output examples if applicable -->


## 🤔 Additional Context
<!-- Add any other context about the PR here -->


---

## 📋 Reviewer Guidelines

### What to Review
- [ ] Code correctness and logic
- [ ] Error handling and edge cases
- [ ] Performance implications
- [ ] Security considerations
- [ ] Test coverage
- [ ] Documentation accuracy
- [ ] Breaking changes impact

### Testing Requirements
- [ ] Run the BOM converter with sample data
- [ ] Test tag compliance checker with policy files
- [ ] Verify CI/CD scripts help and basic functionality
- [ ] Verify no regressions in existing functionality
- [ ] Check output formats (Excel/Word/CSV) are correct
- [ ] Validate tag compliance reports are accurate
- [ ] Test core inventag package imports and basic functionality