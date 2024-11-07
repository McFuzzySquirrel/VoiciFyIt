import azure.functions as func
import logging
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import azure.cognitiveservices.speech as speechsdk
import os
import tempfile

app = func.FunctionApp()

@app.route(route="ProcessSSML", auth_level=func.AuthLevel.ANONYMOUS)
def ProcessSSML(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Get the SSML blob name from the request
    ssml_blob_name = req.params.get('ssml_blob_name')
    logging.info(f"Query parameter ssml_blob_name: {ssml_blob_name}")
    if not ssml_blob_name:
        try:
            req_body = req.get_json()
            logging.info(f"Request body: {req_body}")
        except ValueError:
            req_body = None
            logging.error("Failed to parse request body")

        if req_body:
            ssml_blob_name = req_body.get('ssml_blob_name')
            logging.info(f"Body parameter ssml_blob_name: {ssml_blob_name}")

    if not ssml_blob_name:
        logging.error("ssml_blob_name is missing")
        return func.HttpResponse(
            "Please pass the ssml_blob_name in the query string or in the request body",
            status_code=400
        )

    # Azure Blob Storage connection string and container name
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not connect_str:
        logging.error("Azure Storage connection string is missing or invalid")
        return func.HttpResponse(
            "Azure Storage connection string is missing or invalid",
            status_code=500
        )
    container_name = 'podcaster-ssml'

    try:
        # Initialize Blob Service Client
        logging.info("Initializing Blob Service Client")
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_client = blob_service_client.get_container_client(container_name)

        # Download SSML file from Blob Storage
        logging.info(f"Downloading SSML file: {ssml_blob_name}")
        ssml_blob_client = container_client.get_blob_client(ssml_blob_name)
        ssml_content = ssml_blob_client.download_blob().readall().decode('utf-8')
        logging.info(f"Downloaded SSML content: {ssml_content[:100]}...")  # Log the first 100 characters

        # Validate SSML content
        if not ssml_content.strip().startswith("<speak"):
            logging.error("Invalid SSML content")
            return func.HttpResponse("Invalid SSML content", status_code=400)

        # Initialize Azure Speech Service
        logging.info("Initializing Azure Speech Service")
        speech_key = os.getenv('AZURE_SPEECH_KEY')
        service_region = os.getenv('AZURE_SERVICE_REGION')
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

        # Use a temporary file for the output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
            audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_audio_file.name)

            # Convert SSML to speech
            logging.info(f"Converting SSML to speech, output file: {temp_audio_file.name}")
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
            result = synthesizer.speak_ssml(ssml_content)

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logging.info("Speech synthesized for SSML from blob storage.")
            else:
                logging.error(f"Speech synthesis failed: {result.reason}")
                return func.HttpResponse(f"Speech synthesis failed: {result.reason}", status_code=500)

            # Verify the temporary file exists
            if os.path.exists(temp_audio_file.name):
                logging.info(f"Temporary audio file created: {temp_audio_file.name}")
            else:
                logging.error(f"Temporary audio file not found: {temp_audio_file.name}")
                return func.HttpResponse(f"Temporary audio file not found: {temp_audio_file.name}", status_code=500)

            # Upload the audio file to Blob Storage
            output_blob_name = f"{os.path.splitext(ssml_blob_name)[0]}.mp3"
            logging.info(f"Uploading audio file to Blob Storage: {output_blob_name}")
            output_blob_client = container_client.get_blob_client(output_blob_name)
            with open(temp_audio_file.name, "rb") as data:
                output_blob_client.upload_blob(data, overwrite=True)

            logging.info(f"Audio file {output_blob_name} created successfully.")

        # Clean up the temporary file
        os.remove(temp_audio_file.name)

        return func.HttpResponse(f"Audio file saved as {output_blob_name}", status_code=200)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return func.HttpResponse(f"An error occurred: {str(e)}", status_code=500)