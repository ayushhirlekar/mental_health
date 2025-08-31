from app import create_app
from flask import request, jsonify
from database.database import create_session, save_turn, get_session_turns
from services.ai_service import MentalHealthAI

app = create_app()

# Load AI model once when server starts (this takes 30-60 seconds)
print("🚀 Starting Mental Health Assistant with AI...", flush=True)
ai_service = MentalHealthAI()

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'Zenya AI backend is running! 💙'}

@app.route('/')
def home():
    return {'message': 'Mental Health Assistant API with AI', 'status': 'ready'}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    session_id = data.get('session_id')

    if not session_id:
        session_id = create_session()

    # Save user's message
    save_turn(session_id, 'user', user_message)

    # Get conversation history for AI context
    conversation = get_session_turns(session_id)
    
    # Generate AI response using conversation context
    print(f"🧠 Generating AI response for: {user_message[:50]}...", flush=True)
    assistant_reply = ai_service.generate_response(user_message, 
                                                 [dict(row) for row in conversation])

    # Save assistant response
    save_turn(session_id, 'assistant', assistant_reply)

    # Get updated conversation
    updated_conversation = get_session_turns(session_id)

    return jsonify({
        'session_id': session_id,
        'reply': assistant_reply,
        'conversation': [dict(row) for row in updated_conversation]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
