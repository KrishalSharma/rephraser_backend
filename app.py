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
    You are an expert email editor. Your task is to refine the following email draft to make it more professional and polite, paying special attention to the greeting.

    Follow these rules for the greeting:
    1.  **If the draft already has a formal greeting** (like "Dear Professor," or "Dear Dr. Smith,"), keep that greeting exactly as it is.
    2.  **If the draft has a casual greeting** (like "Hi Kashish" or "Hey team"), change it to its formal equivalent (e.g., "Dear Kashish,").
    3.  **If the draft has no greeting,** do not add one.
    
    After handling the greeting, rephrase the rest of the email body to be more formal, clear, and professional. Correct any grammar or spelling mistakes. Do not add a sign-off like "Sincerely,".
    
    Original Draft:
    "{original_text}"
    
    Refined Email:
    """

    try:
        response = model.generate_content(prompt)
        # Return the rephrased text in a JSON object
        return jsonify({'rephrased_text': response.text.strip()})
    except Exception as e:
        print(f"An error occurred while contacting the AI model: {e}")
        return jsonify({'error': 'Failed to get a response from the AI model.'}), 500
