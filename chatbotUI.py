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
        line = f"- {asset['asset_name']} | ₹{asset['rate']} | {asset['company_name']}  | {asset.get('frequency', 'N/A')} | {asset.get('reach', 'N/A')} | {asset.get('asset_type', 'N/A')}"
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
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Build chat history for OpenAI
        # Inject system context into the user's first message
        # Inject asset list every time as context
        asset_list_header = (
            "ASSET LIST:\n"
            f"{formatted_assets}\n\n"
        )

        system_instruction = (
            "You are an expert media planner helping brands choose advertising assets.\n"
            "Only suggest assets from the provided ASSET LIST. Do not make up new ones or mention digital ad platforms.\n"
            "Be specific, insightful, and helpful based on the budget and brand intent described.\n"
            "Keep responses short, concise, and to the point. Avoid unnecessary elaboration.\n"
        )

        messages = []

        for i, msg in enumerate(st.session_state.messages):
            # First message: combine system + asset list + user query
            if i == 0:
                combined = system_instruction + "\n" + asset_list_header + msg["content"]
                messages.append({"role": "user", "content": combined})
            else:
                # In follow-ups: prepend asset list silently
                if msg["role"] == "user":
                    content = asset_list_header + msg["content"]
                    messages.append({"role": "user", "content": content})
                else:
                    messages.append(msg)



        # First turn only: inject full asset prompt
        if len(st.session_state.messages) == 1:
            custom_prompt = get_asset_chat_recommendation_prompt(user_input, formatted_assets)
            messages[-1]["content"] = custom_prompt

        try:
            response = client.chat.completions.create(
                model="o1-mini-2024-09-12",
                messages=messages,
            )
            assistant_reply = response.choices[0].message.content

            # Show assistant reply
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
            with st.chat_message("assistant"):
                st.markdown(assistant_reply)

        except Exception as e:
            st.error(f"Error while calling OpenAI API: {e}")
