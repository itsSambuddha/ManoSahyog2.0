from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains for development

# Set your OpenAI API key here or set environment variable OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY", "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")

# Define the chatbot FSM in Python (can be used as fallback or context)
chatbot_fsm = {
    "START": {
        "message": "Hello! I'm here to help you with some Cognitive Behavioral Therapy (CBT) exercises. How are you feeling today?",
        "options": {
            "i'm feeling okay": "FEELING_OKAY",
            "i'm feeling a bit down": "FEELING_DOWN",
            "i'm not sure": "FEELING_UNSURE"
        }
    },
    "FEELING_OKAY": {
        "message": "That's good to hear! Would you like to try a simple thought challenging exercise, or perhaps a gratitude practice? (Type 'Thought Challenging' or 'Gratitude Practice')",
        "options": {
            "thought challenging": "THOUGHT_CHALLENGE_INTRO",
            "gratitude practice": "GRATITUDE_INTRO",
            "maybe later": "END_NORMAL"
        }
    },
    "FEELING_DOWN": {
        "message": "I understand. Sometimes, exploring our thoughts can help. Would you like to try a thought record exercise, or something to help with activity scheduling? (Type 'Thought Record' or 'Activity Scheduling')",
        "options": {
            "thought record": "THOUGHT_RECORD_INTRO",
            "activity scheduling": "ACTIVITY_SCHEDULING_INTRO",
            "not right now": "END_GENTLE"
        }
    },
    "FEELING_UNSURE": {
        "message": "That's perfectly fine. Sometimes just taking a moment to breathe can be helpful. Would you like to do a quick breathing exercise? (Type 'Yes' or 'No')",
        "options": {
            "yes": "BREATHING_EXERCISE",
            "no": "END_NORMAL"
        }
    },
    "END_NORMAL": {
        "message": "Okay, thanks for checking in. Remember, these tools are here if you need them. Have a good day!",
        "options": {}
    },
    "END_GENTLE": {
        "message": "That's alright. Take your time. Remember to be kind to yourself. If you feel like talking more later, I'm here.",
        "options": {}
    }
    # Additional states can be added here as needed
}

def call_ai_service(current_state, user_input):
    # Example call to OpenAI ChatCompletion API
    prompt = f"Current state: {current_state}\nUser input: {user_input}\nRespond as a helpful CBT chatbot."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful Cognitive Behavioral Therapy chatbot."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        message = response.choices[0].message.content.strip()
        return message
    except Exception as e:
        print(f"OpenAI API error: {e}")
        # Fallback message
        return "Sorry, I'm having trouble responding right now. Please try again later."

def find_next_state(current_state, user_input):
    state_data = chatbot_fsm.get(current_state)
    if not state_data:
        return "START", chatbot_fsm["START"]["message"]

    options = state_data.get("options", {})
    user_input_lower = user_input.strip().lower()

    for option_text, next_state in options.items():
        if option_text in user_input_lower:
            next_state_data = chatbot_fsm.get(next_state)
            if next_state_data:
                return next_state, next_state_data["message"]
    # If no match, return unrecognized input message or fallback
    return "UNRECOGNIZED_INPUT", "I'm not sure how to respond to that. Would you like to try rephrasing, or go back to the main menu?"

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    current_state = data.get('stateId', 'START')
    user_input = data.get('userInput', '')

    # Call AI API to generate dynamic response
    response_message = call_ai_service(current_state, user_input)

    # Optionally, you can update the state based on AI response or keep FSM logic
    next_state, _ = find_next_state(current_state, user_input)

    response = {
        "nextStateId": next_state,
        "message": response_message
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
