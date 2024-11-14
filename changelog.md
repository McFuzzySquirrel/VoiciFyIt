# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2023-11-13

### Added

- Increased `max_concurrency` for Blob Upload to speed up the upload process of large MP3 files by allowing more concurrent connections.
- Detailed logging to measure the time taken for each step, especially the upload process, and to help diagnose any issues.
- Environment variable logging to verify that the environment variables for Azure Cognitive Services are correctly set.
- Cleaned up temporary files to ensure that temporary files are deleted after processing to avoid unnecessary storage usage
- Commented out the construction of the URL and path of the uploaded MP3 file to test if this improves the completion of the function.
- Updated the response to simplify it by removing the URL and blob path
- Added "Power Platform" directory to hold the Power Platform Solution
-   Added "Style Guides", concept I am playing with to guide the AI Builder to generate podcase in a specific style

