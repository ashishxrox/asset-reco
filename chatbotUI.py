import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
from utils.fetch_assets import fetch_assets_for_location
from utils.prompts import get_asset_chat_recommendation_prompt
from utils.fetch_locations import fetch_locations_from_api

# Load environment variables
load_dotenv()
client = OpenAI()  # Uses your OPENAI_API_KEY from .env
MAX_CHARS = 1000

# Format asset list
def format_assets_list(assets):
    lines = []
    for asset in assets:
        line = f"- Asset Name: {asset['asset_name']} | Asset Rate: ₹{asset['rate']}| Asset Details: {asset.get('details', 'N/A')} | Asset Location: {asset['company_name']}  | Frequency : {asset.get('frequency', 'N/A')} | Reach : {asset.get('reach', 'N/A')} | Asset Type: {asset.get('asset_type', 'N/A')} | Quantity: {asset.get('quantity', 'N/A')}"
        lines.append(line)
    return "\n".join(lines)

# Streamlit page setup
st.set_page_config(page_title="Ad Asset Chat Recommender", page_icon="📍")
st.title("📍 Ad Asset Chat Recommender")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_location" not in st.session_state:
    st.session_state.selected_location = None

if "formatted_assets" not in st.session_state:
    st.session_state.formatted_assets = None

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}

# Sidebar reset
if st.sidebar.button("🧹 Start New Chat"):
    st.session_state.clear()
    st.rerun()

# Step 1: Location selection (only once)
if st.session_state.selected_location is None:
    st.subheader("📍 Choose a Location")
    search_query = st.text_input("Search for a location")

    if search_query:
        locations = fetch_locations_from_api(search_query)
        if not locations:
            st.warning("No locations found for your search.")
            st.stop()

        location_name_map = {loc["company_name"]: loc for loc in locations if "company_name" in loc}
        selected_name = st.selectbox("Select from matching locations", list(location_name_map.keys()))
        selected_location = location_name_map[selected_name]

        if st.button("Confirm Location"):
            st.session_state.selected_location = selected_location
            assets = fetch_assets_for_location(selected_location["location_id"])
            st.session_state.formatted_assets = format_assets_list(assets)
            st.rerun()
else:
    selected_location = st.session_state.selected_location
    formatted_assets = st.session_state.formatted_assets

    st.markdown(f"**Location selected:** {selected_location['company_name']}")

    # Display prior chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Describe your campaign or ask a follow-up")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Build conversation context
        asset_list_header = (
            "ASSET LIST:\n"
            f"{formatted_assets}\n\n"
        )

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
        )


        # Prepare messages
        messages = [{"role": "user", "content": system_instruction}]

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                content = asset_list_header + msg["content"]
                messages.append({"role": "user", "content": content})
            else:
                messages.append(msg)

        try:
            response = client.chat.completions.create(
                model="o1-mini-2024-09-12",
                messages=messages,
            )
            assistant_reply = response.choices[0].message.content

            # If keyword found, switch to recommendation mode
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
            st.error(f"Error while calling OpenAI API: {e}")
