import azure.functions as func
import logging
import os
import json
import re
import tempfile
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.storage.queue import QueueClient
import azure.cognitiveservices.speech as speechsdk

app = func.FunctionApp()

# Access the blob container name and connection string from the environment variables
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME", "default-container-name")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")
QUEUE_NAME = os.getenv("QUEUE_NAME", "ssml-queue")

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
                json.dumps({"status": "error", "message": "Please provide ssml_content, ssml_file_name, and mp3_file_name in the request body"}),
                status_code=400,
                mimetype="application/json"
            )

        # Enqueue the request
        queue_client = QueueClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING, QUEUE_NAME)
        message = json.dumps({
            "ssml_content": ssml_content,
            "ssml_file_name": ssml_file_name,
            "mp3_file_name": mp3_file_name
        })
        queue_client.send_message(message)
        logging.info(f"Message sent to queue: {message}")

        return func.HttpResponse(
            json.dumps({"status": "queued", "message": "Request has been queued for processing."}),
            status_code=202,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Exception: {str(e)}")
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.function_name(name="ProcessSSMLQueue")
@app.queue_trigger(queue_name=QUEUE_NAME, connection="AzureWebJobsStorage")
def ProcessSSMLQueue(msg: func.QueueMessage) -> None:
    logging.info('Processing message from queue.')
    message = json.loads(msg.get_body().decode('utf-8'))
    ssml_content = clean_ssml_content(message.get('ssml_content'))
    mp3_file_name = message.get('mp3_file_name')
    send_to_speech_service(ssml_content, mp3_file_name)

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
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)
        blob_client = container_client.get_blob_client(mp3_file_name)

        # Check if the file already exists
        if blob_client.exists():
            logging.info(f"File {mp3_file_name} already exists in Blob Storage. Skipping upload.")
        else:
            with open(temp_audio_file_path, "rb") as audio_file:
                blob_client.upload_blob(audio_file, overwrite=True, content_settings=ContentSettings(content_type="audio/mpeg"))
            logging.info(f"File {mp3_file_name} uploaded to Blob Storage.")
    finally:
        # Clean up the temporary file
        os.remove(temp_audio_file_path)