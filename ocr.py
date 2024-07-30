import json
import re
from tempfile import _TemporaryFileWrapper
from uuid import uuid4, UUID
from google.cloud import vision, storage
import logging
from tempfile import NamedTemporaryFile
import asyncio
import os
import vertex_pdf_ai

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/orbiszeus/metro_analyst/metro_analsyt_google_key.json"

logger = logging.getLogger(__name__)

client = vision.ImageAnnotatorClient()
storage_client = storage.Client()

vertexAI = vertex_pdf_ai.VertexAI()

def async_detect_document(gcs_source_uri, gcs_destination_uri):
    """OCR with PDF/TIFF as source files on GCS"""

    # Supported mime_types are: 'application/pdf' and 'image/tiff'
    mime_type = "application/pdf"

    # How many pages should be grouped into each json output file.
    batch_size = 1

    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

    gcs_source = vision.GcsSource(uri=gcs_source_uri)
    input_config = vision.InputConfig(gcs_source=gcs_source, mime_type=mime_type)

    gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
    output_config = vision.OutputConfig(
        gcs_destination=gcs_destination, batch_size=batch_size
    )

    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature], input_config=input_config, output_config=output_config
    )

    operation = client.async_batch_annotate_files(requests=[async_request])

    print("Waiting for the operation to finish.")
    operation.result(timeout=420)

    # Once the request has completed and the output has been
    # written to GCS, we can list all the output files.

    match = re.match(r"gs://([^/]+)/(.+)", gcs_destination_uri)
    bucket_name = match.group(1)  # type: ignore
    prefix = match.group(2)  # type: ignore

    bucket = storage_client.get_bucket(bucket_name)

    # List objects with the given prefix, filtering out folders.
    blob_list = [
        blob
        for blob in list(bucket.list_blobs(prefix=prefix))
        if not blob.name.endswith("/")
    ]
    text = ""
    print("Output files:")
    for blob in blob_list:
        print(blob.name)

    # Process the first output file from GCS.
    # Since we specified batch_size=2, the first response contains
    # the first two pages of the input file.
    for blob in blob_list:
        output = blob

        json_string = output.download_as_bytes().decode("utf-8")
        response = json.loads(json_string)

        # The actual response for the first page of the input file.

        # for response in response["responses"]:
        for page_response in response.get("responses", []):
            if "fullTextAnnotation" in page_response:
                text += page_response["fullTextAnnotation"]["text"]
        
    return text


async def process_uploaded_pdf(
    pdf_file: _TemporaryFileWrapper, pdf_content: bytes, id: UUID
):
    try:
        bucket_name = "file-storage23"
        # Create a new document instance and add it to the database

        # Modify the blob_name to be the document_id
        blob_name = f"{str(id)}.pdf"
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        logger.info(f"Uploading PDF file to gs://{bucket_name}/{blob_name}")
        blob.upload_from_string(pdf_content)

        logging.info(f"PDF file uploaded to gs://{bucket_name}/{blob_name}")

        # Update the storage_path in the database with the modified blob_name
        storage_path = f"gs://{bucket_name}/{blob_name}"
        
        '''
        This is where we are calling the vertexAI.
        '''
        # vertexAI.vertex_ai(storage_path)
        
        return {"gsc_uri": storage_path, "document_id": str(id)}
        # return storage_path
    except Exception as e:
        logging.error(f"Error uploading PDFs: {str(e)}")
        raise Exception(f"Error uploading PDFs: {str(e)}")
    
'''
TODO: 1. A while loop around all the menu items will take the place
      of the hard-coded pdf path.   
      2. After crawler finishes it's job it is going to call here.
'''
async def main():
    
    menu_dir = "/Users/orbiszeus/metro_analyst/restaurant_menus/"
    pdf_paths = [os.path.join(menu_dir, f) for f in os.listdir(menu_dir) if f.endswith('.pdf')]

    for pdf_path in pdf_paths:
        id = uuid4()

        # Read the PDF content
        with open("/Users/orbiszeus/metro_analyst/restaurant_menus/menu_ornek_1.pdf", "rb") as file:
            pdf_content = file.read()

        # Create a temporary file wrapper
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(pdf_content)
            temp_file_path = temp_file.name

        # Call the asynchronous function
        result = await process_uploaded_pdf(temp_file_path, pdf_content, id)
        print(result)

        # Define source and destination URIs for OCR
        gcs_source_uri = result["gsc_uri"]
        gcs_destination_uri = f"gs://file-storage23/output/{id}/"

        # Perform OCR on the uploaded PDF
        ocr_text = async_detect_document(gcs_source_uri, gcs_destination_uri)
        vertexAI.ask_gemini(ocr_text, gcs_source_uri)
        # print("OCR Text:", ocr_text)

if __name__ == "__main__":
    asyncio.run(main())