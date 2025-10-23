# Security Policy

## Reporting Security Issues

If you discover a security vulnerability in this project, please report it by:
1. Opening a GitHub Security Advisory
2. Or emailing the maintainers directly (contact info in README)

**Do not** open a public issue for security vulnerabilities.

## Secure Configuration

### Development Mode (Dummy Mode)

This project runs in "dummy mode" by default (`DUMMY_MODE=true`), which:
- Uses mock implementations for all external services
- Requires no real credentials
- Is safe for local development and testing
- Cannot interact with real TikTok accounts or devices

### Production Mode

⚠️ **Production mode requires careful security configuration**

#### Required Steps Before Production:

1. **Environment Variables**
   - Copy `docker/.env.example` to `docker/.env`
   - Replace ALL placeholder values with secure credentials
   - Use strong, randomly generated passwords (minimum 16 characters)
   - Never commit `.env` files to version control

2. **API Keys**
   - Generate unique API keys for each service
   - Rotate keys regularly (recommended: every 90 days)
   - Use different keys for different environments (dev/staging/prod)
   - Store keys securely (use a secrets manager in production)

3. **Database Security**
   - Use strong passwords for PostgreSQL
   - Enable SSL/TLS for database connections
   - Restrict database access to application servers only
   - Regular backups with encryption

4. **Network Security**
   - Run services behind a firewall
   - Use HTTPS/TLS for all external communications
   - Implement rate limiting on API endpoints
   - Use VPN or private networks for internal service communication

5. **Device Farm Security**
   - Secure physical access to devices
   - Use unique credentials per device
   - Enable device encryption
   - Regular security updates for Android OS

6. **GoLogin & Browser Automation**
   - Store GoLogin API keys securely
   - Use dedicated proxy services (avoid free proxies)
   - Rotate proxy IPs regularly
   - Monitor for suspicious activity

## Secrets Management

### What NOT to commit:

❌ **Never commit these to Git:**
- `.env` files (except `.env.example`)
- API keys or tokens
- Passwords
- Private keys (`.key`, `.pem` files)
- TLS certificates
- Database credentials
- Trained model files with proprietary data
- User data or account information

### Protected by .gitignore:

The following patterns are excluded from version control:
- `.env` and `.env.*` (except `.env.example`)
- `config/secrets/` directory
- `*.key`, `*.pem`, `*.crt` files
- `data/` directory (may contain sensitive datasets)
- Large model files (`*.pt`, `*.onnx`, etc.)

## Known Security Considerations

### 1. TikTok Automation

⚠️ **Important**: Automated interaction with TikTok may violate their Terms of Service. Use responsibly:
- Respect rate limits
- Use human-like behavior patterns (included in ML models)
- Monitor for shadowbans and anomalies
- Obtain proper authorization for managed accounts

### 2. ML Models

- Trained models may contain biases from training data
- Ensure training data respects privacy and copyright
- Regularly audit model behavior for unintended patterns
- Document data sources and preprocessing steps

### 3. Dummy Mode Safety

In dummy mode:
✅ No real API calls are made  
✅ No devices are controlled  
✅ No external services are contacted  
✅ Safe for development and CI/CD  

Ensure `DUMMY_MODE=true` in development environments.

### 4. Dependencies

This project uses third-party dependencies that may have vulnerabilities:
- Regularly run `pip audit` or equivalent
- Keep dependencies updated
- Review security advisories for critical packages
- Use virtual environments to isolate dependencies

## Security Checklist for Production

Before deploying to production:

- [ ] All `.env` files use secure, unique credentials
- [ ] `DUMMY_MODE=false` is explicitly set
- [ ] Database uses strong password and SSL
- [ ] API endpoints use authentication (X-API-Key header)
- [ ] Rate limiting is configured
- [ ] HTTPS/TLS is enabled for all external services
- [ ] Firewall rules restrict access to necessary ports only
- [ ] Logs are configured (but don't log sensitive data)
- [ ] Monitoring and alerting is set up
- [ ] Backup strategy is in place
- [ ] Incident response plan is documented
- [ ] Security audit has been performed
- [ ] Team is trained on security practices

## Code Security

### Input Validation

All user inputs are validated:
- File uploads: Type and size checks
- API parameters: Type validation and sanitization
- Screenshot analysis: Image format validation

### Authentication

- API key authentication on all endpoints
- Different keys for development and production
- Keys transmitted via secure headers (X-API-Key)

### Data Privacy

- Minimize data collection
- Anonymize analytics data
- Respect user privacy in logging
- Follow GDPR/privacy regulations if applicable

## Security Updates

- Review security advisories regularly
- Update dependencies when patches are released
- Test updates in staging before production
- Maintain a log of security-related changes

## Compliance

If using this system professionally:
- Ensure compliance with TikTok's Terms of Service
- Respect data protection regulations (GDPR, CCPA, etc.)
- Obtain necessary user consents
- Document your compliance procedures

## Contact

For security-related questions or to report vulnerabilities:
- Create a GitHub Security Advisory
- Contact maintainers via email (see README)

---

**Last Updated**: 2025-10-23  
**Version**: 1.0
