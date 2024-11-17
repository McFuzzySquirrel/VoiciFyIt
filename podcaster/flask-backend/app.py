# flask-backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

logging.basicConfig(level=logging.DEBUG)

@app.route('/api/process-ssml', methods=['POST'])
def process_ssml():
    data = request.json
    ssml_content = data.get('ssmlContent')
    ssml_file_name = data.get('ssmlFileName')
    mp3_file_name = data.get('mp3FileName')
    logging.debug(f"Received SSML content: {ssml_content}")
    
    # Call your Azure Function here
    try:
        response = requests.post('https://mcfuzzypodcaster.azurewebsites.net/api/process-ssml', json={
            'ssml_content': ssml_content,
            'ssml_file_name': ssml_file_name,
            'mp3_file_name': mp3_file_name
        })
        response.raise_for_status()  # Raise an error for bad status codes
        response_json = response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"RequestException: {e}")
        logging.error(f"Response content: {response.text if response else 'No response'}")
        return jsonify({'error': 'Failed to call Azure Function'}), 500
    except requests.exceptions.JSONDecodeError as e:
        logging.error(f"JSONDecodeError: {e}")
        logging.error(f"Response content: {response.text}")
        return jsonify({'error': 'Invalid JSON response from Azure Function'}), 500

    return jsonify(response_json)

if __name__ == '__main__':
    app.run(debug=True)