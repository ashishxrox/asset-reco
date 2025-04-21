import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
from utils.fetch_assets import fetch_assets_for_location
from prompts.asset_prompts import get_asset_chat_recommendation_prompt
from utils.fetch_locations import fetch_locations_from_api
# from utils.infer_location_desc import infer_location_from_description

# Load environment variables
load_dotenv()
client = OpenAI()
MAX_CHARS = 1000

# Format asset list
def format_assets_list(assets):
    lines = []
    for asset in assets:
        line = f"- {asset['asset_name']} | ₹{asset['rate']}| {asset.get('details', 'N/A')} | {asset['company_name']}  | {asset.get('frequency', 'N/A')} | {asset.get('reach', 'N/A')} | {asset.get('asset_type', 'N/A')}"
        lines.append(line)
    return "\n".join(lines)

# Infer best-matching location
def infer_location_from_description(user_input, locations):
    location_names = [loc["company_name"] for loc in locations]
    location_list_text = "\n".join(f"- {name}" for name in location_names)

    print(location_names)

    prompt = (
        f"User campaign description:\n{user_input}\n\n"
        f"List of available locations:\n{location_list_text}\n\n"
        "Pick the most suitable location from the list above for the user's campaign needs. Respond with ONLY the location name."
    )

    print(prompt)

    try:
        response = client.chat.completions.create(
            model="o1-mini-2024-09-12",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Location inference failed: {e}")
        return None

# Page setup
st.set_page_config(page_title="Ad Asset Chat Recommender", page_icon="📍")
st.title("📍 Ad Asset Chat Recommender")

# Init state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_location" not in st.session_state:
    st.session_state.selected_location = None
if "formatted_assets" not in st.session_state:
    st.session_state.formatted_assets = None
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
if "location_suggestion" not in st.session_state:
    st.session_state.location_suggestion = None

# Sidebar reset
if st.sidebar.button("🧹 Start New Chat"):
    st.session_state.clear()
    st.rerun()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Describe your campaign or ask a follow-up")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    if not st.session_state.selected_location and not st.session_state.location_suggestion:
        locations = fetch_locations_from_api("")
        suggested_location_name = infer_location_from_description(user_input, locations)

        matched_location = next((loc for loc in locations if loc["company_name"].strip() == suggested_location_name), None)

        if matched_location:
            st.session_state.location_suggestion = matched_location
            assistant_msg = (
                f"Based on your campaign, I’d recommend running it in **{suggested_location_name}**.\n\n"
                "Would you like me to go ahead with this location?"
            )
        else:
            assistant_msg = "I couldn't confidently suggest a location. Could you please provide a bit more context?"

        st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
        with st.chat_message("assistant"):
            st.markdown(assistant_msg)

    elif not st.session_state.selected_location and st.session_state.location_suggestion:
        user_lower = user_input.strip().lower()
        confirm_phrases = ["yes", "yep", "go ahead", "confirm", "sure"]
        reject_phrases = ["no", "change", "something else", "different", "not sure"]

        if any(phrase in user_lower for phrase in confirm_phrases):
            st.session_state.selected_location = st.session_state.location_suggestion
            assets = fetch_assets_for_location(st.session_state.selected_location["location_id"])
            st.session_state.formatted_assets = format_assets_list(assets)
            assistant_msg = f"Great! We’ve locked in **{st.session_state.selected_location['company_name']}**. Let’s talk about your campaign goals and audience."

        elif any(phrase in user_lower for phrase in reject_phrases):
            st.session_state.location_suggestion = None
            assistant_msg = "No worries! Feel free to rephrase your campaign description, and I’ll suggest a different location."

        else:
            try:
                locations = fetch_locations_from_api("")
                location_names = [loc["company_name"] for loc in locations]
                location_list_text = "\n".join(f"- {name}" for name in location_names)

                prompt = (
                    f"The user is discussing a potential advertising campaign.\n"
                    f"Their original campaign description was:\n\n'''{st.session_state.messages[0]['content']}'''\n\n"
                    f"I previously recommended the location: {st.session_state.location_suggestion['company_name']}\n\n"
                    f"Here is a list of all available locations:\n{location_list_text}\n\n"
                    f"The user has now said:\n\n'''{user_input}'''\n\n"
                    f"Please respond thoughtfully, as if you’re helping them choose the most appropriate location for their brand."
                )

                response = client.chat.completions.create(
                    model="o1-mini-2024-09-12",
                    messages=[{"role": "user", "content": prompt}]
                )
                assistant_msg = response.choices[0].message.content.strip()
            except Exception as e:
                assistant_msg = f"Oops, couldn't generate a smart answer: {e}"

        st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
        with st.chat_message("assistant"):
            st.markdown(assistant_msg)

    elif st.session_state.selected_location and st.session_state.formatted_assets:
        selected_location = st.session_state.selected_location
        formatted_assets = st.session_state.formatted_assets
        asset_list_header = f"ASSET LIST:\n{formatted_assets}\n\n"

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
            "When not recommending assets do not respond in more than 1000 words. Use short and crisp pointers and keep the conversation to the point"
            "After recommending assets, answer all follow-up questions with your own judgment and understanding.\n"
            "Do not repeat the recommendation block again unless explicitly asked for it.\n"
            "Keep responses clear, friendly, and strategic—like a helpful teammate focused on the user's success.\n"
        )

        messages = [{"role": "user", "content": system_instruction}]
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                messages.append({"role": "user", "content": asset_list_header + msg["content"]})
            else:
                messages.append(msg)

        try:
            response = client.chat.completions.create(
                model="o1-mini-2024-09-12",
                messages=messages,
            )
            assistant_reply = response.choices[0].message.content

            if "<<RECOMMEND>>" in assistant_reply:
                last_user_input = st.session_state.messages[-1]["content"]
                rec_prompt = get_asset_chat_recommendation_prompt(last_user_input, formatted_assets)

                try:
                    rec_response = client.chat.completions.create(
                        model="o1-mini-2024-09-12",
                        messages=[{"role": "user", "content": rec_prompt}]
                    )
                    assistant_reply = rec_response.choices[0].message.content
                except Exception as inner_e:
                    st.error(f"Error while getting recommendations: {inner_e}")

            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
            with st.chat_message("assistant"):
                st.markdown(assistant_reply)

        except Exception as e:
            st.error(f"Error calling OpenAI API: {e}")