# Azure Function: ProcessSSML

## Overview

The `ProcessSSML` Azure Function is designed to process Speech Synthesis Markup Language (SSML) files stored in Azure Blob Storage. It converts the SSML content into speech using the Azure Cognitive Services Speech SDK and uploads the resulting MP3 audio file back to Azure Blob Storage.

## Functionality

1. **HTTP Trigger**: The function is triggered via an HTTP POST request.
2. **SSML File Download**: Downloads the specified SSML file from Azure Blob Storage.
3. **SSML Validation**: Validates the SSML content.
4. **Speech Synthesis**: Converts the SSML content into speech and saves it as an MP3 file.
5. **Upload MP3**: Uploads the generated MP3 file to Azure Blob Storage.
6. **Response**: Returns a JSON response with the URL and blob path of the uploaded MP3 file.

## Prerequisites

- Azure Function App
- Azure Blob Storage
- Azure Cognitive Services Speech SDK
- Python 3.6 or later

## Configuration

### Environment Variables

The following environment variables must be set in the Azure Function App settings:

- `AZURE_STORAGE_CONNECTION_STRING`: Connection string for the Azure Blob Storage account.
- `AZURE_SPEECH_KEY`: Subscription key for the Azure Cognitive Services Speech service.
- `AZURE_SERVICE_REGION`: Region for the Azure Cognitive Services Speech service.

