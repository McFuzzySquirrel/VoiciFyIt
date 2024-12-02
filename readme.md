# Azure Function for Podscript to Podcast Conversion (VoiciFyIt)

This Azure Function App converts a podscript (written in SSML - Speech Synthesis Markup Language) into a high-quality audio podcast in MP3 format. It leverages Azure Cognitive Services for speech synthesis and Azure Storage for handling input and output queues and storing the generated audio files. This function can be used by any application or system that sends a well-formed SSML to the relevant `input-queue`

For the **Power Platform based front-end**, please see [README.MD](https://github.com/McFuzzySquirrel/podcaster_function/blob/all_in_one/Power%20Platform%20Bits/readme.md) in the "Power Platform Bits" directory

- **Note**: Documentation for the Power App is is still in progress.

## How It Works

1. **Trigger**: The function is triggered by messages added to an Azure Storage Queue (`input-queue`).
2. **Message Processing**: The function processes the incoming message, which contains the SSML content and metadata (such as file names, title, and description). "title" and "description" are placeholder to be updated after message has been processed from the `output queue`
3. **SSML Content Cleaning**: The function cleans and sanitizes the SSML content to ensure it is well-formed.
4. **Speech Synthesis**: The cleaned SSML content is sent to Azure Cognitive Services for speech synthesis, converting it into an MP3 file.
5. **Audio File Upload**: The generated MP3 file is uploaded to Azure Blob Storage.
6. **Output Queue Message**: A message containing the status, MP3 file name, title (placeholder), and description (placeholder)is sent to an output queue (`output-queue`) for further processing or notifications.

## Configuration

Ensure you have the following settings in your `local.settings.json` file:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_STORAGE_CONNECTION_STRING": "your-azure-storage-connection-string",
    "BLOB_CONTAINER_NAME": "your-container-name",
    "SPEECH_KEY": "your-speech-key",
    "SPEECH_REGION": "your-speech-region",
    "INPUT_QUEUE_NAME": "your input storage queue name",
    "OUTPUT_QUEUE_NAME": "your output azure storage queue name"
  }
}
```
## Function App Settings

### Environment Variables
Ensure that your Function App in Azure has the following envrionment variables set:

- **AzureWebJobsStorage**: Connection string for Azure Storage.
- **FUNCTIONS_WORKER_RUNTIME**: Runtime for Azure Functions (set to python).
- **AZURE_STORAGE_CONNECTION_STRING**: Connection string for Azure Storage.
- **BLOB_CONTAINER_NAME**: Name of the Azure Blob Storage container where MP3 files will be stored.
- **SPEECH_KEY**: Subscription key for Azure Cognitive Services Speech API.
- **SPEECH_REGION**: Region for Azure Cognitive Services Speech API.
- **INPUT_QUEUE_NAME**: The name you have given for Azure Storage Queue Name recieving content from external sources
- **OUTPUT_QUEUE_NAME**: The name you have given for Azure Storage Queue Name recieving content from the Funtion App

### Permissions

- **Storage Account**: The Function App's Managed Identity should have "Blob Storage Data Contributer" role to the relevant Azure Storgae Account
- **Speech Services**: The Function App's Managed Identiry should have "Cognitive Services Contributor" role to the relevant Azure Speech Services

# Conclusion
This function app automates the process of converting a podscript into a high-quality audio podcast. It integrates with Azure Cognitive Services for speech synthesis and Azure Storage for handling input and output queues and storing the generated audio files. This setup allows for seamless integration with other systems, such as Power Platform, to create a robust and scalable podcast generation workflow.
