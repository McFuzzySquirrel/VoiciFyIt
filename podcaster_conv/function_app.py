import azure.functions as func
import logging
import os
import json
from azure.storage.blob import BlobServiceClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest
from markdownify import markdownify as md

BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME", "default-container-name")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
FORM_RECOGNIZER_ENDPOINT = os.getenv("FORM_RECOGNIZER_ENDPOINT")
FORM_RECOGNIZER_KEY = os.getenv("FORM_RECOGNIZER_KEY")

blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
document_intelligence_client = DocumentIntelligenceClient(endpoint=FORM_RECOGNIZER_ENDPOINT, credential=AzureKeyCredential(FORM_RECOGNIZER_KEY))

app = func.FunctionApp()

def get_words(page, line):
    result = []
    for word in page.words:
        if _in_span(word, line.spans):
            result.append(word)
    return result

def _in_span(word, spans):
    for span in spans:
        if word.span.offset >= span.offset and (word.span.offset + word.span.length) <= (span.offset + span.length):
            return True
    return False

@app.route(route="ProcessDocument", auth_level=func.AuthLevel.ANONYMOUS)
def ProcessDocument(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Get the uploaded file
        file = req.files.get('file')
        if not file:
            return func.HttpResponse(
                json.dumps({"error": "Please upload a file"}),
                status_code=400,
                mimetype="application/json"
            )

        # Save the file to Azure Blob Storage
        blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=file.filename)
        blob_client.upload_blob(file.stream.read(), overwrite=True)

        # Verify the URL of the uploaded file
        blob_url = blob_client.url
        logging.info(f"Blob URL: {blob_url}")

        # Analyze the document using Azure AI Document Intelligence
        poller = document_intelligence_client.begin_analyze_document("prebuilt-layout", AnalyzeDocumentRequest(url_source=blob_url))
        result: AnalyzeResult = poller.result()

        # Extract text from the document
        extracted_text = ""
        for page in result.pages:
            extracted_text += f"----Analyzing layout from page #{page.page_number}----\n"
            extracted_text += f"Page has width: {page.width} and height: {page.height}, measured with unit: {page.unit}\n"

            if page.lines:
                for line_idx, line in enumerate(page.lines):
                    words = get_words(page, line)
                    extracted_text += f"...Line # {line_idx} has word count {len(words)} and text '{line.content}' within bounding polygon '{line.polygon}'\n"
                    for word in words:
                        extracted_text += f"......Word '{word.content}' has a confidence of {word.confidence}\n"

            if page.selection_marks:
                for selection_mark in page.selection_marks:
                    extracted_text += f"Selection mark is '{selection_mark.state}' within bounding polygon '{selection_mark.polygon}' and has a confidence of {selection_mark.confidence}\n"

        if result.tables:
            for table_idx, table in enumerate(result.tables):
                extracted_text += f"Table # {table_idx} has {table.row_count} rows and {table.column_count} columns\n"
                if table.bounding_regions:
                    for region in table.bounding_regions:
                        extracted_text += f"Table # {table_idx} location on page: {region.page_number} is {region.polygon}\n"
                for cell in table.cells:
                    extracted_text += f"...Cell[{cell.row_index}][{cell.column_index}] has text '{cell.content}'\n"
                    if cell.bounding_regions:
                        for region in cell.bounding_regions:
                            extracted_text += f"...content on page {region.page_number} is within bounding polygon '{region.polygon}'\n"

        # Convert extracted text to Markdown
        markdown_text = md(extracted_text)

        return func.HttpResponse(
            json.dumps({"markdown_text": markdown_text}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error processing document: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )