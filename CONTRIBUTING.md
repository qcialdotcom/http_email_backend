# Contributing to http_email_backend

Thanks for your interest! We welcome contributions from everyone.

## Code of Conduct

This project is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold it.

## Getting Started

### Setup

```bash
# Clone your fork
git clone https://github.com/PackageSphere/http_email_backend.git
cd http_email_backend

uv sync

cd src && uv run manage.py migrate
```

## Making Changes

1. **Create a branch**: `git checkout -b feature/your-feature` or `fix/issue-description`
2. **Make changes**: Follow PEP 8, add type hints, include docstrings
3. **Commit**: Use clear, descriptive messages
4. **Push**: `git push origin your-branch`
5. **Open PR**: Fill out the template completely

## Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `test/` - Tests
- `refactor/` - Code refactoring

## Code Style

- **PEP 8** compliance (88 char line limit)
- **Type hints** for functions
- **Docstrings** for all public APIs
- **4 spaces** indentation

## What to Update

- **Code changes**: Update relevant files in `src/http_email_backend/`
- **Add tests**: Place in `src/http_email_backend/tests/`
- **New features**: Add tests and update [README.md](README.md)
- **Bug fixes**: Include regression tests
- **Docs**: Keep [README.md](README.md) up-to-date with any changes and ensure clarity

## Pull Request Process

1. Include a clear description of changes
2. Reference any related issues (#123)
3. Ensure all tests pass
4. Wait for review and address feedback
5. Once approved, your PR will be merged
6. Don't Spam: Avoid unnecessary commits or unrelated changes in your PR

## Issue Reporting

- Check existing issues first
- Provide a clear description and steps to reproduce the issue (if possible add screenshots or code snippets)
- Include relevant environment details (Python version, Django version, etc.)
- Reference any related issues or pull requests

## Questions?

- Join our discussions on GitHub
- Check existing issues first
- Email: krsahil8825@gmail.com

Thank you for contributing! 🎉