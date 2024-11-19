import json
import logging
import azure.functions as func

def convert_to_ssml(script, voice_host1, voice_host2):
    ssml_start = "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
    ssml_end = "</speak>"
    
    lines = script.split('\n')
    ssml_content = ""
    
    for line in lines:
        if line.strip():
            speaker, text = line.split(": ", 1)
            if speaker == "Host 1":
                voice = voice_host1
            elif speaker == "Host 2":
                voice = voice_host2
            else:
                voice = "en-US-JennyNeural"  # Default voice
            ssml_content += f"<voice name='{voice}'><p>{text}</p></voice>\n"
    
    ssml = f"{ssml_start}\n{ssml_content}{ssml_end}"
    return ssml

app = func.FunctionApp()

@app.function_name(name="ConvertToSSML")
@app.route(route="ConvertToSSML", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def ConvertToSSML(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        logging.info(f"Request body: {req_body}")

        script = req_body.get('script')
        voice_host1 = req_body.get('voice_host1')
        voice_host2 = req_body.get('voice_host2')

        if not script or not voice_host1 or not voice_host2:
            logging.error("script, voice_host1, or voice_host2 is missing")
            return func.HttpResponse(
                json.dumps({"error": "Please provide script, voice_host1, and voice_host2 in the request body"}),
                status_code=400,
                mimetype="application/json"
            )

        # Convert script to SSML
        ssml_content = convert_to_ssml(script, voice_host1, voice_host2)
        logging.info(f"Generated SSML content: {ssml_content}")

        return func.HttpResponse(
            json.dumps({"ssml_content": ssml_content}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Exception: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )