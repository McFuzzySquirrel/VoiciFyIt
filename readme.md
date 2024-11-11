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

The following environment variables must be set in the Azure Function App settings. You can use the `local.settings.example.json` file as a template.

1. **AzureWebJobsStorage**: Connection string for the Azure Storage account used by the function app.
2. **FUNCTIONS_WORKER_RUNTIME**: The runtime stack for the function app (e.g., `python`).
3. **AZURE_STORAGE_CONNECTION_STRING**: Connection string for the Azure Blob Storage account.
4. **AZURE_SPEECH_KEY**: Subscription key for the Azure Cognitive Services Speech service.
5. **AZURE_SERVICE_REGION**: Region for the Azure Cognitive Services Speech service.

### Example `local.settings.json`

Copy the `local.settings.example.json` file to `local.settings.json` and replace the placeholders with your actual values.

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_STORAGE_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=<YourAccountName>;AccountKey=<YourAccountKey>;EndpointSuffix=core.windows.net",
    "AZURE_SPEECH_KEY": "<YourAzureSpeechKey>",
    "AZURE_SERVICE_REGION": "<YourAzureServiceRegion>"
  }
}


