from flask import Flask, request, jsonify, session
from flask_session import Session
from flask_cors import CORS
import os
import json
import uuid
from openai import OpenAI
from dotenv import load_dotenv
from utils.prompts import get_asset_chat_recommendation_prompt


load_dotenv()
client = OpenAI()

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Temporary in-memory store
conversation_assets = {}

@app.route("/init-chat", methods=["POST"])
def init_chat():
    data = request.json
    asset_list = data.get("asset_list")

    if not asset_list:
        return jsonify({"error": "Asset list is required"}), 400

    conversation_id = str(uuid.uuid4())
    conversation_assets[conversation_id] = asset_list
    # print(conversation_assets)

    return jsonify({"conversation_id": conversation_id})


# System instruction to be added only once
system_instruction = (
    "You are an expert media planner helping brands choose advertising assets.\n"
    "You're curious and passionate about understanding the brand, their goals, and target audience.\n"
    "Ask 1-2 friendly follow-up questions to understand their budget, campaign duration, product, or audience better—especially if the query is vague.\n"
    "If the prompt is clear and clean, with all the data we need there is no need of follow up questions"
    "Make sure you keep asking questions till you dont have knowedge about what their brand is about, what their budget is, what are they trying to sell and who they are trying to sell.\n"
    "First understand what the brand is like what they sell and who they sell then ask questions about the campign and budget.\n"
    "Never proceed to recommend assets unless you fully understand:\n"
    "- What the brand sells\n"
    "- Who their audience is\n"
    "- Their campaign goals (awareness/sales/etc.)\n"
    "- Their budget or at least duration and scale\n"
    "If the user sounds confused first ask clarifying questions to understand their need better"
    "Don't ask any questions related to city or location of the campaign"
    "If the user asks 'what should be my ideal budget?', DO NOT recommend assets yet.\n"
    "Instead, ask clarifying questions like:\n"
    "- How long is the campaign intended to run?\n"
    "Once you have enough detail, suggest a realistic budget range (e.g., ₹25,000–₹50,000).\n"
    "If there are no assets within the budget tell them the same and ask them to increase it or try choosing a different location"
    "ONLY AFTER the user agrees to that range or asks for recommendations, proceed to recommend 2–3 assets.\n"
    "Do not disclose about the asset list to the user"
    "Use the keyword <<RECOMMEND>> before the first recommendation block.\n"
    "You must use <<RECOMMEND>> ONLY ONCE. Never use it again in the same conversation.\n"
    "After recommending assets, answer all follow-up questions with your own judgment and understanding.\n"
    "Do not repeat the recommendation block again unless explicitly asked for it.\n"
    "Keep responses clear, friendly, and strategic—like a helpful teammate focused on the user's success.\n"
    "Keep your responses concise. Avoid large markdown blocks. Do Not use very huge sized texts. Do not use heading style for parahraphs"
)
messages = [{"role": "user", "content": system_instruction}]






@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("user_input", "")
    conversation_id = data.get("conversation_id")
    
    # Check for a new conversation or hard refresh (by checking for missing conversation_id)
    if not conversation_id or conversation_id not in conversation_assets:
        session.clear()  # Clear the session to reset it
        return jsonify({"error": "Invalid or missing conversation_id"}), 400

    asset_list_raw = conversation_assets[conversation_id]

    asset_list_header = (
            "ASSET LIST:\n"
            f"{asset_list_raw}\n\n"
        )

    # Initialize session messages if it's the first conversation
    if "messages" not in session:
        session["messages"] = []
    
    # Append user input to the session
    if len(session["messages"]) == 0:
        session["messages"] = [{"role": "user", "content": user_input}]
    else:
        session["messages"].append({"role": "user", "content": user_input})
    
    # messages = []
    # Add user input with asset list context
    for msg in session["messages"]:
        if msg["role"] == "user":
            content = asset_list_header + msg["content"]
            messages.append({"role": "user", "content": content})
        else:
            messages.append(msg)

    try:
        # for m in messages:
        #     print(m["role"])
        #     print(m["content"])
        # print(session)
        response = client.chat.completions.create(
            model="o1-mini-2024-09-12",
            messages=messages,
        )

        assistant_reply = response.choices[0].message.content

        # Handle recommendation trigger
        if "<<RECOMMEND>>" in assistant_reply:
            rec_prompt = get_asset_chat_recommendation_prompt(user_input, asset_list_raw)
            rec_response = client.chat.completions.create(
                model="o1-mini-2024-09-12",
                messages=[{"role": "user", "content": rec_prompt}]
            )
            assistant_reply = rec_response.choices[0].message.content

        session["messages"].append({"role": "assistant", "content": assistant_reply})
        messages.append({"role": "assistant", "content": assistant_reply})

        return jsonify({"reply": assistant_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True)
