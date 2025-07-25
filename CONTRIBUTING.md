# Contributing to AWS InvenTag

Thank you for your interest in contributing to **AWS InvenTag**! This document provides guidelines and information for contributors.

> **AWS InvenTag**: Python tool to check on AWS cloud inventory and tagging. Integrate into your CI/CD flow to meet your organization's stringent compliance requirements.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- AWS CLI (for testing with real data)
- GitHub account

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/aws-inventag.git
   cd aws-inventag
   ```

2. **Set up Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If it exists
   ```

3. **Install Development Tools**
   ```bash
   pip install black flake8 mypy pytest pytest-cov
   ```

## 📋 Pull Request Process

### Before You Start

1. **Check existing issues** - Look for related issues or feature requests
2. **Create an issue** - If none exists, create one to discuss your proposal
3. **Get feedback** - Wait for maintainer feedback before starting large changes

### Making Changes

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Follow Naming Conventions**
   - `feature/`: New features
   - `fix/`: Bug fixes
   - `docs/`: Documentation updates
   - `refactor/`: Code refactoring
   - `test/`: Test additions/modifications

3. **Make Your Changes**
   - Write clear, commented code
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   # Run linting
   flake8 scripts/
   
   # Format code
   black scripts/
   
   # Type checking
   mypy scripts/
   
   # Run tests
   pytest tests/
   
   # Test BOM converter functionality
   python scripts/bom_converter.py --help
   ```

### Commit Guidelines

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples:**
```
feat(bom): add account_id extraction from ARNs
fix(parser): resolve S3 bucket name parsing issue
docs: update README with new CLI options
```

### Pull Request Checklist

Before submitting your PR, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New code has appropriate test coverage
- [ ] Documentation is updated
- [ ] Commit messages follow conventional format
- [ ] PR description explains the changes
- [ ] No secrets or sensitive data in code
- [ ] Breaking changes are clearly documented

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=scripts --cov-report=html

# Run specific test file
pytest tests/test_bom_converter.py
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies (AWS APIs)

Example test structure:
```python
def test_bom_converter_basic_functionality():
    """Test basic BOM conversion functionality."""
    # Arrange
    sample_data = {...}
    
    # Act
    result = convert_data(sample_data)
    
    # Assert
    assert result is not None
    assert len(result) > 0
```

## 🎯 Code Style

### Python Style Guidelines

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for code formatting
- Line length: 88 characters (Black default)
- Use type hints where possible
- Write docstrings for functions and classes

### Code Structure

```python
def function_name(param: str, optional_param: int = 0) -> Dict[str, Any]:
    """
    Brief description of function.
    
    Args:
        param: Description of parameter
        optional_param: Description with default value
        
    Returns:
        Description of return value
        
    Raises:
        Exception: Description of when this is raised
    """
    # Implementation
    pass
```

## 🐛 Reporting Issues

### Bug Reports

Include:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS)
- Sample data (anonymized)
- Error messages/stack traces

### Feature Requests

Include:
- Clear use case description
- Proposed solution
- Alternative solutions considered
- Additional context

## 📖 Documentation

### Code Documentation

- Write clear docstrings
- Comment complex logic
- Include usage examples
- Document parameters and return values

### README Updates

- Keep installation instructions current
- Update usage examples
- Document new features
- Include troubleshooting info

## 🔒 Security

### Security Guidelines

- Never commit secrets, API keys, or credentials
- Use environment variables for sensitive data
- Validate all inputs
- Follow secure coding practices
- Report security issues privately

### Sensitive Data

- Use `.gitignore` to exclude sensitive files
- Anonymize sample data
- Don't include real AWS account IDs or ARNs

## 🎉 Recognition

Contributors will be recognized in:
- README contributors section
- Release notes
- GitHub contributor graphs

## ❓ Getting Help

- **Issues**: Create a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Email**: Contact maintainers directly for sensitive issues

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to AWS InvenTag! 🚀