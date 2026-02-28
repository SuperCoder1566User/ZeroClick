import os
from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv

# Load .env for local testing, but Vercel will use Environment Variables
load_dotenv()

# We tell Flask that the static and template folders are one level UP (..) 
# because this file is now inside the /api folder.
app = Flask(__name__, 
            template_folder='../templates', 
            static_folder='../static')

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get("query")

    if not user_input or len(user_input) < 2:
        return jsonify({"answer": "", "suggestions": []})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # I updated this to a current Groq model
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a fast autocomplete engine. "
                        "Return ONLY JSON: "
                        "{'answer':'short result','suggestions':['3 short related queries']}"
                    )
                },
                {"role": "user", "content": user_input}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )

        # Groq returns a string, so we return it directly as it is already JSON
        return completion.choices[0].message.content

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"answer": "Error", "suggestions": ["Try again"]}), 500

@app.route('/dictionary', methods=['POST'])
def dictionary():
    user_input = request.json.get("query", "").strip()

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return ONLY JSON: "
                        "{'Page_title':'...', 'paragraph_1':'...', 'paragraph_2':'...'} "
                        "Provide two detailed paragraphs."
                    )
                },
                {"role": "user", "content": user_input}
            ],
            response_format={"type": "json_object"}
        )

        return completion.choices[0].message.content

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "Page_title": "Error",
            "paragraph_1": "Could not reach library.",
            "paragraph_2": ""
        }), 500

# This is required for Vercel to treat this as a serverless function
app.debug = False
