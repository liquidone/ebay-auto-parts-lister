# Changelog

All notable changes to the eBay Auto Parts Lister project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2025-08-09

### Fixed
- Added automatic service restart to deploy.sh script after pulling code changes
- Deploy script now properly reloads the application with new code

### Added
- Created proper deploy.sh script with service restart functionality
- Auto-update of pip dependencies when requirements.txt changes

## [1.0.1] - 2025-08-09

### Fixed
- Fixed `encoded_images` undefined error in part_identifier.py (line 304)
- Added missing `_get_fallback_response` method for error handling
- Fixed SEO processing call in main.py (temporarily disabled, needs implementation)
- Changed fallback logic to use `_get_fallback_response` when demo methods unavailable
- Added missing datetime import in main.py that was causing "name 'datetime' is not defined" error
- Image processing now works correctly after clicking "Process Images" button

### Changed
- Modified comprehensive_analysis to use `len(images)` instead of undefined `encoded_images`
- Disabled SEO image processing temporarily (method not available in ImageProcessorSimple)
- Deployed to new DigitalOcean droplet (143.110.157.23)
- All dependencies properly installed via pip

### Added
- Fallback response method for graceful error handling when APIs unavailable
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
