# Development Guide - Universal Automation Platform

## Getting Started

### Prerequisites
- Python 3.12+
- Git
- Make
- Basic understanding of async/await patterns

### Setup
1. Clone the repository
2. Switch to the apply branch: `git checkout apply`
3. Run the apply system: `python3 apply_system.py`
4. Start development: `make wake`

## Architecture Overview

The platform uses a modular architecture with three main branches:

### Rama (TikTok ML)
- Machine learning models for content analysis
- Device farm for mobile automation
- Monitoring and health checking

### Meta (Meta Ads)
- Meta advertising automation
- GoLogin browser profile management
- Social media monitoring

### Tele (Like4Like)
- Telegram bot for user interaction
- YouTube automation via Selenium
- Database management for exchanges

## Development Workflow

1. **Start with dummy mode**: Always develop with `DUMMY_MODE=true`
2. **Use the apply system**: Run quality checks regularly
3. **Test individual branches**: Use `make rama`, `make meta`, `make tele`
4. **Validate changes**: Run `python3 validate_system.py`
5. **Test integration**: Use `make wake` for full system test

## Best Practices

### Code Organization
- Keep modules focused and cohesive
- Use dependency injection for testability
- Implement proper separation of concerns
- Follow the established directory structure

### Error Handling
- Always use specific exception types
- Implement retry logic for external services
- Log errors with sufficient context
- Provide fallback mechanisms

### Performance
- Use async/await for I/O operations
- Implement connection pooling for databases
- Cache frequently accessed data
- Monitor resource usage

### Security
- Never commit real credentials
- Use environment variables for configuration
- Implement proper input validation
- Follow security best practices for web scraping

## Testing Strategy

### Unit Tests
- Test individual functions and classes
- Mock external dependencies
- Cover edge cases and error conditions

### Integration Tests
- Test component interactions
- Verify database operations
- Test API endpoints

### System Tests
- Full end-to-end testing
- Cross-branch compatibility
- Performance under load

## Deployment

### Dummy Mode Deployment
- Use for development and testing
- No external dependencies required
- Safe for continuous integration

### Production Deployment
- Set `DUMMY_MODE=false`
- Install full dependency requirements
- Configure real API credentials
- Monitor system health

## Troubleshooting

### Common Issues
1. Import errors: Run dependency resolver
2. Service startup failures: Check logs
3. Database connection issues: Verify dummy mode
4. Browser automation problems: Check Chrome installation

### Debug Mode
```bash
export DEBUG=true
make wake
```

### Log Analysis
```bash
tail -f logs/*.log
```

## Contributing

1. Create feature branch from apply
2. Implement changes with tests
3. Run apply system for quality check
4. Submit pull request with documentation

---

Happy coding! 🚀
