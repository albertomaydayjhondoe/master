# Contributing to TikTok Viral ML System

## Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd master
```

2. **Set up the environment**
```bash
# For Telegram automation
cd telegram_automation
make setup-dev
```

3. **Run tests**
```bash
make test
```

## Branch Structure

- `main` - Production ready code
- `tele` - Telegram automation system
- `rama` - TikTok ML components
- `meta` - Meta advertising automation

## Coding Standards

- Use type hints for all functions
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Document all public APIs
- Use meaningful commit messages

## Testing

- Unit tests for individual components
- Integration tests for system workflows  
- End-to-end tests for complete scenarios
- All tests must pass before merging

## Security

- Never commit API keys or secrets
- Use environment variables for configuration
- Implement proper input validation
- Follow security best practices
