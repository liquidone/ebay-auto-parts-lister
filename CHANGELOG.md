# Changelog

All notable changes to the eBay Auto Parts Lister project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-08-09

### Fixed
- Added missing datetime import in main.py that was causing "name 'datetime' is not defined" error
- Image processing now works correctly after clicking "Process Images" button

### Changed
- Deployed to new DigitalOcean droplet (143.110.157.23)
- All dependencies properly installed via pip

### Security
- Removed sensitive files (.env, vision-credentials.json) from Git repository
- Added comprehensive .gitignore to prevent future secret commits

## [1.0.0] - 2025-08-09

### Added
- Initial clean deployment of eBay Auto Parts Lister
- FastAPI backend with image processing capabilities
- Google Vision API integration for OCR
- Google Gemini API integration for part identification
- Web interface for uploading and processing auto part images
- Debug panel for monitoring API responses
- Systemd service configuration for automatic startup
- Nginx reverse proxy configuration
- Auto-deploy script for easy updates

### Removed
- All dummy/fallback data from codebase
- Legacy branches (master, feature/browser-fallback) from GitHub repository
