from flask import Flask, request, jsonify
from flask_cors import CORS
import g4f
import re
import uuid
import json
import os

app = Flask(__name__)
CORS(app)

# Developer credit
DEVELOPER = "Bn0mar"

# Store conversation history with unique session IDs
conversation_memory = {}

# Function to extract code blocks from text
def extract_code_blocks(text):
    # Pattern to match code blocks (text between triple backticks)
    pattern = r"```(?:\w+)?\n([\s\S]*?)```"
    
    # Find all code blocks
    code_blocks = re.findall(pattern, text)
    
    # Replace code blocks with placeholders to get clean text
    clean_text = re.sub(pattern, "[CODE_BLOCK]", text)
    
    return {
        "text": clean_text,
        "code_blocks": code_blocks
    }

# Get all available models from g4f
def get_available_models():
    try:
        providers = [provider.__name__ for provider in g4f.Provider.__all__]
        models = [model.name for model in g4f.models.Model]
        return {
            "providers": providers,
            "models": models
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/models', methods=['GET'])
def models():
    """Returns all available models and providers from g4f"""
    return jsonify(get_available_models())

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        
        # Get user input
        user_input = data.get('text', '')
        
        # Get session ID (create if not exists)
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Get selected model (use default if not specified)
        model_name = data.get('model', 'gpt-3.5-turbo')
        
        # Initialize conversation if this is a new session
        if session_id not in conversation_memory:
            conversation_memory[session_id] = [
                {"role": "system", "content": f"You are an AI assistant developed by {DEVELOPER}. You're helpful, creative, and able to understand and respond in multiple languages. When sharing code examples, always format them properly with triple backticks and language specifiers."}
            ]
        
        # Add user message to conversation history
        conversation_memory[session_id].append({"role": "user", "content": user_input})
        
        # Select the model
        try:
            model = getattr(g4f.models, model_name, g4f.models.gpt_35_turbo)
        except:
            model = g4f.models.gpt_35_turbo
        
        # Generate response
        response = g4f.ChatCompletion.create(
            model=model,
            messages=conversation_memory[session_id],
            stream=False
        )
        
        # Process response to separate code blocks
        processed_response = extract_code_blocks(response)
        
        # Add AI response to conversation history
        conversation_memory[session_id].append({"role": "assistant", "content": response})
        
        # Return processed response with session ID
        return jsonify({
            "response": response,
            "processed": processed_response,
            "session_id": session_id
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to clear a specific conversation
@app.route('/clear-conversation', methods=['POST'])
def clear_conversation():
    data = request.json
    session_id = data.get('session_id')
    
    if session_id and session_id in conversation_memory:
        del conversation_memory[session_id]
        return jsonify({"status": "success", "message": "Conversation cleared"})
    
    return jsonify({"status": "error", "message": "Session ID not found"}), 404

# Route to get conversation history
@app.route('/conversation-history', methods=['GET'])
def get_conversation():
    session_id = request.args.get('session_id')
    
    if session_id and session_id in conversation_memory:
        return jsonify({
            "history": conversation_memory[session_id],
            "session_id": session_id
        })
    
    return jsonify({"status": "error", "message": "Session ID not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
