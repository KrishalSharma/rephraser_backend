import os
from flask import Flask, request, jsonify
import google.generativeai as genai

# Initialize Flask App
app = Flask(__name__)

# --- AI Model Configuration ---
# The API key will be read from the server's environment variables for security
api_key = os.environ.get('GOOGLE_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
else:
    print("API Key not found. Please set GOOGLE_API_KEY environment variable.")

# This is the main API endpoint that the Google Add-on will call
@app.route('/rephrase', methods=['POST'])
def rephrase_endpoint():
    """Receives text, rephrases it, and returns it as JSON."""
    
    # Check if the AI model was configured correctly
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"Error initializing model: {e}")
        return jsonify({'error': 'AI model could not be initialized. Check API Key.'}), 500

    # Get the text from the incoming request
    data = request.get_json()
    original_text = data.get('text', '')

    if not original_text:
        return jsonify({'rephrased_text': ''}) # Return empty if no text provided

    # This is the instruction given to the AI.
    prompt = f"""
    You are a professional communication assistant.
    Your task is to rephrase the following email draft to make it more formal, polite, clear, and professional.
    Correct any grammar or spelling mistakes.
    Do not add a salutation like "Dear Sir" or "Hello". Just rephrase the main content.
    The tone should be suitable for writing to a professor, a manager, or a corporate contact.

    Original Draft:
    "{original_text}"

    Rephrased Professional Draft:
    """

    try:
        response = model.generate_content(prompt)
        # Return the rephrased text in a JSON object
        return jsonify({'rephrased_text': response.text.strip()})
    except Exception as e:
        print(f"An error occurred while contacting the AI model: {e}")
        return jsonify({'error': 'Failed to get a response from the AI model.'}), 500