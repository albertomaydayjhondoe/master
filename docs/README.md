# Documentation Index

This directory contains comprehensive documentation for the Social Media Automation ML System.

## 📚 Quick Start

New to the project? Start here:
1. [Main README](../README.md) - Project overview and quick start
2. [API Integration Guide](./api_integration.md) - How to use the API
3. [Local Testing Guide](./setup/07_local_testing.md) - Run locally in dummy mode

## 📖 Documentation Files

### Core Documentation

#### [API Integration Guide](./api_integration.md)
Complete guide to integrating with the ML API including:
- Python client usage (sync and async)
- REST API endpoints
- Authentication and rate limiting
- Error handling
- cURL examples
- Technical integrations (Ultralytics, GoLogin, Google Cloud)

**Use when:** You need to call the API from your application

---

#### [Technical Integrations Guide](./technical_integrations.md)
Detailed setup instructions for external services:
- **Ultralytics YOLOv8** - Computer vision setup and training
- **GoLogin** - Browser profile management and credentials
- **Google Cloud** - Optional cloud services integration
- Installation procedures
- Configuration examples
- Troubleshooting guides
- Security best practices

**Use when:** Setting up production environment or training models

---

#### [Migration Guide](./migration_guide.md)
Step-by-step guide for migrating from TikTok-specific to multi-platform:
- What changed in v0.2.0
- Platform-specific implementation strategies
- Model training for new platforms
- Backward compatibility
- 4-week incremental migration plan
- Rollback procedures

**Use when:** Upgrading from v0.1.x or adding new platforms

---

### Reference Documentation

#### [Audit Summary](./AUDIT_SUMMARY.md)
Executive summary of the October 2025 repository audit:
- Complete inventory of changes
- Files modified list
- Technical contacts added
- Security review
- Next steps for maintainer

**Use when:** You need to understand what changed and why

---

#### [Local Testing Guide](./setup/07_local_testing.md)
Quick reference for running tests locally:
- Virtualenv setup
- Running the API in dummy mode
- Executing tests
- Docker Compose usage

**Use when:** You want to run and test locally

---

## 🗺️ Documentation Roadmap

### Current Documentation (v0.2.0)
- ✅ API integration guide
- ✅ Technical integrations (Ultralytics, GoLogin, Google Cloud)
- ✅ Migration guide
- ✅ Local testing guide
- ✅ Audit summary

### Planned Documentation
- ⏳ Platform-specific guides (Twitter, Instagram, etc.)
- ⏳ Model training tutorial with examples
- ⏳ Deployment guide (Docker, Kubernetes, Cloud)
- ⏳ Architecture deep dive
- ⏳ Performance tuning guide
- ⏳ Troubleshooting FAQ

## 🎯 Use Cases

### "I want to start developing locally"
1. Read [Main README](../README.md)
2. Follow [Local Testing Guide](./setup/07_local_testing.md)
3. Check [API Integration Guide](./api_integration.md) for API usage

### "I want to deploy to production"
1. Read [Technical Integrations Guide](./technical_integrations.md)
2. Follow [Migration Guide](./migration_guide.md) for platform setup
3. Set up credentials and services
4. Exit dummy mode

### "I want to add a new platform"
1. Read [Migration Guide](./migration_guide.md) - Platform implementation section
2. Follow model training steps in [Technical Integrations](./technical_integrations.md)
3. Implement platform-specific modules

### "I want to train custom models"
1. Read [Technical Integrations Guide](./technical_integrations.md) - Ultralytics section
2. Collect and label platform-specific screenshots
3. Update `config/ml/data.yaml`
4. Run training script

### "I want to understand what changed"
1. Read [Audit Summary](./AUDIT_SUMMARY.md)
2. Check [CHANGELOG](../CHANGELOG.md)
3. Review [Migration Guide](./migration_guide.md)

## 🔗 External Resources

### Ultralytics YOLOv8
- [Official Documentation](https://docs.ultralytics.com/)
- [Training Guide](https://docs.ultralytics.com/modes/train/)
- [GitHub Repository](https://github.com/ultralytics/ultralytics)

### GoLogin
- [Official Documentation](https://gologin.com/docs)
- [API Reference](https://api.gologin.com/docs)
- [Support](https://gologin.com/support)

### Google Cloud
- [Getting Started](https://cloud.google.com/docs/get-started)
- [Authentication Guide](https://cloud.google.com/docs/authentication)
- [Vertex AI](https://cloud.google.com/vertex-ai/docs)
- [Cloud Storage](https://cloud.google.com/storage/docs)

### Python Libraries
- [FastAPI](https://fastapi.tiangolo.com/)
- [PyTorch](https://pytorch.org/docs/)
- [Selenium](https://selenium-python.readthedocs.io/)

## 📝 Contributing to Documentation

### Adding New Documentation

1. Create markdown file in appropriate directory
2. Follow existing structure and style
3. Add entry to this README
4. Update relevant documentation links
5. Test all code examples

### Documentation Standards

- Use clear, concise language
- Include code examples for concepts
- Add links to external resources
- Keep examples up-to-date
- Test all commands and code snippets

### Markdown Guidelines

- Use proper heading hierarchy (# → ## → ###)
- Include table of contents for long documents
- Use code blocks with language specification
- Add emojis for visual appeal (sparingly)
- Include diagrams where helpful

## 🆘 Getting Help

### Documentation Issues
- **Missing information?** Open an issue requesting documentation
- **Found an error?** Open a PR with corrections
- **Need clarification?** Open an issue with questions

### Technical Support
- **API issues:** Check [API Integration Guide](./api_integration.md)
- **Setup problems:** Check [Technical Integrations](./technical_integrations.md)
- **Training issues:** Check Ultralytics documentation
- **General questions:** Open a GitHub issue

## 📊 Documentation Statistics

- **Total documents:** 5 markdown files
- **Total size:** ~40KB
- **Lines of documentation:** ~1,000+
- **Code examples:** 50+
- **External links:** 30+
- **Last updated:** 2025-10-23

## 🔄 Versioning

Documentation follows the same versioning as the main project:
- **v0.1.x:** TikTok-specific documentation
- **v0.2.0:** Multi-platform generic documentation (current)
- **v0.3.0+:** Platform-specific guides (planned)

## 📅 Maintenance

### Regular Updates Needed
- Update external links (check quarterly)
- Verify code examples work (on each release)
- Add new platform guides (as platforms are added)
- Update screenshots/examples (on UI changes)
- Sync with CHANGELOG (on each version)

### Review Schedule
- **Monthly:** Check for broken links
- **Per Release:** Update version-specific content
- **Quarterly:** Review all examples and commands
- **Annually:** Major documentation refresh

---

**Last Updated:** 2025-10-23  
**Version:** 0.2.0  
**Status:** ✅ Complete and up-to-date
