import os
import json
from quart import Quart, request, jsonify, Response
import azure_form_recognizer
import blob_access_azure

app = Quart(__name__)

blob_access = blob_access_azure.AzureBlobAccess()

@app.route('/get_blob_list', methods=['GET'])
async def get_blob_list():
    """
    Retrieve and return the list of blobs in the specified container.

    :return: JSON response containing the list of blobs.
    :rtype: Response
    """
    try:
        return jsonify(blob_access.get_blob_list(os.environ['AZURE_CONTAINER_NAME']))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/get_blob_url', methods=['GET'])
async def get_blob_url():
    """
    Retrieve and return the URL of the blob with a SAS token appended for secure access.

    :return: JSON response containing the blob URL.
    :rtype: Response
    """
    try:
        return jsonify(blob_access.get_blob_url(os.environ['AZURE_CONTAINER_NAME']))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_content_from_blob', methods=['POST'])
async def get_content_from_blob():
    """
    Handle the POST request to retrieve content from a blob URL and stream JSON response.

    :return: Streaming JSON response containing the analyzed form content.
    :rtype: Response
    """
    try:
        data = await request.get_json()
        blob_url = data.get('blob_url')
        
        if not blob_url:
            return jsonify({'error': 'blob_url is missing'}), 400

        document_intelligence = azure_form_recognizer.AzureFormRecognizerUtils(form_url=blob_url)

        async def generate():
            try:
                for page in document_intelligence.get_content():
                    yield json.dumps({'content': page})
            except Exception as e:
                yield json.dumps({'error': str(e)})

        return Response(generate(), content_type='application/json')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_tables_from_blob', methods=['POST'])
async def get_tables_from_blob():
    """
    Handle the POST request to retrieve tables from a blob URL and stream JSON response.

    :return: Streaming JSON response containing the table content.
    :rtype: Response
    """
    try:
        data = await request.get_json()
        blob_url = data.get('blob_url')

        if not blob_url:
            return jsonify({'error': 'blob_url is missing'}), 400

        document_intelligence = azure_form_recognizer.AzureFormRecognizerUtils(form_url=blob_url)

        async def generate():
            try:
                for table in document_intelligence.get_tables():
                    yield json.dumps({'table': table})
            except Exception as e:
                yield json.dumps({'error': str(e)})

        return Response(generate(), content_type='application/json')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
