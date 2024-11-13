import azure.functions as func
import logging
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings
import azure.cognitiveservices.speech as speechsdk
import os
import json
import re
import tempfile
import time

app = func.FunctionApp()

# Access the blob container name and connection string from the environment variables
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME", "default-container-name")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

def clean_ssml_content(ssml_content):
    # Escape special characters and remove newlines within the text content between the tags
    def escape_special_chars(match):
        text = match.group(1)
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('\n', ' ')  # Replace newlines with space
        text = text.replace('\\', '')  # Remove backslashes
        return f'>{text}<'

    # Use regular expression to find text content between the tags and escape special characters
    cleaned_content = re.sub(r'>([^<]+)<', escape_special_chars, ssml_content)
    return cleaned_content

@app.route(route="ProcessSSML", auth_level=func.AuthLevel.ANONYMOUS)
def ProcessSSML(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        logging.info(f"Request body: {req_body}")

        ssml_content = req_body.get('ssml_content')
        ssml_file_name = req_body.get('ssml_file_name')
        mp3_file_name = req_body.get('mp3_file_name')

        if not ssml_content or not ssml_file_name or not mp3_file_name:
            logging.error("ssml_content, ssml_file_name, or mp3_file_name is missing")
            return func.HttpResponse(
                json.dumps({"error": "Please provide ssml_content, ssml_file_name, and mp3_file_name in the request body"}),
                status_code=400,
                mimetype="application/json"
            )

        # Clean up the SSML content
        cleaned_ssml_content = clean_ssml_content(ssml_content)
        logging.info(f"Cleaned SSML content: {cleaned_ssml_content}")

        # Initialize the Blob Service Client
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)
        ssml_blob_client = container_client.get_blob_client(ssml_file_name)

        # Verify Blob Storage configuration
        logging.info(f"BLOB_CONTAINER_NAME: {BLOB_CONTAINER_NAME}")
        logging.info(f"AZURE_STORAGE_CONNECTION_STRING: {AZURE_STORAGE_CONNECTION_STRING}")

        # Upload the cleaned SSML content to Blob Storage with the correct content type
        logging.info(f"Uploading SSML file {ssml_file_name} to Blob Storage")
        ssml_blob_client.upload_blob(
            cleaned_ssml_content,
            overwrite=True,
            content_settings=ContentSettings(content_type='text/plain')
        )
        logging.info("Upload completed successfully.")

        # Wait for the SSML file to be created
        logging.info(f"Waiting for SSML file {ssml_file_name} to be created in Blob Storage")
        while not ssml_blob_client.exists():
            logging.info(f"SSML file {ssml_file_name} not found, waiting...")
            time.sleep(5)  # Wait for 5 seconds before checking again

        # Download the SSML file content
        logging.info(f"Downloading SSML file {ssml_file_name} from Blob Storage")
        ssml_content = ssml_blob_client.download_blob().readall().decode('utf-8')
        logging.info(f"SSML content from file: {ssml_content}")

        # Retrieve and log the environment variables
        speech_key = os.getenv("SPEECH_KEY")
        speech_region = os.getenv("SPEECH_REGION")
        logging.info(f"SPEECH_KEY: {speech_key}")
        logging.info(f"SPEECH_REGION: {speech_region}")

        if not speech_key or not speech_region:
            logging.error("SPEECH_KEY or SPEECH_REGION environment variable is missing")
            return func.HttpResponse(
                json.dumps({"error": "SPEECH_KEY or SPEECH_REGION environment variable is missing"}),
                status_code=500,
                mimetype="application/json"
            )

        # Create a temporary file for the MP3 output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_mp3_file:
            temp_mp3_file_name = temp_mp3_file.name

        # Initialize the speech synthesis client
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_mp3_file_name)

        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        # Synthesize the SSML content to an MP3 file
        logging.info("Starting speech synthesis")
        result = synthesizer.speak_ssml_async(ssml_content).get()
        logging.info("Speech synthesis completed")

        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            logging.error(f"Speech synthesis failed: {result.error_details}")
            return func.HttpResponse(
                json.dumps({"error": f"Speech synthesis failed: {result.error_details}"}),
                status_code=500,
                mimetype="application/json"
            )

        # Upload the MP3 file to Blob Storage using chunked upload
        logging.info("Uploading MP3 file to Blob Storage")
        output_blob_client = container_client.get_blob_client(mp3_file_name)

        start_time = time.time()
        with open(temp_mp3_file_name, "rb") as data:
            output_blob_client.upload_blob(data, overwrite=True, max_concurrency=8)  # Increased max_concurrency
        end_time = time.time()
        logging.info(f"Upload completed successfully in {end_time - start_time} seconds.")

        # Construct the URL and path of the uploaded MP3 file
        # mp3_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{BLOB_CONTAINER_NAME}/{mp3_file_name}"
        # blob_path = f"{BLOB_CONTAINER_NAME}/{mp3_file_name}"

        # Return the response
        response = func.HttpResponse(
            json.dumps({"message": f"Audio file saved as {mp3_file_name}"}),
            status_code=200,
            mimetype="application/json"
        )
        logging.info(f"Returning HTTP response with status code: {response.status_code}")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"An error occurred: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )

    finally:
        # Clean up the temporary files if they exist
        if os.path.exists(temp_mp3_file_name):
            os.remove(temp_mp3_file_name)

    return response