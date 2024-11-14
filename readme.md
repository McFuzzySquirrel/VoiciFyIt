# Azure Function: ProcessSSML

## Overview

The `ProcessSSML` Azure Function is designed to process Speech Synthesis Markup Language (SSML) content, convert it into speech using the Azure Cognitive Services Speech SDK, and upload the resulting MP3 audio file to Azure Blob Storage. The function is triggered via an HTTP POST request and returns a response indicating the success of the operation.

## Functionality

1. **HTTP Trigger**: The function is triggered via an HTTP POST request. The request body should contain the SSML content, the name of the SSML file, and the name of the MP3 file to be created.
2. **SSML Content Cleaning**: Cleans the SSML content to escape special characters and remove newlines within the text content between the tags.
3. **Blob Storage Initialization**: Initializes the Azure Blob Storage client using the connection string and container name provided in the environment variables.
4. **Upload SSML Content**: Uploads the cleaned SSML content to Azure Blob Storage.
5. **Wait for File Creation**: Waits for the SSML file to be created in Blob Storage.
6. **Download SSML Content**: Downloads the SSML content from Blob Storage.
7. **Speech Synthesis**: he function initializes the Azure Cognitive Services Speech client using the subscription key and region provided in the environment variables. It then synthesizes the SSML content to an MP3 file.
8. **Upload MP3 File**: he resulting MP3 file is uploaded to Azure Blob Storage using chunked upload with increased concurrency to speed up the process
9. **Response**: The function returns an HTTP response indicating that the audio file has been saved.

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
4. **BLOB_CONTAINER_NAME**: Name of the Blob Storage container.
5. **SPEECH_KEY**: Azure Cognitive Services Speech API key.
6. **SPEECH_REGION**: Azure Cognitive Services Speech API region.

### Example `local.settings.json`

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_STORAGE_CONNECTION_STRING": "your-azure-storage-connection-string",
    "BLOB_CONTAINER_NAME": "your-container-name",
    "SPEECH_KEY": "your-speech-key",
    "SPEECH_REGION": "your-speech-region"
  }
}