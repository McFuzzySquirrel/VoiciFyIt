import azure.functions as func
import logging
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings
import azure.cognitiveservices.speech as speechsdk
import os
import json
import re
import tempfile

app = func.FunctionApp()

# Access the blob container name and connection string from the environment variables
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME", "default-container-name")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")

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

def send_to_speech_service(ssml_content, mp3_file_name):
    # Create a temporary file to store the audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
        temp_audio_file_path = temp_audio_file.name

    try:
        # Set up the speech configuration
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_audio_file_path)

        # Create a speech synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        # Synthesize the SSML content to an audio file
        logging.info("Synthesizing speech from SSML content...")
        result = synthesizer.speak_ssml_async(ssml_content).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logging.info("Speech synthesis succeeded.")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logging.error(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                logging.error(f"Error details: {cancellation_details.error_details}")
            raise Exception("Speech synthesis failed")

        # Upload the audio file to Azure Blob Storage
        logging.info(f"Uploading audio file to Blob Storage: {mp3_file_name}")
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)
        blob_client = container_client.get_blob_client(mp3_file_name)

        # Check if the file already exists
        if blob_client.exists():
            logging.info(f"File {mp3_file_name} already exists in Blob Storage. Skipping upload.")
            return func.HttpResponse(
                json.dumps({"status": "exists", "message": f"Audio file {mp3_file_name} already exists in Blob Storage."}),
                status_code=200,
                mimetype="application/json"
            )
        else:
            with open(temp_audio_file_path, "rb") as audio_file:
                blob_client.upload_blob(audio_file, overwrite=True, content_settings=ContentSettings(content_type="audio/mpeg"))
            logging.info(f"File {mp3_file_name} uploaded to Blob Storage.")

        # Return the response
        response = func.HttpResponse(
            json.dumps({"status": "success", "message": f"Audio file saved as {mp3_file_name}"}),
            status_code=200,
            mimetype="application/json"
        )
        logging.info(f"Returning HTTP response with status code: {response.status_code}")
        return response

    finally:
        # Clean up the temporary file
        os.remove(temp_audio_file_path)

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
                json.dumps({"status": "error", "message": "Please provide ssml_content, ssml_file_name, and mp3_file_name in the request body"}),
                status_code=400,
                mimetype="application/json"
            )

        # Clean up the SSML content
        cleaned_ssml_content = clean_ssml_content(ssml_content)
        logging.info(f"Cleaned SSML content: {cleaned_ssml_content}")

        # Send the cleaned SSML content to the speech services for conversion
        response = send_to_speech_service(cleaned_ssml_content, mp3_file_name)

        return response

    except Exception as e:
        logging.error(f"Exception: {str(e)}")
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            status_code=500,
            mimetype="application/json"
        )